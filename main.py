import os
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineQueryResultPhoto

# ===================== CONFIG =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE") # রেন্ডারে এনভায়রনমেন্ট ভ্যারিয়েবল হিসেবে টোকেন দিবি
bot = telebot.TeleBot(BOT_TOKEN)

# ===================== KEEP ALIVE SERVER =====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Image Generation Bot is Alive!")

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# ===================== INLINE QUERY HANDLER (@bot prompt) =====================
@bot.inline_handler(func=lambda query: len(query.query) > 2)
def query_photo(inline_query):
    prompt = inline_query.query
    safe_prompt = urllib.parse.quote(prompt)
    
    # Pollinations AI ডাইরেক্ট ইমেজ জেনারেশন URL
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        result = InlineQueryResultPhoto(
            id='1',
            photo_url=image_url,
            thumbnail_url=image_url, # থাম্বনেইল হিসেবেও সেম ছবি লোড হবে
            caption=f"🎨 **Prompt:** `{prompt}`",
            parse_mode="Markdown"
        )
        bot.answer_inline_query(inline_query.id, [result], cache_time=1)
    except Exception as e:
        print(f"Inline Error: {e}")

# ===================== DIRECT MESSAGE HANDLER =====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 স্বাগতম! আমাকে যেকোনো টেক্সট (Prompt) দাও, আমি ছবি বানিয়ে দেবো।\n\n"
                          "তুমি চাইলে যেকোনো গ্রুপ বা চ্যাটে `@তোমার_বটের_ইউজারনেম prompt` লিখেও ছবি বানাতে পারো।")

@bot.message_handler(func=lambda message: True)
def generate_photo_direct(message):
    prompt = message.text
    msg = bot.reply_to(message, "⏳ ছবি জেনারেট হচ্ছে... একটু অপেক্ষা করো!")
    
    safe_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        # সরাসরি URL থেকে ছবি টেলিগ্রামে পাঠানো হচ্ছে
        bot.send_photo(message.chat.id, image_url, caption=f"🎨 **Prompt:** `{prompt}`", parse_mode="Markdown")
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ এরর! ছবি বানাতে সমস্যা হয়েছে। অন্য কোনো English Prompt দিয়ে ট্রাই করো।", message.chat.id, msg.message_id)

# ===================== BOT START =====================
if __name__ == "__main__":
    print("[+] Bot is running...")
    bot.infinity_polling()
