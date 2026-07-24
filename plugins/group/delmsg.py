from telethon import events
from plugins.core.permissions import is_authorized

def setup(bot, userbot):
    """Delete a message quickly
    Usage: .del   (reply to any message)
    """

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]del$'))
        async def delete_message(event):
            if not await is_authorized(event, userbot or bot):
                return await event.reply("❌ Only group admins can use this.")

            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("❌ Reply to a message to delete it.")

            try:
                await reply.delete()
                await event.delete()  # also delete the command
            except Exception as e:
                await event.edit(f"❌ Cannot delete: {str(e)}")

    # ===================== BOT (limited) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/del$'))
        async def bot_del_info(event):
            await event.reply("Use `.del` (reply) from your **Personal Account** to delete messages.")

register = setup
