# Invoice Commands

## List Invoices

### User
Zeig mir alle Rechnungen

### Assistant
*[Runs get-invoices.sh RE 2026]*

📋 *Rechnungen 2026*

1. RE-6001
2. RE-6002
3. RE-6003

Gesamt: 3 Rechnungen

## Show Specific Invoice

### User
Zeig mir RE-6001

### Assistant
*[Runs get-invoices.sh RE 2026 6001 -> returns JSON]*
*[Runs calc-preview.sh with the fetched JSON]*

🧾 *Rechnung RE-6001*

📅 Rechnungsdatum: 08.02.2026
📅 Leistungszeitraum: 03.02.2026 - 08.02.2026

📋 *Positionen:*

1. Softwareentwicklung
   1 x 1.000,00 EUR
   = 1.000,00 EUR

💰 *Zusammenfassung:*
Netto: 1.000,00 EUR
_Der Rechnungsbetrag enthält gem. §6 Abs. 1 Z 27 UStG 1994 keine Umsatzsteuer_
*Gesamt: 1.000,00 EUR*

## Invoice with Discount

### User
Angebot an Musterfirma GmbH, 4 Stk IT Dienstleistung 10er Block je 1500 EUR mit 5% Rabatt

### Assistant
*[Runs get-next-number.sh AN 2026 -> returns 6003]*
*[Builds JSON with customer address, discountPercent 5]*
*[Runs calc-preview.sh with the JSON]*

📄 *Angebot AN-6003*

📅 Angebotsdatum: 17.02.2026

👤 *Kunde:*
Musterfirma GmbH
Musterstraße 1
9500 Villach
Österreich

📋 *Positionen:*

1. IT Dienstleistung - 10er Block
   4 x 1.500,00 EUR
   Rabatt 5%: -300,00 EUR
   = 5.700,00 EUR

💰 *Zusammenfassung:*
Netto: 5.700,00 EUR
_Der Rechnungsbetrag enthält gem. §6 Abs. 1 Z 27 UStG 1994 keine Umsatzsteuer_
*Gesamt: 5.700,00 EUR*

Soll ich das Angebot hochladen?
