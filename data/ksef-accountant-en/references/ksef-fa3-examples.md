# FA(3) XML Examples

**NOTE:** All examples are purely illustrative and simplified. They do not guarantee correct validation against the XSD schema. Before using in a production environment, verify compliance with the current FA(3) technical specification and perform validation tests.

---

## Basic VAT Invoice

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

    <!-- Seller -->
    <Podmiot1>
        <DaneIdentyfikacyjne>
            <NIP>1234567890</NIP>
            <Nazwa>Moja Firma Sp. z o.o.</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <AdresL1>ul. Przykladowa 1</AdresL1>
            <AdresL2>00-001 Warszawa</AdresL2>
        </Adres>
    </Podmiot1>

    <!-- Buyer -->
    <Podmiot2>
        <DaneIdentyfikacyjne>
            <NIP>0987654321</NIP>
            <Nazwa>Klient Sp. z o.o.</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <AdresL1>ul. Testowa 10</AdresL1>
            <AdresL2>02-222 Krakow</AdresL2>
        </Adres>
    </Podmiot2>

    <!-- Invoice data -->
    <Fa>
        <KodWaluty>PLN</KodWaluty>
        <P_1>2026-02-08</P_1> <!-- Issue date -->
        <P_2>FV/2026/02/0008</P_2> <!-- Invoice number -->
        <P_6>2026-02-08</P_6> <!-- Sale date -->

        <!-- Invoice line items -->
        <FaWiersz>
            <NrWierszaFa>1</NrWierszaFa>
            <P_7>Programming service</P_7>
            <P_8A>hrs</P_8A>
            <P_8B>100</P_8B>
            <P_9A>100.00</P_9A>
            <P_11>10000.00</P_11> <!-- Net value -->
            <P_12>23</P_12> <!-- VAT rate -->
        </FaWiersz>

        <!-- Summary -->
        <P_13_1>10000.00</P_13_1> <!-- Net 23% -->
        <P_14_1>2300.00</P_14_1> <!-- VAT 23% -->
        <P_15>12300.00</P_15> <!-- Gross -->

        <RodzajFaktury>VAT</RodzajFaktury>

        <!-- Payment -->
        <Platnosc>
            <Zaplacono>0</Zaplacono>
            <DataZaplaty>2026-02-22</DataZaplaty>
            <FormaPlatnosci>6</FormaPlatnosci> <!-- Bank transfer -->
            <RachunekBankowy>12 3456 7890 1234 5678 9012 3456</RachunekBankowy>
        </Platnosc>
    </Fa>
</Faktura>
```

---

## Invoice with Multiple Items and VAT Rates

```xml
<Fa>
    <KodWaluty>PLN</KodWaluty>
    <P_1>2026-02-09</P_1>
    <P_2>FV/2026/02/0009</P_2>
    <P_6>2026-02-09</P_6>

    <!-- Item 1: VAT 23% -->
    <FaWiersz>
        <NrWierszaFa>1</NrWierszaFa>
        <P_7>Laptop Dell XPS 15</P_7>
        <P_8A>pcs</P_8A>
        <P_8B>2</P_8B>
        <P_9A>5000.00</P_9A>
        <P_11>10000.00</P_11>
        <P_12>23</P_12>
    </FaWiersz>

    <!-- Item 2: VAT 8% -->
    <FaWiersz>
        <NrWierszaFa>2</NrWierszaFa>
        <P_7>Technical books</P_7>
        <P_8A>pcs</P_8A>
        <P_8B>10</P_8B>
        <P_9A>50.00</P_9A>
        <P_11>500.00</P_11>
        <P_12>8</P_12>
    </FaWiersz>

    <!-- Item 3: VAT 0% (export) -->
    <FaWiersz>
        <NrWierszaFa>3</NrWierszaFa>
        <P_7>Consulting services (export)</P_7>
        <P_8A>hrs</P_8A>
        <P_8B>40</P_8B>
        <P_9A>200.00</P_9A>
        <P_11>8000.00</P_11>
        <P_12>0</P_12>
    </FaWiersz>

    <!-- Summary -->
    <P_13_1>10000.00</P_13_1> <!-- Net 23% -->
    <P_14_1>2300.00</P_14_1> <!-- VAT 23% -->
    <P_13_2>500.00</P_13_2> <!-- Net 8% -->
    <P_14_2>40.00</P_14_2> <!-- VAT 8% -->
    <P_13_3>8000.00</P_13_3> <!-- Net 0% -->
    <P_15>20840.00</P_15> <!-- Gross -->

    <RodzajFaktury>VAT</RodzajFaktury>
