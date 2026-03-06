---
name: apple-serial-lookup
description: Look up Apple device information from a serial number. Supports iPhones, iPads, Macs (MacBook, iMac, Mac mini, Mac Pro, Mac Studio), Apple Watch, Apple TV, and iPods. Use when a user provides an Apple serial number and wants to identify the device, check specs, manufacturing date/location, warranty status, or get detailed model information.
---

# Apple Serial Lookup

Identify any Apple device from its serial number by combining local decoding with web lookups.

## Workflow

### 1. Decode locally (old 11-12 char format)

Run the bundled decoder script:

```bash
python3 scripts/decode_serial.py <SERIAL>
```

This extracts:
- Manufacturing location and date
- Model codes and configuration identifiers
- **Model identifier** (e.g., MacBookPro10,1, iPhone9,1) when known
- **Basic specs** (RAM, storage options) from built-in database

The script includes a database of common model codes compiled from repair sources and EveryMac.

### 2. Web lookup for complete specs and unknown models

For full specifications or unknown model codes, perform web lookup:

- **Primary:** `web_search` for `"Apple serial number <SERIAL> specs"` or `"<SERIAL> site:everymac.com"`
- **Fallback:** `web_fetch` from `https://everymac.com/ultimate-mac-lookup/?search_keywords=<SERIAL>`

If EveryMac is blocked by captcha, try:
- `https://appleserialnumberinfo.com/Desktop/index.php?sn=<SERIAL>` (may need browser)
- Search for the model code (e.g., "Apple DKQ model identifier") to match to a specific device

For **new-format (post-2021) serials**, web search won't help — direct the user to check Apple's coverage page themselves:
- **Apple Check Coverage:** `https://checkcoverage.apple.com/` (requires captcha, but returns device model + warranty status)
- This is the only reliable source for randomized 10-character serials
- Apple switched to randomized serials starting in **late 2020/early 2021** (beginning with iPhone 12 and M1 Macs), fully rolled out across all products by 2021

### 3. Present results

Combine local decode + web data into a comprehensive summary:

**Enhanced Output (from local decode):**
- **Device:** Model name and identifier (e.g., MacBook Pro 15" Mid-2012, MacBookPro10,1)
- **Serial:** Full serial number
- **Manufactured:** Location, week, year (e.g., ~Week 38, Sep 2012, Quanta Shanghai)
- **Specs:** RAM and storage options from built-in database
- **Model Codes:** Last 4 characters with decode attempt

**Web Enhancement (when needed):**
- Exact processor specifications
- Complete technical specifications
- Warranty status (Apple Check Coverage)
- Current market value

## Reference

- **Serial format & encoding:** [references/serial-format.md](references/serial-format.md)
- **Model code database:** [references/model-codes.md](references/model-codes.md) - mappings from model codes to device specs and model identifiers

The model code database is continuously expandable as new mappings are discovered.

## Notes

- Old format (12 chars): decodable locally for location/date, web needed for exact model
- New format (10-14 chars, 2021+): fully randomized, web lookup is the only option
- IMEI numbers (15 digits) are NOT serial numbers — note this if a user provides one
- The script outputs JSON for easy parsing
