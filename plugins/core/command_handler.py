"""
AIPIC Universal Command System (Big Architectural Change)

Features:
- Supports: .ping   !ping   /ping   ping   /ping@YourBot
- Works in Group + Private Inbox
- Owner fully controls which commands non-owners can use in inbox
- Easy to use for all future plugins

Usage in any plugin:

from plugins.core.command_handler import register_universal_command

def setup(bot, userbot):

    async def my_ping(event):
        await event.reply("Pong!")

    register_universal_command(
        userbot=userbot,
        bot=bot,
        commands=["ping", "p"],
        handler=my_ping,
        owner_only=False,           # Anyone can use
        allow_in_private=True,      # Can be used in inbox
        allow_in_group=True
    )
"""

import re
from telethon import events
from plugins.core.permissions import is_authorized, is_global_owner

# === CONFIG (Owner can change these via commands later) ===
DEFAULT_PREFIXES = ['.', '!', '/']

# Commands that NON-OWNERS are allowed to use in your private inbox
# Owner can manage this list using future commands (e.g. .allow ping)
PUBLIC_INBOX_COMMANDS = {
    "ping", "alive", "id", "help", "stats", "chatinfo", "link"
}

# Will be set automatically from environment
OWNER_ID = None

def set_owner(owner_id: int):
    global OWNER_ID
    OWNER_ID = owner_id

def is_owner(user_id: int) -> bool:
    return is_global_owner(user_id)

def build_universal_pattern(commands: list) -> str:
    """
    Creates a powerful regex that matches almost everything:
    - .ping
    - !ping
    - /ping
    - ping
    - /ping@MyBotUsername
    - /ping@mybot
    """
    cmd_group = '|'.join(re.escape(c) for c in commands)
    
    # Optional prefix
    prefix = rf'[{"".join(re.escape(p) for p in DEFAULT_PREFIXES)}]?'
    
    # Optional @botusername after command
    bot_mention = r'(?:@\w+)?'
    
    # Final regex
    return rf'(?i)^{prefix}({cmd_group}){bot_mention}(?:\s|$)'

def register_universal_command(
    user=None,
    bot=None,
    userbot=None,
    commands: list | str = None,
    handler=None,
    owner_only: bool = False,
    allow_in_private: bool = True,
    allow_in_group: bool = True
):
    # Backward compatibility: support both "user" and "userbot" parameter names
    actual_user = user or userbot
    """
    The main function every plugin should use from now on.
    """
    if not commands or not handler:
        return

    if isinstance(commands, str):
        commands = [commands]

    pattern = build_universal_pattern(commands)

    async def smart_handler(event):
        sender = event.sender_id

        # === NEW PERMISSION (MissRose style) ===
        # Global OWNER or any admin of a managed group (from Supabase) can use
        authorized = await is_authorized(event, userbot or bot)

        if not authorized:
            if owner_only:
                return
            # For non-owner-only commands, still respect inbox whitelist below

        # Owner-only commands
        if owner_only and not authorized:
            return

        # Group vs Private control
        if event.is_group and not allow_in_group:
            return
        if event.is_private and not allow_in_private:
            return

        # Inbox public command whitelist (only for non-owners)
        if event.is_private and not is_owner(sender):
            cmd_name = event.pattern_match.group(1).lower() if event.pattern_match else ""
            if cmd_name not in PUBLIC_INBOX_COMMANDS:
                return

        await handler(event)

    # Register on both clients
    if userbot:
        userbot.add_event_handler(smart_handler, events.NewMessage(pattern=pattern))
    if bot:
        bot.add_event_handler(smart_handler, events.NewMessage(pattern=pattern))

# Convenience function for multiple commands at once
def register_multiple(userbot=None, bot=None, command_list: dict = None):
    for cmd, opts in (command_list or {}).items():
        register_universal_command(
            userbot=userbot,
            bot=bot,
            commands=cmd if isinstance(cmd, list) else [cmd],
            handler=opts.get("handler"),
            owner_only=opts.get("owner_only", False),
            allow_in_private=opts.get("allow_in_private", True),
            allow_in_group=opts.get("allow_in_group", True)
        )
