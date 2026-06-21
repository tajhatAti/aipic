import os
import threading
import urllib.parse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException  # এরর হ্যান্ডেল করার জন্য
import google.generativeai as genai

# ===================== CONFIG =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")
ADMIN_ID = 8768764605
DB_FILE = "users_db.json"

# ফিক্স ১: বটের থ্রেড সংখ্যা বাড়িয়ে ১৫ করা হলো, যাতে একসাথে ১৫ জন ইউজার রিকোয়েস্ট পাঠাতে পারে (Fix Blocking I/O)
bot = telebot.TeleBot(BOT_TOKEN, num_threads=15)

# ফিক্স ২: থ্রেড লক তৈরি (Race Condition বন্ধ করার জন্য)
db_lock = threading.Lock()

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# ===================== DATABASE LOGIC =====================
# এই ফাংশনগুলো এখন সরাসরি কল হবে না, লকের ভেতরে রেখে কল করা হবে
def load_db_internal():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_db_internal(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def track_user_prompt(user_id, username, prompt):
    # ফিক্স ৩: সম্পূর্ণ Read-Modify-Write প্রসেস লক করা হলো
    with db_lock:
        db = load_db_internal()
        uid = str(user_id)
        
        if uid not in db:
            db[uid] = {"username": username, "history": []}
            
        db[uid]["username"] = username 
        
        if "history" not in db[uid]:
            db[uid]["history"] = []
            
        db[uid]["history"].append(prompt)
        db[uid]["history"] = db[uid]["history"][-50:] 
        
        save_db_internal(db)

# ===================== IMAGE PROMPT ENHANCER =====================
def enhance_prompt(user_input):
    instruction = "Rewrite this into a highly detailed visual prompt for an AI image generator. No text rendering instructions. Return English only."
    try:
        response = ai_model.generate_content(instruction + "\nUser Input: " + user_input)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return user_input

# ===================== ADMIN COMMANDS =====================
@bot.message_handler(commands=['view'])
def admin_view_users(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You do not have admin permission.")
        return
    
    # লক করে ডাটা রিড করা হচ্ছে
    with db_lock:
        db = load_db_internal()
        
    if not db:
        bot.reply_to(message, "📭 Database is empty. No users yet.")
        return
        
    markup = InlineKeyboardMarkup()
    for uid, data in db.items():
        uname = data.get("username", "Unknown")
        btn_text = f"👤 {uname}"
        markup.row(InlineKeyboardButton(btn_text, callback_data=f"view_{uid}"))
        
    bot.reply_to(message, "📋 **Total User List:**\nClick a user to view their prompt history.", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def handle_view_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Access Denied.")
        return
        
    uid = call.data.split('_')[1]
    
    # লক করে ডাটা রিড করা হচ্ছে
    with db_lock:
        db = load_db_internal()
    
    if uid in db:
        uname = db[uid].get("username", "Unknown")
        history = db[uid].get("history", [])
        
        if not history:
            text = f"📭 User **{uname}** has no generated prompts yet."
        else:
            text = f"📜 **Prompt History for {uname} (Last 10):**\n\n"
            for i, p in enumerate(history[-10:], start=1):
                text += f"**{i}.** `{p}`\n\n"
                
        if len(text) > 4000:
            text = text[:4000] + "\n...[Truncated]"
            
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        except ApiTelegramException as e:
            # ফিক্স ৪: একই বাটনে বারবার চাপ দিলে যেন বট ক্র্যাশ না করে
            if "message is not modified" in e.description:
                bot.answer_callback_query(call.id, "⚠️ You are already viewing this history.")
            else:
                print(f"Telegram API Error: {e}")
    else:
        bot.answer_callback_query(call.id, "❌ User not found in DB.")

# ===================== USER HANDLERS =====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Just send me any text prompt, and I will enhance it using AI and generate a beautiful image for you!")

@bot.message_handler(func=lambda message: True)
def handle_text_prompt(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    user_text = message.text
    
    # ব্যাকগ্রাউন্ড থ্রেড থেকে নিরাপদে ডাটা সেভ হবে
    track_user_prompt(user_id, username, user_text)
    
    processing_msg = bot.reply_to(message, "⏳ Processing... Enhancing your prompt and generating image.")
    
    # এই লাইনে Gemini এপিআই কল চলাকালীন অন্য থ্রেডগুলো সচল থাকবে
    smart_prompt = enhance_prompt(user_text)
    
    safe_prompt = urllib.parse.quote(smart_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
    
    caption = f"👤 **Your Input:** `{user_text}`\n✨ **Enhanced by AI:** `{smart_prompt}`"
    
    if len(caption) > 1000:
        caption = caption[:1000] + "..."
    
    try:
        bot.send_photo(message.chat.id, image_url, caption=caption, parse_mode="Markdown")
        bot.delete_message(message.chat.id, processing_msg.message_id)
    except Exception as e:
        print(f"Image Generation Error: {e}")
        bot.edit_message_text("❌ Error generating image. Please try a different prompt.", message.chat.id, processing_msg.message_id)

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
    print("[+] Simple Image Bot Running with Thread-Lock...")
    bot.infinity_polling()
