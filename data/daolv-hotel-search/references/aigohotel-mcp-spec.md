# AIGoHotel MCP Live Spec (2026-02-11)

Source snapshot provided by user.

## Tools

1. `searchHotels`
2. `getHotelDetail`
3. `getHotelSearchTags`

## Key Compatibility Notes

- `searchHotels.price` is an object (not a scalar number).
  - Prefer: `price.lowestPrice`, `price.currency`, `price.hasPrice`.
- `searchHotels` may return nullable or missing fields by supplier.
- `getHotelDetail` may fail with plain text error (e.g. “获取价格失败，请稍后重试”).
- `roomRatePlans` can be large; clients should cap displayed rows.
- Date defaults/fallbacks are server-side tolerant:
  - `checkInDate` invalid/past/empty → tomorrow
  - `checkOutDate` invalid/non-later → `checkInDate + 1 day`

## searchHotels required fields

- `originQuery` (string)
- `place` (string)
- `placeType` (string)

`placeType` supports:
- 城市, 机场, 景点, 火车站, 地铁站, 酒店, 区/县, 详细地址

## searchHotels optional highlights

- `queryParsing` (default true)
- `checkInDate` (`YYYY-MM-DD`)
- `stayNights` (default 1)
- `adultCount` (default 2)
- `countryCode` (ISO 3166-1 alpha-2)
- `distanceInMeter` (POI scenario)
- `starRatings` (default `[0.0,5.0]`, step 0.5)
- `size` (default 5, max 20)
- `withHotelAmenities`
- `language` (default `zh_CN`)
- `hotelTags`
  - `preferredTags`
  - `requiredTags`
  - `excludedTags`
  - `preferredBrands`
  - `maxPricePerNight`
  - `minRoomSize`

## getHotelDetail input highlights

- one of: `hotelId` or `name` (hotelId wins)
- `checkInDate`, `checkOutDate`
- `adultCount`, `childCount`, `childAgeDetails`
- `roomCount`
- `countryCode` (default CN)
- `currency` (default CNY)

## getHotelSearchTags output use

- fetch once and cache per task
- map intent to:
  - `hotelTags.preferredTags`
  - `hotelTags.requiredTags`
  - `hotelTags.excludedTags`

## Embedded Client Preset

- See `references/mcp-client-config.json` for the prefilled server config and Authorization header.

## Links

- Source repo: https://github.com/longcreat/aigohotel-mcp
- API key apply: https://mcp.agentichotel.cn/apply
- MCP spec: https://modelcontextprotocol.io/
