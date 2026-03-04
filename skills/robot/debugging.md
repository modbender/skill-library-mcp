# Debugging — Systematic Troubleshooting

## The Debug Order

Always follow this sequence. Most problems are in steps 1-3.

```
1. POWER
   ↓
2. WIRING  
   ↓
3. LIBRARY/VERSION
   ↓
4. CODE LOGIC
```

**Do NOT skip to code debugging until hardware is verified.**

## Step 1: Power Verification

### Checklist
```
□ Power LED on board is lit
□ Voltage at board matches spec (3.3V or 5V rail)
□ Voltage under load (motor running) doesn't drop >10%
□ Motors/servos on SEPARATE power from logic
□ All grounds connected together
```

### Measuring Power

```
Multimeter settings:
- DC Voltage: Check rails
- DC Current: Check total draw (in series with power)

Expected voltages:
- USB: 4.75V - 5.25V
- 3.3V rail: 3.0V - 3.6V
- LiPo 1S: 3.0V (empty) - 4.2V (full)
- LiPo 2S: 6.0V - 8.4V
```

### Common Power Problems

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Board resets randomly | Motor brownout | Separate power rails |
| Board won't boot | Voltage too low | Check USB cable, power supply |
| Works on USB, not battery | Battery voltage wrong | Check battery voltage, regulator |
| Components hot | Overcurrent | Check for shorts, reduce load |

## Step 2: Wiring Verification

### Visual Check
```
□ No loose connections
□ No bare wires touching
□ Correct pins (double-check datasheet)
□ Pull-up/pull-down resistors where needed
□ Voltage dividers for 5V→3.3V
```

### Continuity Test (Multimeter)
```
1. Power OFF
2. Set multimeter to continuity (beep mode)
3. Touch probes to both ends of each wire
4. Should beep immediately
5. Check there's NO continuity between power and ground (short check)
```

### I2C Debug

```cpp
// Run this FIRST if I2C device not responding
#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("I2C Scanner");
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.printf("Device at 0x%02X\n", addr);
    }
  }
  Serial.println("Scan complete");
}

void loop() {}
```

**If scan finds nothing:**
1. SDA/SCL swapped? (most common)
2. Pull-up resistors present? (4.7kΩ for long wires)
3. Correct voltage level? (5V device on 3.3V bus)
4. Device address correct? (check if configurable)

### SPI Debug

```
□ MOSI → MOSI (or SDI)
□ MISO → MISO (or SDO)  
□ SCK → SCK (or CLK)
□ CS → Correct chip select pin
□ Clock speed not too high (try 1MHz first)
```

## Step 3: Library & Version Check

### Arduino IDE
```cpp
// Print library version at startup
void setup() {
  Serial.begin(115200);
  
  // Most libraries have version macros
  #ifdef SERVO_VERSION
    Serial.printf("Servo: %s\n", SERVO_VERSION);
  #endif
}
```

### Common Version Conflicts

| Symptom | Cause | Fix |
|---------|-------|-----|
| Compile error on ESP32 | Arduino library on ESP32 | Use ESP32-specific library |
| "Multiple definitions" | Library installed twice | Remove duplicate from libraries folder |
| Works on Uno, fails on Mega | Pin mapping different | Check board-specific pins |
| ROS2 "module not found" | Didn't source workspace | `source install/setup.bash` |

### Library Compatibility Matrix

| Library | Arduino AVR | ESP32 | RP2040 |
|---------|-------------|-------|--------|
| Servo.h | ✅ | ❌ | ✅ |
| ESP32Servo | ❌ | ✅ | ❌ |
| Wire.h | ✅ | ✅ | ✅ |
| SPI.h | ✅ | ✅ | ✅ |
| analogWrite() | ✅ | ❌ | ✅ |

## Step 4: Code Logic Debug

### Serial Debug Pattern

```cpp
#define DEBUG 1

#if DEBUG
  #define DBG(x) Serial.println(x)
  #define DBGF(x, ...) Serial.printf(x, __VA_ARGS__)
#else
  #define DBG(x)
  #define DBGF(x, ...)
#endif

void setup() {
  Serial.begin(115200);
  DBG("Setup started");
}

void loop() {
  int sensorVal = analogRead(A0);
  DBGF("Sensor: %d\n", sensorVal);
  
  if (sensorVal > 500) {
    DBG("Threshold exceeded");
    // ... action ...
  }
}
```

### Timing Debug

```cpp
unsigned long start = micros();
// ... code to measure ...
unsigned long elapsed = micros() - start;
Serial.printf("Took %lu μs\n", elapsed);
```

### State Machine Debug

```cpp
enum State { IDLE, MOVING, STOPPED, ERROR };
State currentState = IDLE;

const char* stateNames[] = {"IDLE", "MOVING", "STOPPED", "ERROR"};

void changeState(State newState) {
  Serial.printf("State: %s -> %s\n", 
    stateNames[currentState], 
    stateNames[newState]);
  currentState = newState;
}
```

## Quick Diagnosis Table

| Symptom | First Check | Second Check | Third Check |
|---------|-------------|--------------|-------------|
| Nothing works | Power LED on? | Correct board selected? | USB cable data-capable? |
| Upload fails | Correct port? | Board in boot mode? | Another serial monitor open? |
| Sensor returns 0 | Wiring correct? | I2C address right? | Library initialized? |
| Motor doesn't move | Enable pin set? | H-bridge powered? | PWM value > 0? |
| Servo jitters | Power supply? | Signal wire loose? | PWM frequency correct? |
| Random resets | Power rail stable? | Watchdog timeout? | Stack overflow? |
| I2C hangs | Pull-ups present? | Clock stretching? | Bus locked? |

## ESP32-Specific Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Boot loop | GPIO 12 high at boot | Don't use GPIO 12, or pull low |
| WiFi crashes system | GPIO 6-11 used | These are flash pins, never use |
| ADC2 not working | WiFi is on | Use ADC1 pins when WiFi active |
| Serial garbage | Wrong baud rate | Match Serial.begin() with monitor |
| OTA fails | Partition too small | Check partition scheme in IDE |

## When to Ask for Help

After verifying:
1. ✅ Power is correct and stable
2. ✅ Wiring matches schematic
3. ✅ Correct library for board
4. ✅ Serial debug shows expected flow

Provide:
- Exact board model and core version
- Library names and versions
- Schematic or clear wiring description
- Serial output showing the problem
- What you already tried
