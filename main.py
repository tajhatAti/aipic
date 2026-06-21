import os
import threading
import urllib.parse
import io
import json
import datetime
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
from PIL import Image

# ===================== CONFIG =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")
HF_API_KEY = os.environ.get("HF_API_KEY", "YOUR_HF_TOKEN_HERE")

ADMIN_ID = 8768764605
DB_FILE = "users_db.json"
ADMIN_CONTACT_URL = "https://t.me/YourAdminUsername" # এখানে তোর আসল ইউজারনেম দিবি

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# টেম্পোরারি প্রম্পট স্টোরেজ
user_prompts = {}

# ===================== DATABASE LOGIC =====================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

def get_user_data(user_id):
    db = load_db()
    uid = str(user_id)
    today = str(datetime.date.today())
    
    if uid not in db:
        db[uid] = {"limit": 4, "used": 0, "last_used_date": today}
    else:
        # নতুন দিন হলে লিমিট রিসেট হবে
        if db[uid]["last_used_date"] != today:
            db[uid]["used"] = 0
            db[uid]["last_used_date"] = today
            
    save_db(db)
    return db[uid]

def update_user_usage(user_id):
    db = load_db()
    uid = str(user_id)
    db[uid]["used"] += 1
    save_db(db)

def set_user_limit(user_id, new_limit):
    db = load_db()
    uid = str(user_id)
    today = str(datetime.date.today())
    if uid not in db:
        db[uid] = {"limit": new_limit, "used": 0, "last_used_date": today}
    else:
        db[uid]["limit"] = new_limit
    save_db(db)

# ===================== IMAGE GENERATORS =====================
def generate_hf_image(prompt):
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

def enhance_prompt(user_input):
    instruction = "Rewrite this into a highly detailed visual prompt for an AI image generator. No text rendering instructions. Return English only."
    try:
        response = ai_model.generate_content(instruction + "\nUser Input: " + user_input)
        return response.text.strip()
    except:
        return user_input

# ===================== ADMIN COMMAND =====================
@bot.message_handler(commands=['limit'])
def admin_set_limit(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You do not have admin permission.")
        return
    
    try:
        parts = message.text.split()
        target_uid = parts[1]
        new_limit = int(parts[2])
        set_user_limit(target_uid, new_limit)
        bot.reply_to(message, f"✅ User {target_uid}'s limit has been updated to {new_limit} per day.")
    except:
        bot.reply_to(message, "⚠️ Format error. Use: `/limit user_id number` (e.g., /limit 12345 10)", parse_mode="Markdown")

# ===================== USER HANDLERS =====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Send me a text prompt to generate an image.\n\n"
                          "🔹 **Free Mode:** Unlimited (Basic Quality)\n"
                          "🔸 **Pro Mode:** High Quality (Limit: 4/day)", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text_prompt(message):
    user_id = message.from_user.id
    user_prompts[user_id] = message.text
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🟢 Free (Unlimited)", callback_data="model_free"))
    markup.row(InlineKeyboardButton("🌟 Pro (High Quality)", callback_data="model_pro"))
    
    bot.reply_to(message, "⚙️ Choose generation mode:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if user_id not in user_prompts:
        bot.answer_callback_query(call.id, "❌ Prompt expired. Send text again.")
        return
        
    user_text = user_prompts[user_id]
    
    if call.data == "model_free":
        bot.edit_message_text("⏳ Generating Free Image...", call.message.chat.id, call.message.message_id)
        smart_prompt = enhance_prompt(user_text)
        safe_prompt = urllib.parse.quote(smart_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
        
        caption = f"👤 **Input:** `{user_text}`\n⚙️ **Mode:** Free"
        try:
            bot.send_photo(call.message.chat.id, image_url, caption=caption, parse_mode="Markdown")
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            bot.edit_message_text("❌ Error generating image.", call.message.chat.id, call.message.message_id)
            
    elif call.data == "model_pro":
        user_data = get_user_data(user_id)
        if user_data["used"] >= user_data["limit"]:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("👨‍💻 Admin Contact", url=ADMIN_CONTACT_URL))
            bot.edit_message_text("🚫 **Daily Pro Limit Reached!**\n\nYou have used your daily limit. Contact the admin to increase your limit.", 
                                  call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
            return
            
        bot.edit_message_text("🌟 Generating Pro Image... Please wait.", call.message.chat.id, call.message.message_id)
        smart_prompt = enhance_prompt(user_text)
        image_bytes = generate_hf_image(smart_prompt)
        
        if image_bytes:
            update_user_usage(user_id)
            new_data = get_user_data(user_id)
            caption = f"👤 **Input:** `{user_text}`\n🌟 **Mode:** Pro\n📊 **Used:** {new_data['used']}/{new_data['limit']}"
            
            bot.send_photo(call.message.chat.id, photo=io.BytesIO(image_bytes), caption=caption, parse_mode="Markdown")
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text("❌ Hugging Face Server is busy. Try Free mode or try again later.", call.message.chat.id, call.message.message_id)

# ===================== KEEP ALIVE SERVER =====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Alive!")

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), DummyServer).serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    print("[+] Freemium Bot Running...")
    bot.infinity_polling()
        
