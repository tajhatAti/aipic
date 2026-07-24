from telethon import events
from plugins.core.command_handler import register_universal_command

def setup(bot, userbot):

    async def admins_handler(event):
        if not event.is_group:
            return await event.reply("❌ Only works in groups.")

        try:
            admins = []
            async for user in event.client.iter_participants(event.chat_id, filter='administrators'):
                name = user.first_name or "User"
                username = f"@{user.username}" if user.username else ""
                admins.append(f"• [{name}](tg://user?id={user.id}) {username}")

            if not admins:
                return await event.reply("No admins found.")

            text = "**👑 Group Admins:**\n\n" + "\n".join(admins)
            await event.reply(text)
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["admins", "adminlist"],
        handler=admins_handler,
        owner_only=False,
        allow_in_private=False,   # Only useful in groups
        allow_in_group=True
    )

register = setup
