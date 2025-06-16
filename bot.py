import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# توكن البوت الخاص بك
BOT_TOKEN = "7543220305:AAG6Qll7pr_pg0193_apjHVJmrzmIZHiFsc"
bot = telebot.TeleBot(BOT_TOKEN)

# روابط القنوات الإخبارية
channels = {
    "📺 قناة المسيرة": "https://masirahtv.net/live",
    "📺 قناة الميادين": "https://www.almayadeen.net/live",
    "📺 قناة الساحات": "https://alsahatv.net/live",
    "📺 قناة اليمن الفضائية": "https://yemen-tv.net/live"
}

# القناة الإلزامية و رابط الإحالة (غيّرهم حسب حسابك)
required = {
    "قناة البوت الرسمية 🗞️": "@hackrs98",  # ← غيّرها بقناتك
    "بوت الإحالة XWorld 💰": "https://t.me/xworld/app?startapp=bT10Z19pbnZpdGUmYz0xODAwNjgxMjYz"
}

# التحقق من الاشتراك
def check_subscription(user_id):
    not_joined = []

    # التحقق من القناة
    channel_username = required["قناة البوت الرسمية 🗞️"]
    try:
        member = bot.get_chat_member(channel_username, user_id)
        if member.status in ["left", "kicked"]:
            not_joined.append("قناة البوت الرسمية 🗞️")
    except:
        not_joined.append("قناة البوت الرسمية 🗞️")

    # التحقق من الإحالة (ما نقدر نتحقق تلقائيًا من رابط خارجي لكن نطلب منه الضغط عليه)
    # سنطلب منه يضغط الرابط ويتابع
    return not_joined

# رسالة البداية
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    not_joined = check_subscription(user_id)

    if not_joined:
        text = "🔒 لا يمكنك استخدام البوت حتى تشترك في القنوات التالية:\n\n"
        markup = InlineKeyboardMarkup()
        
        for name, channel in required.items():
            if "@" in channel:
                markup.add(InlineKeyboardButton(f"📢 اشترك في {name}", url=f"https://t.me/{channel.strip( @ )}"))
            else:
                markup.add(InlineKeyboardButton(f"🤑 اشترك في {name}", url=channel))
        
        markup.add(InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
        bot.send_message(user_id, text, reply_markup=markup)
        return

    # إذا مشترك، عرض القنوات
    welcome_text = f"أهلاً وسهلاً بك يا {message.from_user.first_name} في بوت البث الإخباري 📡\nاختر القناة التي تريد مشاهدتها:"
    markup = InlineKeyboardMarkup()
    for name, url in channels.items():
        markup.add(InlineKeyboardButton(name, web_app=WebAppInfo(url)))
    markup.add(InlineKeyboardButton("ℹ️ حول البوت", callback_data="about"))
    bot.send_message(user_id, welcome_text, reply_markup=markup)

# التحقق بعد الضغط على الزر
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def recheck(call):
    user_id = call.from_user.id
    not_joined = check_subscription(user_id)

    if not_joined:
        text = "🚫 لم تكمل الاشتراك في القنوات التالية:\n\n"
        markup = InlineKeyboardMarkup()
        for name, channel in required.items():
            if "@" in channel:
                markup.add(InlineKeyboardButton(f"📢 اشترك في {name}", url=f"https://t.me/{channel.strip( @ )}"))
            else:
                markup.add(InlineKeyboardButton(f"🤑 اشترك في {name}", url=channel))
        markup.add(InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "✅ تم التحقق من الاشتراك بنجاح!")
        start(call.message)

# زر حول البوت
@bot.callback_query_handler(func=lambda call: call.data == "about")
def about_bot(call):
    text = (
        "📡 بوت البث الإخباري\n\n"
        "يعرض قنوات إخبارية مباشرة بجودة عالية عبر WebApp.\n"
        "✅ اشترك أولاً بالقناة الرسمية ورابط الربح.\n\n"
        "📺 القنوات المتوفرة:\n"
        "✔️ المسيرة\n✔️ الميادين\n✔️ الساحات\n✔️ اليمن الفضائية\n\n"
        "👨‍💻 صانع البوت: المهندس أشرف المهدي"
    )
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

# تشغيل البوت
bot.infinity_polling()