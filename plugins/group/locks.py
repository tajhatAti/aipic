from telethon import events
from plugins.core.permissions import is_authorized, Button
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights

def setup(bot, userbot):
    """Chat Locks - Lock/Unlock permissions (Best with Userbot)"""

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        async def set_lock(chat_id, lock_type, value):
            """Helper to change default banned rights"""
            current = await userbot.get_permissions(chat_id)
            rights = current.default_banned_rights or ChatBannedRights()

            if lock_type == "all":
                rights.send_messages = value
                rights.send_media = value
                rights.send_stickers = value
                rights.send_gifs = value
                rights.send_games = value
                rights.send_inline = value
                rights.embed_links = value
            elif lock_type == "media":
                rights.send_media = value
            elif lock_type == "stickers":
                rights.send_stickers = value
            elif lock_type == "links":
                rights.embed_links = value
            elif lock_type == "forward":
                rights.forward_messages = value

            await userbot(EditChatDefaultBannedRightsRequest(chat_id, rights))

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]lock\s+(all|media|stickers|links|forward)$'))
        async def lock_cmd(event):
            if not event.is_group or not event.out:
                return
            lock_type = event.pattern_match.group(1).lower()
            await set_lock(event.chat_id, lock_type, True)
            await event.edit(f"🔒 **Locked** `{lock_type}` in this chat")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]unlock\s+(all|media|stickers|links|forward)$'))
        async def unlock_cmd(event):
            if not event.is_group or not event.out:
                return
            lock_type = event.pattern_match.group(1).lower()
            await set_lock(event.chat_id, lock_type, False)
            await event.edit(f"🔓 **Unlocked** `{lock_type}` in this chat")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]locks$'))
        async def locks_status(event):
            if not event.is_group or not event.out:
                return
            perms = await userbot.get_permissions(event.chat_id)
            r = perms.default_banned_rights or ChatBannedRights()

            text = "**Current Locks:**\n"
            text += f"• Messages: {'🔒' if r.send_messages else '🔓'}\n"
            text += f"• Media: {'🔒' if r.send_media else '🔓'}\n"
            text += f"• Stickers/GIFs: {'🔒' if r.send_stickers else '🔓'}\n"
            text += f"• Links: {'🔒' if r.embed_links else '🔓'}\n"
            await event.edit(text)

    # ===================== BOT (Info only) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/locks$'))
        async def bot_locks(event):
            await event.reply("Use `.lock all` / `.unlock media` etc from your **Personal Account** (userbot) for best results.")

register = setup
