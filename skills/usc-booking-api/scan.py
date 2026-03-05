#!/usr/bin/env python3
"""
Urban Sports Scanner
Scannt konfigurierte Studios und gibt Kurse für einen Tag zurück.
"""

import asyncio
from playwright.async_api import async_playwright
import re
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import VENUES, PLAN_TYPE, BUSINESS_TYPE


async def scan_venue(page, venue_key, venue_data, target_date):
    """Scannt eine einzelne Venue für ein Datum."""
    url = f"{venue_data['url']}?date={target_date}&business_type%5B%5D={BUSINESS_TYPE}&plan_type={PLAN_TYPE}"

    try:
        print(f"  {venue_data['name']}...", file=sys.stderr)

        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Kurse aus DOM-Elementen mit data-appointment-id extrahieren
        elements = await page.locator("[data-appointment-id]").all()
        classes = []

        for el in elements:
            appointment_id = await el.get_attribute("data-appointment-id")
            text = await el.inner_text()

            time_match = re.search(r'\b(0[6-9]|1[0-9]|2[0-3]):([0-5]\d)\b', text)
            if not time_match:
                continue
            time_str = time_match.group(0)

            name = "Unknown"
            for line in text.split('\n'):
                line = line.strip()
                if any(kw in line for kw in venue_data["keywords"]):
                    if 5 < len(line) < 100:
                        name = line
                        break

            duration = None
            dur_match = re.search(r'(\d+)\s*Min', text)
            if dur_match:
                duration = int(dur_match.group(1))

            booking_url = f"https://www.urbansportsclub.com/de/activities?class={appointment_id}"

            classes.append({
                "venue": venue_key,
                "venue_name": venue_data["name"],
                "type": venue_data["type"],
                "time": time_str,
                "name": name,
                "duration": duration or 45,
                "date": target_date,
                "url": booking_url,
            })

        print(f"    {len(classes)} Kurse gefunden", file=sys.stderr)
        return classes

    except Exception as e:
        print(f"    Fehler: {e}", file=sys.stderr)
        return []


def load_credentials():
    """Laedt Zugangsdaten aus credentials.json."""
    creds_path = Path(__file__).parent / "credentials.json"
    if not creds_path.exists():
        print("Fehler: credentials.json nicht gefunden.", file=sys.stderr)
        print("Kopiere credentials.example.json -> credentials.json und trage deine Daten ein.", file=sys.stderr)
        return None

    with open(creds_path) as f:
        creds = json.load(f)

    if not creds.get("email") or not creds.get("password"):
        print("Fehler: email oder password in credentials.json ist leer.", file=sys.stderr)
        return None

    return creds


async def login(page):
    """Loggt sich bei Urban Sports Club ein. Gibt True zurueck bei Erfolg."""
    creds = load_credentials()
    if not creds:
        return False

    print("  Login...", file=sys.stderr)
    await page.goto("https://urbansportsclub.com/de/login", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)

    try:
        await page.locator('button:has-text("Alle Cookies akzeptieren")').first.click(timeout=3000)
        await page.wait_for_timeout(500)
    except Exception:
        pass

    await page.locator('input[name="email"]:visible').fill(creds["email"])
    await page.locator('input[name="password"]:visible').fill(creds["password"])
    await page.locator('input[name="login"]:visible').first.click()
    await page.wait_for_timeout(5000)
    return True


