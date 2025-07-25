import logging
import asyncio
import os
import requests
import json
from datetime import datetime, timedelta
from app import app, db
from models import User, Download, BotStats
from config import Config
from video_downloader import VideoDownloader

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot_token = Config.BOT_TOKEN
        self.subscription_checker = SubscriptionChecker(self.bot_token)
        self.video_downloader = VideoDownloader()
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("download", self.download))
        self.application.add_handler(CommandHandler("stats", self.stats))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Create or update user in database
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user.id).first()
            if not db_user:
                db_user = User(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                db.session.add(db_user)
            else:
                db_user.username = user.username
                db_user.first_name = user.first_name
                db_user.last_name = user.last_name
            
            db.session.commit()
        
        # Check subscription
        is_subscribed = await self.subscription_checker.check_subscription(user.id)
        
        if is_subscribed:
            await update.message.reply_text(Config.MESSAGES['welcome'])
        else:
            await self.send_subscription_message(update)
    
    async def send_subscription_message(self, update: Update):
        """Send subscription required message"""
        keyboard = [
            [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")],
            [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{Config.CHANNEL_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            Config.MESSAGES['not_subscribed'],
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "check_subscription":
            user_id = query.from_user.id
            is_subscribed = await self.subscription_checker.check_subscription(user_id)
            
            if is_subscribed:
                # Update user subscription status
                with app.app_context():
                    db_user = User.query.filter_by(telegram_id=user_id).first()
                    if db_user:
                        db_user.is_subscribed = True
                        db_user.subscription_checked_at = datetime.utcnow()
                        db.session.commit()
                
                await query.edit_message_text(Config.MESSAGES['subscription_verified'])
            else:
                await query.edit_message_text(Config.MESSAGES['not_subscribed'])
    
    async def download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /download command"""
        user_id = update.effective_user.id
        
        # Check subscription
        if not await self.check_user_subscription(user_id):
            await self.send_subscription_message(update)
            return
        
        # Check daily limit
        if not await self.check_daily_limit(user_id):
            await update.message.reply_text(Config.MESSAGES['daily_limit'])
            return
        
        await update.message.reply_text(Config.MESSAGES['send_url'])
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (URLs)"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check subscription
        if not await self.check_user_subscription(user_id):
            await self.send_subscription_message(update)
            return
        
        # Check if message is a URL
        if self.video_downloader.is_supported_url(message_text):
            await self.process_video_download(update, message_text)
        else:
            await update.message.reply_text(Config.MESSAGES['invalid_url'])
    
    async def process_video_download(self, update: Update, url: str):
        """Process video download"""
        user_id = update.effective_user.id
        
        # Send processing message
        processing_message = await update.message.reply_text(Config.MESSAGES['processing'])
        
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
                
                # Send file to user
                await processing_message.edit_text(Config.MESSAGES['download_complete'])
                
                with open(result['file_path'], 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption=f"📹 {result['title']}\n📊 {result['filesize'] / 1024 / 1024:.1f} MB"
                    )
                
                # Clean up file
                os.remove(result['file_path'])
                
            else:
                # Update download record with error
                with app.app_context():
                    download = Download.query.get(download_id)
                    download.status = 'failed'
                    download.error_message = result['error']
                    db.session.commit()
                
                await processing_message.edit_text(f"{Config.MESSAGES['download_failed']}\n\n{result['error']}")
                
        except Exception as e:
            logger.error(f"Error processing download: {e}")
            
            # Update download record with error
            with app.app_context():
                download = Download.query.get(download_id)
                download.status = 'failed'
                download.error_message = str(e)
                db.session.commit()
            
            await processing_message.edit_text(Config.MESSAGES['download_failed'])
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                await update.message.reply_text("❌ خطأ في النظام")
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
            
            stats_text = f"""
📊 إحصائياتك الشخصية

👤 الاسم: {db_user.display_name}
📅 تاريخ التسجيل: {db_user.created_at.strftime('%Y-%m-%d')}

📥 إجمالي التحميلات: {total_downloads}
✅ التحميلات الناجحة: {successful_downloads}
❌ التحميلات الفاشلة: {failed_downloads}
📊 تحميلات اليوم: {today_downloads}
⏰ الحد المتبقي اليوم: {Config.MAX_DOWNLOADS_PER_USER_PER_DAY - today_downloads}
            """
            
            await update.message.reply_text(stats_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await update.message.reply_text(Config.MESSAGES['help'])
    
    async def check_user_subscription(self, user_id):
        """Check if user is subscribed"""
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                return False
            
            # Check if subscription was verified recently (within 24 hours)
            if db_user.subscription_checked_at:
                time_since_check = datetime.utcnow() - db_user.subscription_checked_at
                if time_since_check.total_seconds() < 86400:  # 24 hours
                    return db_user.is_subscribed
            
            # Re-check subscription
            is_subscribed = await self.subscription_checker.check_subscription(user_id)
            db_user.is_subscribed = is_subscribed
            db_user.subscription_checked_at = datetime.utcnow()
            db.session.commit()
            
            return is_subscribed
    
    async def check_daily_limit(self, user_id):
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
    
    async def run(self):
        """Run the bot"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)

# Global bot instance
bot_instance = None

def run_bot():
    """Run bot in a separate thread"""
    global bot_instance
    bot_instance = TelegramBot()
    
    # Run bot
    asyncio.run(bot_instance.run())
