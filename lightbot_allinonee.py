# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json
import random
import datetime
import time
from PIL import Image
import pytesseract
import os

TOKEN = "8079195084:AAGpyZDM36N-7r7rAs5IehELpepo-zzBjbk"
bot = telebot.TeleBot(TOKEN)

CHANNEL_ID = "@LIGHTHOU3E"
ADMIN_ID = 722369763

SCORES_FILE = "scores.json"
OCR_FILE = "ocr_uses.json"
REF_FILE = "referrals.json"

REWARDS = {
    10: "📱 شارژ تلفن ۱۰ هزار تومانی",
    20: "🛍 ۱ کا آیتم پلاتویی از شاپ",
    30: "🛍 ۲.۵ کا آیتم پلاتویی از شاپ",
    40: "📱 شارژ تلفن ۴۰ هزار تومانی",
    50: "🌐 ۱۵ گیگ وی‌پی‌ان اختصاصی",
    60: "🛍 ۵ کا آیتم پلاتویی از شاپ",
    80: "🛍 ۱۰ کا آیتم پلاتویی از شاپ"
}

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

scores = load_json(SCORES_FILE)
ocr_uses = load_json(OCR_FILE)
referrals = load_json(REF_FILE)

def is_user_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 گردونه شانس", "🛒 فروشگاه", "📸 استخراج متن از عکس")
    markup.add("💬 چت با لایت‌چت", "🏆 امتیاز من", "👤 درباره ما")
    markup.add("📥 ارسال پیام ناشناس", "🏠 منوی اصلی")
    bot.send_message(chat_id, "🏠 منوی اصلی:", reply_markup=markup)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = str(message.from_user.id)
    ref = message.text.split()[-1] if len(message.text.split()) > 1 else None

    if ref and ref != user_id and ref not in referrals.get(user_id, []):
        scores[ref] = scores.get(ref, 0) + 1
        referrals.setdefault(user_id, []).append(ref)
        save_json(SCORES_FILE, scores)
        save_json(REF_FILE, referrals)
        bot.send_message(int(ref),
            f"🎉 تبریک میگم!

"
            f"یک نفر با لینک دعوت شما وارد ربات شد، و شما ۱ امتیاز به دست آوردید.

"
            f"✅ امتیاز جدید شما: {scores[ref]}")

    if not is_user_member(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/LIGHTHOU3E"))
        bot.send_message(message.chat.id,
            "🔒 برای استفاده از ربات باید عضو کانال ما بشی.

"
            "بعد از عضویت، روی /start بزن تا ادامه بدیم.",
            reply_markup=markup)
        return

    scores.setdefault(user_id, 0)
    save_json(SCORES_FILE, scores)

    bot.send_message(message.chat.id,
        "🎉 خوش اومدی به ربات لایت‌هاوس!

"
        "🔹 اینجا می‌تونی امتیاز جمع کنی، گردونه شانس بچرخونی، جوایز مختلف بگیری، از هوش مصنوعی استفاده کنی، متن از عکس دربیاری و کلی چیز باحال دیگه.

"
        "📢 یادت نره عضو کانالمون باشی تا ربات برات فعال باشه: @LIGHTHOU3E

"
        "🤖 هر جا گیر کردی، "🏠 منوی اصلی" رو بزن تا برگردی اینجا.

"
        "🫡 با افتخار: تیم لایت‌هاوس (تورنادو سابق)")

    show_main_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🏆 امتیاز من")
def show_score(message):
    user_id = str(message.from_user.id)
    score = scores.get(user_id, 0)
    bot.send_message(message.chat.id, f"🎯 امتیاز فعلی شما: {score}")

@bot.message_handler(func=lambda m: m.text == "🛒 فروشگاه")
def show_shop(message):
    user_id = str(message.from_user.id)
    msg = "🛍 لیست جوایز فروشگاه:

"
    for point, prize in sorted(REWARDS.items()):
        msg += f"⭐ {point} امتیاز = {prize}
"
    msg += "
برای دریافت جایزه، شماره امتیازشو بفرست (مثلاً 20)"
    show_main_menu(message.chat.id)
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text.isdigit() and int(m.text) in REWARDS)
def redeem_reward(message):
    user_id = str(message.from_user.id)
    req = int(message.text)
    if scores.get(user_id, 0) >= req:
        scores[user_id] -= req
        save_json(SCORES_FILE, scores)
        bot.send_message(message.chat.id, "✅ جایزه انتخاب شد! ادمین بررسی می‌کنه.")
        bot.send_message(ADMIN_ID, f"🎁 کاربر {message.from_user.first_name} ({user_id}) جایزه خواست:
{REWARDS[req]}")
    else:
        bot.send_message(message.chat.id, "❌ امتیاز شما کافی نیست!")

@bot.message_handler(func=lambda m: m.text == "🎰 گردونه شانس")
def spin_wheel(message):
    user_id = str(message.from_user.id)
    today = str(datetime.date.today())
    if "last_spin" in scores and scores["last_spin"].get(user_id) == today:
        bot.send_message(message.chat.id, "⏳ امروز گردونه رو چرخوندی! فردا دوباره امتحان کن.")
        return

    scores.setdefault("last_spin", {})[user_id] = today
    save_json(SCORES_FILE, scores)

    bot.send_animation(message.chat.id, open("spin.gif", "rb"))
    time.sleep(2.5)

    prize = random.choice(["1", "1", "2", "2", "5", "0", "0", "0"])
    if prize != "0":
        scores[user_id] = scores.get(user_id, 0) + int(prize)
        save_json(SCORES_FILE, scores)
        bot.send_message(message.chat.id, f"🎉 تبریک! {prize} امتیاز بردی!")
    else:
        bot.send_message(message.chat.id, "❌ این بار چیزی نبردی. شانست رو فردا امتحان کن!")

@bot.message_handler(func=lambda m: m.text == "📸 استخراج متن از عکس")
def ask_for_photo(message):
    bot.send_message(message.chat.id, "📸 لطفاً عکس رو بفرست
📅 روزی ۳ بار رایگانه. بعدش هر بار ۱ امتیاز کم میشه.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = str(message.from_user.id)
    today = str(datetime.date.today())
    ocr_uses.setdefault(user_id, {}).setdefault(today, 0)

    if ocr_uses[user_id][today] >= 3:
        if scores.get(user_id, 0) >= 1:
            scores[user_id] -= 1
            save_json(SCORES_FILE, scores)
        else:
            bot.send_message(message.chat.id, "❌ رایگان‌هات تموم شده و امتیاز نداری.")
            return

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded = bot.download_file(file_info.file_path)
    with open("temp.jpg", "wb") as f:
        f.write(downloaded)
    text = pytesseract.image_to_string(Image.open("temp.jpg"))
    bot.send_message(message.chat.id, f"📝 متن تشخیص داده‌شده:
{text}")
    ocr_uses[user_id][today] += 1
    save_json(OCR_FILE, ocr_uses)

@bot.message_handler(func=lambda m: m.text == "💬 چت با لایت‌چت")
def chat_ai(message):
    bot.send_message(message.chat.id, "🧠 فعلاً این بخش در حال توسعه‌س...")

@bot.message_handler(func=lambda m: m.text == "📥 ارسال پیام ناشناس")
def ask_anon(message):
    bot.send_message(message.chat.id, "✉️ پیام ناشناس خودت رو بنویس:")

@bot.message_handler(func=lambda m: m.text == "👤 درباره ما")
def about_us(message):
    bot.send_message(message.chat.id,
        "📢 درباره ما

"
        "تیم لایت هاوس (تورنادو سابق) با حضور چندین و چند ساله در پلاتو و حدودا از سال ۱۴۰۱ در خدمت شماست.
"
        "اگه مشکلی برای استفاده از ربات یا پیشنهاد و انتقادی به گروه پلاتو یا چنل تلگرام یا ربات دارید به ایدی زیر مراجعه فرمایید:

"
        "📬 @Rahimipv")

@bot.message_handler(func=lambda m: m.text == "🏠 منوی اصلی")
def back_to_main(message):
    show_main_menu(message.chat.id)

print("ربات فعال شد...")
bot.infinity_polling()
