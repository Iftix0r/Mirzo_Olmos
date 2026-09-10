import os
import logging
import asyncio
import html

# Python 3.10-3.14+ asyncio compatibility for Pyrogram
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.types import Message

from aiogram import Bot, Dispatcher, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from config import API_ID, API_HASH, BOT_TOKEN, TARGET_CHAT_ID
from filter import is_passenger_message, add_keyword_live, refresh_keywords
import db

# Logging sozlamalari
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)


# Aiogram Bot
aiogram_bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

db.init_db()
refresh_keywords()

# Bot qayta ishga tushganda ham raqamlar takrorlanmasligi uchun
# oxirgi berilgan zakaz raqamidan davom etamiz.
order_number = db.get_last_order_number() or 12533

# Admin panelga faqat userbot ulangan akkaunt (bot egasi) kira oladi.
# Aniq qiymati userbot.start() dan keyin uning get_me().id bilan to'ldiriladi.
ADMIN_ID: int | None = None


async def safe_answer_callback(callback: types.CallbackQuery, text: str | None = None):
    """
    Bot qayta ishga tushganda navbatda qolgan eski callback so'rovlari
    Telegram tomonidan "query is too old" deb rad etilishi mumkin - bu holatda
    botni yiqitmasdan shunchaki e'tiborsiz qoldiramiz.
    """
    try:
        await callback.answer(text)
    except TelegramBadRequest as e:
        logger.debug(f"⚠️  Eski callback so'rovi e'tiborsiz qoldirildi: {e}")


def is_owner(message: types.Message) -> bool:
    return ADMIN_ID is not None and bool(message.from_user) and message.from_user.id == ADMIN_ID


def is_admin(message: types.Message) -> bool:
    if not message.from_user:
        return False
    return is_owner(message) or db.is_admin_db(message.from_user.id)


# --- Admin panel tugmalari ---
BTN_STATS = "📊 Statistika"
BTN_SEARCH = "🔍 Qidiruv"
BTN_ADD_WORD = "📝 So'zlar qo'shish"
BTN_SETTINGS = "⚙️ Sozlamalar"
BTN_GROUP_STATS = "📋 Guruh statistikasi"
BTN_LAST_ORDERS = "🎯 Oxirgi 10 ta zakaz"
BTN_INCOMPLETE = "⚠️ To'liq bo'lmagan zakazlar"
BTN_COMPLETE_ORDER = "✅ Zakazni to'ldirish"

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_STATS, style="primary"), KeyboardButton(text=BTN_SEARCH, style="primary")],
        [KeyboardButton(text=BTN_ADD_WORD, style="success"), KeyboardButton(text=BTN_SETTINGS, style="primary")],
        [KeyboardButton(text=BTN_GROUP_STATS, style="primary"), KeyboardButton(text=BTN_LAST_ORDERS, style="primary")],
        [KeyboardButton(text=BTN_INCOMPLETE, style="danger"), KeyboardButton(text=BTN_COMPLETE_ORDER, style="success")],
    ],
    resize_keyboard=True,
)


class AdminStates(StatesGroup):
    waiting_keyword_words = State()
    waiting_search = State()
    waiting_close_order = State()
    waiting_new_admin_id = State()
    waiting_remove_admin_id = State()

