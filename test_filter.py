from filter import is_passenger_message

# Test misollari
test_cases = [
    # (matn, kutilgan_natija)
    ("Toshkentdan Chustga 2 ta odam bor", True),
    ("1 kishi bor Toshkentga ketishga", True),
    ("Moshina kerak Toshkentdan Vodiyga", True),
    ("Sroshni Taxi kerak 1 kishi bor", True),
    ("1 kishi kerak Toshkentga olib ketamiz Cobalt", False), # Haydovchi
    ("Cobalt bor Toshkentga 2 ta kam olamiz yuramiz", False), # Haydovchi
    ("Puchta olamiz va odam olamiz Toshkentga yuramiz", False), # Haydovchi
    ("Bu o'ta uzun xabar bo'lib 100 ta belgidan oshib ketgan xabarlar bot tomonidan qayta ishlanmaydi va rad etiladi chunki shart bo'yicha 100 belgidan kam bo'lishi kerak!", False), # > 100 belgi
]

def run_tests():
    print("--- FILTR TESTLARI ---")
    passed = 0
    for text, expected in test_cases:
        result, reason = is_passenger_message(text)
        status = "PASSED" if result == expected else "FAILED"
        if result == expected:
            passed += 1
        print(f"[{status}] Natija: {result} (Sabab/Kalit: '{reason}') | Matn: '{text[:50]}...'")
    
    print(f"\nJami testlar: {len(test_cases)}, Muvaffaqiyatli: {passed}")

if __name__ == "__main__":
    run_tests()
