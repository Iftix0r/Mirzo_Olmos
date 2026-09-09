import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Telegram API sozlamalari
API_ID = os.getenv("API_ID", "123456")
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "-1001234567890"))

# Max xabar uzunligi
MAX_MSG_LENGTH = 100

# Yo'lovchi kalit so'zlari (95 ta)
PASSENGER_KEYWORDS = [
    "kerak", "ketish kerak", "olib keting", "yo'lovchi kerak", "borish kerak", "ketmoqchiman",
    "1 kishi bor", "1 kiwi bor", "1 ta odam bor", "1 киши бор", "1 та одам бор", "1ита одам бор",
    "2 kishi bor", "2 ta odam bor", "2 та одам бор", "2ta odam bor", "2та одам бор",
    "3 kishi bor", "3 ta odam bor", "3 та одам бор", "3ta odam bor",
    "4 kishi bor", "4 ta odam bor", "4 та одам бор",
    "5 ta odam bor", "Assalomu aleykum xayrli kech hammaga ertaga Toshkentdan Chustga ketishga taksilar bormi",
    "Bitta odam bor", "Kamfort", "Ketaman", "Moshina kerak", "Odam bor", "Orqa salon",
    "Pochta bor", "Poshta", "Poshta bor", "Powta bor", "Pustoy kerak", "Sroshni Taxi kerak",
    "Taksi ketak", "Taxi kerak", "ayol kishi", "bir kishi bor", "bitta odam bor", "boraman",
    "borish kerak", "borishim kerak", "kamfort", "kerak", "ketaman", "ketish kerak",
    "ketmoqchiman", "kishi bor", "mashina", "mashina kerak", "mashina kk", "moshina kerak",
    "odam bor", "oldi mestaga odam bor", "olib keting", "olib ketishingiz", "orqa salon",
    "pochta bor", "poshta bor", "powta bor", "pustoy kerak", "taksi", "taksi kerak",
    "taksi ketak", "taksi kk", "taxi kerak", "yo'lovchi", "yo'lovchi kerak",
    "Ассалому алейкум тошкентдан чустга 2 киши бор яанги йолдан", "Аёл киши", "Рошта бор",
    "айол кишига мошина керак", "битта одам бор", "кетаман", "мoshina kerak", "машина борми",
    "машина керак", "мошина борми", "мошина керак", "оdam bor", "одам бор", "олди местага одам бор",
    "орка салон", "орқа салон", "почта бор", "пустой", "салон", "такси борми", "такси керак",
    "uchun rahmat", "mm qandayma"
]

# Haydovchi kalit so'zlari (115 ta) - bu so'zlar bo'lsa xabar haydovchiga tegishli deb hisoblanadi va rad etiladi
DRIVER_KEYWORDS = [
    "ketaman", "boraman", "olib ketaman", "haydovchiman", "mashina bor", "taksi", "qo'shishingiz",
    "yozish uchun", "1 KISHI KERAK", "1 kishi kerak", "1 ta kam", "2 ta kam", "2 ta odam poshta olamz",
    "3 ta kam", "AVTO COBALT", "Almatov Adhamjon olib yuramz", "Benzin", "Beraman",
    "Beton ishi qilamiz apalifka", "Biyagomis", "Bolsa ham olamiz", "Elektrik montajga", "Gaz",
    "Gisht", "G’ozapoya", "Harakatdamiz",
    "Ishonchli mega semichka urug‘larbor T6 36 kg narxi 38 dollor urug‘ga garantiya beramiz",
    "Jiyanboy urugi bor ishonchlik", "Kamdamiz", "Kamdamiz Камдамиз", "Karam koʻchat",
    "Kartoshka urugʻ sotiladigan", "Kilyonka", "Koʻchat", "Kulok", "Labo", "MIGIRIM", "Makka",
    "Makka poya sotiladi", "Mol savzi", "ODAM KERAK", "OLAMAN", "Odam kerak", "Olamiz",
    "Oq Gurbak uruq garantiylik", "Oqlovya", "Oqloʻvla", "Osmon yonģoq", "POCHTA OLAMIZ",
    "POSHTA OLAMZ", "Piyoz urugʻ sotaman", "Poya", "Premium", "Qizil Sabzi", "Qovun",
    "Qovun urug' kerak ishonchli  Koʻkcha bilan", "Sabzi", "Samon maydalagich aparat kimda  kattasidan",
    "Santa kartoshka", "Semichka", "Semichkadan", "Sinamal obnovot urugʻ", "Sotiladi", "Tarvuz",
    "Tarvuz koʻchat", "Tarvuz kulok uchun tuproq", "Tel qilib yuboring", "Tom bagaj bor", "Urugʻ",
    "Xashak sotiladi", "Xizmati", "YURAMIZ", "Yongoq pochoq sotiladi", "Yuramiz", "Yuryapmiz", "Zaruri",
    "aksiya arzon narxlarda guruhizga juvoy qushiib beraman admiinla kimga kerak lichkamga yozing narxlarni tashlayman siiz aytgan viloyatdan qushib beraman",
    "arzon narxlarda guruhizga qushiib beramiz narxiini siiz aytasiz savdolashamiz  lichkamga",
    "beraman", "bolsa", "boraman", "elab qoplangan tozza quruq biyogumis", "haydovchiman",
    "kam srochni yuramiz", "ketaman", "ketamiz", "kimda damazga zadnimos", "kimga", "kishi kerak",
    "lic", "mashina bor", "olib", "olib ketaman", "pochta olib yuramz",
    "qayda bozor boladi biladiganla", "taksi", "yozinglar", "yuramiz", "БИЛАН",
    "БИЛАН \nКЕТОРАМИЗ", "БИЛАН КЕТАМИЗ", "КЕТАМИЗ", "Новый год на носу",
    "Нужно покосить траву у меня на даче", "ОЛАМИЗ", "ОЛИП КЕТОРАМИЗ", "Олип Авто",
    "Олип юраммиз Авто кобальт", "клент", "пустой", "пустой?",
    "шу нумерда ТОШКЕНТ дан тошкургонда аёл кишиборлар тел килилар", "юрерамиз",
    "MASHINA KOBALT", "MASHINA    KOBILT"
]
