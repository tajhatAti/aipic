import os
import asyncio
import logging
import importlib
import inspect
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# =====================================================
# CONFIGURATION
# =====================================================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PORT = int(os.environ.get("PORT", 8080))
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not API_ID or not API_HASH:
    logger.error("❌ API_ID and API_HASH are required!")
    exit(1)

if not STRING_SESSION and not BOT_TOKEN:
    logger.error("❌ At least one of STRING_SESSION or BOT_TOKEN is required!")
    exit(1)

# =====================================================
# DUAL CLIENTS (Hybrid Mode)
# =====================================================
user_client = None
bot_client = None

if STRING_SESSION:
    user_client = TelegramClient(
        StringSession(STRING_SESSION),
        API_ID,
        API_HASH
    )
    logger.info("✅ Userbot client (Personal Account) initialized")

if BOT_TOKEN:
    bot_client = TelegramClient(
        f"bot_{BOT_TOKEN.split(':')[0]}",
        API_ID,
        API_HASH
    )
    logger.info("✅ Bot client initialized")

# =====================================================
# ROBUST PLUGIN LOADER (MissRose ready)
# =====================================================
def get_callable_params(func):
    try:
        sig = inspect.signature(func)
        return [
            name for name, param in sig.parameters.items()
            if param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY
            )
        ]
    except Exception:
        return []

def call_register_safely(reg, bot=None, userbot=None):
    if not callable(reg):
        return False, "not callable"

    accepted = get_callable_params(reg)
    kwargs = {}
    if bot is not None and "bot" in accepted:
        kwargs["bot"] = bot
    if userbot is not None and "userbot" in accepted:
        kwargs["userbot"] = userbot
    if userbot is not None and "user" in accepted and "userbot" not in accepted:
        kwargs["user"] = userbot

    if kwargs:
        try:
            reg(**kwargs)
            return True, None
        except TypeError:
            pass
        except Exception as e:
            return False, str(e)

    if len(accepted) >= 2:
        try:
            reg(bot, userbot)
            return True, None
        except TypeError:
            pass
        try:
            reg(userbot, bot)
            return True, None
        except TypeError:
            pass

    try:
        if bot is not None and userbot is not None:
            reg(bot, userbot)
            return True, None
    except Exception:
        pass

    return False, f"signature mismatch (accepted={accepted})"

def load_plugins():
    """Load all plugins + activate MissRose-style auto registry"""
    base_path = "plugins"
    plugin_count = 0
    failed_plugins = []

    # Early init
    try:
        init_mod = importlib.import_module("plugins.core.init_core")
        reg = getattr(init_mod, "register", getattr(init_mod, "setup", None))
        if reg:
            call_register_safely(reg, bot=bot_client, userbot=user_client)
    except Exception as e:
        logger.warning(f"init_core issue: {e}")

    # Load all other plugins
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = os.path.relpath(os.path.join(root, file), base_path)
                module_name = rel_path.replace(os.sep, ".").replace(".py", "")

                if module_name == "core.init_core":
                    continue

                try:
                    module = importlib.import_module(f"plugins.{module_name}")
                    reg = getattr(module, "register", getattr(module, "setup", None))
                    if reg and callable(reg):
                        success, err = call_register_safely(reg, bot=bot_client, userbot=user_client)
                        if success:
                            plugin_count += 1
                            logger.info(f"✅ Loaded: {module_name}")
                        else:
                            failed_plugins.append(module_name)
                            logger.error(f"❌ Failed: {module_name} — {err}")
                except Exception as e:
                    failed_plugins.append(module_name)
                    logger.error(f"❌ Load error {module_name}: {e}")

    logger.info(f"📦 Total plugins loaded: {plugin_count}")

    # =====================================================
    # ACTIVATE MISSROSE AUTO-REGISTRY (THE IMPORTANT PART)
    # =====================================================
    try:
        from plugins.core.group_registry import setup_auto_group_registry
        setup_auto_group_registry(user_client=user_client, bot_client=bot_client)
        logger.info("✅ MissRose-style auto group registry is ACTIVE")
    except Exception as e:
        logger.warning(f"⚠️ Could not activate auto group registry: {e}")

    return plugin_count

# =====================================================
# WEB SERVER
# =====================================================
async def handle_ping(request):
    status = "✅ AIPIC Hybrid Bot is running"
    if user_client:
        status += " | Userbot: ON"
    if bot_client:
        status += " | Bot: ON"
    return web.Response(text=status, status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"🌐 Web server running on port {PORT}")

# =====================================================
# STARTUP
# =====================================================
async def main():
    logger.info("🚀 Starting AIPIC Hybrid (MissRose-style) ...")

    tasks = []

    if user_client:
        await user_client.start()
        me = await user_client.get_me()
        logger.info(f"👤 Userbot: {me.first_name} ({me.id})")
        tasks.append(user_client.run_until_disconnected())

    if bot_client:
        await bot_client.start(bot_token=BOT_TOKEN)
        bot_me = await bot_client.get_me()
        logger.info(f"🤖 Bot: @{bot_me.username} ({bot_me.id})")
        tasks.append(bot_client.run_until_disconnected())

    loaded = load_plugins()

    await start_web_server()

    logger.info("✅ Hybrid system ready (MissRose mode)")
    logger.info("   • Add bot to group → promote to admin")
    logger.info("   • All Telegram admins of that group can use commands")
    logger.info("   • Use .addgroup manually if needed")
    logger.info(f"   • Plugins loaded: {loaded}")

    if tasks:
        await asyncio.gather(*tasks)
    else:
        logger.error("No clients started!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Stopped")
    except Exception as e:
        logger.error(f"Fatal: {e}")
