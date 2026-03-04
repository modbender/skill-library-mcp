# Hotel Search Prompt

Call the searchHotels tool when the user expresses hotel search intent.

## Trigger Scenarios

- User wants to find hotels
- User mentions location + accommodation needs
- User asks for hotel recommendations in a certain place

## Parameter Extraction Rules

Extract the following structured parameters from user input:

| Parameter | Description | Required | Example |
|-----------|-------------|----------|---------|
| originQuery | User's original query (sensitive information filtered) | Yes | "Find 3-star hotels in Zhengzhou" |
| place | Location name, as detailed as possible (city/airport/scenic spot/detailed address, etc.) | Yes | Zhengzhou, Miaoli Commercial Center, Ocean Park |
| placeType | Location type | Yes | city/airport/scenic spot/railway station/subway station/hotel/district/county/detailed address |
| queryParsing | Whether to parse user's natural language preferences, default true | No | true |
| checkInDate | Check-in date, format YYYY-MM-DD. If not provided or earlier than today, "tomorrow" is automatically used | No | 2026-02-26 |
| stayNights | Number of nights, default 1 | No | 1 |
| adultCount | Number of adults per room, default 2 | No | 2 |
| countryCode | Country two-letter code (ISO 3166-1) | No | CN |
| distanceInMeter | Straight-line distance from POI (meters), default 5000 for POI scenarios | No | 5000 |
| starRatings | Star rating range, default [0.0, 5.0], step 0.5 | No | [3.0] |
| size | Number of hotels to return, default 5, maximum 20 | No | 5 |
| withHotelAmenities | Whether to include hotel amenities information | No | true |
| language | Language environment, default zh_CN | No | zh_CN |
| hotelTags | Tag/brand/budget filtering | No | See below for details |

## hotelTags Sub-fields

| Field | Description |
|-------|-------------|
| preferredTags | Preferred tags (string[]) |
| requiredTags | Must-have tags (strong constraint, string[]) |
| excludedTags | Excluded tags (string[]) |
| preferredBrands | Preferred brands (string[]) |
| maxPricePerNight | Maximum price per night (CNY, number) |
| minRoomSize | Minimum room size (square meters, number) |

## originQuery Processing Requirements

**Important**: originQuery needs to be processed:

1. Extract search intent from user input
2. **Remove any personal identification information** (name, phone number, email, ID card, etc.)
3. Retain search-related information such as location, date, and conditions

Example:
- User input: "My name is Zhang San, I want to book a 5-star hotel in Beijing"
- originQuery should be: "5-star hotel in Beijing" (remove name)

## Call Example

User: "Help me find hotels near Shanghai Bund, check-in on March 1st for 2 nights, budget under 1000"

```json
{
  "originQuery": "Help me find hotels near Shanghai Bund, check-in on March 1st for 2 nights, budget under 1000",
  "place": "Bund",
  "placeType": "scenic spot",
  "checkInDate": "2026-03-01",
  "stayNights": 2,
  "hotelTags": {
    "maxPricePerNight": 1000
  },
  "size": 5
}
```

User: "Find 3-star hotels in Zhengzhou, check-in on February 26th, budget under 200 yuan"

```json
{
  "originQuery": "Find 3-star hotels in Zhengzhou, check-in on February 26th, budget under 200 yuan",
  "place": "Zhengzhou",
  "placeType": "city",
  "checkInDate": "2026-02-26",
  "stayNights": 1,
  "starRatings": [3.0],
  "hotelTags": {
    "maxPricePerNight": 200
  },
  "size": 5
}
```

## Output Structure Description

```json
{
  "message": "Hotel search successful",
  "hotelInformationList": [
    {
      "hotelId": 43615,
      "bookingUrl": "Booking link",
      "name": "Hotel name",
      "brand": "Brand",
      "address": "Hotel location",
      "starRating": 5.0,
      "price": {
        "message": "Price check successful, lowest price: 626.0, currency: CNY",
        "hasPrice": true,
        "currency": "CNY",
        "lowestPrice": 626.0
      },
      "hotelAmenities": ["24-hour front desk", "WIFI"],
      "tags": ["Near shopping mall", "Free WiFi"]
    }
  ]
}
```

Note: price is an object, not a number.
