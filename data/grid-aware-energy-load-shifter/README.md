# Grid-Aware Energy Load Shifter

An OpenClaw skill that bridges Home Assistant's energy management data to an autonomous AI agent. Reads real-time electricity prices, solar production forecasts, battery state of charge, and consumption data from Home Assistant. Schedules deferrable household loads - EV charging, HVAC pre-conditioning, pool pumps, water heaters, dishwashers, and laundry - to the cheapest rate windows, optimizing solar self-consumption and supporting demand response / virtual power plant (VPP) signals.

## What This Skill Does

| Capability | Description |
|---|---|
| **Price-Aware Scheduling** | Reads TOU (time-of-use), dynamic, and real-time pricing from Nordpool, ENTSO-e, Tibber, Octopus Energy, Amber Electric, and any utility rate plan worldwide |
| **Solar Self-Consumption** | Aligns load timing with solar production forecasts (Solcast, Forecast.Solar) to minimize grid import |
| **Battery Arbitrage** | Charges home batteries (Tesla Powerwall, Enphase) during off-peak/solar, discharges during peak |
| **HVAC Pre-Conditioning** | Pre-cools or pre-heats during cheap hours so the home coasts through expensive peak periods |
| **Water Heater Scheduling** | Heats during cheapest window, coasts through peak (4.5 kW typical load) |
| **Demand Response / VPP** | Sheds load during DR events, estimates DR payments for enrolled homes |
| **Cost Estimation** | Calculates per-device savings from each recommended load shift |

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Agent-facing instructions with load-shifting workflow, price interpretation, and DER optimization strategies |
| `scripts/ha_bridge.py` | REST API bridge - 5 CLI commands, zero pip dependencies, Python stdlib only |
| `references/energy_entities.md` | Comprehensive entity reference for 7+ energy pricing providers and all HA energy entity patterns |

## Quick Start

```bash
# Set HA connection (REST API mode)
export HA_URL=http://homeassistant.local:8123
export HA_TOKEN=your_long_lived_access_token

# Discover energy entities
python3 scripts/ha_bridge.py discover

# Get full energy dashboard
python3 scripts/ha_bridge.py energy-summary

# Control a device
python3 scripts/ha_bridge.py call-service switch/turn_on --entity-id switch.ev_charger
```

## Technical Design

- **Zero external dependencies** - uses only Python standard library (`urllib`, `json`, `argparse`)
- **Universal compatibility** - no hardcoded rate schedules; reads whatever pricing entities HA provides
- **Dual connectivity** - works via HA MCP server or REST API fallback
- **JSON output** - all commands emit structured JSON for agent parsing
- **Exit codes** - `0` success, `1` API error, `2` configuration error

## Keywords

Distributed energy resources (DER), demand-side management (DSM), time-of-use (TOU) rate optimization, dynamic electricity pricing, residential load shifting, grid-edge intelligence, virtual power plant (VPP), demand response (DR), behind-the-meter optimization, home energy management system (HEMS), smart grid, energy arbitrage, solar self-consumption, battery storage optimization, EV managed charging, HVAC pre-conditioning, thermal storage.

---

Built by [Omer Bese](https://linkedin.com/in/omerbese) | Energy Systems Engineer | Columbia University MS Sustainability Management
