# Tempest API Notes (quick reference)

## Endpoint used by this skill

- Current station observations:
  - `GET https://swd.weatherflow.com/swd/rest/observations/station/{station_id}?token={token}`
- Current device observations:
  - `GET https://swd.weatherflow.com/swd/rest/observations/device/{device_id}?token={token}`
- Historical station statistics:
  - `GET https://swd.weatherflow.com/swd/rest/stats/station/{station_id}?token={token}`

## Typical response fields

- Observations payload:
  - `obs`: array of observation arrays (most recent usually first)
  - Some payloads may use `obs_st`; the script supports both
- Station stats payload:
  - `stats_day`: day-level rows keyed by local date (`YYYY-MM-DD`)
  - `stats_month`: month-level rows keyed by first day of month (`YYYY-MM-01`)
  - `stats_year`: year-level rows keyed by first day of year (`YYYY-01-01`)
  - `first_ob_day_local`, `last_ob_day_local` availability window

## Station stats index mapping used in script

Given `stats = [ ... ]` from `stats_day`, `stats_month`, or `stats_year`:

- `stats[0]` date
- `stats[1]` pressure (avg)
- `stats[2]` pressure (high)
- `stats[3]` pressure (low)
- `stats[4]` temperature (avg)
- `stats[5]` temperature (high)
- `stats[6]` temperature (low)
- `stats[7]` humidity (avg)
- `stats[8]` humidity (high)
- `stats[9]` humidity (low)
- `stats[10]` lux (avg)
- `stats[11]` lux (high)
- `stats[12]` lux (low)
- `stats[13]` UV (avg)
- `stats[14]` UV (high)
- `stats[15]` UV (low)
- `stats[16]` solar radiation (avg)
- `stats[17]` solar radiation (high)
- `stats[18]` solar radiation (low)
- `stats[19]` wind (average)
- `stats[20]` wind (gust)
- `stats[21]` wind (lull)
- `stats[22]` wind direction
- `stats[23]` wind interval
- `stats[24]` strike count
- `stats[25]` strike average distance
- `stats[26]` record count
- `stats[27]` battery
- `stats[28]` local precip accumulation (today)
- `stats[29]` local precip accumulation (final)
- `stats[30]` local precip minutes (today)
- `stats[31]` local precip minutes (final)
- `stats[32]` precipitation type
- `stats[33]` precipitation analysis type

## Observation index mapping used in script

Given `obs = [ ... ]`:

- `obs[0]` timestamp epoch (seconds)
- `obs[1]` wind lull (m/s)
- `obs[2]` wind average (m/s)
- `obs[3]` wind gust (m/s)
- `obs[4]` wind direction (degrees)
- `obs[6]` station pressure (mb)
- `obs[7]` air temperature (°C)
- `obs[8]` relative humidity (%)
- `obs[9]` illuminance (lux)
- `obs[10]` UV index
- `obs[11]` solar radiation (W/m²)
- `obs[12]` rain accumulated in interval (mm)
- `obs[13]` precipitation type code
- `obs[14]` lightning average distance (km)
- `obs[15]` lightning strike count in interval
- `obs[16]` battery (V)
- `obs[17]` report interval (min)
- `obs[18]` local daily rain accumulation (mm)

## Configuration defaults

The skill expects these environment variables:
- You can set TEMPEST_STATION_ID, TEMPEST_DEVICE_ID, or both. If both are set, TEMPEST_DEVICE_ID is used.

- `TEMPEST_API_TOKEN`
- `TEMPEST_STATION_ID`
- `TEMPEST_DEVICE_ID`
- `TEMPEST_UNITS` (`us` or `metric`)

## Security

- Never hardcode token values in the skill files.
- Pass token via env var or CLI argument.
