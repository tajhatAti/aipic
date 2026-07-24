"""
Inbox Command Permission Control (Owner Only)

Commands:
.owner only
.allow ping          → Allow non-owners to use .ping in your inbox
.disallow ping       → Block non-owners from using .ping in inbox
.inboxlist           → See which commands are allowed for others in inbox
"""

from telethon import events
from plugins.core.command_handler import PUBLIC_INBOX_COMMANDS

def setup(bot, userbot):

    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/](allow|disallow)\s+(\w+)$'))
        async def toggle_inbox_command(event):
            if not event.out:
                return

            action = event.pattern_match.group(1).lower()
            cmd = event.pattern_match.group(2).lower().strip()

            if action == "allow":
                PUBLIC_INBOX_COMMANDS.add(cmd)
                await event.edit(f"✅ `{cmd}` is now **allowed** for others in your inbox.")
            else:
                PUBLIC_INBOX_COMMANDS.discard(cmd)
                await event.edit(f"❌ `{cmd}` is now **blocked** for others in your inbox.")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]inboxlist$'))
        async def list_inbox_commands(event):
            if not event.out:
                return

            if not PUBLIC_INBOX_COMMANDS:
                await event.edit("No commands are currently allowed for others in inbox.")
                return

            text = "**Commands others can use in your Inbox:**\n\n"
            for cmd in sorted(PUBLIC_INBOX_COMMANDS):
                text += f"• `{cmd}`\n"
            await event.edit(text)

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]owneronly$'))
        async def owner_only_mode(event):
            if not event.out:
                return
            # Clear all public inbox commands
            PUBLIC_INBOX_COMMANDS.clear()
            await event.edit("🔒 **Owner Only Mode** enabled.\nNo one else can use commands in your inbox now.")

# Register this for both
register = setup
