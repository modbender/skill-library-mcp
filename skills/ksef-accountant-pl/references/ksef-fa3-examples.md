# Przykłady FA(3) XML

**UWAGA:** Wszystkie przykłady mają charakter wyłącznie poglądowy i uproszczony. Nie stanowią gwarancji poprawnej walidacji względem schematu XSD. Przed użyciem w środowisku produkcyjnym należy zweryfikować zgodność z aktualną specyfikacją techniczną FA(3) oraz przeprowadzić testy walidacji.

---

## Podstawowa Faktura VAT

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Faktura xmlns="http://crd.gov.pl/wzor/2023/06/29/12648/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Naglowek>
        <KodFormularza kodSystemowy="FA(3)" wersjaSchemy="1-0E">FA</KodFormularza>
        <WariantFormularza>3</WariantFormularza>
        <DataWytworzeniaFa>2026-02-08T14:30:00</DataWytworzeniaFa>
        <SystemInfo>Autonomous KSeF Agent v2.1</SystemInfo>
    </Naglowek>

    <!-- Sprzedawca -->
    <Podmiot1>
        <DaneIdentyfikacyjne>
            <NIP>1234567890</NIP>
            <Nazwa>Moja Firma Sp. z o.o.</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <AdresL1>ul. Przykładowa 1</AdresL1>
            <AdresL2>00-001 Warszawa</AdresL2>
        </Adres>
    </Podmiot1>

    <!-- Nabywca -->
    <Podmiot2>
        <DaneIdentyfikacyjne>
            <NIP>0987654321</NIP>
            <Nazwa>Klient Sp. z o.o.</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <AdresL1>ul. Testowa 10</AdresL1>
            <AdresL2>02-222 Kraków</AdresL2>
        </Adres>
    </Podmiot2>

    <!-- Dane faktury -->
    <Fa>
        <KodWaluty>PLN</KodWaluty>
        <P_1>2026-02-08</P_1> <!-- Data wystawienia -->
        <P_2>FV/2026/02/0008</P_2> <!-- Numer faktury -->
        <P_6>2026-02-08</P_6> <!-- Data sprzedaży -->

        <!-- Pozycje faktury -->
        <FaWiersz>
            <NrWierszaFa>1</NrWierszaFa>
            <P_7>Usługa programistyczna</P_7>
            <P_8A>godz.</P_8A>
            <P_8B>100</P_8B>
            <P_9A>100.00</P_9A>
            <P_11>10000.00</P_11> <!-- Wartość netto -->
            <P_12>23</P_12> <!-- Stawka VAT -->
        </FaWiersz>

        <!-- Podsumowanie -->
        <P_13_1>10000.00</P_13_1> <!-- Netto 23% -->
        <P_14_1>2300.00</P_14_1> <!-- VAT 23% -->
        <P_15>12300.00</P_15> <!-- Brutto -->

        <RodzajFaktury>VAT</RodzajFaktury>

        <!-- Płatność -->
        <Platnosc>
            <Zaplacono>0</Zaplacono>
            <DataZaplaty>2026-02-22</DataZaplaty>
            <FormaPlatnosci>6</FormaPlatnosci> <!-- Przelew -->
            <RachunekBankowy>12 3456 7890 1234 5678 9012 3456</RachunekBankowy>
        </Platnosc>
    </Fa>
