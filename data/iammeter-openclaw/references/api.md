# IAMMETER API Reference

Based on https://www.iammeter.com/swaggerui/swagger.json

## Authentication

**POST /api/v1/user/login**
- Body: `{ userName, password }`
- Response: `{ data: { id, token, refreshToken }, successful, message }`
- Note: You can also obtain the token directly from the IAMMETER web console and
  pass it via the request header `token: YOUR_TOKEN`.

All read endpoints require the header: `token: YOUR_TOKEN`

---

## Endpoints

### 1. List Sites
```
GET /api/v1/user/sitelist
```
- Response: `{ data: [ { id, name, meters: [ { name, sn }, ... ] } ], successful, message }`
- Use this to retrieve place (site) IDs and meter serial numbers (SN).

---

### 2. Latest Data for All Meters
```
GET /api/v1/site/metersdata
```
- Response: `{ data: [ { sn, values, gmtTime }, ... ], successful, message }`
- Rate limit: **1 request / 5 minutes**
- `values` — see [Data Array Fields](#data-array-fields) below.

---

### 3. Latest Data for a Single Meter
```
GET /api/v1/site/meterdata/{sn}
GET /api/v1/site/meterdata2/{sn}
```
- Path param: `sn` — meter serial number
- Response: `{ data: { values: [ [...], ... ], localTime, gmtTime }, successful, message }`
- Rate limit: **12 requests / hour** per meter
- `values[N]` — see [Data Array Fields](#data-array-fields) below.

---

### 4. Energy History
```
GET /api/v1/site/energyhistory/{id}
```
- Path param: `id` — place (site) ID
- Query params: `startTime` (YYYY-MM-DD), `endTime` (YYYY-MM-DD), `groupby` = `hour` | `day` | `month` | `year`
- Response: `{ data: [ { time, yield, fromGrid, toGrid, specialLoad, selfUse }, ... ], successful, message }`
- Limits: hourly data max 7 days; daily data max 90 days.

---

### 5. Power Analysis
```
GET /api/v1/site/poweranalysis?sn=&startTime=&endTime=
```
- Rate limit: **5 requests / day**

---

### 6. Offline Analysis
```
GET /api/v1/site/offlineanalysis?sn=&startTime=&endTime=&interval=
```
- `interval`: sampling interval in minutes (default 5)
- Rate limit: **5 requests / day**

---

## Data Array Fields

Both `metersdata` and `meterdata` return a `values` array (or array of arrays).
Each row is an array where the fields are positional:

| Index | Field          | Unit |
|-------|----------------|------|
| 0     | Voltage        | V    |
| 1     | Current        | A    |
| 2     | Power          | W    |
| 3     | Forward energy | kWh  |
| 4     | Reverse energy | kWh  |
| 5+    | Additional fields (vary by device / firmware) | — |

Example row: `[230.1, 5.2, 1196.5, 320.44, 12.01, ...]`

---

## Error Handling

| HTTP Status | Meaning                      | Action                            |
|-------------|------------------------------|-----------------------------------|
| 401         | Invalid or expired token     | Refresh token in IAMMETER console |
| 429         | Rate limit exceeded          | Exponential back-off and retry    |
| 5xx         | Server error                 | Retry with back-off               |

---

## Response Example (meterdata)

```json
{
  "data": {
    "values": [[230.1, 5.2, 1196.5, 320.44, 12.01]],
    "localTime": "2026/2/25 19:00:00",
    "gmtTime": "2026/2/25 11:00:00"
  },
  "successful": true,
  "message": null
}
```

> For full field definitions refer to the official Swagger spec:
> https://www.iammeter.com/swaggerui/swagger.json