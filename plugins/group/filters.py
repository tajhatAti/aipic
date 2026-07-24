from telethon import events
from plugins.core.permissions import is_authorized

# Simple in-memory filters (per chat)
# Format: {chat_id: {"trigger": "response"}}
FILTERS = {}

def setup(bot, userbot):
    """Auto Reply Filters
    Usage (Userbot):
    .filter <trigger> <response>
    .filters
    .stop <trigger>
    """

    # ===================== USERBOT =====================
    if userbot:
        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]filter\s+(.+?)\s+(.+)$'))
        async def add_filter(event):
            if not event.is_group or not event.out:
                return

            trigger = event.pattern_match.group(1).lower().strip()
            response = event.pattern_match.group(2).strip()

            chat_id = event.chat_id
            if chat_id not in FILTERS:
                FILTERS[chat_id] = {}
            FILTERS[chat_id][trigger] = response

            await event.edit(f"✅ Filter added:\n`{trigger}` → `{response}`")

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]filters$'))
        async def list_filters(event):
            if not event.is_group or not event.out:
                return

            chat_id = event.chat_id
            if chat_id not in FILTERS or not FILTERS[chat_id]:
                return await event.edit("No filters in this chat.")

            text = "**Current Filters:**\n\n"
            for trig, resp in FILTERS[chat_id].items():
                text += f"• `{trig}` → `{resp[:50]}{'...' if len(resp) > 50 else ''}`\n"
            await event.edit(text)

        @userbot.on(events.NewMessage(pattern=r'(?i)^[.!/]stop\s+(.+)$'))
        async def remove_filter(event):
            if not event.is_group or not event.out:
                return

            trigger = event.pattern_match.group(1).lower().strip()
            chat_id = event.chat_id

            if chat_id in FILTERS and trigger in FILTERS[chat_id]:
                del FILTERS[chat_id][trigger]
                await event.edit(f"✅ Filter removed: `{trigger}`")
            else:
                await event.edit("Filter not found.")

        # Auto reply when trigger is said
        @userbot.on(events.NewMessage(incoming=True))
        async def check_filters(event):
            if not event.is_group:
                return
            chat_id = event.chat_id
            if chat_id not in FILTERS:
                return

            text = (event.raw_text or "").lower().strip()
            for trigger, response in FILTERS[chat_id].items():
                if trigger in text:
                    await event.reply(response)
                    break

    # ===================== BOT (info) =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/filter$'))
        async def bot_filter_info(event):
            await event.reply("Filters work best with your **Personal Account** (.filter)")

register = setup