# TEST MODE - 3 ta fake zakazni simulyatsiya qilish
# TEST MODE - 3 ta fake zakazni simulyatsiya qilish
TEST_MODE = os.getenv("TEST_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}
TEST_MESSAGES = [
    "Assalamu alaykum, 2 ta odam bor, Chinobod dan Tashkentga kerak",
    "Marhamat, 3 ta yo'lovchi bor, Sergeli dan Evropark tomonga ketish kerak",
    "Salom, 1 ta odam, Parkentdan Samarqandga kerak"
]
# Custom Pyrogram Client - peer ID xatolarini avtomatik tushurib qo'yadigan
class CustomClient(Client):
    async def handle_updates(self, *args, **kwargs):
        """
        Pyrogram handle_updates methodini ustiga yozish - 
        peer ID xatolarini xira darajasida log qilish va to'xtatmaslik
        """
        try:
            await super().handle_updates(*args, **kwargs)
        except ValueError as e:
            error_msg = str(e)
            if "Peer id invalid" in error_msg or "ID not found" in error_msg:
                logger.debug(f"⚠️  Peer ID xatosi (tushurib qo'yildi): {error_msg}")
            else:
                logger.error(f"❌ ValueError: {e}")
                raise
        except Exception as e:
            logger.error(f"❌ handle_updates xatosi: {type(e).__name__}: {e}")

# USERBOT - Guruhlardan zakazlarni eshitadi
userbot = CustomClient(
    "taxi_userbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    device_model="PC 64bit",
    system_version="Linux",
    app_version="1.0.0"
)

@userbot.on_message(filters.group)
async def handle_group_message(client: Client, message: Message):
    """
    Userbot: Taksi guruhlaridan kelgan xabarlarni eshitish va filtrlash
    """
    try:
        # Target buyurtmalar guruhidan kelgan xabarlarni qayta ishlamaymiz (rekursiya oldini olish)
        if message.chat and message.chat.id == TARGET_CHAT_ID:
            logger.debug(f"⏭️  Buyurtmalar guruhidan xabar - e'tiborsiz qoldirish")
            return

        # Botlardan kelgan xabarlarni e'tiborsiz qoldirish - faqat odamlarga qabul qilish
        if message.from_user and message.from_user.is_bot:
            logger.debug(f"🤖 Bot xabari - e'tiborsiz qoldirish: {message.from_user.first_name}")
            return

        try:
            message_text = message.text
            message_caption = message.caption
        except UnicodeDecodeError:
            logger.debug("⏭️  Unicode xabari o'qilmadi")
            return

        text = message_text if isinstance(message_text, str) else message_caption
        if not isinstance(text, str):
            logger.debug("⏭️  Matn formati noto'g'ri - e'tiborsiz qoldirish")
            return
        text = str(text)

        if not text:
            logger.debug(f"⏭️  Bo'sh xabar - e'tiborsiz qoldirish")
            return

        # Bot yuborgan tayyor zakazlar boshqa kanalda ko'rinsa ham qayta ishlanmaydi.
        if text.startswith("🚖 YANGI YO'LOVCHI BUYURTMASI") or (
            text.startswith("🚕 ") and "Buyurtma:" in text
        ):
            logger.debug("⏭️  Tayyor zakaz xabari - e'tiborsiz qoldirish")
            return

        # Filtrlash funksiyasini chaqiramiz
        is_match, reason = is_passenger_message(text)
        logger.debug(f"🔍 Filtrlash: {text[:50]} -> {is_match} ({reason})")
        
        if is_match:
            sender = message.from_user
            if sender and db.is_blocked(sender.id):
                logger.debug(f"🚫 Bloklangan foydalanuvchi xabari - e'tiborsiz qoldirish: {sender.id}")
                return

            logger.info("📥 Zakaz keldi")
            sender_name = sender.first_name if sender else "Noma'lum"
            sender_id = sender.id if sender else "N/A"
            sender_phone = sender.phone_number if sender and sender.phone_number else "+998"
            sender_username = getattr(sender, "username", None) if sender else None

            chat_title = message.chat.title if message.chat else "Guruh"
            
            # Xabarga havola tayyorlash
            msg_link = message.link if message.link else "Havola mavjud emas"

            global order_number
            order_number += 1

            has_username = bool(sender_username)
            profile_link = f"https://t.me/{sender_username}" if has_username else None

            group_id = message.chat.id if message.chat else None
            if group_id is not None:
                db.upsert_group(group_id, chat_title)
            db.create_order(
                order_number, group_id, chat_title, sender_id, sender_name,
                sender_phone, text, msg_link,
            )

            # Har bir tugma alohida qatorda bo'ladi.
            keyboard_rows = []
            if has_username:
                keyboard_rows.append(
                    [InlineKeyboardButton(text="📬 Profilga o'tish", url=profile_link, style="primary")]
                )
            keyboard_rows.extend([
                [InlineKeyboardButton(text="☎️ Qo'ng'iroq qilish", url=f"https://onmap.uz/tel/{sender_phone}", style="primary")],
                [InlineKeyboardButton(text="📝 Xabarga o'tish", url=msg_link, style="primary")],
                [InlineKeyboardButton(text="✅ Zakazni yopish", callback_data=f"close_order:{order_number}", style="success")],
                [InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"block_user:{sender_id}", style="danger")],
            ])
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

            # Username yo'q (maxfiy akkaunt) bo'lsa, profilga faqat lichka havolasi orqali kirish mumkin -
            # bot tugmasida bunday havola ishlamaydi, shu sababli matn ichida ID orqali mention beramiz.
            mijoz_label = "Mijoz" if has_username else "Mijoz lichkasi"

            # Buyurtma xabari formati (tugmalar tagida)
            order_msg = (
                f"🚕 <b>Yangi buyurtma</b>\n\n"
                f"👤 <b>{mijoz_label}:</b> <a href=\"tg://user?id={sender_id}\">{html.escape(sender_name)}</a>\n\n"
                f"📞 <b>Aloqa:</b> {html.escape(sender_phone)}\n\n"
                f"📍 <b>Guruh:</b> {html.escape(chat_title)}\n\n"
                f"📋 <b>Buyurtma:</b>\n\n"
                f"{html.escape(text)}"
            )

            try:
                # AIOGRAM BOT orqali zakazni yuborish
                logger.debug(f"🚀 Zakazni yuborish: {order_msg[:100]}...")
                await aiogram_bot.send_message(
                    chat_id=TARGET_CHAT_ID,
                    text=order_msg,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                    parse_mode="HTML"
                )
                logger.info("✅ Zakaz yuborildi")
            except Exception as e:
                logger.error(f"❌ Zakaz yuborilmadi: {type(e).__name__}: {e}")
    except ValueError as e:
        # Pyrogram peer ID errors - ignore them gracefully
        if "Peer id invalid" in str(e) or "ID not found" in str(e):
            logger.debug(f"⚠️  Peer ID resolved: {e}")
            return
        raise
    except Exception as e:
        logger.error(f"❌ Xabar qo'llanishda kutilmagan xatolik: {type(e).__name__}: {e}")

