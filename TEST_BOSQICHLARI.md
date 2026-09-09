# 🧪 Taxi Userbot - Test Bosqichlari

## 📋 Zakazlar Kelaybdimi Tekshirish

### Bosqich 1: Configni Tekshirish
```bash
# .env faylini tekshiring
cat .env

# Shu ma'lumotlar bo'lishi kerak:
# API_ID=xxxxx
# API_HASH=xxxxx
# BOT_TOKEN=xxxxxxx:xxx
# TARGET_CHAT_ID=-1001234567890
```

### Bosqich 2: Userbot Ishga Tushirish
```bash
python main.py
```

**Console da ko'rsatilishi kerak:**
```
============================================================
🚀 Taxi Userbot ishga tushmoqda...
📱 Userbot: Guruhlardan zakazlarni eshitadi
🤖 Bot: Zakazlarni tugmalar bilan yuboradi
🎯 TARGET_CHAT_ID: -1001234567890
============================================================
🔍 Sozlamalarni tekshiryapman...
✅ BOT_TOKEN soxlangan: 7949314462...
🔌 Userbot Telegramga ulanmoqda...
✅ Userbot ulanildi
🔌 Bot Telegramga ulanmoqda...
✅ Bot ulanildi
============================================================
✅ USERBOT VA BOT ISHGA TUSHDI!
📡 Xabarlarni qabul qilishni boshlandi...
============================================================
```

---

## 🧪 Test Xabarlar

### Test 1: Yo'lovchi Buyurtmasi
Taksi guruhga yozing:
```
kerak
```

**Console-da ko'rsatilishi kerak:**
```
📨 Xabar qabul qilindi - Guruh: TAKSI GURUH, Matn: kerak
🔍 Filtrlash: kerak -> True (kerak)
🚀 Zakazni yuborish: 🚖 YANGI YO'LOVCHI BUYURTMASI...
✅ Buyurtma yuborildi! Guruh: TAKSI GURUH | Matn: kerak
```

### Test 2: Ikkita Odam
```
2 ta odam bor, Chustga kerak
```

**Console-da ko'rsatilishi kerak:**
```
📨 Xabar qabul qilindi - Guruh: ..., Matn: 2 ta odam bor, Chustga kerak
🔍 Filtrlash: 2 ta odam bor... -> True (2 ta odam bor)
✅ Buyurtma yuborildi! Guruh: ... | Matn: 2 ta odam bor...
```

### Test 3: Haydovchi Xabari (Filtrlash)
```
olib ketaman, mashina bor
```

**Console-da ko'rsatilishi kerak:**
```
📨 Xabar qabul qilindi - Guruh: ..., Matn: olib ketaman, mashina bor
🔍 Filtrlash: olib ketaman, mashina... -> False (Haydovchi...)
```

---

## ⚠️ Agar Zakazlar Tushmasa

### Error 1: `❌ Xabarni yuborishda XATOLIK`
```
❌ Xabarni yuborishda XATOLIK: BadRequest: Channel private...
   Chat ID: -1001234567890
   Matn: ...
```

**Yechim:**
- `TARGET_CHAT_ID` to'g'ri yozilgandi?
- Bot shu guruhga qo'shilgandi?
- Guruh yopiq (private) bo'lsada admin boladimi?

### Error 2: `❌ ERROR: BOT_TOKEN .env-da soxlanmagan!`
```
❌ ERROR: BOT_TOKEN .env-da soxlanmagan!
   .env-ga qo'shing: BOT_TOKEN=your_bot_token
```

**Yechim:**
```bash
# .env-ni o'chiring va qayta yarating
rm .env

# Yoki qo'shing:
echo 'BOT_TOKEN=your_bot_token_here' >> .env
```

### Error 3: Xabarlar kelmaydimi
```
📨 Xabar qabul qilindi - Guruh: ... (ko'rsatilmaydi)
```

**Yechim:**
- Userbot shu guruhda mi?
- Guruhning foydalanuvchi sessiyaga ruxsati bar mi?

---

## 📊 Log Tushunchalari

| Log | Ma'nosi | Amali |
|-----|---------|------|
| `📨 Xabar qabul qilindi` | Xabar keldi | Keyin filtrlash |
| `🔍 Filtrlash: ... -> True` | Yo'lovchi xabari | Zakazni yuborish |
| `🔍 Filtrlash: ... -> False` | Haydovchi xabari | E'tiborsiz qoldirish |
| `🚀 Zakazni yuborish:` | Bot zakazni yubormoqda | Kutish |
| `✅ Buyurtma yuborildi!` | Muvaffaqiyat! | Tugatildi ✅ |
| `❌ Xabarni yuborishda XATOLIK` | Bot yuborolmadi | Xatoni tekshiring |

---

## 🎯 To'g'ri Natija

Taksi guruhga "kerak" yuborsangiz:

**Taksi Guruhda:**
```
👤 Siz: kerak
```

**Buyurtmalar Guruhda:**
```
🚖 YANGI YO'LOVCHI BUYURTMASI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Mijoz: Your Name
☎️ Aloqa: +998...
📍 Guruh: TAKSI GURUH

📋 Buyurtma:
kerak

[👤 Profil] [☎️ Qo'ng'iroq] [📝 Xabar]
```

---

## 💡 Tips

1. **Console da barcha habarlarni ko'rish uchun:**
   - Logging level DEBUG bo'lsa, barcha debug habarlar ko'rsatiladi

2. **Performance:**
   - Juda ko'p guruhda bo'lsa, lag bo'lishi mumkin

3. **Xatolarni log faylida sohlaash:**
   ```bash
   python main.py > userbot.log 2>&1
   ```

---

**Test boshlang! 🚀**
