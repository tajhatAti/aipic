from telethon import events, Button

def setup(bot, userbot):
    """
    BOT FEATURES (using Bot Token)
    Inline buttons, callbacks, and public bot commands.
    These are things your personal account (userbot) cannot do well.
    """

    # ===================== INLINE BUTTON EXAMPLE =====================
    if bot:
        @bot.on(events.NewMessage(pattern=r'(?i)^/start$'))
        async def start_handler(event):
            buttons = [
                [Button.inline("📊 Group Tools", b"group_tools")],
                [Button.inline("👤 User Info", b"user_info")],
                [Button.url("🌐 GitHub", "https://github.com")]
            ]
            await event.reply(
                "✅ **Welcome to AIPIC Hybrid Bot!**\n\n"
                "I can work as both a **Bot** and your **Personal Account** (userbot).\n\n"
                "Use the buttons below:",
                buttons=buttons
            )

        @bot.on(events.CallbackQuery(data=b"group_tools"))
        async def group_tools_callback(event):
            await event.edit(
                "**Group Management Tools**\n\n"
                "These commands work best when used from your **Personal Account**:\n"
                "• `.ban` (reply)\n"
                "• `.kick` (reply)\n"
                "• `.mute` / `.unmute`\n"
                "• `.promote` / `.demote`\n"
                "• `.tagall`\n"
                "• `.purge`\n"
                "• `.lock` / `.unlock`",
                buttons=[[Button.inline("← Back", b"back_to_main")]]
            )

        @bot.on(events.CallbackQuery(data=b"user_info"))
        async def user_info_callback(event):
            user = await event.get_sender()
            await event.edit(
                f"**Your Info:**\n\n"
                f"• Name: {user.first_name}\n"
                f"• ID: `{user.id}`\n"
                f"• Username: @{user.username or 'None'}",
                buttons=[[Button.inline("← Back", b"back_to_main")]]
            )

        @bot.on(events.CallbackQuery(data=b"back_to_main"))
        async def back_callback(event):
            buttons = [
                [Button.inline("📊 Group Tools", b"group_tools")],
                [Button.inline("👤 User Info", b"user_info")],
            ]
            await event.edit(
                "✅ **AIPIC Hybrid**\nChoose an option:",
                buttons=buttons
            )

        # Public bot command example
        @bot.on(events.NewMessage(pattern=r'(?i)^/bothelp$'))
        async def bot_help(event):
            await event.reply(
                "**Bot Commands (via Bot Token):**\n"
                "/start - Main menu with buttons\n"
                "/bothelp - This message\n\n"
                "Most powerful group commands are available via your **Personal Account** (use `.command`)."
            )

# Compatibility with main.py loader
register = setup