def handle_task_exception(loop, context):
    """
    Background task xatolarini qayta ishlash - 
    peer ID xatolarini e'tiborsiz qoldirish
    """
    exception = context.get('exception')
    
    if exception:
        error_msg = str(exception)
        
        # Peer ID xatolarini tushurib qo'yish
        if isinstance(exception, ValueError) and ("Peer id invalid" in error_msg or "ID not found" in error_msg):
            logger.debug(f"⚠️  Background task Peer ID xatosi (tushurib qo'yildi): {error_msg}")
            return
        
        # Boshqa xatolarni logga yozish
        logger.error(f"❌ Background task xatosi: {type(exception).__name__}: {error_msg}")
    else:
        logger.error(f"❌ Background task xatosi: {context}")

async def simulate_test_orders():
    """
    TEST MODE: 3 ta fake zakazni simulyatsiya qilish
    """
    if not TEST_MODE:
        return
    
    logger.debug("🧪 TEST MODE: Fake zakazlarni 5 soniyadan keyin yuborishni boshlayapman...")
    await asyncio.sleep(5)  # Botni ishga tushishiga vaqt berish
    
    test_users = [
        {"name": "Alisher", "id": 123456789, "phone": "+998901234567"},
        {"name": "Gulnora", "id": 987654321, "phone": "+998902345678"},
        {"name": "Karim", "id": 555555555, "phone": "+998903456789"}
    ]
    
    for idx, (user, text) in enumerate(zip(test_users, TEST_MESSAGES)):
        try:
            logger.debug(f"🧪 TEST {idx+1}: Simulyatsiya qilinyapman - {text[:40]}...")
            
            sender_name = user["name"]
            sender_id = user["id"]
            sender_phone = user["phone"]
            chat_title = "Test Taxi Guruh"
            msg_link = "https://t.me/c/1234567890/1"

            global order_number
            order_number += 1
            db.create_order(
                order_number, None, chat_title, sender_id, sender_name,
                sender_phone, text, msg_link,
            )

            # Test foydalanuvchilarida username yo'q - shu sababli "Mijoz lichkasi" mention orqali ochiladi.
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="☎️ Qo'ng'iroq qilish", url=f"https://onmap.uz/tel/{sender_phone}", style="primary")],
                    [InlineKeyboardButton(text="📝 Xabarga o'tish", url=msg_link, style="primary")],
                    [InlineKeyboardButton(text="✅ Zakazni yopish", callback_data=f"close_order:{order_number}", style="success")],
                    [InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"block_user:{sender_id}", style="danger")]
                ]
            )

            # Buyurtma xabari
            order_msg = (
                f"🚕 <b>Yangi buyurtma</b>\n\n"
                f"👤 <b>Mijoz lichkasi:</b> <a href=\"tg://user?id={sender_id}\">{html.escape(sender_name)}</a>\n\n"
                f"📞 <b>Aloqa:</b> {html.escape(sender_phone)}\n\n"
                f"📍 <b>Guruh:</b> {html.escape(chat_title)}\n\n"
                f"📋 <b>Buyurtma:</b>\n\n"
                f"{html.escape(text)}"
            )

            # Yuborish
            await aiogram_bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=order_msg,
                reply_markup=keyboard,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
            logger.info("✅ Zakaz yuborildi")
            
            await asyncio.sleep(2)  # Habarlar orasida 2 soniya
        except Exception as e:
            logger.error(f"❌ Zakaz yuborilmadi: {type(e).__name__}: {e}")

