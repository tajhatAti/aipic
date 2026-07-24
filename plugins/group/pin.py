from telethon import events
from plugins.core.permissions import is_authorized

def setup(bot, userbot):
    """Pin / Unpin messages in group
    Usage:
    .pin          (reply to message)
    .unpin        (reply or last pinned)
    .unpin all
    """

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]pin$'))
        async def pin_message(event):
            if not event.is_group or not event.out:
                return

            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("❌ Reply to a message to pin it.")

            try:
                await userbot.pin_message(event.chat_id, reply.id, notify=False)
                await event.edit("📌 **Message Pinned**")
            except Exception as e:
                await event.edit(f"❌ Failed to pin: {str(e)}")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]unpin(?:\s+(all))?$'))
        async def unpin_message(event):
            if not event.is_group or not event.out:
                return

            cmd = event.pattern_match.group(1)
            try:
                if cmd == "all":
                    await userbot.unpin_all_messages(event.chat_id)
                    await event.edit("📌 **All messages unpinned**")
                else:
                    reply = await event.get_reply_message()
                    if reply:
                        await userbot.unpin_message(event.chat_id, reply.id)
                    else:
                        await userbot.unpin_message(event.chat_id)
                    await event.edit("📌 **Message Unpinned**")
            except Exception as e:
                await event.edit(f"❌ Error: {str(e)}")

    # ===================== BOT (info) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/pin$'))
        async def bot_pin_info(event):
            await event.reply("Pin/Unpin works best with your **Personal Account** (.pin / .unpin)")

register = setup
