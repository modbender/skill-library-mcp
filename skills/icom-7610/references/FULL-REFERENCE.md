---
name: icom-7610
description: Control an Icom IC-7610 transceiver over USB/LAN. Use when you need to get or set frequency, mode (SSB/CW/FT8/AM/FM), power, VFO, read S-meter, SWR, or perform other radio operations.
---

# Icom IC-7610

## Configuration

Station-specific parameters are stored in `.env` (not committed to git).
On first install: `cp .env.example .env` and fill in your values.

```bash
# Load config (insert at the top of scripts)
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ENV_FILE="${SKILL_DIR:-.}/.env"
[ -f "$ENV_FILE" ] || ENV_FILE="$(dirname "$0")/.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

# Short aliases for commands
PORT="$SERIAL_PORT"
BAUD="$BAUD_RATE"
MODEL="$HAMLIB_MODEL"
CIV="$CIV_ADDRESS"
FLRIG="$FLRIG_URL"
MAX_POWER="$MAX_POWER_W"
```

Files:
- **`.env`** — your values (in `.gitignore`)
- **`.env.example`** — template for new users (tracked in git)

Examples below use variables: `$CALLSIGN`, `$PORT`, `$BAUD`, `$MODEL`, `$CIV`, `$RADIO_IP`, `$FLRIG`.

## Requirements

