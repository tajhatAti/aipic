import os
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import google.generativeai as genai

# ===================== CONFIG =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")

bot = telebot.TeleBot(BOT_TOKEN)

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
# Gemini 1.5 Flash একদম ফ্রি এবং ফাস্ট
ai_model = genai.GenerativeModel('gemini-1.5-flash') 

# ===================== KEEP ALIVE =====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"AI Image Bot Alive!")

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), DummyServer).serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# ===================== PROMPT OPTIMIZER =====================
def enhance_prompt(user_input):
    system_instruction = """
    You are an expert AI image prompt engineer. 
    The user will give you a messy or basic prompt. 
    Your job is to rewrite it into a highly detailed, professional prompt for an AI image generator (like Midjourney). 
    CRITICAL RULE: DO NOT include any instructions to write text, words, or usernames on the image. Translate the core idea into pure visual elements.
    Return ONLY the English prompt, nothing else.
    """
    try:
        response = ai_model.generate_content(system_instruction + "\nUser Input: " + user_input)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return user_input # এরর দিলে ইউজারের অরিজিনাল প্রম্পটটাই রিটার্ন করবে

# ===================== BOT HANDLER =====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 আমাকে যেকোনো হাবিজাবি টেক্সট দাও, আমি সেটাকে প্রফেশনাল ছবিতে রূপান্তর করবো!")

@bot.message_handler(func=lambda message: True)
def generate_smart_photo(message):
    user_text = message.text
    msg = bot.reply_to(message, "🧠 তোমার প্রম্পট এনালাইসিস করছি...")
    
    # ১. Gemini দিয়ে প্রম্পট স্মার্ট করা
    smart_prompt = enhance_prompt(user_text)
    
    bot.edit_message_text("🎨 ছবি জেনারেট হচ্ছে...", message.chat.id, msg.message_id)
    
    # ২. Pollinations দিয়ে ছবি বানানো
    safe_prompt = urllib.parse.quote(smart_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        caption = f"👤 **Your Input:** `{user_text}`\n\n✨ **AI Optimized Prompt:** `{smart_prompt}`"
        bot.send_photo(message.chat.id, image_url, caption=caption, parse_mode="Markdown")
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ সমস্যা হয়েছে! আবার ট্রাই করো।", message.chat.id, msg.message_id)

# ===================== RUN =====================
if __name__ == "__main__":
    print("[+] Smart Image Bot is running...")
    bot.infinity_polling()
    