async def get_bookings():
    """Holt anstehende Buchungen aus dem Profil."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        if not await login(page):
            await browser.close()
            return []

        await page.goto("https://urbansportsclub.com/de/profile/schedule", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        elements = await page.locator("[data-appointment-id]").all()
        bookings = []

        for el in elements:
            appointment_id = await el.get_attribute("data-appointment-id")
            text = await el.inner_text()

            # Zeit parsen (z.B. "07:30 — 08:15")
            time_match = re.search(r'(\d{2}:\d{2})\s*[—–-]\s*(\d{2}:\d{2})', text)
            time_start = time_match.group(1) if time_match else "?"
            time_end = time_match.group(2) if time_match else "?"

            # Name: laengste Zeile die kein reines Keyword ist
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            name = "Unknown"
            for line in lines:
                if len(line) > 10 and line not in ("Gebucht", "Weiter") and "—" not in line:
                    if not re.match(r'^[\d:—–\-\s]+$', line) and "M L XL" not in line:
                        name = line
                        break

            # Datum: Suche nach "Tag DD. Monat" im umgebenden Text
            # Das Datum steht als Ueberschrift VOR dem Element
            date_str = None

            bookings.append({
                "class_id": appointment_id,
                "time": f"{time_start} - {time_end}",
                "name": name,
                "url": f"https://www.urbansportsclub.com/de/activities?class={appointment_id}",
            })

        await browser.close()
        return bookings


async def book_class(class_id):
    """Bucht einen Kurs ueber die Class ID."""
    print(f"Buche Kurs {class_id}...", file=sys.stderr)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        if not await login(page):
            await browser.close()
            return "Login fehlgeschlagen"

        # 2. Zur Class-Seite
        url = f"https://www.urbansportsclub.com/de/activities?class={class_id}"
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # 3. Buchen
        book_btn = page.locator('button:has-text("Sofort buchen"):visible')
        if await book_btn.count() > 0:
            await book_btn.first.click()
            await page.wait_for_timeout(5000)

            # Button weg = Buchung erfolgreich
            if await book_btn.count() == 0:
                print("  Gebucht!", file=sys.stderr)
                await browser.close()
                return True

            # Alert pruefen: Erfolg oder Fehler?
            alerts = page.locator('[role="alert"], .alert, .notification, .toast, .error-message')
            if await alerts.count() > 0:
                msg = (await alerts.first.inner_text()).strip()
                msg = msg.replace("Schließen", "").replace("Schliessen", "").strip()
                if "erfolgreich" in msg.lower() or "gebucht" in msg.lower():
                    print("  Gebucht!", file=sys.stderr)
                    await browser.close()
                    return True
                await browser.close()
                return msg or "Buchung fehlgeschlagen"

            await browser.close()
            return "Buchung fehlgeschlagen - Button noch sichtbar"
        else:
            cancel_btn = page.locator('button:has-text("Buchung stornieren"):visible')
            if await cancel_btn.count() > 0:
                await browser.close()
                return "Kurs ist bereits gebucht"
            await browser.close()
            return "'Sofort buchen' Button nicht gefunden"


async def cancel_class(class_id):
    """Storniert eine Buchung ueber die Class ID."""
    print(f"Storniere Kurs {class_id}...", file=sys.stderr)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        if not await login(page):
            await browser.close()
            return "Login fehlgeschlagen"

        url = f"https://www.urbansportsclub.com/de/activities?class={class_id}"
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        cancel_btn = page.locator('button:has-text("Buchung stornieren")')
        if await cancel_btn.count() > 0:
            await cancel_btn.first.click()
            await page.wait_for_timeout(2000)

            # Bestaetigungs-Modal: "Ja, ich möchte stornieren"
            confirm_btn = page.locator('button:has-text("Ja, ich möchte stornieren")')
            if await confirm_btn.count() > 0:
                await confirm_btn.first.click()
                await page.wait_for_timeout(5000)

            # Erfolg pruefen: "Sofort buchen" sichtbar = Stornierung war erfolgreich
            book_btn = page.locator('button:has-text("Sofort buchen")')
            if await book_btn.count() > 0:
                print("  Storniert!", file=sys.stderr)
                await browser.close()
                return True

            if await cancel_btn.count() == 0:
                print("  Storniert!", file=sys.stderr)
                await browser.close()
                return True

            alerts = page.locator('[role="alert"], .alert, .notification, .toast, .error-message')
            if await alerts.count() > 0:
                msg = (await alerts.first.inner_text()).strip()
                msg = msg.replace("Schließen", "").replace("Schliessen", "").strip()
                if "storniert" in msg.lower() or "erfolgreich" in msg.lower():
                    print("  Storniert!", file=sys.stderr)
                    await browser.close()
                    return True
                await browser.close()
                return msg or "Stornierung fehlgeschlagen"

            await browser.close()
            return "Stornierung fehlgeschlagen"
        else:
            await browser.close()
            return "'Buchung stornieren' Button nicht gefunden"


async def scan_all_venues(target_date=None, venue_filter=None):
    """Scannt alle Venues (oder eine einzelne)."""
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")

    venues_to_scan = VENUES
    if venue_filter:
        if venue_filter in VENUES:
            venues_to_scan = {venue_filter: VENUES[venue_filter]}
        else:
            print(f"Unbekannte Venue: {venue_filter}", file=sys.stderr)
            print(f"Verfuegbar: {', '.join(VENUES.keys())}", file=sys.stderr)
            return []

    all_classes = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        for venue_key, venue_data in venues_to_scan.items():
            classes = await scan_venue(page, venue_key, venue_data, target_date)
            all_classes.extend(classes)

        await browser.close()

    all_classes.sort(key=lambda c: c["time"])
    return all_classes


def main():
    import argparse

    venue_keys = ', '.join(VENUES.keys()) if VENUES else 'keine konfiguriert'
    parser = argparse.ArgumentParser(description="Urban Sports Club - Kurse scannen & buchen")
    parser.add_argument("--date", help="Datum (YYYY-MM-DD), default: heute", default=None)
    parser.add_argument("--venue", help=f"Venue-Key ({venue_keys})", default=None)
    parser.add_argument("--json", action="store_true", help="JSON-Ausgabe")
    parser.add_argument("--book", metavar="CLASS_ID", help="Kurs buchen (Class ID)")
    parser.add_argument("--cancel", metavar="CLASS_ID", help="Buchung stornieren (Class ID)")
    parser.add_argument("--bookings", action="store_true", help="Anstehende Buchungen anzeigen")
    args = parser.parse_args()

    # Credentials pruefen fuer Login-Aktionen
    if args.book or args.cancel or args.bookings:
        if not load_credentials():
            sys.exit(1)

    # Venues pruefen fuer Scan-Aktionen
    if not (args.book or args.cancel or args.bookings) and not VENUES:
        print("Fehler: Keine Venues konfiguriert.", file=sys.stderr)
        print("Trage deine Venues in config.py ein (siehe Beispiel in der Datei).", file=sys.stderr)
        sys.exit(1)

    if args.cancel:
        result = asyncio.run(cancel_class(args.cancel))
        if result is True:
            print(f"Kurs {args.cancel} storniert")
        else:
            print(f"Stornierung fehlgeschlagen: {result}")
        return

    if args.bookings:
        bookings = asyncio.run(get_bookings())
        if args.json:
            print(json.dumps(bookings, indent=2, ensure_ascii=False))
        elif bookings:
            print(f"\n{len(bookings)} anstehende Buchung(en):\n")
            for b in bookings:
                print(f"  {b['time']}  {b['name']}")
                print(f"         {b['url']}")
        else:
            print("Keine anstehenden Buchungen")
        return

    if args.book:
        result = asyncio.run(book_class(args.book))
        if result is True:
            print(f"Kurs {args.book} gebucht")
        else:
            print(f"Buchung fehlgeschlagen: {result}")
        return

    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    classes = asyncio.run(scan_all_venues(target_date=target_date, venue_filter=args.venue))

    if args.json:
        print(json.dumps(classes, indent=2, ensure_ascii=False))
    else:
        if classes:
            print(f"\n{len(classes)} Kurse am {target_date}:\n")
            for cls in classes:
                print(f"  {cls['time']}  {cls['venue_name']:30s}  {cls['name']}")
                print(f"         {cls['url']}")
        else:
            print(f"Keine Kurse gefunden fuer {target_date}")


if __name__ == "__main__":
    main()