</Faktura>
```

---

## Faktura z Wieloma Pozycjami i Stawkami VAT

```xml
<Fa>
    <KodWaluty>PLN</KodWaluty>
    <P_1>2026-02-09</P_1>
    <P_2>FV/2026/02/0009</P_2>
    <P_6>2026-02-09</P_6>

    <!-- Pozycja 1: VAT 23% -->
    <FaWiersz>
        <NrWierszaFa>1</NrWierszaFa>
        <P_7>Laptop Dell XPS 15</P_7>
        <P_8A>szt.</P_8A>
        <P_8B>2</P_8B>
        <P_9A>5000.00</P_9A>
        <P_11>10000.00</P_11>
        <P_12>23</P_12>
    </FaWiersz>

    <!-- Pozycja 2: VAT 8% -->
    <FaWiersz>
        <NrWierszaFa>2</NrWierszaFa>
        <P_7>Książki techniczne</P_7>
        <P_8A>szt.</P_8A>
        <P_8B>10</P_8B>
        <P_9A>50.00</P_9A>
        <P_11>500.00</P_11>
        <P_12>8</P_12>
    </FaWiersz>

    <!-- Pozycja 3: VAT 0% (eksport) -->
    <FaWiersz>
        <NrWierszaFa>3</NrWierszaFa>
        <P_7>Usługi konsultingowe (eksport)</P_7>
        <P_8A>godz.</P_8A>
        <P_8B>40</P_8B>
        <P_9A>200.00</P_9A>
        <P_11>8000.00</P_11>
        <P_12>0</P_12>
    </FaWiersz>

    <!-- Podsumowanie -->
    <P_13_1>10000.00</P_13_1> <!-- Netto 23% -->
    <P_14_1>2300.00</P_14_1> <!-- VAT 23% -->
    <P_13_2>500.00</P_13_2> <!-- Netto 8% -->
    <P_14_2>40.00</P_14_2> <!-- VAT 8% -->
    <P_13_3>8000.00</P_13_3> <!-- Netto 0% -->
    <P_15>20840.00</P_15> <!-- Brutto -->

    <RodzajFaktury>VAT</RodzajFaktury>
</Fa>
```

---

## Faktura Korygująca

```xml
<Fa>
    <P_2>FV/2026/02/0005/K01</P_2> <!-- Numer korekty -->
    <RodzajFaktury>KOREKTA</RodzajFaktury>
    <PrzyczynaKorekty>Błąd w cenie jednostkowej</PrzyczynaKorekty>

    <!-- Dane faktury korygowanej -->
    <DaneFaKorygowanej>
        <DataWystFaKorygowanej>2026-02-05</DataWystFaKorygowanej>
        <NrFaKorygowanej>FV/2026/02/0005</NrFaKorygowanej>
        <NrKSeFFaKorygowanej>1234567890-20260205-ORIGINAL123456-12</NrKSeFFaKorygowanej>
    </DaneFaKorygowanej>

    <!-- Dane PRZED korektą -->
    <FaWierszCtrl>
        <LiczbaWierszyFa>1</LiczbaWierszyFa>
        <WartoscWierszyFa>12300.00</WartoscWierszyFa>
    </FaWierszCtrl>

    <!-- Dane PO korekcie -->
    <FaWiersz>
        <NrWierszaFa>1</NrWierszaFa>
        <P_7>Usługa programistyczna (cena skorygowana)</P_7>
        <P_8A>godz.</P_8A>
        <P_8B>100</P_8B>
        <P_9A>50.00</P_9A> <!-- Nowa cena: 50 zamiast 100 -->
        <P_11>5000.00</P_11>
        <P_12>23</P_12>
    </FaWiersz>

    <!-- Nowe podsumowanie -->
    <P_13_1>5000.00</P_13_1>
    <P_14_1>1150.00</P_14_1>
    <P_15>6150.00</P_15>
</Fa>
```

---

## Faktura z Kontrahent PRACOWNIK (Delegacja)

**Nowość FA(3):** Nowy typ kontrahenta do rozliczania delegacji

```xml
<Podmiot2>
    <DaneIdentyfikacyjne>
        <TypPodmiotu>PRACOWNIK</TypPodmiotu>
        <PESEL>85010112345</PESEL>
        <ImieNazwisko>Jan Kowalski</ImieNazwisko>
    </DaneIdentyfikacyjne>
    <Adres>
        <KodKraju>PL</KodKraju>
        <AdresL1>ul. Pracownicza 5</AdresL1>
        <AdresL2>03-333 Warszawa</AdresL2>
    </Adres>
</Podmiot2>

<Fa>
    <P_2>DEL/2026/02/001</P_2>
    <FaWiersz>
        <P_7>Rozliczenie delegacji - luty 2026</P_7>
        <P_8A>dni</P_8A>
        <P_8B>5</P_8B>
        <P_9A>150.00</P_9A>
        <P_11>750.00</P_11>
        <P_12>zw</P_12> <!-- VAT zwolniony -->
    </FaWiersz>
    <RodzajFaktury>VAT</RodzajFaktury>
