# Basic Invoice Creation

## User
/invoice

## Assistant
Lass uns eine neue Rechnung erstellen! Bitte gib mir folgende Infos:
- Kundenname und Adresse (oder Kundennummer)
- Positionen (Titel, Beschreibung, Menge, Einzelpreis)
- Besondere Hinweise (optional)

## User
Rechnung an Musterfirma GmbH, Musterstraße 1, 9500 Villach. Softwareentwicklung pauschal 1000 EUR

## Assistant
*[Runs get-next-number.sh RE 2026 -> returns 6008]*

*[Builds JSON with sender data from data.json, recipient address, one item]*

*[Runs calc-preview.sh with the JSON]*

🧾 *Rechnung RE-6008*

📅 Rechnungsdatum: 17.02.2026

👤 *Kunde:*
Musterfirma GmbH
Musterstraße 1
9500 Villach
Österreich

📋 *Positionen:*

1. Softwareentwicklung
   1 x 1.000,00 EUR
   = 1.000,00 EUR

💰 *Zusammenfassung:*
Netto: 1.000,00 EUR
_Der Rechnungsbetrag enthält gem. §6 Abs. 1 Z 27 UStG 1994 keine Umsatzsteuer_
*Gesamt: 1.000,00 EUR*

📝 Zahlungsbedingungen: Zahlung innerhalb von 14 Tagen ab Rechnungseingang ohne Abzüge.
Der Rechnungsbetrag ist sofort fällig. Zahlbar und klagbar in Wien.

Soll ich die Rechnung hochladen?

## User
Ja

## Assistant
*[Runs push-invoice.sh RE 2026 6008 '...']*

Rechnung RE-6008 wurde erfolgreich auf GitHub hochgeladen!

Die GitHub Action wird jetzt automatisch das PDF bauen und per E-Mail versenden.
