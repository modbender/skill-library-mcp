# Tempest Observation Field Reference

Complete mapping of Tempest REST API observation fields for the `obs_st` (Tempest device) response type.

---

## Station Observation Response Structure

The REST endpoint `GET /observations/station/{id}` returns:

```json
{
  "station_id": 12345,
  "station_name": "My Station",
  "public_name": "My Station",
  "latitude": 37.123,
  "longitude": -122.456,
  "timezone": "America/Los_Angeles",
  "elevation": 52.0,
  "is_public": false,
  "status": { "status_code": 0, "status_message": "SUCCESS" },
  "obs": [
    {
      "timestamp": 1705329120,
      "wind_lull": 0.9,
      "wind_avg": 2.3,
      "wind_gust": 4.1,
      "wind_direction": 245,
      "wind_sample_interval": 6,
      "station_pressure": 1013.4,
      "sea_level_pressure": 1016.2,
      "pressure_trend": "steady",
      "air_temperature": 18.5,
      "relative_humidity": 62,
      "uv": 3,
      "solar_radiation": 412,
      "illuminance": 28500,
      "lightning_strike_last_epoch": null,
      "lightning_strike_last_distance": null,
      "lightning_strike_count": 0,
      "lightning_strike_count_last_1hr": 0,
      "lightning_strike_count_last_3hr": 0,
      "feels_like": 16.2,
      "heat_index": 17.1,
      "wind_chill": 16.2,
      "dew_point": 11.3,
      "wet_bulb_temperature": 14.1,
      "delta_t": 4.4,
      "air_density": 1.214,
      "precip_accum_last_1hr": 0.0,
      "precip_accum_local_day": 2.4,
      "precip_accum_local_yesterday": 0.0,
      "precip_minutes_local_day": 0,
      "precip_type": 0,
      "precip_analysis_type_filtered": 1,
      "battery": 2.42,
      "report_interval": 1
    }
  ]
}
```

---

## Key Field Descriptions

### Conditions
| Field | Type | Units | Notes |
|---|---|---|---|
| `air_temperature` | float | °C | Convert to °F: `(C * 9/5) + 32` |
| `relative_humidity` | int | % | 0–100 |
| `station_pressure` | float | mb | Raw station pressure (not sea-level corrected) |
| `sea_level_pressure` | float | mb | Derived: sea-level adjusted |
| `pressure_trend` | string | — | `"rising"`, `"falling"`, `"steady"` |
| `feels_like` | float | °C | Derived; uses heat index or wind chill depending on conditions |
| `dew_point` | float | °C | Derived |

### Wind
| Field | Type | Units | Notes |
|---|---|---|---|
| `wind_avg` | float | m/s | Average over report interval |
| `wind_lull` | float | m/s | Minimum 3-second sample in interval |
| `wind_gust` | float | m/s | Maximum 3-second sample in interval |
| `wind_direction` | int | degrees | 0=N, 90=E, 180=S, 270=W |
| `wind_sample_interval` | int | seconds | How often samples were taken |

### Precipitation
| Field | Type | Units | Notes |
|---|---|---|---|
| `precip_accum_last_1hr` | float | mm | Rain in the last 60 minutes |
| `precip_accum_local_day` | float | mm | Rain since midnight local time |
| `precip_accum_local_yesterday` | float | mm | Prior day total |
| `precip_minutes_local_day` | int | minutes | Minutes of precipitation today |
| `precip_type` | int | code | `0=none`, `1=rain`, `2=hail` |
| `precip_analysis_type_filtered` | int | code | `0=none`, `1=Rain Check on`, `2=Rain Check off` |

### Lightning
| Field | Type | Units | Notes |
|---|---|---|---|
| `lightning_strike_count` | int | count | Strikes in report interval |
| `lightning_strike_count_last_1hr` | int | count | Strikes in last 1 hour |
| `lightning_strike_count_last_3hr` | int | count | Strikes in last 3 hours |
| `lightning_strike_last_epoch` | int or null | seconds | Unix timestamp of last strike |
| `lightning_strike_last_distance` | int or null | km | Distance to last strike |

### Solar
| Field | Type | Units | Notes |
|---|---|---|---|
| `uv` | float | index | UV index |
| `solar_radiation` | int | W/m² | Solar irradiance |
| `illuminance` | int | lux | Visible light level |

---

## Wind Direction → Cardinal Conversion

```
  0–11°   = N
 12–33°   = NNE
 34–56°   = NE
 57–78°   = ENE
 79–101°  = E
102–123°  = ESE
124–146°  = SE
147–168°  = SSE
169–191°  = S
192–213°  = SSW
214–236°  = SW
237–258°  = WSW
259–281°  = W
282–303°  = WNW
304–326°  = NW
327–348°  = NNW
349–360°  = N
```

---

## Websocket obs_st Array Format (for reference)

If using the WebSocket API instead of REST, `obs_st` observations arrive as arrays. Index mapping:

| Index | Field | Units |
|---|---|---|
| 0 | Time Epoch | Seconds |
| 1 | Wind Lull | m/s |
| 2 | Wind Avg | m/s |
| 3 | Wind Gust | m/s |
| 4 | Wind Direction | Degrees |
| 5 | Wind Sample Interval | Seconds |
| 6 | Station Pressure | mb |
| 7 | Air Temperature | °C |
| 8 | Relative Humidity | % |
| 9 | Illuminance | Lux |
| 10 | UV | Index |
| 11 | Solar Radiation | W/m² |
| 12 | Rain Accumulated | mm |
| 13 | Precipitation Type | 0/1/2 |
| 14 | Lightning Strike Avg Distance | km |
| 15 | Lightning Strike Count | count |
| 16 | Battery | Volts |
| 17 | Report Interval | Minutes |
| 18 | Local Daily Rain Accumulation | mm |
| 19 | Rain Accumulated Final (Rain Check) | mm |
| 20 | Local Daily Rain Accumulation Final (Rain Check) | mm |
| 21 | Precipitation Analysis Type | 0/1/2 |

---

## Authentication

All requests require `?token=YOUR_TOKEN` as a query parameter.

- **Personal Access Token**: Generated at tempestwx.com → Settings → Data Authorizations → Create Token
- **OAuth**: For multi-user applications (see Tempest OAuth docs)

Token is passed as a query param, not a header.

---

## Rate Limits

Tempest enforces rate limits on personal tokens. For on-demand use, polling more than once per minute is unnecessary since observations are published every 1–5 minutes. Avoid polling loops; use the WebSocket API if real-time data is needed.
