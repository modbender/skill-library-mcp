# Bluetooth Tools Reference

## Linux

### bluetoothctl (Primary)
```bash
# Start interactive mode
bluetoothctl

# Inside bluetoothctl:
power on                    # Enable adapter
scan on                     # Start discovery
devices                     # List discovered
pair XX:XX:XX:XX:XX:XX      # Pair device
connect XX:XX:XX:XX:XX:XX   # Connect
info XX:XX:XX:XX:XX:XX      # Device details
disconnect                  # Disconnect current
```

### gatttool (BLE GATT operations)
```bash
# Connect and interactive
gatttool -b XX:XX:XX:XX:XX:XX -I

# Read characteristic
char-read-hnd 0x0025

# Write characteristic
char-write-cmd 0x0025 0100
```

### btmon (Packet capture)
```bash
# Capture HCI traffic (requires root)
sudo btmon

# Save to file
sudo btmon -w capture.btsnoop
```

---

## macOS

### blueutil
```bash
# Install
brew install blueutil

# Commands
blueutil --power 1              # Enable Bluetooth
blueutil --discoverable 1       # Make discoverable
blueutil --inquiry 5            # Scan for 5 seconds
blueutil --pair XX:XX:XX        # Pair device
blueutil --connect XX:XX:XX     # Connect
blueutil --disconnect XX:XX:XX  # Disconnect
blueutil --info XX:XX:XX        # Device info
blueutil --paired               # List paired devices
```

### system_profiler
```bash
# List Bluetooth info
system_profiler SPBluetoothDataType

# JSON output
system_profiler SPBluetoothDataType -json
```

---

## Windows

### PowerShell
```powershell
# List Bluetooth devices
Get-PnpDevice -Class Bluetooth

# Device properties
Get-PnpDeviceProperty -InstanceId "BTHENUM\..."

# Enable/Disable adapter
# (Requires third-party tools or WinRT)
```

### WinRT (via Python/C#)
```python
# Use Bleak library for cross-platform BLE on Windows
```

---

## Cross-Platform Libraries

### Bleak (Python) — Recommended
```bash
pip install bleak
```

```python
import asyncio
from bleak import BleakScanner, BleakClient

# Scan
async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"{d.name}: {d.address}")

# Connect and read
async def read_device(address):
    async with BleakClient(address) as client:
        services = client.services
        for s in services:
            print(f"Service: {s.uuid}")
            for c in s.characteristics:
                print(f"  Char: {c.uuid}")
                if "read" in c.properties:
                    value = await client.read_gatt_char(c.uuid)
                    print(f"    Value: {value}")
```

### Noble (Node.js)
```javascript
const noble = require('@abandonware/noble');

noble.on('stateChange', (state) => {
    if (state === 'poweredOn') noble.startScanning();
});

noble.on('discover', (peripheral) => {
    console.log(peripheral.advertisement.localName, peripheral.address);
});
```

---

## Tool Selection Guide

| Task | Linux | macOS | Windows | Cross-Platform |
|------|-------|-------|---------|----------------|
| Quick scan | bluetoothctl | blueutil | - | Bleak |
| Pair device | bluetoothctl | blueutil | Settings GUI | - |
| BLE GATT | gatttool/bluetoothctl | - | - | Bleak |
| Packet capture | btmon | PacketLogger | Wireshark | - |
| Scripting | bluetoothctl | blueutil | - | Bleak/Noble |
