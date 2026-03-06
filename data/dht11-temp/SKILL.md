---
name: dht11-temp
description: Read temperature and humidity from DHT11 sensor. Supports custom GPIO pins via CLI argument or environment variable.
metadata: {"openclaw": {"emoji": "🌡️", "requires": {"bins": ["python3", "sudo", "RPi.GPIO"]}}}
---

# DHT11 Temperature & Humidity Sensor

Read temperature and humidity from a DHT11 sensor.

## Hardware Setup

**Wiring (adjust pin as needed):**
```
DHT11 Pinout:
─────────────
1. VCC     → 5V (Pin 2 oder 4)
2. DATA    → GPIO <PIN> + 10K Pull-Up Widerstand → 5V
3. GND     → GND (Pin 6)
```

**Important:** The 10K pull-up resistor must be connected between DATA and VCC (5V)!

## Installation

```bash
# Install dependencies
pip3 install RPi.GPIO
```

## Usage

### Read Sensor (default pin 19)
```bash
sudo python3 scripts/dht/main.py
```

### Read Sensor (custom pin)
```bash
sudo python3 scripts/dht/main.py 4     # Uses GPIO 4
```

### Using Environment Variable
```bash
export DHT_PIN=4
sudo python3 scripts/dht/main.py
```

## Output

- Line 1: Temperature (°C)
- Line 2: Humidity (%)

## Customization

| Variable | Default | Description |
|----------|---------|-------------|
| DHT_PIN | 19 | GPIO pin number |

## Example crontab entry

```bash
# Read every 30 minutes
*/30 * * * * sudo python3 ~/scripts/dht/main.py >> /var/log/dht.log 2>&1
```
