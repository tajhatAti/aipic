#!/usr/bin/env python3
"""
Session String Generator for AIPIC Userbot

Run this script locally to generate your personal account session string.
You will need:
- Your API_ID and API_HASH from https://my.telegram.org
"""

import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from getpass import getpass

print("🔐 AIPIC Session String Generator\n")

# Try to load from environment or ask user
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

if not API_ID:
    API_ID = input("Enter your API_ID: ").strip()
if not API_HASH:
    API_HASH = input("Enter your API_HASH: ").strip()

API_ID = int(API_ID)

print("\n📱 Starting login process...")
print("You will receive a code in your Telegram app.\n")

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    
    await client.start()
    
    me = await client.get_me()
    print(f"\n✅ Successfully logged in as: {me.first_name} (@{me.username or 'no username'})")
    print(f"   User ID: {me.id}\n")
    
    session_string = client.session.save()
    
    print("🔑 Your STRING_SESSION (copy this carefully):\n")
    print(session_string)
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: Keep this string SECRET!")
    print("   Paste it into your .env file or Render environment variables.")
    print("="*60 + "\n")
    
    # Optional: save to file
    save = input("Save to 'my_session.txt'? (y/n): ").lower().strip()
    if save == 'y':
        with open("my_session.txt", "w") as f:
            f.write(session_string)
        print("✅ Saved to my_session.txt (add to .gitignore!)")

    await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
