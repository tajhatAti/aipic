"""
MissRose Auto-Registration System
=================================

This is what makes the bot feel like MissRose.

When you:
- Add the bot to a group, OR
- Promote the bot to admin

This module automatically:
- Detects the event
- Fetches all current Telegram admins of the group
- Saves them to Supabase

After this, `is_authorized()` in permissions.py will allow any of those admins to use commands.

This is the core "structure".
"""

import asyncio
import logging
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import (
    ChannelParticipantAdmin, ChannelParticipantCreator,
    ChatParticipantAdmin, ChatParticipantCreator
)

from plugins.core.supabase_client import save_managed_group, get_supabase

logger = logging.getLogger(__name__)

async def _get_my_id(client):
    me = await client.get_me()
    return me.id

async def _i_am_admin(client, chat_id: int) -> bool:
    try:
        my_id = await _get_my_id(client)
        part = await client(GetParticipantRequest(chat_id, my_id))
        p = part.participant
        return isinstance(p, (ChannelParticipantAdmin, ChannelParticipantCreator,
                              ChatParticipantAdmin, ChatParticipantCreator)) or                bool(getattr(p, "admin_rights", None))
    except Exception:
        return False

async def _save_admins(client, chat_id: int):
    """Save current Telegram admins to Supabase"""
    try:
        admins = []
        async for u in client.iter_participants(chat_id, filter="administrators"):
            admins.append(u.id)

        if not admins:
            return False

        chat = await client.get_entity(chat_id)
        title = getattr(chat, "title", str(chat_id))

        ok = save_managed_group(chat_id, title, list(set(admins)))
        if ok:
            logger.info(f"✅ [AutoRegistry] Registered group: {title} ({chat_id}) — {len(admins)} admins")
        return ok
    except Exception as e:
        logger.error(f"[AutoRegistry] Error saving {chat_id}: {e}")
        return False

def setup_auto_group_registry(user_client=None, bot_client=None):
    """
    Activate automatic group registration.
    Call this in main.py after clients start.
    """
    clients = [c for c in [user_client, bot_client] if c]

    for client in clients:
        if not client:
            continue

        # Detect when we are added or promoted
        @client.on(events.ChatAction)
        async def on_action(event):
            if not (event.user_added or event.user_joined or event.user_promoted):
                return
            try:
                my_id = await _get_my_id(client)
                if event.user_id != my_id:
                    return

                chat_id = event.chat_id
                logger.info(f"[AutoRegistry] Added/promoted in {chat_id}")

                await asyncio.sleep(2)
                if await _i_am_admin(client, chat_id):
                    await _save_admins(client, chat_id)
            except Exception as e:
                logger.error(f"[AutoRegistry] Action error: {e}")

        # Fallback: first message in unknown groups
        @client.on(events.NewMessage(func=lambda e: e.is_group))
        async def on_msg(event):
            try:
                if await _i_am_admin(client, event.chat_id):
                    sb = get_supabase()
                    if sb:
                        res = sb.table("managed_groups").select("chat_id").eq("chat_id", event.chat_id).execute()
                        if not res.data:
                            await _save_admins(client, event.chat_id)
            except Exception:
                pass

    logger.info("✅ MissRose Auto-Registry is ACTIVE")

async def manual_register(client, chat_id: int) -> bool:
    """For .addgroup command"""
    if await _i_am_admin(client, chat_id):
        return await _save_admins(client, chat_id)
    return False
