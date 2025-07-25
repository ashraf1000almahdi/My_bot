import logging
import requests
import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from app import app, db
from models import User, Download, BotStats
from config import Config
from video_downloader import VideoDownloader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    def __init__(self):
        self.bot_token = Config.BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.video_downloader = VideoDownloader()
        self.running = False
        self.last_update_id = 0
        
    def send_message(self, chat_id, text, reply_markup=None):
        """Send a message to a chat"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def edit_message(self, chat_id, message_id, text):
        """Edit a message"""
        url = f"{self.base_url}/editMessageText"
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return None
    
    def send_video(self, chat_id, video_path, caption=None):
        """Send a video file"""
        url = f"{self.base_url}/sendVideo"
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {'chat_id': chat_id}
                if caption:
                    data['caption'] = caption
                
                response = requests.post(url, files=files, data=data)
                return response.json()
        except Exception as e:
            logger.error(f"Error sending video: {e}")
            return None
    
    def get_updates(self):
        """Get updates from Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {
            'offset': self.last_update_id + 1,
            'limit': 100,
            'timeout': 30
        }
        
        try:
            response = requests.get(url, params=params, timeout=35)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return None
    
    def check_subscription(self, user_id):
        """Check if user is subscribed to the channel"""
        url = f"{self.base_url}/getChatMember"
        params = {
            'chat_id': Config.CHANNEL_ID,
            'user_id': user_id
        }
        
        try:
            response = requests.get(url, params=params)
            result = response.json()
            
            if result.get('ok'):
                status = result['result']['status']
                return status in ['member', 'administrator', 'creator']
            return False
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            return False
    
    def handle_start(self, chat_id, user_data):
        """Handle /start command"""
        user_id = user_data['id']
        
        # Create or update user in database
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                db_user = User(
                    telegram_id=user_id,
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name')
                )
                db.session.add(db_user)
            else:
                db_user.username = user_data.get('username')
                db_user.first_name = user_data.get('first_name')
                db_user.last_name = user_data.get('last_name')
            
            db.session.commit()
        
        # Check subscription
        is_subscribed = self.check_subscription(user_id)
        
        if is_subscribed:
            self.send_main_menu(chat_id)
        else:
            self.send_subscription_message(chat_id)
    
    def send_main_menu(self, chat_id):
        """Send main menu with all options"""
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📥 تحميل فيديو", "callback_data": "download_video"},
                    {"text": "📊 إحصائياتي", "callback_data": "my_stats"}
                ],
                [
                    {"text": "⚙️ الإعدادات", "callback_data": "settings_menu"},
                    {"text": "❓ المساعدة", "callback_data": "help_menu"}
                ],
                [
                    {"text": "ℹ️ حول البوت", "callback_data": "about_menu"},
                    {"text": "📊 إحصائيات عامة", "callback_data": "global_stats"}
                ],
                [
                    {"text": "📢 القناة الرسمية", "url": "https://t.me/hackrs98"},
                    {"text": "👨‍💻 المطور", "url": "https://t.me/A_H_a_h_a_h_a_hn"}
                ]
            ]
        }
        
        welcome_message = f"""
🎬 مرحباً بك في بوت تحميل الفيديوهات المحترف!

⚡ البوت يدعم تحميل الفيديوهات من جميع المنصات الشائعة:
• YouTube • Instagram • TikTok • Twitter
• Facebook • Vimeo • وغيرها الكثير!

🔥 الميزات:
✅ تحميل بجودات متعددة (144p إلى 1080p)
✅ صيغ مختلفة (MP4, MP3, WEBM, AVI)
✅ واجهة عربية كاملة
✅ تحميلات غير محدودة!

اختر من القائمة أدناه:
        """
        
        self.send_message(chat_id, welcome_message, keyboard)
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id == Config.ADMIN_ID
    
    def handle_admin_panel(self, chat_id):
        """Handle admin panel command"""
        try:
            with app.app_context():
                total_users = User.query.count()
                total_downloads = Download.query.count()
                successful_downloads = Download.query.filter_by(status='completed').count()
                
                message = Config.MESSAGES['admin_panel'].format(
                    total_users, total_downloads, successful_downloads
                )
                
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "📊 إحصائيات مفصلة", "callback_data": "admin_detailed_stats"},
                            {"text": "👥 إدارة المستخدمين", "callback_data": "admin_users"}
                        ],
                        [
                            {"text": "📢 إرسال رسالة", "callback_data": "admin_broadcast"},
                            {"text": "🧹 تنظيف الملفات", "callback_data": "admin_cleanup"}
                        ],
                        [
                            {"text": "🚫 حظر مستخدم", "callback_data": "admin_ban"},
                            {"text": "✅ إلغاء حظر", "callback_data": "admin_unban"}
                        ],
                        [
                            {"text": "↩️ العودة للقائمة", "callback_data": "back_to_main"}
                        ]
                    ]
                }
                
                self.send_message(chat_id, message, keyboard)
        except Exception as e:
            logger.error(f"Error in admin panel: {e}")
            self.send_message(chat_id, "حدث خطأ في لوحة الإدارة")
    
    def handle_broadcast(self, chat_id, message_text):
        """Broadcast message to all users"""
        try:
            with app.app_context():
                users = User.query.filter_by(is_active=True).all()
                sent_count = 0
                failed_count = 0
                
                for user in users:
                    try:
                        self.send_message(user.telegram_id, message_text)
                        sent_count += 1
                    except:
                        failed_count += 1
                
                result_message = f"""
📢 نتائج الإرسال:
✅ تم الإرسال: {sent_count}
❌ فشل: {failed_count}
📊 إجمالي: {len(users)}
                """
                self.send_message(chat_id, result_message)
        except Exception as e:
            logger.error(f"Error in broadcast: {e}")
            self.send_message(chat_id, "حدث خطأ في الإرسال")
    
    def handle_ban_user(self, user_id):
        """Ban a user"""
        try:
            with app.app_context():
                user = User.query.filter_by(telegram_id=user_id).first()
                if user:
                    user.is_active = False
                    db.session.commit()
                    return True
        except Exception as e:
            logger.error(f"Error banning user: {e}")
        return False
    
    def handle_unban_user(self, user_id):
        """Unban a user"""
        try:
            with app.app_context():
                user = User.query.filter_by(telegram_id=user_id).first()
                if user:
                    user.is_active = True
                    db.session.commit()
                    return True
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
        return False
    
    def cleanup_old_files(self):
        """Clean up old downloaded files"""
        try:
            import os
            import time
            downloads_path = Config.DOWNLOAD_PATH
            if os.path.exists(downloads_path):
                deleted_count = 0
                total_size = 0
                
                for filename in os.listdir(downloads_path):
                    file_path = os.path.join(downloads_path, filename)
                    if os.path.isfile(file_path):
                        file_age = time.time() - os.path.getmtime(file_path)
                        # Delete files older than 24 hours
                        if file_age > 86400:  # 24 hours in seconds
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted_count += 1
                            total_size += file_size
                
                return deleted_count, total_size / (1024 * 1024)  # MB
        except Exception as e:
            logger.error(f"Error cleaning files: {e}")
        return 0, 0
    
    def handle_admin_detailed_stats(self, chat_id):
        """Handle detailed admin statistics"""
        try:
            with app.app_context():
                total_users = User.query.count()
                active_users = User.query.filter_by(is_active=True).count()
                banned_users = User.query.filter_by(is_active=False).count()
                
                total_downloads = Download.query.count()
                successful_downloads = Download.query.filter_by(status='completed').count()
                failed_downloads = Download.query.filter_by(status='failed').count()
                
                today = datetime.utcnow().date()
                today_downloads = Download.query.filter(
                    Download.created_at >= today
                ).count()
                
                # Calculate file statistics
                import os
                downloads_path = Config.DOWNLOAD_PATH
                file_count = 0
                total_size = 0
                
                if os.path.exists(downloads_path):
                    for filename in os.listdir(downloads_path):
                        file_path = os.path.join(downloads_path, filename)
                        if os.path.isfile(file_path):
                            file_count += 1
                            total_size += os.path.getsize(file_path)
                
                total_size_mb = total_size / (1024 * 1024)
                
                message = Config.MESSAGES['admin_stats'].format(
                    total_users, active_users, banned_users,
                    total_downloads, successful_downloads, failed_downloads, today_downloads,
                    file_count, total_size_mb
                )
                
                self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Error getting detailed stats: {e}")
            self.send_message(chat_id, "حدث خطأ في جلب الإحصائيات المفصلة")
    
    def handle_admin_users(self, chat_id):
        """Handle admin users management"""
        try:
            with app.app_context():
                recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
                
                message = "👥 آخر 10 مستخدمين:\n\n"
                for user in recent_users:
                    status = "✅ نشط" if user.is_active else "🚫 محظور"
                    subscription_status = "⭐ مشترك" if user.is_subscribed else "❌ غير مشترك"
                    display_name = user.display_name() or "بدون اسم"
                    
                    message += f"👤 {display_name}\n"
                    message += f"🆔 {user.telegram_id}\n"
                    message += f"📊 {status} | {subscription_status}\n"
                    message += f"📅 {user.created_at.strftime('%Y-%m-%d')}\n\n"
                
                message += "\n💡 لحظر مستخدم: /ban <user_id>"
                message += "\n💡 لإلغاء الحظر: /unban <user_id>"
                
                self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            self.send_message(chat_id, "حدث خطأ في جلب المستخدمين")
    
    def send_subscription_message(self, chat_id):
        """Send subscription required message"""
        keyboard = {
            'inline_keyboard': [
                [{'text': '✅ تحقق من الاشتراك', 'callback_data': 'check_subscription'}],
                [{'text': '📢 اشترك في القناة', 'url': f'https://t.me/{Config.CHANNEL_USERNAME}'}]
            ]
        }
        
        self.send_message(chat_id, Config.MESSAGES['not_subscribed'], keyboard)
    
    def handle_download(self, chat_id, user_id):
        """Handle /download command"""
        # Check subscription
        if not self.check_subscription(user_id):
            self.send_subscription_message(chat_id)
            return
        
        # Daily limit disabled - unlimited downloads
        # if not self.check_daily_limit(user_id):
        #     self.send_message(chat_id, Config.MESSAGES['daily_limit'])
        #     return
        
        self.send_message(chat_id, Config.MESSAGES['send_url'])
    
    def handle_url(self, chat_id, user_id, url):
        """Handle URL message"""
        # Check subscription
        if not self.check_subscription(user_id):
            self.send_subscription_message(chat_id)
            return
        
        # Check if URL is supported
        if not self.video_downloader.is_supported_url(url):
            self.send_message(chat_id, Config.MESSAGES['invalid_url'])
            return
        
        # Send processing message
        processing_msg = self.send_message(chat_id, Config.MESSAGES['processing'])
        
        # Create download record
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            download = Download(
                user_id=db_user.id,
                url=url,
                status='processing'
            )
            db.session.add(download)
            db.session.commit()
            download_id = download.id
        
        try:
            # Download video
            result = self.video_downloader.download_video(url, user_id=user_id)
            
            if result['success']:
                # Update download record
                with app.app_context():
                    download = Download.query.get(download_id)
                    download.status = 'completed'
                    download.title = result['title']
                    download.file_path = result['file_path']
                    download.file_size = result['filesize']
                    download.completed_at = datetime.utcnow()
                    db.session.commit()
                
                # Edit processing message
                self.edit_message(chat_id, processing_msg['result']['message_id'], Config.MESSAGES['download_complete'])
                
                # Send video file
                caption = f"📹 {result['title']}\n📊 {result['filesize'] / 1024 / 1024:.1f} MB"
                self.send_video(chat_id, result['file_path'], caption)
                
                # Clean up file
                import os
                try:
                    os.remove(result['file_path'])
                except:
                    pass
                
            else:
                # Update download record with error
                with app.app_context():
                    download = Download.query.get(download_id)
                    download.status = 'failed'
                    download.error_message = result['error']
                    db.session.commit()
                
                error_msg = f"{Config.MESSAGES['download_failed']}\n\n{result['error']}"
                self.edit_message(chat_id, processing_msg['result']['message_id'], error_msg)
                
        except Exception as e:
            logger.error(f"Error processing download: {e}")
            
            # Update download record with error
            with app.app_context():
                download = Download.query.get(download_id)
                download.status = 'failed'
                download.error_message = str(e)
                db.session.commit()
            
            self.edit_message(chat_id, processing_msg['result']['message_id'], Config.MESSAGES['download_failed'])
    
    def handle_stats(self, chat_id, user_id):
        """Handle /stats command"""
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                self.send_message(chat_id, "❌ خطأ في النظام")
                return
            
            total_downloads = Download.query.filter_by(user_id=db_user.id).count()
            successful_downloads = Download.query.filter_by(user_id=db_user.id, status='completed').count()
            failed_downloads = Download.query.filter_by(user_id=db_user.id, status='failed').count()
            
            # Get today's downloads
            today = datetime.utcnow().date()
            today_downloads = Download.query.filter(
                Download.user_id == db_user.id,
                Download.created_at >= today
            ).count()
            
            display_name = db_user.first_name or db_user.username or f"User {db_user.telegram_id}"
            
            stats_text = f"""
📊 إحصائياتك الشخصية

👤 الاسم: {display_name}
📅 تاريخ التسجيل: {db_user.created_at.strftime('%Y-%m-%d')}

📥 إجمالي التحميلات: {total_downloads}
✅ التحميلات الناجحة: {successful_downloads}
❌ التحميلات الفاشلة: {failed_downloads}
📊 تحميلات اليوم: {today_downloads}
⏰ الحد المتبقي اليوم: {Config.MAX_DOWNLOADS_PER_USER_PER_DAY - today_downloads}
            """
            
            self.send_message(chat_id, stats_text)
    
    def handle_help(self, chat_id):
        """Handle /help command"""
        self.send_message(chat_id, Config.MESSAGES['help'])
    
    def handle_settings(self, chat_id):
        """Handle /settings command"""
        # Create inline keyboard for settings
        quality_buttons = [
            [
                {"text": "144p", "callback_data": "quality_144p"},
                {"text": "240p", "callback_data": "quality_240p"},
                {"text": "360p", "callback_data": "quality_360p"}
            ],
            [
                {"text": "480p", "callback_data": "quality_480p"},
                {"text": "720p", "callback_data": "quality_720p"},
                {"text": "1080p", "callback_data": "quality_1080p"}
            ],
            [
                {"text": "🎯 الأفضل", "callback_data": "quality_best"}
            ]
        ]
        
        format_buttons = [
            [
                {"text": "📹 MP4", "callback_data": "format_mp4"},
                {"text": "🎵 MP3", "callback_data": "format_mp3"}
            ],
            [
                {"text": "🎬 WEBM", "callback_data": "format_webm"},
                {"text": "📼 AVI", "callback_data": "format_avi"}
            ]
        ]
        
        all_buttons = quality_buttons + format_buttons + [[{"text": "↩️ العودة للقائمة", "callback_data": "back_to_main"}]]
        
        keyboard = {"inline_keyboard": all_buttons}
        self.send_message(chat_id, Config.MESSAGES['settings'], keyboard)
    
    def handle_about(self, chat_id):
        """Handle /about command"""
        # Create inline keyboard for about
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📢 القناة الرسمية", "url": "https://t.me/hackrs98"},
                    {"text": "👨‍💻 المطور", "url": "https://t.me/A_H_a_h_a_h_a_hn"}
                ],
                [
                    {"text": "🔄 تحديث البوت", "callback_data": "update_bot"},
                    {"text": "📊 إحصائيات عامة", "callback_data": "global_stats"}
                ],
                [
                    {"text": "↩️ العودة للقائمة", "callback_data": "back_to_main"}
                ]
            ]
        }
        self.send_message(chat_id, Config.MESSAGES['about'], keyboard)
    
    def update_user_preference(self, user_id, preference_type, value):
        """Update user preference in database"""
        try:
            with app.app_context():
                db_user = User.query.filter_by(telegram_id=user_id).first()
                if db_user:
                    # Store preferences in a simple format
                    if preference_type == "quality":
                        # You could add preference columns to User model if needed
                        # For now, we'll just log the preference
                        logger.info(f"User {user_id} set quality preference to {value}")
                    elif preference_type == "format":
                        logger.info(f"User {user_id} set format preference to {value}")
        except Exception as e:
            logger.error(f"Error updating user preference: {e}")
    
    def handle_global_stats(self, chat_id):
        """Handle global statistics request"""
        try:
            with app.app_context():
                total_users = User.query.count()
                total_downloads = Download.query.count()
                successful_downloads = Download.query.filter_by(status='completed').count()
                
                today = datetime.utcnow().date()
                today_downloads = Download.query.filter(
                    Download.created_at >= today
                ).count()
                
                stats_message = f"""
📊 الإحصائيات العامة للبوت

👥 إجمالي المستخدمين: {total_users:,}
📥 إجمالي التحميلات: {total_downloads:,}
✅ التحميلات الناجحة: {successful_downloads:,}
📅 تحميلات اليوم: {today_downloads:,}

🔥 البوت يعمل بكفاءة عالية!
💪 انضم إلى المجتمع المتنامي من المستخدمين
                """
                
                self.send_message(chat_id, stats_message)
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            self.send_message(chat_id, "حدث خطأ في جلب الإحصائيات. حاول مرة أخرى.")
    
    def check_daily_limit(self, user_id):
        """Check if user has exceeded daily download limit"""
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                return False
            
            today = datetime.utcnow().date()
            today_downloads = Download.query.filter(
                Download.user_id == db_user.id,
                Download.created_at >= today
            ).count()
            
            return today_downloads < Config.MAX_DOWNLOADS_PER_USER_PER_DAY
    
    def handle_callback_query(self, callback_query):
        """Handle inline keyboard callbacks"""
        query_id = callback_query['id']
        chat_id = callback_query['message']['chat']['id']
        user_id = callback_query['from']['id']
        data = callback_query['data']
        
        # Answer callback query
        url = f"{self.base_url}/answerCallbackQuery"
        requests.post(url, data={'callback_query_id': query_id})
        
        if data == "check_subscription":
            is_subscribed = self.check_subscription(user_id)
            
            if is_subscribed:
                # Update user subscription status
                with app.app_context():
                    db_user = User.query.filter_by(telegram_id=user_id).first()
                    if db_user:
                        db_user.is_subscribed = True
                        db_user.subscription_checked_at = datetime.utcnow()
                        db.session.commit()
                
                self.edit_message(chat_id, callback_query['message']['message_id'], Config.MESSAGES['subscription_verified'])
            else:
                self.edit_message(chat_id, callback_query['message']['message_id'], Config.MESSAGES['not_subscribed'])
        
        # Handle quality settings
        elif data.startswith("quality_"):
            quality = data.replace("quality_", "")
            quality_display = {
                "144p": "144p",
                "240p": "240p", 
                "360p": "360p",
                "480p": "480p",
                "720p": "720p",
                "1080p": "1080p",
                "best": "الأفضل"
            }.get(quality, quality)
            
            # Store user preference in database
            self.update_user_preference(user_id, "quality", quality)
            
            # Send confirmation
            confirmation = Config.MESSAGES['quality_changed'].format(quality_display)
            self.send_message(chat_id, confirmation)
        
        # Handle format settings
        elif data.startswith("format_"):
            format_type = data.replace("format_", "")
            format_display = {
                "mp4": "MP4",
                "mp3": "MP3",
                "webm": "WEBM", 
                "avi": "AVI"
            }.get(format_type, format_type)
            
            # Store user preference in database
            self.update_user_preference(user_id, "format", format_type)
            
            # Send confirmation
            confirmation = Config.MESSAGES['format_changed'].format(format_display)
            self.send_message(chat_id, confirmation)
        
        # Handle navigation buttons
        elif data == "back_to_main":
            self.handle_start(chat_id, callback_query['from'])
        
        elif data == "update_bot":
            update_message = """
🔄 تحديث البوت

✅ آخر تحديث: يناير 2025
🔧 الإصدار الحالي: 2.0.0

📋 التحديثات الجديدة:
• تحسين سرعة التحميل
• إضافة منصات جديدة
• تحسين الواجهة العربية
• إصلاح الأخطاء

البوت محدث دائماً تلقائياً! ✨
            """
            self.send_message(chat_id, update_message)
        
        elif data == "global_stats":
            self.handle_global_stats(chat_id)
        
        # Handle main menu buttons
        elif data == "download_video":
            self.handle_download(chat_id, user_id)
        
        elif data == "my_stats":
            self.handle_stats(chat_id, user_id)
        
        elif data == "settings_menu":
            self.handle_settings(chat_id)
        
        elif data == "help_menu":
            self.handle_help(chat_id)
        
        elif data == "about_menu":
            self.handle_about(chat_id)
        
        # Handle admin callback buttons
        elif data == "admin_detailed_stats" and self.is_admin(user_id):
            self.handle_admin_detailed_stats(chat_id)
        
        elif data == "admin_users" and self.is_admin(user_id):
            self.handle_admin_users(chat_id)
        
        elif data == "admin_broadcast" and self.is_admin(user_id):
            self.send_message(chat_id, "أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:")
        
        elif data == "admin_cleanup" and self.is_admin(user_id):
            deleted_count, deleted_size = self.cleanup_old_files()
            self.send_message(chat_id, f"🧹 تم تنظيف {deleted_count} ملف\n💾 تم توفير {deleted_size:.2f} MB")
        
        elif data == "admin_ban" and self.is_admin(user_id):
            self.send_message(chat_id, "أرسل ID المستخدم الذي تريد حظره:\nمثال: /ban 123456789")
        
        elif data == "admin_unban" and self.is_admin(user_id):
            self.send_message(chat_id, "أرسل ID المستخدم الذي تريد إلغاء حظره:\nمثال: /unban 123456789")
    
    def process_update(self, update):
        """Process a single update"""
        try:
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                user_data = message['from']
                
                if 'text' in message:
                    text = message['text']
                    
                    if text.startswith('/start'):
                        self.handle_start(chat_id, user_data)
                    elif text.startswith('/download'):
                        self.handle_download(chat_id, user_id)
                    elif text.startswith('/stats'):
                        self.handle_stats(chat_id, user_id)
                    elif text.startswith('/help'):
                        self.handle_help(chat_id)
                    elif text.startswith('/settings'):
                        self.handle_settings(chat_id)
                    elif text.startswith('/about'):
                        self.handle_about(chat_id)
                    elif text.startswith('/admin') and self.is_admin(user_id):
                        self.handle_admin_panel(chat_id)
                    elif text.startswith('/broadcast') and self.is_admin(user_id):
                        # Extract message after /broadcast command
                        message_parts = text.split(' ', 1)
                        if len(message_parts) > 1:
                            self.handle_broadcast(chat_id, message_parts[1])
                        else:
                            self.send_message(chat_id, "استخدم: /broadcast <الرسالة>")
                    elif text.startswith('/ban') and self.is_admin(user_id):
                        # Extract user ID after /ban command
                        parts = text.split(' ')
                        if len(parts) > 1 and parts[1].isdigit():
                            user_to_ban = int(parts[1])
                            if self.handle_ban_user(user_to_ban):
                                self.send_message(chat_id, Config.MESSAGES['user_banned'])
                            else:
                                self.send_message(chat_id, "فشل في حظر المستخدم")
                        else:
                            self.send_message(chat_id, "استخدم: /ban <user_id>")
                    elif text.startswith('/unban') and self.is_admin(user_id):
                        # Extract user ID after /unban command
                        parts = text.split(' ')
                        if len(parts) > 1 and parts[1].isdigit():
                            user_to_unban = int(parts[1])
                            if self.handle_unban_user(user_to_unban):
                                self.send_message(chat_id, Config.MESSAGES['user_unbanned'])
                            else:
                                self.send_message(chat_id, "فشل في إلغاء حظر المستخدم")
                        else:
                            self.send_message(chat_id, "استخدم: /unban <user_id>")
                    elif text.startswith('/cleanup') and self.is_admin(user_id):
                        deleted_count, deleted_size = self.cleanup_old_files()
                        self.send_message(chat_id, f"🧹 تم تنظيف {deleted_count} ملف\n💾 تم توفير {deleted_size:.2f} MB")
                    elif self.video_downloader.is_supported_url(text):
                        self.handle_url(chat_id, user_id, text)
                    else:
                        self.send_message(chat_id, Config.MESSAGES['invalid_url'])
            
            elif 'callback_query' in update:
                self.handle_callback_query(update['callback_query'])
                
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def run(self):
        """Main bot loop"""
        self.running = True
        logger.info("Bot started successfully!")
        
        while self.running:
            try:
                # Get updates
                response = self.get_updates()
                
                if response and response.get('ok'):
                    updates = response.get('result', [])
                    
                    for update in updates:
                        # Update last_update_id
                        self.last_update_id = max(self.last_update_id, update['update_id'])
                        
                        # Process update
                        self.process_update(update)
                
                # Small delay to prevent excessive API calls
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in bot loop: {e}")
                time.sleep(5)  # Wait longer on error
    
    def stop(self):
        """Stop the bot"""
        self.running = False

# Global bot instance
bot_instance = None

def run_bot():
    """Run bot in a separate thread"""
    global bot_instance
    bot_instance = SimpleTelegramBot()
    
    # Run bot
    bot_instance.run()