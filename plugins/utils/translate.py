from telethon import events
import requests

def setup(bot, userbot):
    """Simple Translate Plugin
    Usage: .tr <lang> <text>   or reply to a message
    Example: .tr bn Hello how are you
    """

    # ===================== USERBOT + BOT =====================
    async def translate_handler(event):
        # Get text
        text = ""
        lang = "en"

        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text
        else:
            parts = event.raw_text.split(maxsplit=2)
            if len(parts) >= 3:
                lang = parts[1].lower()
                text = parts[2]
            elif len(parts) == 2:
                lang = parts[1].lower()
                text = "Hello, how are you?"

        if not text:
            return await event.reply("Usage: `.tr <lang> <text>`\nExample: `.tr bn Hello`")

        try:
            # Using free Google Translate unofficial API (no key needed)
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "auto",
                "tl": lang,
                "dt": "t",
                "q": text
            }
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            translated = "".join([item[0] for item in result[0] if item[0]])

            await event.reply(
                f"**Translated** (`{lang}`):\n\n"
                f"`{translated}`"
            )
        except Exception as e:
            await event.reply(f"❌ Translation failed: {str(e)}")

    pattern = r'(?i)^[.!/]tr(?:anslate)?'

    if userbot:
        userbot.add_event_handler(translate_handler, events.NewMessage(pattern=pattern))
    if bot:
        bot.add_event_handler(translate_handler, events.NewMessage(pattern=pattern))

register = setup