</Fa>
```

---

## Corrective Invoice

```xml
<Fa>
    <P_2>FV/2026/02/0005/K01</P_2> <!-- Correction number -->
    <RodzajFaktury>KOREKTA</RodzajFaktury>
    <PrzyczynaKorekty>Error in unit price</PrzyczynaKorekty>

    <!-- Corrected invoice data -->
    <DaneFaKorygowanej>
        <DataWystFaKorygowanej>2026-02-05</DataWystFaKorygowanej>
        <NrFaKorygowanej>FV/2026/02/0005</NrFaKorygowanej>
        <NrKSeFFaKorygowanej>1234567890-20260205-ORIGINAL123456-12</NrKSeFFaKorygowanej>
    </DaneFaKorygowanej>

    <!-- Data BEFORE correction -->
    <FaWierszCtrl>
        <LiczbaWierszyFa>1</LiczbaWierszyFa>
        <WartoscWierszyFa>12300.00</WartoscWierszyFa>
    </FaWierszCtrl>

    <!-- Data AFTER correction -->
    <FaWiersz>
        <NrWierszaFa>1</NrWierszaFa>
        <P_7>Programming service (price corrected)</P_7>
        <P_8A>hrs</P_8A>
        <P_8B>100</P_8B>
        <P_9A>50.00</P_9A> <!-- New price: 50 instead of 100 -->
        <P_11>5000.00</P_11>
        <P_12>23</P_12>
    </FaWiersz>

    <!-- New summary -->
    <P_13_1>5000.00</P_13_1>
    <P_14_1>1150.00</P_14_1>
    <P_15>6150.00</P_15>
</Fa>
```

---

## Invoice with EMPLOYEE Contractor Type (Business Trip)

**New in FA(3):** New contractor type for business trip settlements

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
        <P_7>Business trip settlement - February 2026</P_7>
        <P_8A>days</P_8A>
        <P_8B>5</P_8B>
        <P_9A>150.00</P_9A>
        <P_11>750.00</P_11>
        <P_12>zw</P_12> <!-- VAT exempt -->
    </FaWiersz>
    <RodzajFaktury>VAT</RodzajFaktury>
</Fa>
```

---

## Offline24 Mode Invoice

```xml
<Naglowek>
    <KodFormularza kodSystemowy="FA(3)" wersjaSchemy="1-0E">FA</KodFormularza>
    <WariantFormularza>3</WariantFormularza>
    <DataWytworzeniaFa>2026-02-10T08:00:00</DataWytworzeniaFa>
    <SystemInfo>Offline24</SystemInfo> <!-- Offline designation -->
</Naglowek>
```

**Note:** Must be sent to KSeF within 24h of connectivity restoration. Receipt date = date of KSeF number assignment.

---

## Invoice with Attachments

**New in FA(3):** Ability to include attachments

```xml
<Fa>
    <!-- Standard invoice data -->
    <P_2>FV/2026/02/0010</P_2>

    <!-- Attachments -->
    <Zalaczniki>
        <Zalacznik>
            <NazwaPliku>technical_specification.pdf</NazwaPliku>
            <TypZalacznika>SPECYFIKACJA</TypZalacznika>
            <RozmiarKB>256</RozmiarKB>
            <HashSHA256>a1b2c3d4e5f6...</HashSHA256>
        </Zalacznik>
        <Zalacznik>
            <NazwaPliku>delivery_protocol.pdf</NazwaPliku>
            <TypZalacznika>PROTOKOL</TypZalacznika>
            <RozmiarKB>128</RozmiarKB>
            <HashSHA256>f6e5d4c3b2a1...</HashSHA256>
        </Zalacznik>
    </Zalaczniki>
</Fa>
```

---

## Invoice with MPP (Split Payment Mechanism)

```xml
<Fa>
    <P_2>FV/2026/02/0011</P_2>

    <FaWiersz>
        <P_7>Structural steel (Annex 15)</P_7>
        <P_8A>kg</P_8A>
        <P_8B>1000</P_8B>
        <P_9A>20.00</P_9A>
        <P_11>20000.00</P_11>
        <P_12>23</P_12>
        <OznaczenieMPP>1</OznaczenieMPP> <!-- Requires MPP -->
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

## Validation before Sending

```python
def validate_fa3_before_send(xml_content):
    """
    Basic validation before sending to KSeF
    """
    checks = []

    # 1. UTF-8 encoding
    try:
        xml_content.encode('utf-8')
        checks.append(('UTF-8 Encoding', True))
    except:
        checks.append(('UTF-8 Encoding', False))

    # 2. XML parsing
    try:
        root = ET.fromstring(xml_content)
        checks.append(('Valid XML', True))
    except:
        checks.append(('Valid XML', False))
        return checks

    # 3. Namespace
    if 'http://crd.gov.pl/wzor/2023/06/29/12648/' in xml_content:
        checks.append(('FA(3) Namespace', True))
    else:
        checks.append(('FA(3) Namespace', False))

    # 4. Schema version
    if 'wersjaSchemy="1-0E"' in xml_content:
        checks.append(('Schema version 1-0E', True))
    else:
        checks.append(('Schema version 1-0E', False))

    # 5. Required fields
    required = ['KodFormularza', 'P_1', 'P_2', 'P_15', 'NIP']
    for field in required:
        if f'<{field}' in xml_content or f'<{field}>' in xml_content:
            checks.append((f'Field {field}', True))
        else:
            checks.append((f'Field {field}', False))

    return checks
```

---

**Official FA(3) documentation:**
https://ksef.podatki.gov.pl/media/4u1bmhx4/information-sheet-on-the-fa-3-logical-structure.pdf
