sample_data = {
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [18.4174, -33.9288]
  },
  "properties": {
    "meta": {
      "updated_at": "2026-02-22T04:00:00Z",
      "units": {
        "air_pressure_at_sea_level": "hPa",
        "air_temperature": "celsius",
        "relative_humidity": "%",
        "wind_speed": "m/s"
      }
    },
    "timeseries": [
      {
        "time": "2026-02-22T04:00:00Z",
        "data": {
          "instant": {
            "details": {
              "air_temperature": 18.5,
              "relative_humidity": 75,
              "wind_speed": 3.2
            }
          },
          "next_1_hours": {
            "summary": {
              "symbol_code": "partlycloudy_night"
            }
          }
        }
      }
    ]
  }
}
