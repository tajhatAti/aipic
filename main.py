import os
import threading
import urllib.parse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai

# ===================== CONFIG =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")
ADMIN_ID = 8768764605
DB_FILE = "users_db.json"

bot = telebot.TeleBot(BOT_TOKEN)

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# ===================== DATABASE LOGIC =====================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def track_user_prompt(user_id, username, prompt):
    db = load_db()
    uid = str(user_id)
    
    if uid not in db:
        db[uid] = {"username": username, "history": []}
        
    # Update username in case they changed it
    db[uid]["username"] = username 
    
    # Initialize history list if it's an old DB structure
    if "history" not in db[uid]:
        db[uid]["history"] = []
        
    db[uid]["history"].append(prompt)
    
    # Keep only the last 50 prompts so the DB doesn't get too large
    db[uid]["history"] = db[uid]["history"][-50:] 
    
    save_db(db)

# ===================== IMAGE PROMPT ENHANCER =====================
def enhance_prompt(user_input):
    instruction = "Rewrite this into a highly detailed visual prompt for an AI image generator. No text rendering instructions. Return English only."
    try:
        response = ai_model.generate_content(instruction + "\nUser Input: " + user_input)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return user_input # Fallback to original if API fails

# ===================== ADMIN COMMANDS =====================
@bot.message_handler(commands=['view'])
def admin_view_users(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You do not have admin permission.")
        return
    
    db = load_db()
    if not db:
        bot.reply_to(message, "📭 Database is empty. No users yet.")
        return
        
    markup = InlineKeyboardMarkup()
    for uid, data in db.items():
        uname = data.get("username", "Unknown")
        # Creating button for each user
        btn_text = f"👤 {uname}"
        markup.row(InlineKeyboardButton(btn_text, callback_data=f"view_{uid}"))
        
    bot.reply_to(message, "📋 **Total User List:**\nClick a user to view their prompt history.", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def handle_view_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Access Denied.")
        return
        
    uid = call.data.split('_')[1]
    db = load_db()
    
    if uid in db:
        uname = db[uid].get("username", "Unknown")
        history = db[uid].get("history", [])
        
        if not history:
            text = f"📭 User **{uname}** has no generated prompts yet."
        else:
            text = f"📜 **Prompt History for {uname} (Last 10):**\n\n"
            # Display last 10 prompts to prevent huge messages
            for i, p in enumerate(history[-10:], start=1):
                text += f"**{i}.** `{p}`\n\n"
                
        # Truncate text if it exceeds Telegram's limit
        if len(text) > 4000:
            text = text[:4000] + "\n...[Truncated]"
            
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
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
    
    # Save to database
    track_user_prompt(user_id, username, user_text)
    
    # Sending a loading message
    processing_msg = bot.reply_to(message, "⏳ Processing... Enhancing your prompt and generating image.")
    
    # 1. Send to Gemini for enhancement
    smart_prompt = enhance_prompt(user_text)
    
    # 2. Generate Image using Pollinations AI (Free Unlimited Logic)
    safe_prompt = urllib.parse.quote(smart_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
    
    caption = f"👤 **Your Input:** `{user_text}`\n✨ **Enhanced by AI:** `{smart_prompt}`"
    
    # Truncate caption if it's too long (Telegram limit is 1024 chars for photo captions)
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
    print("[+] Simple Image Bot Running...")
    bot.infinity_polling()
        
