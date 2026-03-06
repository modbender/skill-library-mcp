# Apple Serial Number Formats

## Old Format (11-12 characters, pre-2021)

Applies to all Apple hardware: Macs, iPhones, iPads, iPods, Apple Watch, Apple TV.

Structure (12-char): `PPP Y W D III MMMM`

| Position | Length | Meaning |
|----------|--------|---------|
| 1-3 | 1-3 | Manufacturing location code |
| 4 | 1 | Year + half of manufacture |
| 5 | 1 | Week within the half-year |
| 6 | 1 | Day/production refinement |
| 7-8 | 2-3 | Unique device identifier |
| 9-12 | 4 | Model: chars 9-11 = model+color, char 12 = config/storage |

### Manufacturing Location Codes (position 1-3)

Sources: Beetstech, Techable, Apple Community, MacRumors

| Code | Location |
|------|----------|
| FC | Fountain Colorado, USA |
| F | Fremont, California, USA |
| XA, XB, QP, G8 | USA |
| RN | Mexico |
| GQ | Foxconn, Brazil |
| CK | Cork, Ireland |
| VM | Foxconn, Pardubice, Czech Republic |
| SG, E | Singapore |
| MB | Malaysia |
| PT, CY | Korea |
| EE, QT, UV | Taiwan |
| FK, F1, F2 | Foxconn, Zhengzhou, China |
| F7, 1C, 4H, WQ | China |
| W8 | Shanghai, China |
| DL, DM | Foxconn, China |
| DN | Foxconn, Chengdu, China |
| DX | Foxconn, Zhengzhou, China |
| YM, 7J | Hon Hai/Foxconn, China |
| C0, C02, C07, C17 | Tech Com/Quanta, China |
| C3 | Foxconn, Shenzhen, China |
| C6, C6K | Foxconn, Zhengzhou, China |
| C7 | Pentragon, Shanghai, China |
| G0 | Pegatron, Shanghai, China |
| G6 | Foxconn, Shenzhen, China |
| J2 | Pegatron, Shanghai, China |
| H0, HN | Foxconn, India |
| RM | Refurbished/Remanufactured |

### Year Codes (position 4)

Each letter represents one half-year. Letters A, B, E, I, O, U are skipped.

| Code | Period | Code | Period |
|------|--------|------|--------|
| C | 2010 H1 | D | 2010 H2 |
| F | 2011 H1 | G | 2011 H2 |
| H | 2012 H1 | J | 2012 H2 |
| K | 2013 H1 | L | 2013 H2 |
| M | 2014 H1 | N | 2014 H2 |
| P | 2015 H1 | Q | 2015 H2 |
| R | 2016 H1 | S | 2016 H2 |
| T | 2017 H1 | V | 2017 H2 |
| W | 2018 H1 | X | 2018 H2 |
| Y | 2019 H1 | Z | 2019 H2 |

### Week Codes (position 5)

Represents week within the half-year (1-27). For H2 devices, add 26 to get actual week of year.
Letters A, B, E, I, O, S, U are skipped.

| Code | Week | Code | Week | Code | Week |
|------|------|------|------|------|------|
| 1 | 1 | C | 10 | P | 20 |
| 2 | 2 | D | 11 | Q | 21 |
| 3 | 3 | F | 12 | R | 22 |
| 4 | 4 | G | 13 | T | 23 |
| 5 | 5 | H | 14 | V | 24 |
| 6 | 6 | J | 15 | W | 25 |
| 7 | 7 | K | 16 | X | 26 |
| 8 | 8 | L | 17 | Y | 27 |
| 9 | 9 | M | 18 | | |
| | | N | 19 | | |

### iPhone-Specific (last 4 characters)

For iPhones, the last 4 digits encode additional info:
- Characters 9-11: model + color
- Character 12: storage capacity

These codes are model-specific and not fully publicly documented. Use web lookup for exact mapping.

## New Format (randomized, 2021+)

Starting in 2021, Apple switched to randomized serial numbers (typically 10 characters). These have NO decodable structure — web lookup is the only option.

## Identifying the Format

- **11-12 characters, 4th char is a letter C-Z** → Old format (decodable)
- **10 characters** → New randomized format (2021+)
- **15 digits** → IMEI, not a serial number

## Useful Lookup URLs

- EveryMac (Macs): `https://everymac.com/ultimate-mac-lookup/?search_keywords=SERIAL`
- Apple Coverage: `https://checkcoverage.apple.com/`
- Beetstech: `https://beetstech.com/apple-device-lookup`
- IMEI.info: `https://www.imei.info/apple-sn-check/?sn=SERIAL`
