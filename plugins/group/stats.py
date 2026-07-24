from telethon import events
from plugins.core.permissions import is_authorized

def setup(bot, userbot):
    """Show basic group statistics
    Usage: .stats   (works for any group admin)
    """

    async def group_stats(event):
        if not event.is_group:
            return
        if not await is_authorized(event, userbot or bot):
            return await event.reply("❌ Only group admins can use this.")

        client = userbot or bot
        try:
            chat = await client.get_entity(event.chat_id)
            total = bots = admins = 0

            async for user in client.iter_participants(event.chat_id):
                total += 1
                if user.bot:
                    bots += 1
                if getattr(user, 'participant', None) and getattr(user.participant, 'admin_rights', None):
                    admins += 1

            text = f"**📊 Group Stats**\n\n**Title:** {chat.title}\n**Total Members:** {total}\n**Bots:** {bots}\n**Admins:** {admins}\n**ID:** `{chat.id}`"
            await event.edit(text)
        except Exception as e:
            await event.edit(f"❌ Error: {e}")

    if userbot:
        userbot.add_event_handler(group_stats, events.NewMessage(pattern=r'(?i)^[.!/]stats$'))
    if bot:
        bot.add_event_handler(group_stats, events.NewMessage(pattern=r'(?i)^/stats$'))

register = setup
