# Home Assistant Energy Entity Reference

Reference for interpreting energy-related entities in Home Assistant. Read this when you need deeper context about entity attributes or discovery patterns.

## Table of Contents

1. [Electricity Price Sensors](#electricity-price-sensors)
2. [Consumption Sensors](#consumption-sensors)
3. [Solar Production Sensors](#solar-production-sensors)
4. [Battery / Storage Sensors](#battery--storage-sensors)
5. [Utility Meter Entities](#utility-meter-entities)
6. [Controllable Devices](#controllable-devices)
7. [HVAC & Water Heater Entities](#hvac--water-heater-entities)
8. [Common HA Services for Load Control](#common-ha-services-for-load-control)
9. [Supported Integrations](#supported-integrations)

---

## Electricity Price Sensors

These track the current electricity rate from the user's utility provider.

| Integration | Typical Entity ID | Key Attributes |
|---|---|---|
| Nordpool | `sensor.nordpool_kwh_*` | `today` (24-element array of hourly prices), `tomorrow` (available after ~13:00), `current_price`, `average`, `peak`, `off_peak_1`, `off_peak_2`, `unit` |
| Tibber | `sensor.tibber_prices` | `price_level` (VERY_CHEAP / CHEAP / NORMAL / EXPENSIVE / VERY_EXPENSIVE), `estimated_annual_consumption` |
| ENTSO-e | `sensor.entsoe_*` | `prices_today` (hourly array), `prices_tomorrow`, `min_price`, `max_price`, `avg_price` |
| Amber Electric | `sensor.amber_*` | `price`, `renewables_percentage`, `spike_status` |
| Octopus Energy | `sensor.octopus_energy_*` | `rates` (array of rate objects with `start`, `end`, `value_inc_vat`) |
| Manual / Static | `sensor.electricity_price` | `current_price`, `unit_of_measurement` (e.g. USD/kWh) |
| Utility Meter Tariff | `sensor.daily_electricity_peak` | `tariff` (peak / offpeak / shoulder), `status` |

**How to find the cheapest window:** Read the hourly price array attributes (`today`/`tomorrow`/`prices_today`/`rates`), find the contiguous block of N hours with the lowest sum. That's your optimal load-shifting window.

---

## Consumption Sensors

Track energy drawn from the grid or consumed by devices.

| Pattern | Example Entity | Description |
|---|---|---|
| Grid import | `sensor.grid_consumption`, `sensor.grid_import_energy` | Total kWh imported from grid |
| Grid export | `sensor.grid_export_energy`, `sensor.grid_feed_in` | kWh returned to grid (solar) |
| Device power | `sensor.<device>_power` | Instantaneous watts (W) |
| Device energy | `sensor.<device>_energy` | Cumulative kWh consumed |
| Whole-home | `sensor.house_consumption`, `sensor.total_power` | Sum of all loads |

**Required attributes for Energy Dashboard compatibility:**
- `device_class: energy`
- `state_class: total_increasing`
- `unit_of_measurement: kWh`

---

## Solar Production Sensors

| Pattern | Example Entity | Key Attributes |
|---|---|---|
| Current production | `sensor.solar_production`, `sensor.pv_power` | Instantaneous W or kW |
| Total production | `sensor.solar_energy_today` | Cumulative kWh today |
| Forecast | `sensor.energy_production_today`, `sensor.energy_production_tomorrow` | From Forecast.Solar or Solcast |
| Solcast detail | `sensor.solcast_pv_forecast_*` | `detailedForecast` (30-min intervals), `forecast_today`, `forecast_tomorrow` |

**Self-consumption optimization:** Compare solar production forecast against planned load timing. Shifting loads to align with solar peaks avoids grid import entirely.

---

## Battery / Storage Sensors

| Pattern | Example Entity | Key Attributes |
|---|---|---|
| State of charge | `sensor.<battery>_soc`, `sensor.<battery>_battery_level` | Value in %, `device_class: battery` |
| Power flow | `sensor.<battery>_power` | Positive = charging, negative = discharging (W) |
| Capacity | `sensor.<battery>_energy_capacity` | Total capacity in kWh |

**Battery arbitrage:** Charge during off-peak or solar surplus. Discharge during peak to avoid expensive grid import.

---

## Utility Meter Entities

Home Assistant's Utility Meter helper creates tariff-aware sensors.

| Example | Description |
|---|---|
| `sensor.daily_electricity_peak` | kWh consumed during peak tariff |
| `sensor.daily_electricity_offpeak` | kWh consumed during off-peak tariff |
| `sensor.monthly_electricity` | Monthly total |

**Tariff switching:** HA automations call `utility_meter.select_tariff` at scheduled times to switch between `peak` and `offpeak`.

---

## Controllable Devices

These are the entities you control to shift loads:

| Domain | Example | Action |
|---|---|---|
| `switch` | `switch.ev_charger`, `switch.pool_pump`, `switch.dishwasher` | `switch.turn_on` / `switch.turn_off` |
| `automation` | `automation.charge_ev_offpeak` | `automation.trigger` to run now |
| `script` | `script.start_laundry_cycle` | `script.turn_on` to execute |
| `input_boolean` | `input_boolean.allow_ev_charging` | Toggle to enable/disable automations |
| `climate` | `climate.water_heater` | `climate.set_temperature` to pre-heat |

---

## HVAC & Water Heater Entities

| Pattern | Example Entity | Key Attributes |
|---|---|---|
| HVAC | `climate.thermostat`, `climate.heat_pump` | `hvac_mode`, `temperature`, `current_temperature` |
| Water heater | `switch.water_heater`, `water_heater.tank` | `current_temperature`, `target_temp_high` |
| HVAC power | `sensor.hvac_power`, `sensor.heat_pump_energy` | `device_class: power`, unit `W` or `kW` |

---

## Common HA Services for Load Control

```
switch.turn_on       {"entity_id": "switch.ev_charger"}
switch.turn_off      {"entity_id": "switch.pool_pump"}
automation.trigger    {"entity_id": "automation.offpeak_dishwasher"}
script.turn_on       {"entity_id": "script.delayed_charge"}
climate.set_temperature  {"entity_id": "climate.thermostat", "temperature": 68}
homeassistant.turn_on  {"entity_id": "switch.dryer"}   # generic, works on any domain
homeassistant.turn_off {"entity_id": "switch.dryer"}
```

---

## Supported Integrations

| Integration | Price Entity Pattern | Forecast Available |
|---|---|---|
| Nordpool | `sensor.nordpool_*` | today + tomorrow arrays |
| ENTSO-e | `sensor.entsoe_*` | today + tomorrow arrays |
| Tibber | `sensor.tibber_*` | price_level attribute |
| Octopus Energy | `sensor.octopus_*` | current + upcoming rates |
| Amber Electric | `sensor.amber_*` | real-time 5-min pricing |
| Solcast | `sensor.solcast_*` | solar forecast |
| Forecast.Solar | `sensor.forecast_solar_*` | solar forecast |
| Tesla Powerwall | `sensor.powerwall_*` | battery SOC + grid status |
| Enphase | `sensor.enphase_*` | battery + solar + grid |
| Pila Energy | (upcoming) | mesh battery fleet |
