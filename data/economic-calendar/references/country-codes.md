# Country Codes Reference

## Major Economies

| Code | Country/Region | Currency | Importance |
|------|----------------|----------|------------|
| `us` | United States | USD | Primary |
| `eu` | Euro Zone | EUR | Primary |
| `de` | Germany | EUR | Secondary |
| `gb` | United Kingdom | GBP | Secondary |
| `jp` | Japan | JPY | Secondary |
| `cn` | China | CNY | Secondary |
| `ca` | Canada | CAD | Secondary |
| `au` | Australia | AUD | Secondary |
| `ch` | Switzerland | CHF | Tertiary |

## Secondary Markets

| Code | Country | Currency |
|------|---------|----------|
| `fr` | France | EUR |
| `it` | Italy | EUR |
| `es` | Spain | EUR |
| `nl` | Netherlands | EUR |
| `nz` | New Zealand | NZD |
| `se` | Sweden | SEK |
| `no` | Norway | NOK |
| `dk` | Denmark | DKK |

## Emerging Markets

| Code | Country | Currency |
|------|---------|----------|
| `br` | Brazil | BRL |
| `in` | India | INR |
| `mx` | Mexico | MXN |
| `za` | South Africa | ZAR |
| `ru` | Russia | RUB |
| `kr` | South Korea | KRW |

## Usage in Skill

```bash
# Major economies only
--country us,eu,de,gb

# G10 currencies
--country us,eu,jp,gb,ch,ca,au,nz,se,no

# All tracked
--country us,eu,de,gb,jp,cn,ca,au,ch,fr,it
```
