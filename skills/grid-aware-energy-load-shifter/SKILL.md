---
name: grid-aware-energy-load-shifter
description: >
  Grid-aware energy load shifter for Home Assistant. Reads real-time
  electricity prices (TOU, time-of-use, dynamic pricing), solar production
  forecasts, battery state of charge, and consumption data from Home
  Assistant. Schedules deferrable household loads (EV charging, HVAC
  pre-conditioning, pool pump, dishwasher, laundry, water heater) to
  cheapest rate windows. Calculates cost savings, optimizes solar
  self-consumption, and supports virtual power plant (VPP) demand response
  signals. Works with Nordpool, ENTSO-e, Tibber, Octopus Energy, Amber
  Electric, and any utility rate plan worldwide. Built for distributed
  energy resource (DER) optimization and residential demand-side management.
metadata:
  openclaw:
    emoji: "⚡"
    requires:
      env:
        - HA_URL
        - HA_TOKEN
    tags:
      - energy
      - home-assistant
      - load-shifting
      - time-of-use
      - solar
      - battery-storage
      - demand-response
      - vpp
      - ev-charging
      - smart-home
      - DER
      - grid-optimization
---

# Grid-Aware Energy Load Shifter

Shift heavy residential loads to the cheapest electricity hours using Home Assistant energy data.

## Quick Start

```bash
# Find all energy-related entities in HA
python3 {baseDir}/scripts/ha_bridge.py discover

# Get a full energy dashboard snapshot (prices, solar, consumption, batteries)
python3 {baseDir}/scripts/ha_bridge.py energy-summary

# Turn on the EV charger
python3 {baseDir}/scripts/ha_bridge.py call-service switch/turn_on --entity-id switch.ev_charger
```

## Connection

Two paths to reach Home Assistant:

1. **MCP (preferred):** If the HA MCP server is configured, use `mcporter call homeassistant.<tool>` directly.
2. **REST API:** Use `python3 {baseDir}/scripts/ha_bridge.py`. Requires `HA_URL` and `HA_TOKEN` environment variables.

## Security

**Required credentials:**

| Variable | Description |
|---|---|
| `HA_URL` | Home Assistant base URL (e.g. `http://homeassistant.local:8123`) |
| `HA_TOKEN` | Home Assistant Long-Lived Access Token |

**Least-privilege recommendations:**

- Create a dedicated Home Assistant user account for this skill (e.g. `openclaw-energy`)
- Generate a Long-Lived Access Token from that account only
- Limit the account's entity access to energy-related entities if your HA setup supports entity-level permissions
- Test with read-only commands first (`discover`, `energy-summary`) before enabling device control

**Domain allowlist:** The `call-service` command restricts actions to energy-related domains only: `switch`, `automation`, `script`, `climate`, `water_heater`, `input_boolean`, `input_number`, `number`. All other domains (e.g. `lock`, `alarm_control_panel`) are blocked with exit code 2.

## Commands

| Command | What it does | Example |
|---|---|---|
| `discover` | List all energy entities | `ha_bridge.py discover` |
| `energy-summary` | One-shot dashboard (prices + consumption + solar + storage) | `ha_bridge.py energy-summary` |
| `status <entity>` | Read a single entity's state and attributes | `ha_bridge.py status sensor.electricity_price` |
| `call-service <d/s>` | Call an energy-related HA service (restricted to allowed domains) | `ha_bridge.py call-service switch/turn_on --entity-id switch.ev_charger` |
| `history <entity>` | Get state changes over last N hours | `ha_bridge.py history sensor.grid_import --hours 24` |

All commands output JSON to stdout.

## Load-Shifting Workflow

Follow these steps when asked about energy optimization:

1. **Discover** available energy entities: run `discover` or `energy-summary`
2. **Read prices**: Check pricing entities' state and attributes — look for:
   - Hourly price arrays in `today` / `tomorrow` / `prices_today` / `rates` attributes
   - `price_level` attribute (CHEAP / NORMAL / EXPENSIVE)
   - Current vs. average price comparison
3. **Identify deferrable loads**: Find `switch.*` entities for schedulable devices (EV charger, pool pump, dishwasher, washer/dryer, water heater)
4. **Find the cheapest window**: Scan hourly prices for the contiguous N-hour block with the lowest sum (N = estimated run time of device)
5. **Execute**: Call `switch/turn_on` at the optimal time, or `automation/trigger` if the user has an existing automation

## Interpreting Price Data

Different integrations expose prices differently:

- **Hourly arrays** (Nordpool, ENTSO-e, Octopus): Read `today`/`tomorrow` attributes → find cheapest hours
- **Price level** (Tibber): Read `price_level` → act when CHEAP or VERY_CHEAP
- **Real-time** (Amber Electric): Read 5-minute pricing → shift loads immediately when cheap
- **Utility meter tariffs**: Read `sensor.*_peak` vs `sensor.*_offpeak` → user's HA automations switch tariffs at configured times
- **Static TOU**: Read `current_price` attribute → compare against historical average

## Cost Savings Estimate

When recommending a shift, show estimated savings:

```
savings = (current_rate - cheapest_rate) × device_power_kw × run_duration_hours
```

## Solar Self-Consumption

If solar sensors exist, align loads with peak production:

- Read `sensor.forecast_solar_*` or `sensor.solcast_*` for today's forecast
- Shift loads to hours with highest expected production
- This avoids grid import entirely — savings = full retail rate × kWh shifted

## HVAC Pre-Conditioning

HVAC is the largest residential load (40-50% of electricity). Pre-cool or pre-heat during cheap/solar hours so the home coasts through expensive peak periods:

1. Read `climate.*` entities for current HVAC mode and setpoint
2. During cheapest window: lower cooling setpoint by 2-3F (pre-cool) or raise heating setpoint by 2-3F (pre-heat)
3. During peak window: raise cooling setpoint by 2-3F to coast on thermal mass
4. Savings estimate: 1.5-3 kW shifted × price differential × hours

## Water Heater Scheduling

Electric water heaters (4.5 kW typical) are ideal deferrable loads:

1. Find `switch.water_heater` or `water_heater.*` entities
2. Heat during cheapest/solar window to full temperature
3. Turn off during peak hours (tank maintains temperature for 4-6 hours)
4. Savings estimate: 4.5 kW × price differential × 3-4 hours/day

## Battery Arbitrage

If home battery entities exist (`sensor.battery_soc`, `sensor.powerwall_*`, `sensor.enphase_*`):

1. Read current state of charge and charge/discharge rate limits
2. Charge from grid during cheapest hours (or from solar)
3. Discharge to home during peak price hours to avoid grid import
4. Advanced: If battery supports grid export and VPP enrollment, discharge to grid during extreme price events ($2,000+/MWh)
5. Savings estimate: battery_capacity_kwh × (peak_rate - valley_rate)

## Demand Response / VPP Integration

For homes enrolled in utility demand response or virtual power plant programs:

1. Read demand response signal entities (if available via HA integration)
2. When DR event active: shed non-critical loads, pre-cool/pre-heat, discharge battery
3. Estimate DR payment: kW reduced × event duration × program rate

## Entity Reference

For detailed entity patterns across providers, read: [energy_entities.md](references/energy_entities.md)
