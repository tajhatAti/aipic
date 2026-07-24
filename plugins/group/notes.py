from telethon import events
from plugins.core.permissions import is_authorized

# Simple in-memory notes (per group)
# For production → use database
NOTES = {}   # {chat_id: {"note_name": "note_content"} }

def setup(bot, userbot):
    """Notes System (like Rose / Combot)
    Usage (from your Personal Account):
    .save <name> <content>
    .get <name>
    .notes
    .clear <name>
    """

    # ===================== USERBOT (Personal Account) =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]save\s+([^\s]+)\s+(.+)$'))
        async def save_note(event):
            if not event.is_group or not event.out:
                return

            name = event.pattern_match.group(1).lower()
            content = event.pattern_match.group(2)

            chat_id = event.chat_id
            if chat_id not in NOTES:
                NOTES[chat_id] = {}
            NOTES[chat_id][name] = content

            await event.edit(f"✅ Note saved as **{name}**")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]get\s+([^\s]+)$'))
        async def get_note(event):
            if not event.is_group:
                return

            name = event.pattern_match.group(1).lower()
            chat_id = event.chat_id

            if chat_id in NOTES and name in NOTES[chat_id]:
                await event.reply(NOTES[chat_id][name])
            else:
                await event.reply(f"❌ Note `{name}` not found.")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]notes$'))
        async def list_notes(event):
            if not event.is_group or not event.out:
                return

            chat_id = event.chat_id
            if chat_id not in NOTES or not NOTES[chat_id]:
                return await event.edit("No notes saved in this group.")

            text = "**Saved Notes:**\n\n"
            for name in NOTES[chat_id]:
                text += f"• `{name}`\n"
            await event.edit(text)

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]clear\s+([^\s]+)$'))
        async def clear_note(event):
            if not event.is_group or not event.out:
                return

            name = event.pattern_match.group(1).lower()
            chat_id = event.chat_id

            if chat_id in NOTES and name in NOTES[chat_id]:
                del NOTES[chat_id][name]
                await event.edit(f"✅ Note `{name}` deleted.")
            else:
                await event.edit("Note not found.")

    # ===================== BOT (info) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/notes$'))
        async def bot_notes_info(event):
            await event.reply("Notes system works best with your **Personal Account** (.save / .get)")

register = setup
