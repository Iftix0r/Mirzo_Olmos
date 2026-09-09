import re
from config import PASSENGER_KEYWORDS, DRIVER_KEYWORDS, MAX_MSG_LENGTH
import db

def normalize_text(text: str) -> str:
    """
    Matnni tekshirish uchun standart ko'rinishga keltirish:
    - Kichik harflarga o'tkazish
    - Har xil turdagi tutuq belgilarni bitta shaklga keltirish
    - Ko'p bo'shliqlarni bitta bo'shliqqa aylantirish
    """
    if not text:
        return ""
    text = text.lower()
    # Tutuq belgilarini standartlashtirish
    text = re.sub(r"['`’‘'ʻʼ]", "'", text)
    # Bir necha bo'shliqlarni bitta bo'shliqqa aylantirish
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Normalizatsiya qilingan ro'yxatlar
NORMALIZED_PASSENGER = [normalize_text(kw) for kw in PASSENGER_KEYWORDS if kw.strip()]
NORMALIZED_DRIVER = [normalize_text(kw) for kw in DRIVER_KEYWORDS if kw.strip()]

# Aniq haydovchi iboralari (agar matnda uchrasa, albatta haydovchi e'loni hisoblanadi)
STRONG_DRIVER_PHRASES = [
    "1 kishi kerak", "1 ta kam", "2 ta kam", "3 ta kam", "odam kerak", "1 kishi kerak",
    "olamiz", "olaman", "haydovchiman", "mashina bor", "yuramiz", "beraman", "sotiladi",
    "pochta olamiz", "poshta olamz", "olib ketaman", "olib yuramz", "yuryapmiz",
    "avto cobalt", "mashina kobalt", "mashina kobilt", "оламиз", "олип кеторамиз",
    "олип юраммиз", "юрерамиз", "кетамиз", "билан кетамиз", "билан кеторамиз"
]


def refresh_keywords():
    """
    Admin panel orqali qo'shilgan so'zlarni bazadan qayta yuklab,
    ishlab turgan filtr ro'yxatlariga qo'shadi (init_db() dan keyin chaqirilishi kerak).
    """
    for word in db.get_keywords("passenger"):
        normalized = normalize_text(word)
        if normalized and normalized not in NORMALIZED_PASSENGER:
            NORMALIZED_PASSENGER.append(normalized)
    for word in db.get_keywords("driver"):
        normalized = normalize_text(word)
        if normalized and normalized not in STRONG_DRIVER_PHRASES:
            STRONG_DRIVER_PHRASES.append(normalized)


def add_keyword_live(kw_type: str, word: str):
    """
    Yangi so'zni bazaga yozadi va joriy jarayonda darhol ishlaydigan qiladi.
    """
    if not db.add_keyword(kw_type, word):
        return False
    normalized = normalize_text(word)
    if not normalized:
        return False
    target_list = NORMALIZED_PASSENGER if kw_type == "passenger" else STRONG_DRIVER_PHRASES
    if normalized not in target_list:
        target_list.append(normalized)
    return True

def is_passenger_message(raw_text: str) -> tuple[bool, str]:
    """
    Xabarni yo'lovchiga tegishli ekanligini filtrlash.
    
    Qaydlar:
    1. Xabar uzunligi MAX_MSG_LENGTH (100) dan kam bo'lishi shart.
    2. Haydovchi kalit iboralari qatnashmagan bo'lishi kerak.
    3. Kamida bitta Yo'lovchi kalit so'zi qatnashgan bo'lishi kerak.

    Returns:
        (is_match: bool, reason_or_keyword: str)
    """
    if not raw_text:
        return False, "Bo'sh xabar"
    
    # 1. Uzunlikni tekshirish (100 ta belgidan kam bo'lishi kerak)
    if len(raw_text) >= MAX_MSG_LENGTH:
        return False, f"Xabar uzunligi {len(raw_text)} (100 ta belgidan oshgan)"
    
    clean_text = normalize_text(raw_text)
    
    # 2. Haydovchiga tegishli kuchli iboralarni tekshirish
    for d_kw in STRONG_DRIVER_PHRASES:
        if d_kw in clean_text:
            return False, f"Haydovchi iborasi topildi: '{d_kw}'"
            
    # 3. Yo'lovchi kalit so'zlarini tekshirish
    for p_kw in NORMALIZED_PASSENGER:
        if p_kw in clean_text:
            return True, p_kw
            
    return False, "Yo'lovchi kalit so'zi topilmadi"
