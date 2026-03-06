# Testing the Persistent Connection Wrapper

## Quick Start

### 1. Check Device Connection
```bash
# Make sure device is connected
ls -la /dev/tty.usbmodem*

# Should show something like:
# crw-rw-rw-  1 root  wheel  0x900000a  /dev/tty.usbmodem21201
```

### 2. Close Meshtastic App
The device can only be used by one process at a time. Close the Meshtastic.app GUI:
```bash
# Method 1: Kill the app
killall Meshtastic

# Method 2: Activity Monitor - Quit manually
# Method 3: Just close the app window
```

### 3. Test the Persistent Wrapper

**Single broadcast message:**
```bash
cd ~/clawd/meshtastic-skill
node scripts/meshtastic-persistent.js "broadcast: hello mesh"
```

Expected output:
```
🔌 Connecting to Meshtastic device...
✅ Connected!
✅ Broadcast sent: "hello mesh"
```

**With debug logging:**
```bash
MESH_DEBUG=true node scripts/meshtastic-persistent.js "broadcast: hello mesh"
```

Expected output (with debug info):
```
[Persistent] Initializing persistent connection wrapper
[Persistent] Verifying connection to /dev/tty.usbmodem21201...
[Persistent] Device info retrieved successfully
[Persistent] Setting up persistent listener...
[Persistent] Persistent listener ready
🔌 Connecting to Meshtastic device...
✅ Connected!
✅ Broadcast sent: "hello mesh"
```

**Interactive mode:**
```bash
node scripts/meshtastic-persistent.js
```

Then type commands:
```
> broadcast: hello mesh
✅ Broadcast sent: "hello mesh"

> nodes
📡 Mesh Nodes:
(shows all nodes)

> info
ℹ️ Device Info:
(shows device info)

> exit
```

### 4. Run Unit Tests
```bash
npm test
# or
node tests/test-persistent.js
```

Expected output:
```
Testing: Wrapper instantiation... ✓
Testing: Environment configuration... ✓
Testing: Command queueing structure... ✓
Testing: Natural language command parsing... ✓
Testing: Disconnected error handling... ✓
Testing: Timeout configuration... ✓
Testing: Proper cleanup on disconnect... ✓
Testing: Debug logging enabled/disabled... ✓
Testing: Message text escaping... ✓
Testing: Node ID normalization... ✓

SUMMARY: Passed 10/10 ✓
```

## Troubleshooting

### Error: "Resource busy"
Device is being used by another process:
```bash
# Kill Meshtastic app
killall Meshtastic

# Or find what's using it
lsof /dev/tty.usbmodem21201
# Kill the process shown
kill -9 <PID>
```

### Error: "The serial device couldn't be opened"
Same as above - device is busy. Close Meshtastic.app.

### Error: "Failed to connect to meshtastic device"
Device not found at expected port. Check:
```bash
# List available devices
ls /dev/tty*

# Set correct port
export MESHTASTIC_PORT=/dev/ttyUSB0  # or whatever your device is
node scripts/meshtastic-persistent.js "broadcast: test"
```

### Timeout Error
Command took too long. Either:
1. Device is slow to respond
2. Increase timeout: `export MESH_TIMEOUT=60`
3. Device is disconnected

### No output / Hangs
Process might be stuck. Press Ctrl+C to kill it:
```bash
^C  # Kill the process
```

## What Success Looks Like

✅ Message sent without ETIMEDOUT
✅ Response within 1-2 seconds
✅ Device stays connected
✅ Can send multiple messages in succession
✅ No process spawning overhead

## Performance Benchmark

Time a broadcast to confirm improvement:

```bash
time node scripts/meshtastic-persistent.js "broadcast: test1"
time node scripts/meshtastic-persistent.js "broadcast: test2"
time node scripts/meshtastic-persistent.js "broadcast: test3"
```

Expected times:
- First run: 2-3 seconds (including connection)
- Later runs: 0.5-1 second (reusing connection)

Compare with old method:
```bash
time meshtastic --port /dev/tty.usbmodem21201 --sendtext "test1"
```

Old method should be slower due to reconnection overhead.

## Integration Test

To verify it works in your Clawdbot skill:

```javascript
// test.js
const MeshtasticPersistent = require('./scripts/meshtastic-persistent.js')

async function test() {
  const mesh = new MeshtasticPersistent()
  
  try {
    console.log('Connecting...')
    await mesh.connect()
    
    console.log('Sending message...')
    const result = await mesh.process('broadcast: integration test')
    console.log(result)
    
  } catch (err) {
    console.error('Error:', err.message)
  } finally {
    mesh.disconnect()
  }
}

test()
```

Run it:
```bash
node test.js
```

## Monitoring

Watch for ETIMEDOUT errors in production by:
1. Logging all errors: `MESH_DEBUG=true`
2. Monitoring process spawning: `ps aux | grep meshtastic | wc -l`
3. Checking message latency: `time node scripts/meshtastic-persistent.js ...`

The persistent wrapper should:
- Spawn 0 new processes (reuses single connection)
- Complete messages in <1s
- Show 0 ETIMEDOUT errors

---

**Questions?** Check IMPLEMENTATION.md for detailed architecture and PERSISTENT_SOLUTION.md for overview.
