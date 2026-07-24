from telethon import events
import asyncio
from plugins.core.command_handler import register_universal_command
from plugins.core.permissions import is_authorized

def setup(bot, userbot):

    async def tagall_handler(event):
        if not event.is_group:
            return await event.reply("❌ Only works in groups.")

        if not await is_authorized(event, userbot or bot):
            return await event.reply("❌ Only group admins can use .tagall")

        message = event.pattern_match.group(1) or "Everyone wake up!" if hasattr(event, 'pattern_match') else "Everyone wake up!"
        
        await event.edit("📢 **Tagging everyone...**")

        users = []
        client = userbot or bot or event.client
        async for user in client.iter_participants(event.chat_id):
            if not user.bot:
                users.append(f"[{user.first_name or 'User'}](tg://user?id={user.id})")

        for i in range(0, len(users), 5):
            chunk = "\n".join(users[i:i+5])
            try:
                await client.send_message(event.chat_id, f"**{message}**\n\n{chunk}")
                await asyncio.sleep(1.2)
            except:
                break

        try:
            await event.delete()
        except:
            pass

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["tagall", "all"],
        handler=tagall_handler,
        owner_only=False,          # Now any admin of managed group
        allow_in_private=False,
        allow_in_group=True
    )

register = setup
