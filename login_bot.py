"""
Alternative login method using bot token instead of phone number
This avoids the two-step verification issue with Pyrogram 2.0.106

To use this:
1. Create a bot with @BotFather on Telegram
2. Get your bot token
3. Set it in your environment: export BOT_TOKEN="your_bot_token_here"
4. Run: python login_bot.py
"""

import asyncio
import os
import sys

# Python 3.10-3.14+ asyncio compatibility
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

if not BOT_TOKEN:
    print("❌ Xato: BOT_TOKEN o'zgaruvchisi soxlanmagan")
    print("\n💡 Bosqichlar:")
    print("1. @BotFather ga Telegram orqali yozing")
    print("2. /newbot buyrug'ini yozing")
    print("3. Bot token oling (masalan: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)")
    print("4. .env faylida soxlash: BOT_TOKEN='your_token_here'")
    sys.exit(1)

app = Client(
    "taxi_userbot_session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    device_model="PC 64bit",
    system_version="Linux",
    app_version="1.0.0"
)

if __name__ == "__main__":
    print("🤖 Telegram bot sessionga kirish...")
    try:
        app.start()
        print("\n✅ Muvaffaqiyatli kirdingiz! Bot session fayli yaratildi.")
        
        # Me (bot) info
        me = app.get_me()
        print(f"Bot nomi: {me.first_name} (@{me.username})")
        
        app.stop()
    except Exception as e:
        print(f"\n❌ Xato: {type(e).__name__}: {e}")
        sys.exit(1)
