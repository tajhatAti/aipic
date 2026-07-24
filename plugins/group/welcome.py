from telethon import events
from plugins.core.permissions import is_authorized

# Simple in-memory welcome (for demo). 
# For production you can use a database later.
WELCOME_TEXT = {}

def setup(bot, userbot):
    """Welcome Message for new members
    Usage:
    .setwelcome <text>   (in group)
    .welcome             (to test)
    """

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]setwelcome(?:\s+(.+))?$'))
        async def set_welcome(event):
            if not event.is_group or not event.out:
                return

            text = event.pattern_match.group(1)
            if not text:
                return await event.edit("Usage: `.setwelcome Hello {first} !`")

            WELCOME_TEXT[event.chat_id] = text
            await event.edit("✅ Welcome message set for this group!")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]welcome$'))
        async def test_welcome(event):
            if not event.is_group or not event.out:
                return
            text = WELCOME_TEXT.get(event.chat_id, "No welcome set. Use `.setwelcome Hello {first}`")
            await event.edit(f"**Current Welcome:**\n\n{text}")

        # Auto welcome when new user joins
        @userbot.on(events.ChatAction)
        async def auto_welcome(event):
            if event.user_joined or event.user_added:
                chat_id = event.chat_id
                if chat_id not in WELCOME_TEXT:
                    return

                user = await event.get_user()
                text = WELCOME_TEXT[chat_id]

                # Simple replacements
                text = text.replace("{first}", user.first_name or "User")
                text = text.replace("{username}", f"@{user.username}" if user.username else "")
                text = text.replace("{id}", str(user.id))

                try:
                    await userbot.send_message(chat_id, text)
                except:
                    pass

    # ===================== BOT (info only) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/setwelcome$'))
        async def bot_welcome_info(event):
            await event.reply("Welcome system works best with your **Personal Account** (.setwelcome)")

register = setup
