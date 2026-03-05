# ✈️ Cabin

**Search and book real flights with USDC.**

Cabin is an AI agent skill that connects to 500+ airlines via Amadeus and lets you search, compare, and book flights — paid in USDC on Base. No credit cards, no banks.

## What It Does

- **Search flights** — real-time availability from Amadeus GDS
- **Visual comparison** — rendered PNG images of search results
- **Book with USDC** — pay on Base, confirmed in seconds
- **Full lifecycle** — search → book → pay → confirm → check in

## Quick Start

### Search

```bash
curl -X POST https://api.cabin.team/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "from": "BKK",
    "to": "NRT",
    "date": "2026-04-01",
    "class": "ECONOMY"
  }'
```

Returns flight options with prices + a rendered comparison image.

### Book

```bash
curl -X POST https://api.cabin.team/v1/book \
  -H "Content-Type: application/json" \
  -d '{
    "offer_id": "offer_1",
    "search_id": "abc123",
    "passengers": [{
      "type": "adult",
      "given_name": "John",
      "family_name": "Doe",
      "email": "john@example.com",
      "born_on": "1990-01-15",
      "gender": "m"
    }]
  }'
```

Returns a booking reference and USDC payment details on Base.

### Pay

Send USDC to the deposit address on Base, or use the checkout URL. Booking confirms automatically after payment.

### Check Status

```bash
curl https://api.cabin.team/v1/booking/CBN-2026-XXXX
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/search` | POST | Search flights |
| `/v1/book` | POST | Create a booking |
| `/v1/booking/:id` | GET | Check booking status |
| `/v1/booking/:id/confirmation` | GET | Confirmation page |
| `/v1/booking/:id/checkin` | GET | Check-in page |

## Payment

- **Chain:** Base (Ethereum L2)
- **Token:** USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- **Gas:** ~$0.01
- **Confirmation:** ~2 seconds

## For AI Agents

See [`SKILL.md`](./SKILL.md) for the full agent skill definition — includes detailed parameters, response formats, workflow examples, and error handling. Drop it into any agent framework that supports skill files.

## Links

- **API:** [api.cabin.team](https://api.cabin.team)
- **Website:** [cabin.team](https://cabin.team)
- **GitHub:** [github.com/yolo-maxi/cabin](https://github.com/yolo-maxi/cabin)

---

Built by [YoloMaxi](https://github.com/yolo-maxi). Flights powered by Amadeus. Payments powered by Base.
