# tempest-weather

See [SKILL.md](./SKILL.md).

## About Tempest

Tempest is a personal weather station and app platform by WeatherFlow.
Learn more: https://tempest.earth

This skill connects to the Tempest REST API to fetch:
- current conditions (temperature, wind, humidity, pressure, rain, lightning, and more) from your station/device
- historical station stats by day/month/year using the Tempest station stats endpoint

> Unofficial skill: This project is community-maintained and is not affiliated with or endorsed by WeatherFlow.

## Troubleshooting

- **Missing env var errors** (`TEMPEST_API_TOKEN`, station/device id)
  - Set env vars in your OpenClaw environment (for gateway installs: `~/.openclaw/.env`) and restart gateway.
  - You can use either `TEMPEST_STATION_ID`, `TEMPEST_DEVICE_ID`, or both (device ID takes precedence if both are set).

- **No observations returned** (`obs`/`obs_st` missing)
  - Verify your token and station/device IDs are valid.
  - Confirm your station/device is online and reporting data.

- **No historical stats row found** (`--stats ... --date ...`)
  - Verify `TEMPEST_STATION_ID` is set (stats require station ID).
  - Check whether the requested date/month/year is between `first_ob_day_local` and `last_ob_day_local`.
