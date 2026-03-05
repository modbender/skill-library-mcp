---
name: aigohotel-mcp
description: A Skill for searching hotels and querying prices via AIGoHotel MCP (searchHotels / getHotelDetail / getHotelSearchTags)
---

## AIGoHotel MCP Hotel Search Skill

This Skill describes how the model should use the `aigohotel-mcp` MCP server to search for hotels, view detailed prices for a specific hotel, and fetch available hotel tag metadata.

### When to use this Skill

- When the user wants to **find hotels in a specific place** (city, airport, attraction, station, detailed address, or a specific hotel), call **`searchHotels`**.
- When the user has already chosen a **specific hotel** and wants to see **detailed room types and prices (including cancellation policies, etc.)**, call **`getHotelDetail`**.
- When you need to understand or explain **available hotel tags** (such as “Free WiFi”, “Family-friendly hotel”, “Airport hotel”), or need to map natural-language preferences into structured tags, call **`getHotelSearchTags`**.

---

## Tool 1: searchHotels

**Purpose**: Search a list of hotels based on destination, dates, star rating, number of guests, budget, and tag filters.

**Key input fields (fill them based on the user’s intent as much as possible):**

- **Required**
  - `originQuery` (string): The user’s original natural-language query.
  - `place` (string): The place name (city / airport / attraction / train station / subway station / hotel / district / detailed address, etc.).
  - `placeType` (string): The type corresponding to `place`. Supported values: `城市` (city), `机场` (airport), `景点` (attraction), `火车站` (train station), `地铁站` (subway station), `酒店` (hotel), `区/县` (district/county), `详细地址` (detailed address).

- **Dates and length of stay**
  - `checkInDate` (string, `YYYY-MM-DD`): Parse from user utterances when possible; if omitted or earlier than today, the service automatically uses “tomorrow”.
  - `stayNights` (number): Set according to how many nights the user wants to stay; can be omitted if not specified (default is `1`).

- **Guests and country**
  - `adultCount` (number): Number of adults per room; use default `2` if not specified.
  - `countryCode` (string): Two-letter country code, e.g. `CN` for China, `US` for the United States.

- **Price and star rating**
  - `starRatings` (number[]): Star rating range. For example, if the user says “4 stars and above”, you can use `[4.0, 5.0]`.
  - `hotelTags.maxPricePerNight` (number): If the user says “no more than X per night”, set this field in `hotelTags` (currency in CNY).

- **Tags and brands (from user preferences or `getHotelSearchTags`)**
  - `hotelTags.preferredTags` (string[]): Tags the user **would like to have** (e.g. “Free WiFi”, “Premium hotel”, “Family-friendly hotel”).
  - `hotelTags.requiredTags` (string[]): Tags that are **must-have** conditions.
  - `hotelTags.excludedTags` (string[]): Tags that the user explicitly does **not** want.
  - `hotelTags.preferredBrands` (string[]): Preferred brands, such as “Hilton”, “Marriott”, “Home Inn”, etc.
  - `hotelTags.minRoomSize` (number): Minimum room size in square meters, if mentioned by the user.

- **Others**
  - `distanceInMeter` (number): When `place` is a POI, you can limit the straight-line distance; a typical value is `5000`.
  - `size` (number): Number of hotels to return. Default is `5`; generally should not exceed `10–20`.
  - `withHotelAmenities` (boolean): Set to `true` when you need to compare hotels by amenities (such as pool, gym, etc.).
  - `language` (string): Locale, e.g. `zh_CN` for Chinese, `en_US` for English.
  - `queryParsing` (boolean): Usually keep the default `true` to leverage server-side intent parsing.

**Output highlights (how to use the result):**

- Common top-level fields: `message`, `hotelInformationList`.
- Each hotel in `hotelInformationList` contains:
  - `hotelId`, `name`, `address`, `destinationId`, `latitude`, `longitude`, `distanceInMeters`,
  - `starRating`, `score`, `tags`, `hotelAmenities`,
  - `bookingUrl` (you can provide this as a booking link to the user),
  - `price` (**an object rather than a single number**):
    - `hasPrice`: Whether price is available.
    - `currency`: Currency code (usually `CNY`).
    - `lowestPrice`: The lowest available price under the current conditions.
