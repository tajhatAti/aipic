from telethon import events
from plugins.core.permissions import is_authorized
from telethon.tl.functions.users import GetFullUserRequest

def setup(bot, userbot):
    """Get detailed info about a user (works best with userbot)"""

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]info(?:\s+(.+))?$'))
        async def user_info(event):
            if not await is_authorized(event, userbot or bot):
                return await event.reply("❌ Only group admins can use this.")

            target = await get_target_user(event, userbot)
            if not target:
                return await event.edit("❌ Reply to a user or give @username / ID.")

            try:
                full = await userbot(GetFullUserRequest(target.id))
                user = full.users[0]
                bio = full.full_user.about or "No bio"

                text = (
                    f"**👤 User Info**\n\n"
                    f"**Name:** {user.first_name or ''} {user.last_name or ''}\n"
                    f"**Username:** @{user.username or 'None'}\n"
                    f"**ID:** `{user.id}`\n"
                    f"**Bot:** {'Yes' if user.bot else 'No'}\n"
                    f"**Premium:** {'Yes' if getattr(user, 'premium', False) else 'No'}\n"
                    f"**Bio:** `{bio}`"
                )
                await event.edit(text)
            except Exception as e:
                await event.edit(f"❌ Error: {str(e)}")

    # ===================== BOT (limited) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/info$'))
        async def bot_info(event):
            await event.reply("Use `.info` (reply to user) from your **Personal Account** for full details.")

    async def get_target_user(event, client):
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            try:
                return await client.get_entity(reply.sender_id)
            except:
                pass
        text = event.raw_text or ""
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            target = parts[1].strip()
            try:
                if target.startswith('@'):
                    return await client.get_entity(target)
                if target.isdigit():
                    return await client.get_entity(int(target))
            except:
                pass
        return None

register = setup
