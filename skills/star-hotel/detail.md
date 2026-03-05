# Hotel Detail Prompt

Call the getHotelDetail tool when the user wants to check room types and prices for a specific hotel.

## Trigger Scenarios

- User wants to view room types and prices for a specific hotel
- User asks about booking information for a hotel
- User inquires about room availability and pricing

## Parameter Extraction Rules

Extract the following parameters from user input:

| Parameter | Description | Required | Example |
|-----------|-------------|----------|---------|
| hotelId | Hotel ID, choose one with name, if both are provided, hotelId is preferred | No | 43615 |
| name | Hotel name (fuzzy matching), choose one with hotelId | No | "Youdi Movie Hotel" |
| checkInDate | Check-in date, format YYYY-MM-DD. If empty/invalid format/earlier than today, "tomorrow" is automatically used | No | 2026-02-26 |
| checkOutDate | Check-out date, format YYYY-MM-DD. If empty/invalid format/not later than check-in date, checkInDate + 1 day is automatically used | No | 2026-02-27 |
| adultCount | Number of adults per room, default 2 | No | 2 |
| childCount | Number of children per room, default 0 | No | 0 |
| childAgeDetails | Children's age list | No | [3, 5] |
| roomCount | Number of rooms, default 1 | No | 1 |
| countryCode | Country two-letter code, default CN | No | CN |
| currency | Currency, default CNY | No | CNY |

## Call Example

User: "Check room types and prices for Youdi Movie Hotel"

```json
{
  "name": "Youdi Movie Hotel",
  "checkInDate": "2026-02-26",
  "checkOutDate": "2026-02-27",
  "adultCount": 2,
  "roomCount": 1
}
```

User: "Check room availability for Beijing Tianlun Dynasty Hotel on March 5th"

```json
{
  "name": "Beijing Tianlun Dynasty Hotel",
  "checkInDate": "2026-03-05",
  "checkOutDate": "2026-03-06",
  "adultCount": 2,
  "roomCount": 1
}
```

## Output Structure Description

```json
{
  "success": true,
  "errorMessage": null,
  "hotelId": 43615,
  "bookingUrl": "Booking link",
  "name": "Beijing Tianlun Dynasty Hotel",
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
      "bedTypeDescription": "Unknown",
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

## Notes

- At least one of hotelId or name must be provided
- If both hotelId and name are provided, hotelId takes precedence
- Check-in date should be in YYYY-MM-DD format
- If check-in date is not provided, tomorrow's date is used by default
- If check-out date is not provided, check-in date + 1 day is used by default
