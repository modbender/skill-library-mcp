---
name: daolv-hotel-booking
description: Hotel discovery, shortlist comparison, and booking handoff using the ai-go-hotel MCP server (getHotelSearchTags, searchHotels, getHotelDetail). Use when users ask to find hotels, compare options by budget/location/amenities, plan city stays, family or business lodging, or complete hotel booking decisions with clear next actions.
---

# Daolv Hotel Booking

Provide reliable hotel planning and booking support with structured MCP calls and decision-ready outputs.

## Workflow

1. Capture booking intent before calling tools
- Extract: destination, check-in date, nights, adults/children, room count, budget, purpose (business/family/leisure), required amenities, preferred/avoided brands.
- If key constraints are missing, ask only the minimum follow-up questions.

2. Prime tags once per task
- Call `ai-go-hotel.getHotelSearchTags` once.
- Cache returned tags for the rest of the conversation.
- Use those tags to build `hotelTags.requiredTags`, `preferredTags`, `excludedTags`, and optional budget constraints.

3. Search hotels with normalized parameters
- Call `ai-go-hotel.searchHotels` with:
  - `place`
  - `placeType`
  - `originQuery`
  - optional `checkInDate`, `stayNights`, `adultCount`, `size`, `starRatings`, `hotelTags`, `countryCode`, `distanceInMeter`, `withHotelAmenities`, `language`
- Prefer `size=8-12` for first pass; narrow to top 3-5 in final output.
- Respect live schema behavior:
  - `checkInDate` invalid/past/empty may fallback to tomorrow
  - `price` is an object (use `price.lowestPrice` + `price.currency`)
  - some fields can be null or missing
- `placeType` can be normalized from user language:
  - 城市/city → 城市
  - 机场/airport → 机场
  - 景点/attraction → 景点
  - 火车站/railway station → 火车站
  - 地铁站/metro → 地铁站
  - 酒店/hotel → 酒店

4. Enrich finalists with room-level details
- For each shortlisted option, call `ai-go-hotel.getHotelDetail` (prefer `hotelId` when available).
- Pass dates with `checkInDate` / `checkOutDate` format `YYYY-MM-DD`.
- Handle fallback and edge behavior:
  - invalid/empty dates may auto-correct
  - failures may return plain text (not structured JSON)
  - `roomRatePlans` can be very large; render only top rows by relevance/price
- Extract actionable room/price data, cancellation policy, breakfast inclusion, and important constraints.

5. Return decision-ready output
- Always provide:
  - Recommended option (best fit)
  - Two alternatives
  - Why each matches constraints
  - Trade-offs (price vs distance vs amenities)
  - Booking handoff steps (what user should confirm next)

## Output Template

Use concise bullet format:

- **行程信息**: 目的地 / 日期 / 人数 / 预算 / 关键偏好
- **推荐酒店（首选）**
  - 酒店名
  - 预估价格（每晚 & 总价）
  - 位置与交通
  - 房型亮点
  - 取消与早餐政策
  - 推荐理由
- **备选 1 / 备选 2**（同结构）
- **决策建议**: 适合人群与风险提示
- **下一步确认**: 仅列 2-4 个必要确认项

## Quality Bar

- Prefer concrete numbers over vague wording.
- Do not invent unavailable policies/prices.
- If data is missing or stale, say so explicitly and suggest a refresh query.
- Keep choices constrained: no long dump lists.
- Avoid credential exposure or config leakage.

## MCP Preset Config

- Embedded MCP preset is included at:
  - `references/mcp-client-config.json`
- It targets `https://mcp.aigohotel.com/mcp` using `streamable_http` and prefilled Authorization header.

## Platform Distribution

When user asks to publish/distribute this skill, follow the checklist in:
- `references/distribution.md`
- `references/promo-copy.md`
