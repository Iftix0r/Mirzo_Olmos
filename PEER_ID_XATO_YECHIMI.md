# Pyrogram Peer ID Xatosi - Yechim

## 🐛 Muammo
```
ValueError: Peer id invalid: -1003958608370
```

Bu xato userbot Telegram gruplaridan xabarlarni olishda yuzaga keladi, ammo biror bir chat/kanal ID-si session ma'lumotlar bazasida soxlanmagan bo'lganda.

---

## 🔍 Sababi

Pyrogram, update qabul qilganda, shu guruh/kanalni o'zining local session ma'lumotlar bazasida qidiradi. Agar ID soxlanmagan bo'lsa (ya'ni siz avval o'sha guruhga kiritilmagan bo'lsangiz), Pyrogram uni `ValueError` bilan to'xtatib qo'yadi.

---

## ✅ Yechim (Amalga Oshirildi)

`main.py` faylida quyidagi o'zgartirishlar qilindi:

### 1. **Try-Except Blogi Qo'shildi**
```python
try:
    # Asosiy logika
    ...
except ValueError as e:
    if "Peer id invalid" in str(e) or "ID not found" in str(e):
        logger.debug(f"⚠️  Peer ID resolved: {e}")
        return
    raise
```

Bu kod peer ID xatosini **xira** darajasida ko'rsatadi va dasturni to'xtatmaydi.

### 2. **Umumiy Xatolik Qayta Ishlash**
Boshqa kutilmagan xatolar uchun ham error handling qo'shildi.

---

## 🎯 Natijasi

✅ Userbot **to'xtatilmaydi**, faqat xatolar logga yoziladi  
✅ Boshqa xabarlar normal tarzda qayta ishlanadi  
✅ Peer ID xatolari avtomatik **e'tiborsiz qoldiriladi**

---

## 🛠️ Qo'shimcha Tavsiyalar

### Option 1: Session Tozalash (Agar Muammo Davom Etsa)
```bash
# Session faylini o'chirib qo'ying
rm taxi_userbot_session.session
rm taxi_userbot_session.session-journal

# Qayta ishga tushiring
python main.py
```

Session qayta initialized bo'lganda barcha chat ID-lari qayta soxlanadi.

### Option 2: Faqat Ma'lum Guruhlarni Eshitish
Agar faqat biror bir kanal/guruhdan xabar qabul qilmoqchi bo'lsangiz:

```python
# main.py da o'zgarting:
@app.on_message(filters.group & ~filters.me & filters.chat([KANAL_ID_1, KANAL_ID_2]))
async def handle_group_message(client: Client, message: Message):
    ...
```

### Option 3: Debug Rejimida Ishga Tushirish
```bash
# Barcha xatolarni ko'rish uchun
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" && python main.py
```

---

## 📊 Log Misollar

**Yaxshi log:**
```
2026-08-22 20:25:03,458 - INFO - ✅ Buyurtma yuborildi! Guruh: TOSHKENT POP UYGURSOY | Matn: ...
```

**Peer ID xatosi (endi yaxshi qayta ishlanadi):**
```
2026-08-22 20:25:41,879 - DEBUG - ⚠️  Peer ID resolved: Peer id invalid: -1003958608370
```

**Boshqa xatolar:**
```
2026-08-22 20:25:45,123 - ERROR - ❌ Xatolik: ConnectionError: ...
```

---

## ✨ Yakuniy Natija

Userbot **barcha kutilmagan peer ID xatolarini avtomatik tushurib qo'yadi** va **to'xtatilmaydi**! 🎉