| Dependency | Purpose | Install |
|-----------|---------|---------|
| **hamlib** (rigctl) | Direct serial control | `brew install hamlib` / `apt install libhamlib-utils` |
| **curl** | flrig XML-RPC calls | Usually pre-installed |
| **python3** | Power on via raw CI-V | Usually pre-installed |
| **pyserial** | Python serial access (power on) | `pip3 install pyserial` |
| **bc** | Math in shell scripts | Usually pre-installed |
| **flrig** (optional) | XML-RPC bridge, LAN control | [w1hkj.com/flrig-help](http://www.w1hkj.com/flrig-help/) |

Minimum: **hamlib** + **curl**. Everything else is optional depending on your workflow.

### RFPOWER Scale (important!)

rigctl uses a **0.0 to 1.0 scale** for RF power, where 1.0 = radio's maximum output.
IC-7610 max = **100 W**, so the conversion is:

```
RFPOWER = desired_watts / 100
```

| Watts | RFPOWER value | rigctl command |
|-------|---------------|----------------|
| 5 W   | 0.05          | `L RFPOWER 0.05` |
| 10 W  | 0.10          | `L RFPOWER 0.10` |
| 25 W  | 0.25          | `L RFPOWER 0.25` |
| 50 W  | 0.50          | `L RFPOWER 0.50` |
| 100 W | 1.00          | `L RFPOWER 1.00` |

⚠️ **Common mistake:** `L RFPOWER 5` sets power to **500 W equivalent** (clamped to max 100 W), NOT 5 watts! Always use the 0.0–1.0 fraction.

flrig uses **watts directly**: `rig.set_power 50` = 50 W. No conversion needed.

## Decision Tree: How to Connect

```
┌─ Is the radio powered on?
│   NO → See "Remote Power On/Off" (raw CI-V, flrig not needed)
│   YES ↓
├─ Is flrig running? (pgrep -x flrig)
│   YES → Use flrig XML-RPC ($FLRIG_URL)
│         ✅ Doesn't block the serial port for other apps
│         ✅ Works alongside WSJT-X, JTDX, etc.
│         ❌ No CW keying or power on/off support
│   NO ↓
├─ Is the serial port free? (lsof $PORT)
│   YES → Use rigctl -m $MODEL -r $PORT -s $BAUD
│         ✅ Full control: CW, power on/off, everything
│         ❌ Blocks the port — WSJT-X and flrig can't connect
│   NO → Port is busy. Free it or use LAN.
└─
```

### Auto-detection (copy to top of scripts)

```bash
# Load config
source "$(dirname "$0")/.env" 2>/dev/null || true
PORT="${SERIAL_PORT:-/dev/cu.usbserial-11320}"
BAUD="${BAUD_RATE:-19200}"
MODEL="${HAMLIB_MODEL:-3078}"
FLRIG="${FLRIG_URL:-http://127.0.0.1:12345/RPC2}"

if pgrep -x flrig >/dev/null 2>&1; then
  RIG_MODE="flrig"
  echo "Mode: flrig XML-RPC"
elif ! lsof "$PORT" >/dev/null 2>&1; then
  RIG_MODE="rigctl"
  echo "Mode: rigctl (serial)"
else
  echo "⚠️ Port $PORT is busy, flrig not running"
  exit 1
fi

rig_cmd() {
  if [ "$RIG_MODE" = "flrig" ]; then
    curl -s --connect-timeout 3 --max-time 5 -X POST "$FLRIG" \
      -H "Content-Type: text/xml" \
      -d "<?xml version=\"1.0\"?><methodCall><methodName>$1</methodName><params>$2</params></methodCall>" | \
      grep -o '<value>[^<]*</value>' | head -1 | sed 's/<[^>]*>//g'
  else
    timeout 10 rigctl -m $MODEL -r "$PORT" -s $BAUD $@
  fi
}
```

## Error Handling

rigctl can hang, the port can be busy, the radio may not respond. All scripts should handle this.

### Timeouts

```bash
# rigctl: always wrap with timeout (default 10s)
timeout 10 rigctl -m $MODEL -r "$PORT" -s $BAUD f || echo "⛔ rigctl timed out"

# flrig: curl with connect + max-time
curl -s --connect-timeout 3 --max-time 5 -X POST "$FLRIG" ...
```

### Retry with backoff

```bash
rig_retry() {
  local max_attempts=${2:-3}
  local delay=2
  for attempt in $(seq 1 $max_attempts); do
    result=$(eval "$1" 2>&1) && { echo "$result"; return 0; }
    echo "⚠️ Attempt $attempt/$max_attempts failed: $result" >&2
    [ $attempt -lt $max_attempts ] && sleep $delay
    delay=$((delay * 2))
  done
  echo "⛔ All $max_attempts attempts failed" >&2
  return 1
}

# Usage:
rig_retry "timeout 10 rigctl -m $MODEL -r '$PORT' -s $BAUD f"
```

### Common errors and recovery

| Error | Cause | Recovery |
|-------|-------|----------|
| `Communication timed out` | Radio off or port wrong | Check power, verify `$PORT` exists |
| `Command rejected by the rig` | Radio booting or in standby | Wait 5–10s, retry |
| `could not open port` | Port busy (flrig/WSJT-X) | Switch to flrig XML-RPC or close the blocking app |
| `Resource temporarily unavailable` | Port locked by another process | `lsof $PORT` to find who, then decide |
| curl: `Connection refused` | flrig not running | Start flrig or switch to rigctl |

### Pre-flight check

```bash
preflight() {
  # 1. Serial port exists?
  if [ ! -e "$PORT" ]; then
    echo "⛔ Serial port $PORT not found. Is the radio connected via USB?"
    return 1
  fi

  # 2. Can we talk to the radio?
  local freq
  freq=$(timeout 10 rigctl -m $MODEL -r "$PORT" -s $BAUD f 2>&1)
  if [ $? -ne 0 ]; then
    echo "⛔ Cannot communicate with radio: $freq"
    return 1
  fi

  echo "✅ Radio online: $freq Hz"
  return 0
}
```

## Pre-TX Safety Checks

**The agent MUST complete ALL checks before any transmission (PTT, CW, beacon).**

### 1. Frequency Validation — US Amateur Band Plan (HF)

| Band | Frequency (MHz)    | CW          | Digital/Data  | SSB Phone    |
|------|--------------------|-------------|---------------|--------------|
| 160m | 1.800 – 2.000      | 1.800–2.000 | 1.800–2.000   | 1.800–2.000  |
| 80m  | 3.500 – 4.000      | 3.500–4.000 | 3.500–4.000   | 3.600–4.000  |
| 60m  | 5 channels (USB)   | —           | —             | channelized  |
| 40m  | 7.000 – 7.300      | 7.000–7.300 | 7.000–7.300   | 7.175–7.300  |
| 30m  | 10.100 – 10.150    | 10.100–10.150 | 10.100–10.150 | — (no phone) |
| 20m  | 14.000 – 14.350    | 14.000–14.350 | 14.000–14.350 | 14.150–14.350 |
| 17m  | 18.068 – 18.168    | 18.068–18.168 | 18.068–18.168 | 18.110–18.168 |
| 15m  | 21.000 – 21.450    | 21.000–21.450 | 21.000–21.450 | 21.200–21.450 |
| 12m  | 24.890 – 24.990    | 24.890–24.990 | 24.890–24.990 | 24.930–24.990 |
| 10m  | 28.000 – 29.700    | 28.000–29.700 | 28.000–29.700 | 28.300–29.700 |

⚠️ Extra class license grants full access. General/Technician have narrower sub-bands.

**Check:** before TX, verify the current frequency falls within the band AND matches the mode (CW in CW segment, Phone in Phone segment).

```bash
# Quick check: is frequency within an amateur band?
freq_valid() {
  local f=$1  # in Hz
  case 1 in
    $(( f >= 1800000  && f <= 2000000  ? 1 : 0 )) ) echo "160m" ;;
    $(( f >= 3500000  && f <= 4000000  ? 1 : 0 )) ) echo "80m"  ;;
    $(( f >= 7000000  && f <= 7300000  ? 1 : 0 )) ) echo "40m"  ;;
    $(( f >= 10100000 && f <= 10150000 ? 1 : 0 )) ) echo "30m"  ;;
    $(( f >= 14000000 && f <= 14350000 ? 1 : 0 )) ) echo "20m"  ;;
    $(( f >= 18068000 && f <= 18168000 ? 1 : 0 )) ) echo "17m"  ;;
    $(( f >= 21000000 && f <= 21450000 ? 1 : 0 )) ) echo "15m"  ;;
    $(( f >= 24890000 && f <= 24990000 ? 1 : 0 )) ) echo "12m"  ;;
    $(( f >= 28000000 && f <= 29700000 ? 1 : 0 )) ) echo "10m"  ;;
    *) echo "⛔ OUT OF BAND"; return 1 ;;
  esac
}
```

### 2. SWR Check

```bash
# Via rigctl
swr=$(rigctl -m $MODEL -r "$PORT" -s $BAUD l SWR 2>&1)

# Via flrig
swr=$(curl -s -X POST "$FLRIG" \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><methodCall><methodName>rig.get_SWR</methodName><params></params></methodCall>' | \
  grep -o '<value>[^<]*</value>' | head -1 | sed 's/<[^>]*>//g')
```

| SWR   | Action |
|-------|--------|
| ≤ 1.5 | ✅ Excellent — transmit |
| ≤ 3.0 | ⚠️ Acceptable — warn operator |
| > 3.0 | ⛔ **REFUSE to transmit.** Notify operator. Possible antenna problem. |

⚠️ SWR can only be measured during transmission (brief tune). If no data is available — warn the operator.

### 3. Power Cap

- **Hard limit by default: $MAX_POWER_W (50 W)**
- If operator requests more — require **explicit confirmation** with reason
- See **RFPOWER Scale** in Configuration for watts ↔ RFPOWER conversion

```bash
set_power_safe() {
  local watts=$1
  local max=${MAX_POWER:-50}
  if [ "$watts" -gt "$max" ]; then
    echo "⛔ $watts W exceeds limit of $max W. Explicit operator confirmation required."
    return 1
  fi
  # Convert watts to RFPOWER (0.0–1.0). IC-7610 max = 100 W.
  local rfpower=$(echo "scale=4; $watts / 100" | bc)
  timeout 10 rigctl -m $MODEL -r "$PORT" -s $BAUD L RFPOWER "$rfpower"
}
```

### Full Pre-TX Checklist (for the agent)

Before **every** transmission, execute in order:

1. ✅ **Operator confirmation** received?
2. ✅ **Frequency** within amateur band?
3. ✅ **Mode** matches band plan segment? (CW not in phone-only, phone not in CW-only)
4. ✅ **Power** ≤ $MAX_POWER_W? (otherwise — additional confirmation)
5. ✅ **SWR** ≤ 3.0? (if data available)
6. ✅ **Antenna** connected? (if SWR unavailable — ask operator)

**If any check fails — DO NOT TRANSMIT. Notify operator.**

## Connecting via flrig

flrig connects to the radio over LAN and provides an XML-RPC API at `$FLRIG_URL`.

⚠️ **flrig must be running!** Check: `pgrep -x flrig`

### Reading State

```bash
call_flrig() {
  curl -s -X POST "$FLRIG" \
    -H "Content-Type: text/xml" \
    -d "<?xml version=\"1.0\"?><methodCall><methodName>$1</methodName><params>$2</params></methodCall>" | \
    grep -o '<value>[^<]*</value>' | head -1 | sed 's/<[^>]*>//g'
}

call_flrig rig.get_vfoA     # VFO A frequency (Hz)
call_flrig rig.get_modeA    # Mode
call_flrig rig.get_Sunits   # S-meter
call_flrig rig.get_bw       # Bandwidth
call_flrig rig.get_ptt      # PTT (transmitting)
call_flrig rig.get_power    # TX power
```

### Setting Parameters

```bash
call_flrig rig.set_vfoA "<param><value><double>14074000</double></value></param>"
call_flrig rig.set_modeA "<param><value><string>USB</string></value></param>"
call_flrig rig.set_power "<param><value><double>50</double></value></param>"
call_flrig rig.set_AB "<param><value><string>B</string></value></param>"
```

### Full List of flrig XML-RPC Methods

**Read:**
rig.get_vfo, rig.get_vfoA, rig.get_vfoB, rig.get_mode, rig.get_modeA, rig.get_modeB,
rig.get_bw, rig.get_bwA, rig.get_bwB, rig.get_bws, rig.get_modes, rig.get_AB,
rig.get_smeter, rig.get_Sunits, rig.get_DBM, rig.get_SWR, rig.get_power,
rig.get_pwrmeter, rig.get_swrmeter, rig.get_ptt, rig.get_split, rig.get_volume,
rig.get_rfgain, rig.get_micgain, rig.get_notch, rig.get_agc, rig.get_xcvr,
rig.get_info, rig.get_update, rig.get_maxpwr, rig.get_sideband,
rig.get_pbt_inner, rig.get_pbt_outer

**Write:**
rig.set_vfo, rig.set_vfoA, rig.set_vfoB, rig.set_mode, rig.set_modeA, rig.set_modeB,
rig.set_bw, rig.set_BW, rig.set_AB, rig.set_power, rig.set_ptt, rig.set_split,
rig.set_volume, rig.set_rfgain, rig.set_micgain, rig.set_notch,
rig.set_pbt_inner, rig.set_pbt_outer, rig.set_swap, rig.set_frequency

**Special:**
rig.tune — start antenna tuner
rig.cat_string — send raw CI-V command
rig.cwio_send — send CW
rig.cwio_set_wpm — set CW speed
rig.shutdown — quit flrig

## Connecting via rigctl (serial)

⚠️ While flrig is running, the serial port is busy. Use XML-RPC instead.

```bash
rigctl -m $MODEL -r "$PORT" -s $BAUD <command>
```

## Quick Status

One command to answer "what's on the radio?"

### Via rigctl

```bash
rigctl -m $MODEL -r "$PORT" -s $BAUD f m l RFPOWER
# Output (3 lines): frequency (Hz), mode, bandwidth, RFPOWER (0.0–1.0)
# Example:
#   14074000
#   USB
#   3000
#   0.500000
```

### Via flrig

```bash
echo "Freq: $(call_flrig rig.get_vfoA) Hz"
echo "Mode: $(call_flrig rig.get_modeA)"
echo "Power: $(call_flrig rig.get_power) W"
echo "S-meter: $(call_flrig rig.get_Sunits)"
echo "SWR: $(call_flrig rig.get_SWR)"
```

### Universal quick_status()

```bash
quick_status() {
  if [ "$RIG_MODE" = "flrig" ]; then
    local freq=$(call_flrig rig.get_vfoA)
    local mode=$(call_flrig rig.get_modeA)
    local power=$(call_flrig rig.get_power)
    local smeter=$(call_flrig rig.get_Sunits)
    printf "%s MHz | %s | %s W | S-meter: %s\n" \
      "$(echo "scale=3; $freq / 1000000" | bc)" "$mode" "$power" "$smeter"
  else
    local output
    output=$(rigctl -m $MODEL -r "$PORT" -s $BAUD f m l RFPOWER 2>&1) || {
      echo "⛔ Radio not responding"; return 1
    }
    local freq mode bw rfp
    read -r freq <<< "$(echo "$output" | sed -n '1p')"
    read -r mode <<< "$(echo "$output" | sed -n '2p')"
    read -r bw   <<< "$(echo "$output" | sed -n '3p')"
    read -r rfp  <<< "$(echo "$output" | sed -n '4p')"
    local watts=$(echo "scale=0; $rfp * 100" | bc | cut -d. -f1)
    printf "%s MHz | %s (BW %s) | %s W\n" \
      "$(echo "scale=3; $freq / 1000000" | bc)" "$mode" "$bw" "$watts"
  fi
}
# Output example: 14.074 MHz | USB (BW 3000) | 50 W
```

## Serial Ports (USB)

- `$SERIAL_PORT` — **CI-V port** (USB 1). Occupied by flrig!
- `$SERIAL_PORT2` — **USB 2** (audio/data, WSJT-X)

⚠️ Baud rate: **19200** (not 115200!)

## Remote Power On/Off (WORKING)

### Requirements
- Rear POWER switch on the IC-7610 must be **ON** (standby)
- **MENU → SET → Network → Power OFF Setting** = **Standby / Shutdown** (NOT "Shutdown only"!)
  - Without this setting, `set_powerstat 0` fully shuts down the radio and it cannot be turned back on remotely

### Power Off

```bash
rigctl -m $MODEL -r "$PORT" -s $BAUD set_powerstat 0
```

Radio enters remote standby (not full shutdown).

### Power On

⚠️ **`rigctl set_powerstat 1` DOES NOT WORK** — rigctl checks echo/freq during rig_open, but the radio rejects commands in standby → timeout at rig_open.

Use raw CI-V via pyserial:

```bash
python3 -c "
import serial, time
ser = serial.Serial('$PORT', $BAUD, timeout=2)
ser.reset_input_buffer()
cmd = bytes([0xFE, 0xFE, $CIV, 0xE0, 0x18, 0x01, 0xFD])
ser.write(cmd)
time.sleep(1)
resp = ser.read(100)
ser.close()
ok = 0xFB in resp
print('Power ON: OK' if ok else f'Power ON: FAIL ({resp.hex(\" \")})')
"
```

Or via shell (no pyserial needed):

```bash
stty -f "$PORT" $BAUD cs8 -cstopb -parenb raw
printf '\xFE\xFE\x98\xE0\x18\x01\xFD' > "$PORT"
```

### Timing
- After power on: **~7–10 seconds** until fully ready
- First few seconds after boot the radio may respond with "Command rejected" — this is normal
- Readiness check: `rigctl -m $MODEL -r "$PORT" -s $BAUD f` — should return a frequency

### CI-V Power Commands
- `FE FE 98 E0 18 01 FD` — Power ON
- `FE FE 98 E0 18 00 FD` — Power OFF
- Response `FB` = OK, `FA` = NG (error)

## CW Keying (WORKING)

Send CW via rigctl directly (flrig XML-RPC does not support CW keying):

```bash
# flrig must be CLOSED (port conflict)
rigctl -m $MODEL -r "$PORT" -s $BAUD b "CQ CQ DE $CALLSIGN K"
```

Radio setting: MENU → SET → Connectors → USB SEND/Keying → USB Keying (CW) → **RTS**

⚠️ Cannot run simultaneously with flrig — port conflict. Close flrig for CW sessions.

## Beacon Mode (WORKING)

Automatic periodic CW transmission for propagation and range testing.

### Message Format

Beacon (not expecting a reply):
```
VVV DE $CALLSIGN VVV DE $CALLSIGN
```

CQ (expecting a reply):
```
CQ CQ CQ DE $CALLSIGN $CALLSIGN K
```

`K` = inviting a reply. Do **not** use for beacons.
`VVV` = test transmission.

### Running a Beacon

```bash
FREQ=14025000   # 20m CW
POWER=0.05      # 5 W
INTERVAL=30     # seconds between transmissions
REPEATS=3
MSG="VVV DE $CALLSIGN VVV DE $CALLSIGN"

rigctl -m $MODEL -r "$PORT" -s $BAUD F $FREQ M CW 500 L RFPOWER $POWER

for i in $(seq 1 $REPEATS); do
  echo "$(date '+%H:%M:%S') — TX #$i"
  rigctl -m $MODEL -r "$PORT" -s $BAUD b "$MSG"
  [ $i -lt $REPEATS ] && sleep $INTERVAL
done
```

### Regulatory Requirements (FCC Part 97)

- **Remote operation** (§97.109d) — controlling a station over the network is legal
- Control operator must be able to cease transmission at any time
- **Unattended beacons** allowed only on: 28.20–28.30, 50.06–50.08 MHz and above (§97.203)
- On HF below 28 MHz — **attended mode only** (operator on comms)

### Safety Rules (for the agent)

- **ALWAYS** request operator confirmation before starting a beacon
- Execute **Pre-TX Safety Checks** before the first transmission
- Immediately stop on operator command ("stop")
- Do not start without explicit frequency/power/interval parameters
- Log every transmission with a timestamp

## CI-V Protocol (Reference)

Command format: `FE FE <to_addr> <from_addr> <cmd> [<sub_cmd>] [<data>] FD`
- IC-7610 address: `$CIV` (default `0x98`)
- Controller (us): `0xE0`

Key commands:
- `0x03` — read frequency
- `0x04` — read mode
- `0x05` — set frequency
- `0x06` — set mode
- `0x14` — levels (RF power, SWR, S-meter, etc.)
- `0x15` — read meter
- `0x1A` — read/write memory and settings

Modes:
- `0x00` LSB, `0x01` USB, `0x02` AM, `0x03` CW, `0x04` RTTY
- `0x05` FM, `0x07` CW-R, `0x08` RTTY-R, `0x17` DV

## Radio Settings (from documentation)

### MENU → SET → Network
- DHCP: ON (default)
- Network Control: **ON** (must be enabled manually)
- **Power OFF Setting: Standby / Shutdown** ← REQUIRED for remote power on/off!
- Control Port (UDP): 50001
- Serial Port (UDP): 50002
- Audio Port (UDP): 50003
- Network User1/User2 — ID and password for remote access

### MENU → SET → Connectors → CI-V
- CI-V Baud Rate: Auto
- CI-V Address: 98h
- CI-V Transceive: ON
- CI-V USB Port: Unlink from [REMOTE]
- CI-V USB Echo Back: OFF

## Safety Rules (Summary)

### No confirmation needed:
- Reading frequency, mode, S-meter, SWR, power
- Switching VFO A/B
- Changing frequency within amateur bands
- Changing mode (CW/SSB/AM/FM/Digital)
- Powering radio on/off

### Require operator confirmation:
- **PTT (transmit)** — ALWAYS
- **CW keying** — ALWAYS
- **Beacon mode** — ALWAYS
- **Power > $MAX_POWER_W** — additional confirmation with reason
- Any action involving RF transmission

### Automatic refusal (agent WILL NOT execute even with confirmation):
- Transmission **outside** amateur bands
- Transmission with SWR > 3.0 (if data available)

## Documentation

Official Icom IC-7610 manuals (download from [icom.co.jp](https://www.icomjapan.com/support/firmware_driver/)):
- **Basic Manual** — setup, basic operation
- **Advanced Manual** — all menu settings, CI-V reference
- **ExtIO / HDSDR Guide** — I/Q output for SDR software
- **I/Q Support Guide** — I/Q data format specs

## Compatibility Notes

This skill is written for the **IC-7610** but the approach (hamlib + flrig + CI-V) applies to most modern Icom HF transceivers. To adapt for another radio:

1. Change `HAMLIB_MODEL` (run `rigctl --list | grep Icom` for model IDs)
2. Change `CIV_ADDRESS` (check your radio's CI-V settings)
3. Verify serial port and baud rate
4. Power on/off CI-V bytes (`0x18 0x01` / `0x18 0x00`) are common across Icom radios

## TODO
- [x] Enable Network Control on radio — DONE
- [x] Connect via flrig XML-RPC — DONE
- [x] Remote power on/off — DONE (2026-02-23)
- [x] Pre-TX Safety Checks — DONE (2026-02-23)
- [x] Decision tree flrig/rigctl — DONE (2026-02-23)
- [x] Configuration without hardcoded data — DONE (2026-02-23)
- [x] English translation — DONE (2026-02-23)
- [x] Quick status command — DONE (2026-02-24)
- [x] Error handling (timeout/retry) — DONE (2026-02-24)
- [x] RFPOWER scale documentation — DONE (2026-02-24)
- [ ] Explore Telnet CLI (port 23) — admin console (ver/save/restart)
- [ ] Download CI-V Reference Guide from Icom website
- [ ] Add audio streaming support (port 50003)
- [ ] Figure out CW sending via rig.cwio_send
- [ ] WSJT-X / FT8 integration
