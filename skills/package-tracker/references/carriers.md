# Supported Carriers

## Auto-Detected Carriers

The tracker auto-detects carriers from tracking number patterns:

| Carrier | Pattern | 17track Code | Tracking URL |
|---------|---------|-------------|-------------|
| CTT Portugal | `XX123456789PT` | 2151 | `ctt.pt/feapl_2/app/open/objectSearch/objectSearch.jspx?objects={tn}` |
| China Post | `XX123456789CN` | 3011 | Falls back to 17track |
| Royal Mail | `XX123456789GB` | 1051 | `royalmail.com/track-your-item#/tracking-results/{tn}` |
| La Poste | `XX123456789FR` | 1031 | `laposte.fr/outils/suivre-vos-envois?code={tn}` |
| Deutsche Post | `XX123456789DE` | 1011 | `deutschepost.de/de/s/sendungsverfolgung.html?piececode={tn}` |
| USPS | `94XXXXXXXXXXXXXXXXXX` (20-24 digits) | 100001 | `tools.usps.com/go/TrackConfirmAction?tLabels={tn}` |
| PostNL | `3SXXXXXXXXXXXXX` | 1071 | `jouw.postnl.nl/track-and-trace/{tn}` |
| UPS | `1ZXXXXXXXXXXXXXXXX` | 100002 | `ups.com/track?tracknum={tn}` |
| FedEx | 12-22 digit number | 100003 | `fedex.com/fedextrack/?trknbr={tn}` |
| DHL | 10-11 digit number | 100001 | `dhl.com/en/express/tracking.html?AWB={tn}` |

**Note:** `XX` = two uppercase letters, digits vary. Patterns are case-insensitive.

## Universal Fallback

For unrecognized carriers, 17track auto-detects and the fallback tracking URL is:
```
https://t.17track.net/en#nums={tracking_number}
```

## Adding New Carriers

To add a carrier, update `CARRIER_PATTERNS` and `TRACKING_URLS` in `tracker.py`:

1. Find the carrier's 17track code in their API docs
2. Add a regex pattern for the tracking number format
3. Add the carrier's tracking URL template with `{tn}` placeholder