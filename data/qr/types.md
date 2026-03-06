# QR Data Types

## URL (Most Common)
```
https://example.com/page
```
- Keep short — every character adds density
- Use URL shorteners for tracking + smaller codes
- HTTPS preferred (some readers warn on HTTP)

## WiFi Network
```
WIFI:T:WPA;S:NetworkName;P:password123;;
```
- T = security type: WPA, WEP, or nopass
- S = SSID (network name)
- P = password
- H = hidden network (optional): true/false
- Perfect for: guest networks, cafes, retail, events

## vCard (Contact)
```
BEGIN:VCARD
VERSION:3.0
N:Doe;John
FN:John Doe
TEL:+1234567890
EMAIL:john@example.com
END:VCARD
```
- Include only essential fields — more data = denser code
- Business cards, networking events
- Some phones add directly to contacts

## Email
```
mailto:hello@example.com?subject=Inquiry&body=Hello
```
- Pre-fill subject and body for specific contexts
- Support forms, feedback collection

## SMS
```
smsto:+1234567890:Your message here
```
- Pre-filled messages for opt-ins, keywords
- Marketing campaigns, support shortcuts

## Phone Call
```
tel:+1234567890
```
- Direct dial — good for support hotlines
- Include country code for international

## Geographic Location
```
geo:40.7128,-74.0060
```
- Opens in maps app
- Store locations, event venues, meeting points

## Calendar Event
```
BEGIN:VEVENT
SUMMARY:Team Meeting
DTSTART:20240115T100000
DTEND:20240115T110000
LOCATION:Room 101
END:VEVENT
```
- Adds event to calendar
- Conferences, appointments, recurring events

## Plain Text
```
Any text content here
```
- Simple messages, codes, reference numbers
- Not clickable — just displays text

## App Store Links
```
https://apps.apple.com/app/id123456789
https://play.google.com/store/apps/details?id=com.example.app
```
- Consider smart links that detect OS
- App download campaigns

## Payment (Emerging)
Various standards:
- **PIX (Brazil):** EMV format
- **UPI (India):** upi://pay?pa=...
- **Bitcoin:** bitcoin:address?amount=0.001
- Check regional standards for payment QRs
