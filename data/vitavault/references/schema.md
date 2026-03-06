# VitaVault Export Schema (v2.0)

## JSON Export Structure

```json
{
  "exportDate": "2026-02-19T12:30:00Z",
  "schemaVersion": "2.0",
  "deviceInfo": { "model": "iPhone 16 Pro", "os": "iOS 19.3" },
  "recordCount": 14523,
  "records": [ ...HealthRecord objects... ]
}
```

## HealthRecord

```json
{
  "id": "UUID-string",
  "schemaVersion": "2.0",
  "type": "heartRate",
  "value": 72.0,
  "categoryValue": null,
  "unit": "count/min",
  "startDate": "2026-02-19T08:30:00Z",
  "endDate": "2026-02-19T08:30:00Z",
  "timezoneOffsetMinutes": -360,
  "sourceName": "Apple Watch",
  "sourceBundle": "com.apple.health.8FA19FF3",
  "sourceVersion": "11.3",
  "sourceProductType": "Watch7,3",
  "deviceName": "Apple Watch",
  "deviceManufacturer": "Apple Inc.",
  "deviceModel": "Watch",
  "deviceSoftwareVersion": "11.3",
  "metadata": {
    "HKMetadataKeyHeartRateMotionContext": 0
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique record UUID from HealthKit |
| schemaVersion | string | Always "2.0" |
| type | string | One of 48 HealthDataType values |
| value | number/null | Numeric value (null for category types) |
| categoryValue | string/null | Category value (sleep stages, etc.) |
| unit | string | HealthKit unit string |
| startDate | string | ISO 8601 UTC |
| endDate | string | ISO 8601 UTC |
| timezoneOffsetMinutes | int | Local TZ offset at sample time |
| sourceName | string | Data source (Apple Watch, iPhone, etc.) |
| sourceBundle | string/null | Bundle ID of source app |
| metadata | object/null | Optional HealthKit metadata |

### Category Types

Sleep (`sleepAnalysis`) uses `categoryValue` instead of `value`:
- `InBed` - Time in bed
- `Asleep` - Generic asleep (older records)
- `AsleepCore` - Core/light sleep
- `AsleepDeep` - Deep sleep
- `AsleepREM` - REM sleep
- `Awake` - Awake during sleep session

### MetadataValue

Metadata values can be: string, number (double), date (ISO 8601 string), or boolean.

## CSV Export Structure

```csv
id,schemaVersion,type,value,categoryValue,unit,startDate,endDate,timezoneOffsetMinutes,sourceName,sourceBundle
abc-123,2.0,heartRate,72.0,,count/min,2026-02-19T08:30:00Z,2026-02-19T08:30:00Z,-360,Apple Watch,com.apple.health.8FA19FF3
```

Same fields as JSON, flattened. Metadata is omitted in CSV exports.
