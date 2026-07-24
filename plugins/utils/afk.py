from telethon import events
import time

# Simple in-memory AFK storage (for one session)
AFK_STATUS = {"is_afk": False, "reason": "", "since": 0}

def setup(bot, userbot):
    """AFK (Away From Keyboard) System
    Best used with your Personal Account (userbot)
    """

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]afk(?:\s+(.*))?$'))
        async def set_afk(event):
            if not event.out:
                return

            reason = event.pattern_match.group(1) or "No reason provided."
            AFK_STATUS["is_afk"] = True
            AFK_STATUS["reason"] = reason
            AFK_STATUS["since"] = time.time()

            await event.edit(f"✅ **AFK Mode ON**\nReason: `{reason}`")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/](unafk|back)$'))
        async def remove_afk(event):
            if not event.out:
                return
            if not AFK_STATUS["is_afk"]:
                return await event.edit("You are not AFK.")

            AFK_STATUS["is_afk"] = False
            await event.edit("✅ **AFK Mode OFF** — Welcome back!")

        # Auto reply when someone messages you while AFK
        @userbot.on(events.NewMessage(incoming=True, func=lambda e: not e.is_private))
        async def afk_auto_reply(event):
            if not AFK_STATUS["is_afk"]:
                return

            # Only reply if someone mentions you or replies to you
            me = await userbot.get_me()
            if event.mentioned or (event.reply_to_msg_id and (await event.get_reply_message()).sender_id == me.id):
                since = int(time.time() - AFK_STATUS["since"])
                hours, rem = divmod(since, 3600)
                mins, _ = divmod(rem, 60)
                time_str = f"{hours}h {mins}m" if hours else f"{mins}m"

                await event.reply(
                    f"**I'm currently AFK**\n"
                    f"Reason: `{AFK_STATUS['reason']}`\n"
                    f"Since: `{time_str} ago`"
                )

    # ===================== BOT (optional info) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/afk$'))
        async def bot_afk_info(event):
            await event.reply(
                "AFK system works best with your **Personal Account**.\n"
                "Use `.afk <reason>` from your userbot."
            )

# Required for the loader
register = setup
