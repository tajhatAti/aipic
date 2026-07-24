# AIPIC - Telegram Personal Account Userbot

**Manage your own groups** using your **personal Telegram account** via **Session String** (Userbot).

- ✅ Uses **Telethon** (fast + full MTProto access)
- ✅ **Session String** login (no .session files needed)
- ✅ All features in **plugins/** folder (modular)
- ✅ Ready for **Render Free Plan** + **UptimeRobot**
- ✅ Group management commands included

---

## 🚀 Features

### Built-in Group Management (in `plugins/group_management.py`)
- `.ban` (reply) — Ban user
- `.unban` (reply) — Unban user
- `.kick` (reply) — Kick user
- `.promote` (reply) — Promote to admin
- `.demote` (reply) — Demote admin
- `.tagall [message]` — Tag all members
- `.purge` (reply) — Delete messages from replied message

### Other Plugins
- `.ping` — Check bot latency

Add more plugins easily in the `plugins/` folder.

---

## 📋 Requirements

1. **Telegram API ID & Hash** → [https://my.telegram.org](https://my.telegram.org)
2. **Session String** from your personal account
3. Python 3.9+

---

## 🔑 How to Generate Session String

### Method 1: Using Python (Recommended)

1. Create a file `get_session.py`:
```python
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

API_ID = 12345678          # ← Your API ID
API_HASH = "your_api_hash" # ← Your API Hash

async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        await client.start()
        print("✅ Session String:")
        print(await client.session.save())

asyncio.run(main())
```

2. Run:
```bash
python get_session.py
```
3. Login with your phone number + OTP
4. Copy the long string starting with `1BQAN...`

> ⚠️ **Never share your session string** with anyone.

---

## 🛠️ Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/aipic.git
cd aipic

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env`:
```env
API_ID=12345678
API_HASH=yourhashhere
STRING_SESSION=1BQANOTEu...your_session_string...
PORT=8080
```

Run:
```bash
python main.py
```

---

## ☁️ Deploy on Render (Free)

### Step-by-step:

1. **Fork** or push this repo to your GitHub

2. Go to [https://dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service**

3. Connect your GitHub repo

4. **Settings:**
   - **Name**: `aipic-userbot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free

5. Add these **Environment Variables**:
   | Key             | Value                              |
   |-----------------|------------------------------------|
   | `API_ID`        | `12345678`                         |
   | `API_HASH`      | `your_api_hash`                    |
   | `STRING_SESSION`| `1BQANOTEu...` (your string)       |
   | `PORT`          | `8080`                             |
   | `OWNER_ID`      | (optional) your Telegram user ID   |

6. Click **Create Web Service**

Render will give you a URL like: `https://aipic-userbot.onrender.com`

---

## ⏰ Keep Alive with UptimeRobot

1. Go to [https://uptimerobot.com](https://uptimerobot.com)
2. Create a **HTTP(s) Monitor**
3. Paste your Render URL: `https://your-app.onrender.com`
4. Set interval to **5 minutes**
5. Save

This prevents Render from sleeping your free instance.

---

## 📁 Project Structure

```
aipic/
├── main.py                 # Main entry point + plugin loader + web server
├── requirements.txt
├── .env.example
├── README.md
├── plugins/
│   ├── __init__.py
│   ├── ping.py
│   └── group_management.py   # All group management features
└── ...
```

**Rule**: Put every new feature/command in a **new file** inside `plugins/`.

Example new plugin:
```python
# plugins/myfeature.py
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'[.!/]hello$'))
    async def hello(event):
        await event.reply("Hello from plugin!")
```

---

## 🔒 Security Notes

- Never commit your real `.env` or session string
- Use environment variables on Render
- Your personal account will be used — be careful with commands
- Do not share your session string

---

## 💡 Usage Examples (in your groups)

```
.ping
.ban (reply to user)
.tagall Wake up guys!
.purge (reply to a message)
```

---

## 📌 Reference

Inspired by: https://github.com/tajhatAti/Bot

---

**Made for personal group management using your own Telegram account.**
```

