from telethon import events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

def setup(bot, userbot):
    """Remove deleted / zombie accounts from group
    Usage: .zombies   (in group)
    """

    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]zombies$'))
        async def clean_zombies(event):
            if not event.is_group or not event.out:
                return

            await event.edit("🔍 Scanning for deleted accounts...")

            deleted = 0
            async for user in userbot.iter_participants(event.chat_id):
                if user.deleted:
                    try:
                        await userbot.kick_participant(event.chat_id, user.id)
                        deleted += 1
                    except:
                        pass

            if deleted:
                await event.edit(f"✅ Removed **{deleted}** deleted accounts.")
            else:
                await event.edit("✅ No deleted accounts found.")

    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/zombies$'))
        async def bot_zombies(event):
            await event.reply("Use `.zombies` from your **Personal Account**.")

register = setup
