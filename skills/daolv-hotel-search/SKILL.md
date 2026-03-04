---
name: daolv-hotel-search
description: Hotel search and shortlist comparison using the ai-go-hotel MCP server (getHotelSearchTags, searchHotels). Use when users need fast hotel discovery by city/POI/date/budget/amenities/brand, but do not yet need full booking-room confirmation.
---

# Daolv Hotel Search

Focus on fast discovery and clean shortlist output.

## Workflow

1. Capture search intent
- Extract destination, check-in date, nights, guests, budget, star range, distance preference, amenities, brand preferences.
- Ask only minimal missing questions.

2. Prime tags once
- Call `ai-go-hotel.getHotelSearchTags` once per task.
- Map user intent into `hotelTags.requiredTags` / `preferredTags` / `excludedTags`.

3. Run hotel search
- Call `ai-go-hotel.searchHotels` with required fields:
  - `originQuery`, `place`, `placeType`
- Include optional fields when available:
  - `checkInDate`, `stayNights`, `adultCount`, `countryCode`, `starRatings`, `distanceInMeter`, `size`, `hotelTags`
- Prefer `size=10` first, then narrow to top 3-5.

4. Return shortlist only
- Output: 1 recommended + 2 alternatives.
- Include quick trade-off: price / location / amenities / star.
- Do not deep-dive room plans unless user asks to proceed to booking.

## Output Template

- **搜索条件**：地点 / 日期 / 人数 / 预算 / 偏好
- **首选酒店**：价格区间、位置、标签命中、推荐理由
- **备选 1-2**：同结构
- **下一步**：是否进入“房型与退改细节”阶段

## Quality Bar

- Use concrete numbers when available.
- Use `price.lowestPrice` + `price.currency` (price is object).
- If price missing/null, mark as “需二次查价”.
- Keep output concise and decision-oriented.

## MCP Preset Config

- Embedded preset: `references/mcp-client-config.json`
- Endpoint: `https://mcp.aigohotel.com/mcp` (`streamable_http` + prefilled Authorization header)
