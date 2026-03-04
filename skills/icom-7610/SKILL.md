---
name: icom-7610
description: Control an Icom IC-7610 transceiver over USB/LAN. Get/set frequency, mode, power, S-meter, SWR. CW keying and beacon mode. Remote power on/off.
metadata: {"openclaw":{"emoji":"📻","homepage":"https://clawhub.ai/morozsm/icom-7610","requires":{"bins":["rigctl","curl","python3"]},"install":[{"id":"hamlib","kind":"brew","formula":"hamlib","bins":["rigctl"],"label":"Install Hamlib (rigctl)"}]}}
---

# Icom IC-7610

## Prerequisites

- **Hamlib** (rigctl): `brew install hamlib`
- **curl**: usually pre-installed
- **python3**: usually pre-installed
- **pyserial** (only for serial power on): `pip3 install pyserial`
- **wfview** (optional, for LAN control): [wfview.org/download](https://wfview.org/download)

## Configuration

Station config in `.env` (not in git). On first install: `cp .env.example .env`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CALLSIGN` | *(required for CW/beacon)* | Your callsign |
| `SERIAL_PORT` | `/dev/cu.usbserial-11320` | CI-V USB serial port |
| `BAUD_RATE` | `19200` | Serial baud rate (⚠️ not 115200!) |
| `HAMLIB_MODEL` | `3078` | Hamlib model ID for IC-7610 |
| `FLRIG_URL` | `http://127.0.0.1:12345/RPC2` | flrig XML-RPC endpoint |
| `RIGCTLD_ADDR` | `127.0.0.1:4533` | rigctld TCP address (wfview/hamlib) |
| `MAX_POWER_W` | `50` | Hard power limit in watts |

```bash
source "$(dirname "$0")/.env" 2>/dev/null || true
PORT="${SERIAL_PORT:-/dev/cu.usbserial-11320}"
BAUD="${BAUD_RATE:-19200}"
MODEL="${HAMLIB_MODEL:-3078}"
FLRIG="${FLRIG_URL:-http://127.0.0.1:12345/RPC2}"
RIGCTLD="${RIGCTLD_ADDR:-127.0.0.1:4533}"
MAX_POWER="${MAX_POWER_W:-50}"
```

### RFPOWER Scale

rigctl uses **0.0–1.0** where 1.0 = 100 W. So: `RFPOWER = watts / 100`.
5 W = `0.05`, 50 W = `0.50`. ⚠️ `L RFPOWER 5` = 500 W equivalent, NOT 5 watts!
flrig uses watts directly: `rig.set_power 50` = 50 W.

## Connecting

Three connection methods, in priority order. **Auto-detect logic:**

```bash
# 1. Check rigctld (wfview LAN or standalone hamlib rigctld)
if rigctl -m 2 -r "$RIGCTLD" f >/dev/null 2>&1; then
  CONN="rigctld"
# 2. Check flrig
elif curl -s --connect-timeout 2 --max-time 3 -X POST "$FLRIG" \
     -H "Content-Type: text/xml" \
     -d '<?xml version="1.0"?><methodCall><methodName>rig.get_vfoA</methodName></methodCall>' \
     | grep -q '<value>'; then
  CONN="flrig"
# 3. Fall back to direct serial
else
  CONN="serial"
fi
```

### rigctld — LAN via wfview (recommended) or standalone hamlib daemon

Connects to IC-7610 over network via wfview (UDP) or a running `rigctld` daemon.
**Full control:** freq, mode, power, S-meter, SWR, CW keying, power on/off.

```bash
rigctl -m 2 -r "$RIGCTLD" <cmd>
# Read:  f   m   l RFPOWER   l SWR
# Write: F 14074000   M USB 3000   L RFPOWER 0.50
# CW:    b "CQ CQ DE YOURCALL K"
# Power: set_powerstat 0 (off)   set_powerstat 1 (on)
```

Setup: wfview → Settings → Enable LAN → connect to radio IP → Enable RigCtld (port 4533).

⚠️ Note: `M` (set mode) may hang waiting for ack from wfview rigctld — command still executes.
Use a timeout wrapper or send as fire-and-forget when needed.

**Advantages over serial:**
- No USB cable needed — Ethernet only
- Power on works with simple `set_powerstat 1` (no raw CI-V / pyserial needed)
- Multiple programs can share the radio via wfview (rigctld + virtual serial port)
- Longer distance (Ethernet 100m vs USB 5m)

### rigctl serial (direct USB, full control incl. CW and power on/off)

```bash
rigctl -m $MODEL -r "$PORT" -s $BAUD <cmd>
# Read:  f (freq)  m (mode+BW)  l RFPOWER  l SWR
# Write: F 14074000   M USB 3000   L RFPOWER 0.50
# CW:    b "CQ CQ DE YOURCALL K"
# Quick: f m l RFPOWER   → freq, mode, BW, power in one call
```

⚠️ Baud **19200** (not 115200!). Always wrap: `timeout 10 rigctl ...`
⚠️ Port busy while flrig runs. Close flrig for CW/power on-off.

### flrig XML-RPC

```bash
call_flrig() {
  curl -s --connect-timeout 3 --max-time 5 -X POST "$FLRIG" \
    -H "Content-Type: text/xml" \
    -d "<?xml version=\"1.0\"?><methodCall><methodName>$1</methodName><params>$2</params></methodCall>" | \
    grep -o '<value>[^<]*</value>' | head -1 | sed 's/<[^>]*>//g'
}
# Read:  call_flrig rig.get_vfoA / rig.get_modeA / rig.get_power / rig.get_Sunits / rig.get_SWR
# Write: call_flrig rig.set_vfoA '<param><value><double>14074000</double></value></param>'
#        call_flrig rig.set_modeA '<param><value><string>USB</string></value></param>'
#        call_flrig rig.set_power '<param><value><double>50</double></value></param>'
```

## Remote Power On/Off

Requires: rear POWER switch ON + **MENU → SET → Network → Power OFF Setting = Standby/Shutdown**.

### Via rigctld (wfview LAN) — simplest

```bash
rigctl -m 2 -r "$RIGCTLD" set_powerstat 0   # off
rigctl -m 2 -r "$RIGCTLD" set_powerstat 1   # on — works! wfview handles it
```

### Via serial — power off works, power on needs raw CI-V

**Off:** `rigctl -m $MODEL -r "$PORT" -s $BAUD set_powerstat 0`

**On:** rigctl `set_powerstat 1` DOES NOT WORK via serial (rig_open fails in standby). Use raw CI-V:

```bash
python3 -c "
import serial, time
ser = serial.Serial('$PORT', $BAUD, timeout=2)
ser.reset_input_buffer()
ser.write(bytes([0xFE,0xFE,0x98,0xE0,0x18,0x01,0xFD]))
time.sleep(1); resp = ser.read(100); ser.close()
print('Power ON: OK' if 0xFB in resp else 'FAIL')
"
```

Wait **7–10 sec** after power on before sending commands. "Command rejected" during boot is normal.

## CW & Beacon

Works via both rigctld (LAN) and direct serial.

```bash
# Via rigctld (LAN):
rigctl -m 2 -r "$RIGCTLD" b "CQ CQ CQ DE $CALLSIGN $CALLSIGN K"

# Via serial:
rigctl -m $MODEL -r "$PORT" -s $BAUD b "CQ CQ CQ DE $CALLSIGN $CALLSIGN K"

# Beacon loop (works with either connection)
for i in $(seq 1 $REPEATS); do
  rigctl -m 2 -r "$RIGCTLD" b "VVV DE $CALLSIGN VVV DE $CALLSIGN"
  [ $i -lt $REPEATS ] && sleep $INTERVAL
done
```

Radio setting for CW: MENU → SET → Connectors → USB Keying (CW) → **RTS**

## Safety Rules

### Pre-TX checklist (MANDATORY before every transmission)
1. Operator confirmation received
2. Frequency within amateur band (1.8–2.0, 3.5–4.0, 7.0–7.3, 10.1–10.15, 14.0–14.35, 18.068–18.168, 21.0–21.45, 24.89–24.99, 28.0–29.7 MHz)
3. Mode matches band segment (no phone below CW/data boundary)
4. Power ≤ $MAX_POWER_W (default 50 W); above → extra confirmation
5. SWR ≤ 3.0 if available; >3.0 → REFUSE (antenna problem)

### No confirmation needed
Reading freq/mode/S-meter/SWR, switching VFO, changing freq/mode, power on/off.

### Always require confirmation
PTT, CW keying, beacon, power > $MAX_POWER_W. Any RF transmission.

### Auto-refuse (even with confirmation)
Transmit outside amateur bands. Transmit with SWR > 3.0.

### Beacon regulatory (FCC)
Remote operation legal (§97.109d). Unattended beacon only 28.2–28.3, 50.06–50.08+ MHz. Below 28 MHz → operator must be on comms.

## Reference

Full documentation in `references/FULL-REFERENCE.md` — consult when needed:
- Complete flrig XML-RPC method list (30+ methods)
- CI-V protocol reference (commands, modes, addressing)
- Error recovery table (common errors + fixes)
- Shell helper functions (freq_valid, set_power_safe, rig_retry, preflight, quick_status)
- Radio menu settings (Network, CI-V, Connectors)
- Compatibility notes for other Icom transceivers
- US Amateur Band Plan table (detailed, with CW/Data/Phone segments)
