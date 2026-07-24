"""
Universal Help Command
Shows available commands and explains the new system.
"""

from telethon import events
from plugins.core.command_handler import register_universal_command

HELP_TEXT = """
**AIPIC - Universal Commands**

**Supported formats (all work):**
• `.ping`   `!ping`   `/ping`   `ping`
• `/ping@YourBotUsername`

**Works in:**
• Groups
• Your Private Inbox (for allowed commands)

**Core Commands:**
• `.ping` / `.p`
• `.alive`
• `.id`
• `.help`

**Inbox Control (Owner Only):**
• `.allow ping` — Allow others to use ping in your inbox
• `.disallow ping`
• `.inboxlist` — See allowed commands
• `.owneronly` — Block everyone in inbox

**Group Management (mostly owner only):**
• `.ban` `.kick` `.mute`
• `.tagall`
• `.zombies` `.stats` etc.

Use commands from your Personal Account for best results.
"""

def setup(bot, userbot):

    async def help_handler(event):
        await event.reply(HELP_TEXT)

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["help", "commands"],
        handler=help_handler,
        owner_only=False,
        allow_in_private=True,
        allow_in_group=True
    )

register = setup
