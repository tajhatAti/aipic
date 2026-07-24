from telethon import events, Button
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from plugins.core.permissions import is_authorized

def setup(bot, userbot):
    """Group Moderation - Ban, Kick, Mute, Promote etc.
    Now works for: Global Owner + Any admin of managed groups (Supabase)
    """

    # ========== USERBOT (Personal Account) - RECOMMENDED ==========
    if userbot:
        BANNED_RIGHTS = ChatBannedRights(
            until_date=None,
            view_messages=True,
            send_messages=True,
            send_media=True,
            send_stickers=True,
            send_gifs=True,
            send_inline=True,
            embed_links=True
        )

        UNBANNED_RIGHTS = ChatBannedRights(
            until_date=None,
            view_messages=False,
            send_messages=False
        )

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/](ban|kick)$'))
        async def ban_kick(event):
            if not event.is_group:
                return await event.reply("❌ This command only works in groups.")

            # NEW: Allow global owner + any admin of this group
            if not await is_authorized(event, userbot):
                return await event.reply("❌ Only group admins can use this.")

            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("❌ Reply to a user to ban/kick.")

            try:
                user = await userbot.get_entity(reply.sender_id)
                if event.pattern_match.group(1).lower() == "kick":
                    await userbot(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
                    await userbot(EditBannedRequest(event.chat_id, user.id, UNBANNED_RIGHTS))
                    await event.edit(f"👢 **Kicked** [{user.first_name}](tg://user?id={user.id})")
                else:
                    await userbot(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
                    await event.edit(f"🔨 **Banned** [{user.first_name}](tg://user?id={user.id})")
            except Exception as e:
                await event.edit(f"❌ Error: {str(e)}")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]unban$'))
        async def unban_handler(event):
            if not event.is_group:
                return
            if not await is_authorized(event, userbot):
                return
            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("Reply to a user.")
            try:
                user = await userbot.get_entity(reply.sender_id)
                await userbot(EditBannedRequest(event.chat_id, user.id, UNBANNED_RIGHTS))
                await event.edit(f"✅ **Unbanned** [{user.first_name}](tg://user?id={user.id})")
            except Exception as e:
                await event.edit(f"❌ {e}")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/](mute|unmute)$'))
        async def mute_handler(event):
            if not event.is_group:
                return
            if not await is_authorized(event, userbot):
                return await event.reply("❌ Only group admins can use this.")
            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("Reply to a user.")

            user = await userbot.get_entity(reply.sender_id)
            if "unmute" in event.raw_text.lower():
                rights = ChatBannedRights(until_date=None, send_messages=False)
                await userbot(EditBannedRequest(event.chat_id, user.id, rights))
                await event.edit(f"🔊 **Unmuted** [{user.first_name}]")
            else:
                rights = ChatBannedRights(until_date=None, send_messages=True)
                await userbot(EditBannedRequest(event.chat_id, user.id, rights))
                await event.edit(f"🔇 **Muted** [{user.first_name}]")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/](promote|demote)$'))
        async def promote_demote(event):
            if not event.is_group:
                return
            if not await is_authorized(event, userbot):
                return await event.reply("❌ Only group admins can use this.")
            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("Reply to a user.")

            user = await userbot.get_entity(reply.sender_id)
            cmd = event.pattern_match.group(1).lower()

            if cmd == "promote":
                await userbot.edit_admin(
                    event.chat_id, user.id,
                    is_admin=True,
                    change_info=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True
                )
                await event.edit(f"👑 **Promoted** [{user.first_name}] to Admin")
            else:
                await userbot.edit_admin(event.chat_id, user.id, is_admin=False)
                await event.edit(f"⬇️ **Demoted** [{user.first_name}]")

    # ========== BOT SIDE (for public / inline) ==========
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/ban$'))
        async def bot_ban(event):
            await event.reply(
                "⚠️ Group moderation commands work best with your **Personal Account**.\n"
                "Use `.ban` from your userbot instead."
            )

# Make compatible with current main.py loader
register = setup
