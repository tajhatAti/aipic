"""
Core Commands - Updated to use Universal Command System

This is the new standard. All future commands should use register_universal_command.
"""

from telethon import events
from plugins.core.command_handler import register_universal_command

def setup(bot, userbot):

    # ===================== PING =====================
    async def ping_handler(event):
        from time import time
        start = time()
        msg = await event.reply("`Pinging...`") if not event.out else await event.edit("`Pinging...`")
        latency = int((time() - start) * 1000)
        await msg.edit(f"🏓 **Pong!** `{latency}ms`")

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["ping", "p"],
        handler=ping_handler,
        owner_only=False,
        allow_in_private=True,
        allow_in_group=True
    )

    # ===================== ALIVE =====================
    async def alive_handler(event):
        text = (
            "✅ **AIPIC Hybrid** is running\n\n"
            "• **Userbot** (Personal Account) → Group Management\n"
            "• **Bot** → Inline buttons & public features\n\n"
            "Use `.help` to see commands."
        )
        if event.out:
            await event.edit(text)
        else:
            await event.reply(text)

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["alive", "status"],
        handler=alive_handler,
        owner_only=False,
        allow_in_private=True,
        allow_in_group=True
    )

    # ===================== ID =====================
    async def id_handler(event):
        text = f"**Chat ID:** `{event.chat_id}`"
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            text += f"\n**User ID:** `{reply.sender_id}`"
        if event.out:
            await event.edit(text)
        else:
            await event.reply(text)

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["id"],
        handler=id_handler,
        owner_only=False,
        allow_in_private=True,
        allow_in_group=True
    )

# For backward compatibility with loader
register = setup
