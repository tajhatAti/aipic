from telethon import events
from plugins.core.permissions import is_authorized

def setup(bot, userbot):
    """Show detailed group/chat information
    Usage: .chatinfo   (in any group)
    """

    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]chatinfo$'))
        async def chat_info(event):
            if not event.is_group:
                return await event.reply("❌ Use this in a group.")

            if not await is_authorized(event, userbot or bot):
                return await event.reply("❌ Only group admins can use this.")

            try:
                chat = await userbot.get_entity(event.chat_id)
                full = await userbot.get_chat(event.chat_id)

                text = "**📊 Chat Information**\n\n"
                text += f"**Title:** {chat.title}\n"
                text += f"**ID:** `{chat.id}`\n"
                text += f"**Type:** {chat.__class__.__name__}\n"
                text += f"**Members:** {full.participants_count}\n"

                if getattr(chat, 'username', None):
                    text += f"**Username:** @{chat.username}\n"

                if full.about:
                    text += f"**Description:** {full.about[:100]}\n"

                await event.edit(text)
            except Exception as e:
                await event.edit(f"❌ Error: {str(e)}")

    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/chatinfo$'))
        async def bot_chatinfo(event):
            await event.reply("Use `.chatinfo` from your **Personal Account** for full details.")

register = setup