- Some fields may be missing or `null`. Do **not** fabricate values that are not returned by the MCP tool.

---

## Tool 2: getHotelDetail

**Purpose**: After the user has chosen a specific hotel, get detailed room types, total prices, and cancellation policies for a given stay period.

**Typical call scenarios:**

- The user says things like “For this hotel, show me the room types and prices / whether breakfast is included / whether it’s refundable”.
- Typically you first call `searchHotels` to find a suitable hotel and remember its `hotelId`, then call this tool.

**Key input fields:**

- `hotelId` (number): Prefer using the `hotelId` returned from `searchHotels`.
- `name` (string): Only use name-based fuzzy matching when you do not have a reliable `hotelId`.
- `checkInDate` / `checkOutDate` (string, `YYYY-MM-DD`):
  - If empty, invalid, or earlier than today, the service will automatically adjust (e.g. use “tomorrow” and `+1` day).
- `adultCount` (number, default `2`), `childCount` (number, default `0`), `childAgeDetails` (number[]):
  - Set according to the actual number and ages of guests.
- `roomCount` (number, default `1`): Number of rooms.
- `countryCode` (string, default `CN`): Country code.
- `currency` (string, default `CNY`): Currency code.

**Output highlights:**

- On success, the response usually contains:
  - `success`, `errorMessage`, `hotelId`, `name`, `bookingUrl`, `checkIn`, `checkOut`,
  - `roomRatePlans`: A list of room types and rate plans.
- Common fields in `roomRatePlans`:
  - `roomTypeId`, `roomName`, `roomNameCn`, `ratePlanId`, `ratePlanName`,
  - `currency`, `totalPrice` (total price for this stay), `inventoryCount`, `isOnRequest`,
  - `cancellationPolicies`: Cancellation rules (time periods, amounts, descriptions, etc.).
- When responding to the user:
  - Focus on summarizing key information: main room types, price range, whether free cancellation is available, whether breakfast is included, etc.
  - You may provide `bookingUrl` (e.g. “You can complete the booking via this link.”).
- On failure, the tool may return an error message directly (e.g. “Failed to get prices, please try again later”). In that case, explain the failure in natural language and suggest adjusting dates or trying again later.

---

## Tool 3: getHotelSearchTags

**Purpose**: Fetch metadata for tags that can be used in `searchHotels.hotelTags`. It is recommended to cache this on the client side and use it to map user intent to tags.

**Output highlights:**

- `tags`: A list of tags, each including:
  - `name`: Tag name (for example “Free WiFi”).
  - `category`: Category (for example “Core Facilities”, “Hotel Type”, etc.).
  - `description`: Human-readable explanation.
- `usageGuide`:
  - `tagUsage`: How to use tag names in `hotelTags.preferredTags` / `requiredTags` / `excludedTags`.
  - `exampleRequest`: Example request JSON.

**Typical categories (non-exhaustive):**

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

When you need complex filtering with tags and are not sure about the exact tag names, you can first call `getHotelSearchTags`, then choose appropriate tags from `tags.name` to fill into `hotelTags`.

---

## General dialogue and safety constraints

- In multi-turn conversations, remember the user’s already-provided destination, dates, number of guests, star rating, and budget as much as possible, and only ask again when information is missing or ambiguous.
- Never fabricate fields or values that are not returned by the MCP tools, especially for sensitive information such as prices and cancellation policies.
- Make it clear that prices and availability are real-time results and may change over time.
- Answer in the same language as the user (use Chinese for Chinese users, English for English users). Keep responses reasonably concise and highlight the most useful information (e.g. 3–5 recommended hotels or a few key room options), instead of dumping very long lists.

---

## Local MCP configuration example (optional)

In development tools that support local MCP configuration (such as Cursor), you can add the following to `mcp.json` to mount AIGoHotel MCP as an available server (the name `aigohotel-mcp-server` is just an example and can be adjusted as needed):

{
  "mcpServers": {
    "aigohotel-mcp-server": {
      "url": "https://mcp.aigohotel.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_AIGOHOTEL_MCP_TOKEN>",
        "Content-Type": "application/json"
      }
    }
  }
}