@dp.callback_query(lambda query: query.data and query.data.startswith("close_order:"))
async def close_order(callback: types.CallbackQuery):
    order_num = callback.data.split(":", 1)[1]
    if order_num.isdigit():
        db.close_order(int(order_num))
    closer = callback.from_user
    closer_name = html.escape(closer.full_name) if closer else "Noma'lum"
    await safe_answer_callback(callback, "Zakaz yopildi ✅")
    if callback.message:
        try:
            await callback.message.edit_text(
                f"{callback.message.html_text}\n\n✅ <b>ZAKAZ YOPILDI</b>\n👤 <b>Yopdi:</b> {closer_name}",
                parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            logger.debug(f"⚠️  Xabarni tahrirlab bo'lmadi: {e}")


@dp.callback_query(lambda query: query.data and query.data.startswith("block_user:"))
async def block_user(callback: types.CallbackQuery):
    if not is_admin(callback):
        await safe_answer_callback(callback, "❌ Bu tugma faqat admin uchun.")
        return
    user_id_raw = callback.data.split(":", 1)[1]
    if not user_id_raw.isdigit():
        await safe_answer_callback(callback, "❌ Foydalanuvchi aniqlanmadi.")
        return
    db.block_user(int(user_id_raw))
    await safe_answer_callback(callback, "🚫 Foydalanuvchi bloklandi")
    if callback.message:
        try:
            await callback.message.edit_text(
                f"{callback.message.html_text}\n\n🚫 <b>FOYDALANUVCHI BLOKLANDI</b>",
                parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            logger.debug(f"⚠️  Xabarni tahrirlab bo'lmadi: {e}")


# ============================================================
# ADMIN PANEL
# ============================================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    if not is_admin(message):
        await message.answer("❌ Bu bot faqat egasi uchun mo'ljallangan.")
        return
    await message.answer(
        "🤖 <b>Userbot boshqaruv paneli</b>\n\nQuyidagi tugmalardan birini tanlang:",
        reply_markup=MAIN_MENU,
        parse_mode="HTML",
    )


@dp.message(F.text == BTN_STATS)
async def show_stats(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.clear()
    stats = db.get_stats()
    await message.answer(
        "📊 <b>Statistika</b>\n\n"
        f"📦 Jami zakazlar: <b>{stats['total']}</b>\n"
        f"🟢 Bugungi zakazlar: <b>{stats['today']}</b>\n"
        f"⚠️ To'liq bo'lmagan: <b>{stats['open']}</b>\n"
        f"✅ Yopilgan: <b>{stats['closed']}</b>",
        parse_mode="HTML",
    )


@dp.message(F.text == BTN_GROUP_STATS)
async def show_group_stats(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.clear()
    rows = db.get_group_stats()
    if not rows:
        await message.answer("📋 Hozircha hech qanday guruhdan zakaz kelmagan.")
        return
    lines = ["📋 <b>Guruh statistikasi</b>\n"]
    for row in rows:
        title = html.escape(row["title"] or str(row["group_id"]))
        lines.append(f"• {title}: <b>{row['order_count']}</b> ta zakaz")
    await message.answer("\n".join(lines), parse_mode="HTML")


def _format_order_line(order) -> str:
    status = "✅ Yopilgan" if order["status"] == "closed" else "⚠️ Ochiq"
    name = html.escape(order["sender_name"] or "Noma'lum")
    return (
        f"🚕 <b>#{order['order_number']}</b> — {name} ({status})\n"
        f"   🕐 {order['created_at']}\n"
        f"   📋 {html.escape((order['text'] or '')[:80])}"
    )


@dp.message(F.text == BTN_LAST_ORDERS)
async def show_last_orders(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.clear()
    orders = db.get_recent_orders(10)
    if not orders:
        await message.answer("🎯 Hozircha zakazlar yo'q.")
        return
    lines = ["🎯 <b>Oxirgi 10 ta zakaz</b>\n"]
    lines.extend(_format_order_line(o) for o in orders)
    await message.answer("\n\n".join(lines), parse_mode="HTML")


@dp.message(F.text == BTN_INCOMPLETE)
async def show_incomplete_orders(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.clear()
    orders = db.get_incomplete_orders()
    if not orders:
        await message.answer("✅ To'liq bo'lmagan zakazlar yo'q.")
        return
    lines = ["⚠️ <b>To'liq bo'lmagan zakazlar</b>\n"]
    lines.extend(_format_order_line(o) for o in orders)
    await message.answer("\n\n".join(lines), parse_mode="HTML")


@dp.message(F.text == BTN_COMPLETE_ORDER)
async def ask_complete_order(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.set_state(AdminStates.waiting_close_order)
    await message.answer("✅ To'ldirmoqchi bo'lgan zakaz raqamini yuboring (masalan: 12534):")


@dp.message(AdminStates.waiting_close_order)
async def complete_order(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer("❌ Iltimos, faqat zakaz raqamini (son) yuboring.")
        return
    order_num = int(raw)
    order = db.get_order(order_num)
    if order is None:
        await message.answer(f"❌ #{order_num} raqamli zakaz topilmadi.")
    elif order["status"] == "closed":
        await message.answer(f"ℹ️ #{order_num} zakaz allaqachon yopilgan.")
    else:
        db.close_order(order_num)
        await message.answer(f"✅ #{order_num} zakaz to'ldirildi (yopildi).")
    await state.clear()


@dp.message(F.text == BTN_SEARCH)
async def ask_search(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.set_state(AdminStates.waiting_search)
    await message.answer("🔍 Qidiruv so'zini yuboring (ism, telefon, zakaz raqami yoki matn):")


@dp.message(AdminStates.waiting_search)
async def do_search(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    query = (message.text or "").strip()
    await state.clear()
    if not query:
        await message.answer("❌ Bo'sh qidiruv so'zi.")
        return
    results = db.search_orders(query)
    if not results:
        await message.answer(f"🔍 \"{html.escape(query)}\" bo'yicha hech narsa topilmadi.")
        return
    lines = [f"🔍 <b>Qidiruv natijalari</b> ({len(results)} ta)\n"]
    lines.extend(_format_order_line(o) for o in results)
    await message.answer("\n\n".join(lines), parse_mode="HTML")


@dp.message(F.text == BTN_ADD_WORD)
async def ask_add_word(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.clear()
    inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧍 Yo'lovchi so'zi", callback_data="kwtype:passenger", style="success")],
            [InlineKeyboardButton(text="🚗 Haydovchi so'zi", callback_data="kwtype:driver", style="danger")],
        ]
    )
    await message.answer(
        "📝 Qaysi turdagi so'z qo'shmoqchisiz?\n\n"
        "🧍 Yo'lovchi so'zi — shu so'z topilsa, xabar yo'lovchi zakazi deb hisoblanadi.\n"
        "🚗 Haydovchi so'zi — shu so'z topilsa, xabar rad etiladi (haydovchi e'loni).",
        reply_markup=inline,
    )


@dp.callback_query(lambda query: query.data and query.data.startswith("kwtype:"))
async def choose_keyword_type(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback):
        await safe_answer_callback(callback)
        return
    kw_type = callback.data.split(":", 1)[1]
    await state.set_state(AdminStates.waiting_keyword_words)
    await state.update_data(kw_type=kw_type)
    await safe_answer_callback(callback)
    label = "yo'lovchi" if kw_type == "passenger" else "haydovchi"
    if callback.message:
        await callback.message.answer(
            f"✍️ Qo'shmoqchi bo'lgan {label} so'z(lar)ini yuboring "
            "(bir nechta so'z bo'lsa, har birini alohida qatorga yozing):"
        )


@dp.message(AdminStates.waiting_keyword_words)
async def add_words(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    data = await state.get_data()
    kw_type = data.get("kw_type", "passenger")
    await state.clear()
    words = [w.strip() for w in (message.text or "").splitlines() if w.strip()]
    if not words:
        await message.answer("❌ Bo'sh so'z yuborildi, hech narsa qo'shilmadi.")
        return
    added = [w for w in words if add_keyword_live(kw_type, w)]
    skipped = len(words) - len(added)
    label = "yo'lovchi" if kw_type == "passenger" else "haydovchi"
    reply = f"✅ {len(added)} ta {label} so'z qo'shildi."
    if skipped:
        reply += f"\nℹ️ {skipped} ta so'z allaqachon mavjud edi."
    await message.answer(reply)


@dp.message(F.text == BTN_SETTINGS)
async def show_settings(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.clear()
    groups = db.get_group_stats()
    group_lines = "\n".join(
        f"  • {html.escape(g['title'] or str(g['group_id']))} ({g['group_id']})" for g in groups
    ) or "  • Hozircha yo'q"
    test_mode_label = "yoqilgan" if TEST_MODE else "o'chirilgan"

    inline_rows = [[InlineKeyboardButton(text="👥 Adminlar ro'yxati", callback_data="admin_list", style="primary")]]
    if is_owner(message):
        inline_rows.append([
            InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="admin_add", style="success"),
            InlineKeyboardButton(text="➖ Admin o'chirish", callback_data="admin_remove", style="danger"),
        ])

    await message.answer(
        "⚙️ <b>Sozlamalar</b>\n\n"
        f"📬 Buyurtmalar guruhi: <code>{TARGET_CHAT_ID}</code>\n\n"
        f"📡 Kuzatilayotgan guruhlar:\n{group_lines}\n\n"
        f"🚫 Bloklangan foydalanuvchilar: <b>{db.count_blocked()}</b>\n\n"
        f"👥 Qo'shilgan adminlar: <b>{len(db.list_admins())}</b>\n\n"
        f"🧪 Test rejimi: {test_mode_label}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_rows),
    )


@dp.callback_query(lambda query: query.data == "admin_list")
async def admin_list_callback(callback: types.CallbackQuery):
    if not is_admin(callback):
        await safe_answer_callback(callback, "❌ Ruxsat yo'q.")
        return
    await safe_answer_callback(callback)
    admins = db.list_admins()
    lines = [f"👑 Egasi (ID: {ADMIN_ID})"]
    lines.extend(
        f"👤 {html.escape(a['name'] or str(a['user_id']))} (ID: {a['user_id']})" for a in admins
    )
    if callback.message:
        await callback.message.answer("👥 <b>Adminlar ro'yxati</b>\n\n" + "\n".join(lines), parse_mode="HTML")


@dp.callback_query(lambda query: query.data == "admin_add")
async def admin_add_callback(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback):
        await safe_answer_callback(callback, "❌ Faqat egasi admin qo'sha oladi.")
        return
    await safe_answer_callback(callback)
    await state.set_state(AdminStates.waiting_new_admin_id)
    if callback.message:
        await callback.message.answer(
            "➕ Yangi adminning Telegram ID raqamini yuboring.\n"
            "(ID ni bilmasa, u @userinfobot ga yozib olishi mumkin.)"
        )


@dp.message(AdminStates.waiting_new_admin_id)
async def add_admin_by_id(message: types.Message, state: FSMContext):
    if not is_owner(message):
        return
    await state.clear()
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer("❌ Iltimos, faqat raqamli Telegram ID yuboring.")
        return
    new_id = int(raw)
    if new_id == ADMIN_ID:
        await message.answer("ℹ️ Bu allaqachon bot egasi.")
        return
    name = None
    try:
        chat = await aiogram_bot.get_chat(new_id)
        name = chat.full_name
    except Exception:
        pass
    if db.add_admin(new_id, name or str(new_id)):
        await message.answer(f"✅ Admin qo'shildi: {html.escape(name or str(new_id))} (ID: {new_id})")
    else:
        await message.answer("ℹ️ Bu foydalanuvchi allaqachon admin.")


@dp.callback_query(lambda query: query.data == "admin_remove")
async def admin_remove_callback(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback):
        await safe_answer_callback(callback, "❌ Faqat egasi adminni o'chira oladi.")
        return
    await safe_answer_callback(callback)
    await state.set_state(AdminStates.waiting_remove_admin_id)
    if callback.message:
        await callback.message.answer("➖ O'chirmoqchi bo'lgan adminning Telegram ID raqamini yuboring:")


@dp.message(AdminStates.waiting_remove_admin_id)
async def remove_admin_by_id(message: types.Message, state: FSMContext):
    if not is_owner(message):
        return
    await state.clear()
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer("❌ Iltimos, faqat raqamli Telegram ID yuboring.")
        return
    if db.remove_admin(int(raw)):
        await message.answer(f"✅ Admin o'chirildi (ID: {raw}).")
    else:
        await message.answer("❌ Bu ID admin sifatida topilmadi.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_task_exception)

    if not BOT_TOKEN:
        logger.error("❌ Zakaz yuborilmadi: BOT_TOKEN sozlanmagan")
        raise SystemExit(1)

    async def run_bot():
        global ADMIN_ID
        await userbot.start()
        owner = await userbot.get_me()
        ADMIN_ID = owner.id
        logger.info(f"👑 Admin panel egasi: {owner.first_name} (ID: {ADMIN_ID})")

        bot_info = await aiogram_bot.get_me()
        logger.info(f"✅ Bot ishga tushdi: @{bot_info.username}")
        if TEST_MODE:
            logger.info("🧪 Test rejimi yoqilgan")
        asyncio.create_task(dp.start_polling(aiogram_bot))
        if TEST_MODE:
            asyncio.create_task(simulate_test_orders())
        await asyncio.Event().wait()

    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        pass
    except Exception as error:
        logger.error(f"❌ Zakaz yuborilmadi: {type(error).__name__}: {error}")
    finally:
        try:
            loop.run_until_complete(userbot.stop())
        except Exception:
            pass
