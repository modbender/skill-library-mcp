# AIGoHotel MCP Server

`aigohotel-mcp` is an MCP (Model Context Protocol) hotel search service.
This document is updated against the latest live `aigohotel-mcp` tool behavior (verified on 2026-02-11).

## Tool List

The online MCP currently provides 3 tools:

1. `searchHotels`: search hotels by location, date, rating, guests, and tags
2. `getHotelDetail`: fetch real-time room-rate details for a selected hotel
3. `getHotelSearchTags`: fetch tag metadata for `searchHotels.hotelTags`

## 1) searchHotels

### Input Parameters

- `originQuery` (string, required): Original user query.
- `place` (string, required): Location name (city/airport/POI/address, etc.).
- `placeType` (string, required): Location type, supports `城市`, `机场`, `景点`, `火车站`, `地铁站`, `酒店`, `区/县`, `详细地址`.
- `queryParsing` (boolean, optional, default: `true`): Parse natural-language intent.
- `checkInDate` (string, optional, format `YYYY-MM-DD`): Check-in date. If omitted or earlier than today, auto-falls back to tomorrow.
- `stayNights` (number, optional, default: `1`): Number of nights.
- `adultCount` (number, optional, default: `2`): Adults per room.
- `countryCode` (string, optional): 2-letter country code (ISO 3166-1), e.g. `CN`, `US`.
- `distanceInMeter` (number, optional): POI distance in meters, default `5000` for POI scenarios.
- `starRatings` (number[], optional): Star range. Default `[0.0, 5.0]`, step `0.5`.
- `size` (number, optional, default: `5`): Number of hotels to return, max `20`.
- `withHotelAmenities` (boolean, optional): Include hotel amenities.
- `language` (string, optional, default: `zh_CN`): Locale, e.g. `zh_CN`, `en_US`.
- `hotelTags` (object, optional): Tag/brand/budget filter object.

`hotelTags` sub-fields:

- `preferredTags` (string[], optional): Preferred tags.
- `requiredTags` (string[], optional): Must-have tags (hard constraint).
- `excludedTags` (string[], optional): Excluded tags.
- `preferredBrands` (string[], optional): Preferred brands.
- `maxPricePerNight` (number, optional): Max nightly budget (CNY).
- `minRoomSize` (number, optional): Minimum room size in square meters.

### Output Structure

```json
{
  "message": "酒店搜索成功",
  "hotelInformationList": [
    {
      "hotelId": 43615,
      "bookingUrl": "https://rollinggo.cn/pages/hotel/detail/index?...",
      "name": "北京天伦王朝酒店(Sunworld Dynasty Hotel Beijing)",
      "brand": null,
      "address": "王府井大街50号",
      "destinationId": "6140156",
      "latitude": 39.917748,
      "longitude": 116.412249,
      "distanceInMeters": 205,
      "starRating": 5.0,
      "price": {
        "message": "查价成功,最低价:626.0, 币种:CNY",
        "hasPrice": true,
        "currency": "CNY",
        "lowestPrice": 626.0
      },
      "areaCode": "CN",
      "description": "...",
      "imageUrl": "https://image-cdn.aigohotel.com/...",
      "hotelAmenities": ["24小时前台", "WIFI"],
      "score": 1.0,
      "tags": ["临近商场", "免费WiFi"]
    }
  ]
}
```

Notes:

- `price` is now an object, not a number.
- Some fields may be missing or `null` depending on supplier coverage.

## 2) getHotelDetail

### Input Parameters

- `hotelId` (number, optional): Hotel ID. Use either `hotelId` or `name`; if both exist, `hotelId` wins.
- `name` (string, optional): Hotel name (fuzzy match).
- `checkInDate` (string, optional, format `YYYY-MM-DD`): Check-in date. Empty/invalid/past values fallback to tomorrow.
- `checkOutDate` (string, optional, format `YYYY-MM-DD`): Check-out date. Empty/invalid/non-later values fallback to `checkInDate + 1 day`.
- `adultCount` (number, optional, default: `2`): Adults per room.
- `childCount` (number, optional, default: `0`): Children per room.
- `childAgeDetails` (number[], optional): Child ages, e.g. `[3, 5]`.
- `roomCount` (number, optional, default: `1`): Room count.
- `countryCode` (string, optional, default: `CN`): 2-letter country code.
- `currency` (string, optional, default: `CNY`): Currency.

