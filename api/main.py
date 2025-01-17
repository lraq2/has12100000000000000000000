import os
import sqlite3
import requests
from flask import Flask, request
from telebot import TeleBot, types

# توكن البوت
TOKEN = "7818149231:AAHamruU30ztSut_8znl-jy4HeNMgNI3r1w"
CHANNEL_LINK = "https://t.me/d_tt3"  # رابط القناة
bot = TeleBot(TOKEN)

# إعداد قاعدة البيانات
def setup_database():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        visit_count INTEGER DEFAULT 0,
        invite_count INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

# إضافة مستخدم جديد إلى قاعدة البيانات
def add_user(user_id, username):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

# التحقق من الاشتراك في القناة
def is_subscribed(user_id):
    try:
        check_url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id=@d_tt3&user_id={user_id}"
        response = requests.get(check_url).json()
        status = response.get('result', {}).get('status', '')
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

# بدء البوت
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    if not is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            f"⚠️ عذراً، يجب الاشتراك في القناة أولاً: [اضغط هنا]({CHANNEL_LINK})",
            parse_mode="Markdown"
        )
        return

    add_user(user_id, username)
    bot.send_message(
        message.chat.id,
        "مرحباً! 😊 اختر من القائمة: 👇",
        reply_markup=main_menu()
    )

# القائمة الرئيسية
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("👤 من زار ملفي الشخصي"),
        types.KeyboardButton("💌 الأشخاص الذين دعوتهم"),
        types.KeyboardButton("📈 ترتيب الجترافي"),
        types.KeyboardButton("❓ طريقة استخدام البوت"),
        types.KeyboardButton("📖 تعليمات وخطوات الدعوة")
    )
    return markup

# Flask لإدارة Webhooks
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json()
    bot.process_new_updates([types.Update.de_json(json_data)])
    return "!", 200

@app.route("/", methods=["GET", "POST"])
def index():
    return "Bot is running", 200

if name == "__main__":
    # إعداد قاعدة البيانات وتشغيل Webhook
    setup_database()
    bot.remove_webhook()
    bot.set_webhook(url=f"https://<Your-Vercel-Domain>.vercel.app/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
