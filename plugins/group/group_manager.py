"""
Group Manager - MissRose style
Commands:
.addgroup     → Register current group (saves all current admins to Supabase)
.groups       → List managed groups (owner only)
.removegroup  → Deactivate a group
"""

from telethon import events
from plugins.core.permissions import register_group, is_global_owner
from plugins.core.supabase_client import get_all_managed_groups
from plugins.core.command_handler import register_universal_command

def setup(bot, userbot):

    async def addgroup_handler(event):
        if not event.is_group:
            return await event.reply("❌ This command only works in groups.")

        # Only global owner or current admins can add
        # We use live check here
        client = userbot or bot
        if not client:
            return

        # Try to register
        success = await register_group(client, event.chat_id, (await event.get_chat()).title if hasattr(event, 'get_chat') else None)
        
        if success:
            await event.reply("✅ Group registered! All current admins can now control the bot here.")
        else:
            await event.reply("❌ Failed to register group. Make sure the bot/userbot is admin.")

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["addgroup", "registergroup"],
        handler=addgroup_handler,
        owner_only=False,           # Anyone who is already admin can run it
        allow_in_private=False,
        allow_in_group=True
    )

    # Owner only commands
    async def list_groups(event):
        if not is_global_owner(event.sender_id):
            return await event.reply("❌ Owner only.")

        groups = get_all_managed_groups()
        if not groups:
            return await event.reply("No groups registered yet.")

        text = "**Managed Groups:**\n\n"
        for g in groups[:15]:
            text += f"• `{g['chat_id']}` — {g.get('title', 'No title')}\n"
        await event.reply(text)

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["groups", "listgroups"],
        handler=list_groups,
        owner_only=True,
        allow_in_private=True,
        allow_in_group=True
    )

register = setup
