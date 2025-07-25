import os

class Config:
    # Bot configuration
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "your-bot-token-here")
    CHANNEL_USERNAME = "hackrs98"  # Channel username without @
    CHANNEL_ID = "@hackrs98"  # Channel ID with @
    ADMIN_ID = 7024930860  # Admin user ID
    DEVELOPER_NAME = "المهندس/اشرف المهدي"  # Developer name
    DEVELOPER_USERNAME = "@A_H_a_h_a_h_a_hn"  # Developer contact
    
    # Download configuration
    DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloads")
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
    SUPPORTED_FORMATS = ['mp4', 'mp3', 'webm', 'avi']
    SUPPORTED_QUALITIES = ['144p', '240p', '360p', '480p', '720p', '1080p', 'best']
    
    # Rate limiting (disabled - unlimited downloads)
    MAX_DOWNLOADS_PER_USER_PER_DAY = 999999  # Unlimited downloads
    
    # Messages in Arabic
    MESSAGES = {
        'welcome': f"""
🎬 مرحباً بك في بوت تحميل الفيديوهات المحترف!

للاستفادة من خدماتنا، يجب عليك الاشتراك في قناتنا أولاً:
👈 @hackrs98

بعد الاشتراك، استخدم الأوامر التالية:
📥 /download - تحميل فيديو
📊 /stats - إحصائياتك
❓ /help - المساعدة

⚡ البوت يدعم تحميل الفيديوهات من جميع المنصات الشائعة!

👨‍💻 صانع البوت: {DEVELOPER_NAME}
📞 للتواصل: {DEVELOPER_USERNAME}
        """,
        'not_subscribed': """
❌ يجب عليك الاشتراك في قناتنا أولاً!

👈 اشترك في: @hackrs98

بعد الاشتراك، اضغط على الزر أدناه للتحقق:
        """,
        'subscription_verified': """
✅ تم التحقق من الاشتراك بنجاح!

يمكنك الآن استخدام البوت بحرية.
استخدم /download لتحميل الفيديوهات.
        """,
        'send_url': """
📎 أرسل رابط الفيديو الذي تريد تحميله

المنصات المدعومة:
• YouTube
• Instagram
• TikTok
• Twitter
• Facebook
• وغيرها الكثير!
        """,
        'processing': "⏳ جاري معالجة الفيديو...",
        'download_complete': "✅ تم تحميل الفيديو بنجاح!",
        'download_failed': "❌ فشل في تحميل الفيديو. حاول مرة أخرى.",
        'invalid_url': "❌ رابط غير صالح. يرجى إرسال رابط صحيح.",
        'daily_limit': "⚠️ تم تجاوز الحد اليومي للتحميلات. حاول غداً.",  # Disabled
        'admin_panel': """
🔧 لوحة تحكم الإدارة

👨‍💻 مرحباً أيها الأدمن!

📊 إحصائيات سريعة:
• المستخدمين: {}
• التحميلات: {}
• النجحة: {}

🛠️ أوامر الإدارة:
• /broadcast - إرسال رسالة للجميع
• /stats_admin - إحصائيات مفصلة
• /users_admin - إدارة المستخدمين
• /ban - حظر مستخدم
• /unban - إلغاء حظر مستخدم
• /cleanup - تنظيف الملفات القديمة
        """,
        'broadcast_sent': "✅ تم إرسال الرسالة لجميع المستخدمين",
        'user_banned': "🚫 تم حظر المستخدم بنجاح",
        'user_unbanned': "✅ تم إلغاء حظر المستخدم بنجاح",
        'admin_stats': """
📈 إحصائيات الإدارة المفصلة

👥 المستخدمين:
• إجمالي: {}
• نشط: {}
• محظور: {}

📥 التحميلات:
• إجمالي: {}
• ناجح: {}
• فاشل: {}
• اليوم: {}

💾 النظام:
• الملفات: {} MB
• المساحة المستخدمة: {} MB
        """,
        'help': """
📖 مساعدة البوت

الأوامر المتاحة:
• /start - بدء البوت
• /download - تحميل فيديو
• /stats - إحصائياتك
• /help - هذه المساعدة
• /settings - إعدادات التحميل
• /about - معلومات عن البوت

💡 نصائح:
- تأكد من الاشتراك في @hackrs98
- أرسل رابط الفيديو مباشرة
- اختر الجودة والصيغة المناسبة
- استخدم /settings لتخصيص جودة التحميل
        """,
        'settings': """
⚙️ إعدادات التحميل

يمكنك تخصيص جودة ونوع التحميل:

📱 الجودة المتاحة:
• 144p - جودة منخفضة (توفير البيانات)
• 240p - جودة متوسطة
• 360p - جودة عادية
• 480p - جودة جيدة
• 720p - جودة عالية (HD)
• 1080p - جودة فائقة (Full HD)
• الأفضل - أعلى جودة متاحة

📁 الصيغ المدعومة:
• MP4 - فيديو (الافتراضي)
• MP3 - صوت فقط
• WEBM - فيديو مضغوط
• AVI - فيديو عالي الجودة

اختر إعداداتك المفضلة من الأزرار أدناه:
        """,
        'about': f"""
ℹ️ معلومات عن البوت

🎬 بوت تحميل الفيديوهات المحترف
⚡ يدعم أكثر من 1000 موقع ومنصة

👨‍💻 المطور: {DEVELOPER_NAME}
📱 للتواصل: {DEVELOPER_USERNAME}
📢 القناة الرسمية: @hackrs98

🔧 الإصدار: 2.0.0
📅 تاريخ التحديث: يناير 2025

✨ الميزات:
• تحميل من جميع المنصات الشائعة
• جودات متعددة (144p إلى 1080p)
• صيغ مختلفة (MP4, MP3, WEBM, AVI)
• واجهة عربية كاملة
• تحقق أمني من الاشتراك
• إحصائيات مفصلة
• دعم فني متواصل

🛡️ آمن وموثوق بنسبة 100%
        """,
        'quality_changed': "✅ تم تغيير الجودة إلى: {}",
        'format_changed': "✅ تم تغيير الصيغة إلى: {}",
        'settings_updated': "✅ تم حفظ الإعدادات بنجاح!"
    }