</Fa>
```

---

## Faktura Trybu Offline24

```xml
<Naglowek>
    <KodFormularza kodSystemowy="FA(3)" wersjaSchemy="1-0E">FA</KodFormularza>
    <WariantFormularza>3</WariantFormularza>
    <DataWytworzeniaFa>2026-02-10T08:00:00</DataWytworzeniaFa>
    <SystemInfo>Offline24</SystemInfo> <!-- Oznaczenie offline -->
</Naglowek>
```

**Uwaga:** Wysłać do KSeF w ciągu 24h od odzyskania łączności. Data odbioru = data przypisania numeru KSeF.

---

## Faktura z Załącznikami

**Nowość FA(3):** Możliwość dołączenia załączników

```xml
<Fa>
    <!-- Standardowe dane faktury -->
    <P_2>FV/2026/02/0010</P_2>

    <!-- Załączniki -->
    <Zalaczniki>
        <Zalacznik>
            <NazwaPliku>specyfikacja_techniczna.pdf</NazwaPliku>
            <TypZalacznika>SPECYFIKACJA</TypZalacznika>
            <RozmiarKB>256</RozmiarKB>
            <HashSHA256>a1b2c3d4e5f6...</HashSHA256>
        </Zalacznik>
        <Zalacznik>
            <NazwaPliku>protokol_dostawy.pdf</NazwaPliku>
            <TypZalacznika>PROTOKOL</TypZalacznika>
            <RozmiarKB>128</RozmiarKB>
            <HashSHA256>f6e5d4c3b2a1...</HashSHA256>
        </Zalacznik>
    </Zalaczniki>
</Fa>
```

---

## Faktura z MPP (Mechanizm Podzielonej Płatności)

```xml
<Fa>
    <P_2>FV/2026/02/0011</P_2>

    <FaWiersz>
        <P_7>Stal konstrukcyjna (załącznik 15)</P_7>
        <P_8A>kg</P_8A>
        <P_8B>1000</P_8B>
        <P_9A>20.00</P_9A>
        <P_11>20000.00</P_11>
        <P_12>23</P_12>
        <OznaczenieMPP>1</OznaczenieMPP> <!-- Wymaga MPP -->
    </FaWiersz>

    <P_13_1>20000.00</P_13_1>
    <P_14_1>4600.00</P_14_1>
    <P_15>24600.00</P_15>

    <Platnosc>
        <TypPlatnosci>MPP</TypPlatnosci>
        <RachunekBankowy>12 3456 7890 1234 5678 9012 3456</RachunekBankowy>
        <RachunekBankowyVAT>98 7654 3210 9876 5432 1098 7654</RachunekBankowyVAT>
    </Platnosc>
</Fa>
```

---

## Walidacja przed Wysłaniem

```python
def validate_fa3_before_send(xml_content):
    """
    Podstawowa walidacja przed wysłaniem do KSeF
    """
    checks = []

    # 1. UTF-8 encoding
    try:
        xml_content.encode('utf-8')
        checks.append(('Encoding UTF-8', True))
    except:
        checks.append(('Encoding UTF-8', False))

    # 2. Parsowanie XML
    try:
        root = ET.fromstring(xml_content)
        checks.append(('Poprawny XML', True))
    except:
        checks.append(('Poprawny XML', False))
        return checks

    # 3. Namespace
    if 'http://crd.gov.pl/wzor/2023/06/29/12648/' in xml_content:
        checks.append(('Namespace FA(3)', True))
    else:
        checks.append(('Namespace FA(3)', False))

    # 4. Wersja schematu
    if 'wersjaSchemy="1-0E"' in xml_content:
        checks.append(('Wersja schematu 1-0E', True))
    else:
        checks.append(('Wersja schematu 1-0E', False))

    # 5. Wymagane pola
    required = ['KodFormularza', 'P_1', 'P_2', 'P_15', 'NIP']
    for field in required:
        if f'<{field}' in xml_content or f'<{field}>' in xml_content:
            checks.append((f'Pole {field}', True))
        else:
            checks.append((f'Pole {field}', False))

    return checks
```

---

**Oficjalna dokumentacja FA(3):**
https://ksef.podatki.gov.pl/media/4u1bmhx4/information-sheet-on-the-fa-3-logical-structure.pdf
