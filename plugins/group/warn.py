from telethon import events
from plugins.core.permissions import is_authorized
from collections import defaultdict

# Simple in-memory warn storage (resets on restart)
WARNS = defaultdict(int)  # {user_id: count}

def setup(bot, userbot):
    """Warn System for groups
    Usage:
    .warn (reply)         → Warn a user
    .warns (reply)        → Check warns
    .resetwarns (reply)   → Reset warns
    """

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]warn$'))
        async def warn_user(event):
            if not event.is_group or not event.out:
                return

            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("❌ Reply to a user to warn.")

            user_id = reply.sender_id
            WARNS[user_id] += 1
            count = WARNS[user_id]

            await event.edit(
                f"⚠️ **Warned** user `{user_id}`\n"
                f"**Total warns:** `{count}`"
            )

            # Optional: auto action at 3 warns
            if count >= 3:
                await event.reply(
                    f"🚨 User has reached **3 warns**!\n"
                    "Consider using `.ban` or `.mute`."
                )

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]warns$'))
        async def check_warns(event):
            if not event.is_group or not event.out:
                return

            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("❌ Reply to a user.")

            user_id = reply.sender_id
            count = WARNS.get(user_id, 0)
            await event.edit(f"**Warns for** `{user_id}`: **{count}**")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]resetwarns$'))
        async def reset_warns(event):
            if not event.is_group or not event.out:
                return

            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("❌ Reply to a user.")

            user_id = reply.sender_id
            WARNS[user_id] = 0
            await event.edit(f"✅ Warns reset for `{user_id}`")

    # ===================== BOT (info) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/warn$'))
        async def bot_warn_info(event):
            await event.reply("Warn system works best with your **Personal Account** (.warn)")

register = setup
