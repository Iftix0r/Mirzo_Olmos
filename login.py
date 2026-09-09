import asyncio
import sys

# Python 3.10-3.14+ asyncio compatibility
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client
from config import API_ID, API_HASH

app = Client(
    "taxi_userbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    device_model="PC 64bit",
    system_version="Linux",
    app_version="1.0.0"
)

if __name__ == "__main__":
    print("🔑 Telegram session tizimiga kirish...")
    try:
        app.start()
        print("\n✅ Muvaffaqiyatli kirdingiz! Session fayli yaratildi.")
        app.stop()
    except AttributeError as e:
        if "'NoneType' object has no attribute 'p'" in str(e):
            print("\n❌ Xato: Pyrogram 2.0.106 da ikki faktorli tasdiqlash bilan muammo bor")
            print("\n💡 Yechimlar:")
            print("1. Bot tokenidan foydalaning: Telegram BotFather orqali bot yarating")
            print("2. yoki login.py da token ishlatishga o'tkazing:")
            print("   app = Client('taxi_userbot_session', bot_token='YOUR_BOT_TOKEN')")
            print("3. yoki Pyrogram kutubxonasini yangilang (agar yangi versiya mavjud bo'lsa)")
            sys.exit(1)
        else:
            raise
    except Exception as e:
        print(f"\n❌ Xato: {type(e).__name__}: {e}")
        sys.exit(1)
