from telethon import events
from plugins.core.permissions import is_authorized
from telethon.tl.functions.messages import ExportChatInviteRequest

def setup(bot, userbot):
    """Get or create group invite link
    Usage: .link   or   .invitelink
    """

    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/](link|invitelink)$'))
        async def get_invite_link(event):
            if not event.is_group or not event.out:
                return

            try:
                link = await userbot(ExportChatInviteRequest(event.chat_id))
                await event.edit(f"🔗 **Invite Link:**\n\n{link.link}")
            except Exception as e:
                await event.edit(f"❌ Failed to get link: {str(e)}")

    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/link$'))
        async def bot_link(event):
            await event.reply("Use `.link` from your **Personal Account** to get invite link.")

register = setup
