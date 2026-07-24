"""
MissRose Permission System (THE CORE)
=====================================

This is the single source of truth for permissions.

=== How @MissRose_Bot Actually Works ===

1. User adds the bot (or userbot) to a group.
2. User goes to Group → Administrators → Promotes the bot to "Admin".
3. Rose automatically detects that it was promoted (via Telegram events).
4. Rose fetches the **full current list of Telegram admins** of that group.
5. Rose saves to its database:
     - chat_id
     - title
     - admins: [user_id1, user_id2, ...]   ← all current Telegram admins

6. Result:
   - From now on, **any person who is an admin in Telegram** for that group
     can use Rose's commands inside the group.
   - No manual .allow, .addadmin, or whitelist needed.

This is exactly the model we are building.

=== For All Future Commands ===

from plugins.core.permissions import is_authorized

async def my_command(event):
    if not await is_authorized(event):
        return await event.reply("❌ Only group admins can use this command.")

    # your logic here
"""

import os
from plugins.core.supabase_client import (
    is_group_admin as db_is_group_admin,
    save_managed_group,
    get_supabase
)

OWNER_ID = int(os.environ.get("OWNER_ID", "0") or 0)


def is_global_owner(user_id: int) -> bool:
    """The person who owns this entire bot (OWNER_ID) has full power everywhere."""
    return OWNER_ID != 0 and user_id == OWNER_ID


async def is_authorized(event, client=None) -> bool:
    """
    Main permission check. Call this in every command.
    """
    if not event or not getattr(event, "sender_id", None):
        return False

    sender = event.sender_id

    # 1. Bot owner (you) always allowed
    if is_global_owner(sender):
        return True

    # 2. Private chat → only owner
    if getattr(event, "is_private", False):
        return is_global_owner(sender)

    # 3. Group → the sender must be a Telegram admin of THIS group
    if not getattr(event, "is_group", False):
        return False

    chat_id = event.chat_id

    # Fast path: we already saved the admins in Supabase
    if db_is_group_admin(chat_id, sender):
        return True

    # Live check from Telegram + refresh our cache
    client = client or getattr(event, "client", None)
    if client:
        try:
            from telethon.tl.types import ChannelParticipantsAdmins
            async for p in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
                if p.id == sender:
                    await _refresh_admins(client, chat_id)
                    return True
        except Exception:
            pass

    return False


async def _refresh_admins(client, chat_id: int):
    """Refresh the list of admins for this group in Supabase."""
    try:
        from telethon.tl.types import ChannelParticipantsAdmins
        admins = [p.id async for p in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins)]
        if admins:
            chat = await client.get_entity(chat_id)
            title = getattr(chat, "title", str(chat_id))
            save_managed_group(chat_id, title, admins)
    except Exception:
        pass


async def register_group(client, chat_id: int, title: str = None) -> bool:
    """
    Manual registration (used by .addgroup command).
    Only works if the bot is currently admin in the group.
    """
    if not client:
        return False
    try:
        from telethon.tl.types import ChannelParticipantsAdmins
        admins = [p.id async for p in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins)]
        if admins:
            save_managed_group(chat_id, title or str(chat_id), admins)
            return True
    except Exception:
        pass
    return False
