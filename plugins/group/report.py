from telethon import events
from plugins.core.permissions import is_authorized

def setup(bot, userbot):
    """Report a user to admins
    Usage: .report (reply to a message)
    """

    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]report$'))
        async def report_user(event):
            if not event.is_group or not event.out:
                return

            reply = await event.get_reply_message()
            if not reply:
                return await event.edit("❌ Reply to a message to report the user.")

            try:
                user = await userbot.get_entity(reply.sender_id)
                chat = await userbot.get_entity(event.chat_id)

                report_text = (
                    f"🚨 **Report**\n\n"
                    f"**From:** [{event.sender.first_name}](tg://user?id={event.sender_id})\n"
                    f"**Reported:** [{user.first_name or 'User'}](tg://user?id={user.id})\n"
                    f"**Group:** {chat.title}\n"
                    f"**Message:** {reply.text[:100] if reply.text else '(media)'}"
                )

                # Send to all admins
                admins = []
                async for admin in userbot.iter_participants(event.chat_id, filter='admins'):
                    if not admin.bot:
                        admins.append(admin.id)

                if admins:
                    for admin_id in admins[:5]:  # limit
                        try:
                            await userbot.send_message(admin_id, report_text)
                        except:
                            pass

                await event.edit("✅ Report sent to group admins.")
            except Exception as e:
                await event.edit(f"❌ Failed: {str(e)}")

    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/report$'))
        async def bot_report(event):
            await event.reply("Use `.report` (reply) from your **Personal Account**.")

register = setup
