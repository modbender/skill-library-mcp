# Hotel Search Tags Prompt

Call the getHotelSearchTags tool when you need to get available filter tags for hotel search.

## Trigger Scenarios

- User wants to know what filter options are available
- You need to provide tag options for users to choose from
- You want to enhance search results with specific tags

## Parameters

No parameters needed, just call the tool directly.

## Call Example

```json
{}
```

## Output Structure Description

```json
{
  "tags": [
    {
      "name": "Free WiFi",
      "category": "Core Facilities",
      "description": "Provides free WiFi"
    },
    {
      "name": "Swimming Pool",
      "category": "Recreation",
      "description": "Has a swimming pool"
    },
    {
      "name": "Fitness Center",
      "category": "Recreation",
      "description": "Has a fitness center"
    },
    {
      "name": "Parking",
      "category": "Convenience",
      "description": "Provides parking facilities"
    },
    {
      "name": "Air Conditioning",
      "category": "Core Facilities",
      "description": "Has air conditioning"
    }
  ],
  "usageGuide": {
    "tagUsage": "Put tag names into hotelTags.preferredTags (preference), requiredTags (must-have) or excludedTags (exclude) lists",
    "exampleRequest": "{\"hotelTags\":{\"preferredTags\":[\"Free WiFi\",\"Swimming Pool\"]}}"
  }
}
```

## How to Use Tags

1. **preferredTags**: Tags that users prefer but are not mandatory
   - Example: `["Free WiFi", "Swimming Pool"]`

2. **requiredTags**: Tags that are mandatory for the search
   - Example: `["Free WiFi"]` (only hotels with free WiFi will be returned)

3. **excludedTags**: Tags that users do not want
   - Example: `["Smoking"]` (exclude smoking rooms)

## Example Usage in Search

User: "Find hotels with free WiFi and swimming pool in Shanghai"

```json
{
  "originQuery": "Find hotels with free WiFi and swimming pool in Shanghai",
  "place": "Shanghai",
  "placeType": "city",
  "hotelTags": {
    "preferredTags": ["Free WiFi", "Swimming Pool"]
  },
  "size": 5
}
```

## Notes

- Tags are case-sensitive, please use the exact names returned by the API
- Not all tags may be available for all locations
- Using too many requiredTags may limit search results
- It's recommended to use preferredTags for better search results
