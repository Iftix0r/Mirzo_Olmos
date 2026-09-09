# Telegram Taxi Yo'lovchi Userbot

Ushbu Telegram Userbot akkauntingiz ulangan barcha taksi guruhlaridagi xabarlarni avtomatik tarzda kuzatib boradi. Xabar **100 ta belgidan kam** bo'lsa va yo'lovchiga tegishli kalit so'zlar topilsa (va haydovchi e'lonlari chetlab o'tilsa), ma'lumotlarni tayinlangan **Buyurtmalar guruhiga** yuboradi.

---

## 🚀 Xususiyatlari

1. **Uzunlik bo'yicha filtr**: 100 ta belgidan oshgan xabarlar ko'rib chiqilmaydi (`len < 100`).
2. **Yo'lovchi kalit so'zlari (95 ta)**: Lotin va Kirill alifbosidagi yo'lovchilar iboralari bo'yicha saralash.
3. **Haydovchilar filtrlanishi (115 ta)**: Haydovchilar tomonidan joylangan takliflar ("1 kishi kerak", "olamiz", "yuramiz" va b.) avtomatik rad etiladi.
4. **Formatlangan xabar**: Buyurtma guruhiga yuboruvchining ismi, unga havola, guruh nomi, xabar matni va xabarga to'g'ridan-to mezoniy havola yuboriladi.

---

## 🛠 O'rnatish bo'yicha yo'riqnoma

### 1. Reformat / Virtual muhit va kutubxonalarni o'rnatish

Terminalda loyiha papkasiga kirib, quyidagi buyruqni bajaring:

```bash
pip install -r requirements.txt
```

### 2. Sozlamalarni kiritish (`.env` fayli)

Loyiha ildizida `.env` faylini yarating (yoki `.env.example` nusxasini ko'chiring):

```bash
cp .env.example .env
```

`.env` faylini ochib, o'zingizning ma'lumotlaringizni kiriting:

```env
API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890
TARGET_CHAT_ID=-1001234567890
```

> **Eslatma**:
> - `API_ID` va `API_HASH` olish uchun [my.telegram.org](https://my.telegram.org) saytiga kiring, telefon raqamingiz orqali avtorizatsiyadan o'ting va **API development tools** bo'limidan ilova yarating.
> - `TARGET_CHAT_ID` - buyurtmalar yuborilishi kerak bo'lgan guruh yoki kanal ID-si (masalan, `-100` bilan boshlanuvchi raqam).

---

## 🧪 Testlarni ishga tushirish

Filtrlash mantiqini tekshirish uchun test faylini ishga tushirishingiz mumkin:

```bash
python3 test_filter.py
```

---

## ▶️ Userbotni ishga tushirish

Userbotni ishga tushirish uchun:

```bash
python3 main.py
```

Birinchi marta ishga tushirilganda Telegram akkauntingiz **telefon raqami** va Telegram'ga kelgan **tasdiqlash kodi** (SMS/Telegram kodi) so'raladi. Avtorizatsiyadan muvaffaqiyatli o'tilgach `taxi_userbot_session.session` fayli yaratiladi va bot avtomatik ishlay boshlaydi.
# Mirzo_Olmos
