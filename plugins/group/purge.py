from telethon import events
import asyncio
from plugins.core.permissions import is_authorized

def setup(bot, userbot):
    """Purge / Delete messages — now works for any admin of managed groups"""

    async def purge_handler(event):
        if not event.is_group:
            return await event.reply("❌ Only in groups.")

        if not await is_authorized(event, userbot or bot):
            return await event.reply("❌ Only group admins can purge.")

        reply = await event.get_reply_message()
        if not reply:
            return await event.edit("❌ Reply to the first message you want to delete from.")

        client = userbot or bot
        count = 0
        try:
            async for msg in client.iter_messages(
                event.chat_id,
                min_id=reply.id - 1,
                reverse=True
            ):
                try:
                    await msg.delete()
                    count += 1
                    if count % 10 == 0:
                        await asyncio.sleep(0.4)
                except:
                    pass
            await event.edit(f"🗑 **Purged {count} messages.**", delete_in=4)
        except Exception as e:
            await event.edit(f"❌ Error: {e}")

    if userbot:
        userbot.add_event_handler(purge_handler, events.NewMessage(pattern=r'(?i)^[.!/]purge$'))
    if bot:
        bot.add_event_handler(purge_handler, events.NewMessage(pattern=r'(?i)^/purge$'))

register = setup
