# PetTracer data model (fields the agent cares about)

The API returns JSON dicts. The exact shape can evolve, but these fields are consistently useful for location tracking.

## Device (collar) object

Common top-level keys:

- `id` (int): device id
- `type` (int, optional): device type
  - `0` = collar (often omitted)
  - `1` = HomeStation
- `details` (dict):
  - `name` (str): pet name (primary label for matching)
- `bat` (int): battery in **mV** (not %)
- `lastContact` (str): last time the device communicated (ISO-like string, often with `+0000`)
- `home` (bool): whether PetTracer considers the pet “home” (if present)
- `mode` (int): tracking mode id (if present)

### Location fields

For **collars**, the latest GPS fix is typically in:
- `lastPos` (dict)

For **HomeStations**, location fields may appear at the top level:
- `posLat`, `posLong`

## lastPos / position object

- `posLat` (float): latitude
- `posLong` (float): longitude
- `timeMeasure` (str): time of fix
- `timeDb` (str): time stored server-side
- `acc` (int): accuracy in metres (if present)
- `horiPrec` (int): horizontal precision (some devices report this instead of `acc`)
- `sat` (int): satellite count
- `rssi` (int): signal strength (format varies)
- `fixS`, `fixP`, `flags` (ints): quality/status flags

### “No fix” scenarios

If `lastPos` is missing or has null-ish fields, report:
- “No recent GPS fix”
- include `lastContact` if available
