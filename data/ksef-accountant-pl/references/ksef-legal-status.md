# Stan Prawny KSeF - Szczegóły

**Data aktualizacji:** 8 lutego 2026
**UWAGA:** Informacje mogą ulec zmianie. Należy regularnie weryfikować aktualne przepisy i komunikaty Ministerstwa Finansów.

---

## Harmonogram Wdrożenia (Planowany)

### Faza 1: Duzi Podatnicy (od 1 lutego 2026)
**Kogo dotyczy:** Obrót >200 mln PLN brutto w 2024 roku

**Obowiązki:**
- ✅ Wystawianie faktur przez KSeF
- ✅ Odbieranie faktur przez KSeF

### Faza 2: Pozostali Podatnicy (od 1 kwietnia 2026)
**Kogo dotyczy:** Obrót ≤200 mln PLN

**Obowiązki:**
- ✅ Odbieranie faktur przez KSeF (od 1 lutego 2026)
- ✅ Wystawianie faktur przez KSeF (od 1 kwietnia 2026)
- ⏳ Do 31 marca 2026 mogą wystawiać faktury poza KSeF

### Faza 3: Mikroprzedsiębiorcy (od 1 stycznia 2027)
**Kogo dotyczy:** Miesięczny obrót <10 tys PLN

**Obowiązki:**
- ✅ Odbieranie: od 1 lutego 2026
- ✅ Wystawianie: od 1 stycznia 2027

---

## Okres Przejściowy

**UWAGA:** Szczegóły mogą ulec zmianie. Przedstawione informacje oparte są na aktualnie dostępnych komunikatach.

### Planowany Grace Period
- **Do 31 grudnia 2026** - przewidywany brak kar za błędy
- Dotyczy: błędów w strukturze FA(3), opóźnień wysyłki
- Nie dotyczy: uchylania się od wystawiania faktur

### Tryb Offline24
- **Status:** Planowany jako stały element systemu
- **Przeznaczenie:** Sytuacje awaryjne (brak internetu, awaria KSeF, katastrofy)
- **Termin wysyłki:** 24h od odzyskania łączności
- **Uwaga prawna:** Prawo do odliczenia VAT od daty przypisania numeru KSeF (nie daty wystawienia offline)

### Faktury poza KSeF
- **Do 31 marca 2026:** Dozwolone dla firm ≤200 mln PLN
- **Od 1 kwietnia 2026:** Zakaz (z wyjątkiem przypadków szczególnych)

---

## Zmiany Systemowe

### KSeF 1.0 → KSeF 2.0
- **KSeF 1.0:** Planowane zamknięcie 26 stycznia 2026
- **Przerwa techniczna:** 5 dni (26-31 stycznia 2026)
- **KSeF 2.0:** Planowany start 1 lutego 2026

### FA(2) → FA(3)
- **FA(2):** Planowane zakończenie obsługi 1 lutego 2026
- **FA(3):** Obowiązkowa od 1 lutego 2026
- **Migracja:** Wszyscy podatnicy muszą dostosować systemy

---

## Konsekwencje Prawne (Przyszłe)

**UWAGA:** Poniższe informacje dotyczą planowanego systemu kar po zakończeniu grace period.

### Po 1 stycznia 2027 (Planowane)
- Brak faktury w KSeF → możliwa kara
- Faktura poza KSeF → możliwa kara
- Opóźniona wysyłka → możliwa kara

**Wysokość kar:** Należy konsultować z aktualną ustawą o VAT

---

## Wymagania Techniczne

### Obligatoryjna Struktura
- **FA(3) ver. 1-0E**
- Format: XML zgodny ze schematem
- Encoding: UTF-8
- Walidacja: Automatyczna przy przyjęciu przez KSeF

### Certyfikaty (MCU)
- **MCU:** Moduł Certyfikatów i Uprawnień
- **Status:** Zgodnie z harmonogramem aktywny od 1.11.2025
- **Przeznaczenie:** Alternatywna metoda autoryzacji (oprócz tokenów)

---

## Źródła Informacji

### Oficjalne
- Portal KSeF: https://ksef.podatki.gov.pl
- Ministerstwo Finansów: https://www.gov.pl/web/kas/ksef

### Monitorowanie Zmian
- Komunikaty MF: https://ksef.podatki.gov.pl/web/ksef/aktualnosci
- KSeF Latarnia (status): https://github.com/CIRFMF/ksef-latarnia

---

**Ostatnia aktualizacja:** 8 lutego 2026
**Następna weryfikacja:** Zalecana co 2 tygodnie