### Output Structure

```json
{
  "success": true,
  "errorMessage": null,
  "hotelId": 43615,
  "bookingUrl": "https://rollinggo.cn/pages/hotel/detail/index?...",
  "name": "北京天伦王朝酒店(Sunworld Dynasty Hotel Beijing)",
  "checkIn": "2026-03-05",
  "checkOut": "2026-03-06",
  "roomRatePlans": [
    {
      "roomTypeId": 4984714,
      "roomName": "Superior Room",
      "roomNameCn": "高级客房",
      "ratePlanId": "7012072001634754626",
      "ratePlanName": "Superior Room King Bed , 1 King Bed",
      "bedType": 73,
      "bedTypeDescription": "未知",
      "currency": "CNY",
      "totalPrice": 0,
      "totalSalesRate": null,
      "inventoryCount": null,
      "isOnRequest": null,
      "recommendIndex": null,
      "cancellationPolicies": [
        {
          "fromDate": "2026-03-02T10:00:00+08:00",
          "toDate": null,
          "amount": 634,
          "percent": null,
          "type": null,
          "description": null
        }
      ],
      "includedFees": null,
      "excludedFees": null,
      "metadata": null
    }
  ]
}
```

Notes:

- On failure, the tool may return plain error text (for example, "获取价格失败，请稍后重试") instead of a structured object.
- `roomRatePlans` can be very large; clients should limit rendered rows.

## 3) getHotelSearchTags

Fetches available tags for `searchHotels.hotelTags`. Recommended for local cache and client-side intent mapping.

### Output Structure

```json
{
  "tags": [
    {
      "name": "免费WiFi",
      "category": "核心设施",
      "description": "提供免费WiFi"
    }
  ],
  "usageGuide": {
    "tagUsage": "Put tag names into hotelTags.preferredTags / requiredTags / excludedTags",
    "exampleRequest": "{...}"
  }
}
```

Common categories include:

- Brand & Rating
- Selling Points
- Core Facilities
- Family & Kids
- Service Details
- Dining & Service
- Transport & Payment
- View & Room Type
- Hotel Type
- Price Related

## Usage Examples

### Example 1: City search

```json
{
  "originQuery": "Find 4-star+ hotels in Beijing for 2 nights",
  "place": "北京",
  "placeType": "城市",
  "checkInDate": "2026-03-01",
  "stayNights": 2,
  "starRatings": [4.0, 5.0],
  "size": 5
}
```

### Example 2: Tags + budget constraints

```json
{
  "originQuery": "Find quality hotels in Beijing with free WiFi and under CNY 1000 per night",
  "place": "北京",
  "placeType": "城市",
  "hotelTags": {
    "preferredTags": ["免费WiFi", "品质酒店"],
    "maxPricePerNight": 1000
  },
  "size": 5
}
```

### Example 3: Room-rate detail query

```json
{
  "hotelId": 43615,
  "checkInDate": "2026-03-05",
  "checkOutDate": "2026-03-06",
  "adultCount": 2,
  "roomCount": 1,
  "currency": "CNY",
  "countryCode": "CN"
}
```

## Deployment & Run

### 1. Get source code

```bash
git clone https://github.com/longcreat/aigohotel-mcp.git
cd aigohotel-mcp
```

### 2. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Start server

```bash
python server.py
```

Default MCP endpoint: `http://127.0.0.1:8000/mcp`

### 4. Pass API key via MCP client headers

The server does not read API keys from `.env`. Send API key in request headers:

- Recommended: `Authorization: Bearer YOUR_API_KEY`
- Compatible: `X-Secret-Key: YOUR_API_KEY`

## MCP Client Config Example

```json
{
  "mcpServers": {
    "aigohotel-mcp": {
      "url": "http://localhost:8000/mcp",
      "type": "http",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

## Links

- API key application: https://mcp.agentichotel.cn/apply
- MCP standard: https://modelcontextprotocol.io/
