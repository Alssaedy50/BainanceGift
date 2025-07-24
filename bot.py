import telebot
from telebot import types
import os
import time

# المتغيرات من بيئة التشغيل (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # قناة نشر الأكواد
SUB_CHANNEL_USERNAME = os.getenv("SUB_CHANNEL_USERNAME")  # قناة الاشتراك الإجباري
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# قائمة الأكواد المؤقتة
codes_queue = []

# التحقق من الاشتراك الإجباري
def is_user_subscribed(user_id):
    try:
        status = bot.get_chat_member(SUB_CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# رسالة الترحيب + أزرار اللغات
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ اشترك الآن", url=f"https://t.me/{SUB_CHANNEL_USERNAME.lstrip('@')}"))
        bot.send_message(user_id, "⚠️ الرجاء الاشتراك في القناة للمتابعة", reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🌍 اختيار اللغة", "ℹ️ حول البوت", "📤 إرسال كود")
    bot.send_message(user_id, "مرحبًا بك! 👋\nاختر من القائمة:", reply_markup=markup)

# إرسال كود
@bot.message_handler(func=lambda message: message.text == "📤 إرسال كود")
def ask_code(message):
    bot.send_message(message.chat.id, "أرسل الكود الآن:")
    bot.register_next_step_handler(message, receive_code)

def receive_code(message):
    code = message.text.strip()
    codes_queue.append(code)
    bot.send_message(message.chat.id, "✅ تم استلام الكود، سيتم نشره قريبًا.")

# النشر التلقائي كل 30 ثانية
def auto_poster():
    while True:
        if codes_queue:
            code = codes_queue.pop(0)
            caption = f"🎁 *New Binance Gift Code!*\n\n`{code}`\n\n📌 Join our channels:\n@{CHANNEL_USERNAME}\n@{SUB_CHANNEL_USERNAME}"
            bot.send_message(f"@{CHANNEL_USERNAME}", caption, parse_mode="Markdown")
        time.sleep(30)

# تشغيل النشر التلقائي في ثريد منفصل
import threading
threading.Thread(target=auto_poster).start()

# تشغيل البوت
print("Bot is running...")
bot.infinity_polling()
