# API Reference - Tesla Smart Charge

Complete parameter and formula reference.

## Command Reference

```bash
python3 scripts/tesla-smart-charge.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--target-time` | string | required | Target time (HH:MM, 24h format) |
| `--target-battery` | int | 100 | Target battery percentage |
| `--charger-power` | float | 2.99 | Charger power in kW |
| `--battery-capacity` | int | 75 | Vehicle battery size in kWh |
| `--vehicle-name` | string | first | Vehicle name to charge |
| `--margin-minutes` | int | 5 | Buffer before target time |
| `--auto-start` | flag | false | Start charging if time is right |
| `--show-plan` | flag | false | Display saved charge plan |

## Charge Time Formula

```
battery_needed = target_battery - current_battery
energy_needed = (battery_capacity × battery_needed / 100) / charge_efficiency
charge_time = energy_needed / charger_power
```

Where:
- `battery_needed`: Percentage points to charge
- `battery_capacity`: Vehicle battery size (kWh)
- `charge_efficiency`: 0.92 (92% typical AC charging efficiency)
- `charger_power`: Your home charger output (kW)

### Example Calculation

**Scenario:** Model 3 at 81%, charge to 100% by 8:00 AM with 13A@230V

- battery_needed = 100 - 81 = 19%
- energy_needed = (75 × 19 / 100) / 0.92 = 15.49 kWh
- charger_power = (230V × 13A) / 1000 = 2.99 kW
- charge_time = 15.49 / 2.99 = **5.18 hours**

**Start time:** 8:00 AM - 5:18 hours - 5 min margin = **02:37 AM**

## Common Charger Powers

Home charging (European):
- **Single-phase 13A @ 230V**: 2.99 kW
- **Single-phase 16A @ 230V**: 3.68 kW
- **Three-phase 16A @ 230V**: 11.0 kW
- **Three-phase 32A @ 230V**: 22.0 kW

Home charging (US):
- **Level 2, 16A @ 240V**: 3.8 kW
- **Level 2, 32A @ 240V**: 7.7 kW
- **Level 2, 40A @ 240V**: 9.6 kW

Tesla Supercharger:
- **Supercharger (V2)**: 120+ kW
- **Supercharger (V3)**: 250 kW

## Output Files

### tesla-charge-plan.json

Saved charge plan with all calculations:

```json
{
  "timestamp": "2026-01-31T18:00:00",
  "current_battery": 81,
  "target_battery": 100,
  "charger_power_kw": 2.99,
  "charge_time_hours": 5.18,
  "charge_time_minutes": 311,
  "start_time": "2026-02-01T02:37:00",
  "target_time": "2026-02-01T08:00:00",
  "time_until_start_hours": 8.62,
  "margin_minutes": 5
}
```

Use this file in automation to know exactly when to trigger charging.
