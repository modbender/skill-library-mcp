# Sensors — Wiring & Code

## Distance Sensors

### HC-SR04 Ultrasonic (5V)

```
ESP32 (3.3V) wiring — NEEDS VOLTAGE DIVIDER ON ECHO

  ESP32           HC-SR04
  ─────           ───────
  5V    ─────────  VCC
  GND   ─────────  GND
  GPIO5 ─────────  TRIG
  GPIO4 ←──┬─────  ECHO
           │
          2kΩ
           │
          GND
          via
          1kΩ
```

```cpp
// ESP32 — HC-SR04
const int TRIG = 5;
const int ECHO = 4;

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
}

float getDistanceCm() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  
  long duration = pulseIn(ECHO, HIGH, 30000);  // 30ms timeout
  if (duration == 0) return -1;  // No echo
  return duration * 0.0343 / 2;
}
```

### VL53L0X ToF (I2C, 3.3V safe)

```cpp
#include <VL53L0X.h>
#include <Wire.h>

VL53L0X sensor;

void setup() {
  Wire.begin();
  sensor.init();
  sensor.setTimeout(500);
  sensor.setMeasurementTimingBudget(20000);  // 20ms, faster
}

int getDistanceMm() {
  int d = sensor.readRangeSingleMillimeters();
  if (sensor.timeoutOccurred()) return -1;
  return d;
}
```

## IMU Sensors

### MPU6050 (I2C, 3.3V or 5V)

```
Default address: 0x68
AD0 pin HIGH: 0x69
```

```cpp
#include <Wire.h>
#include <MPU6050_light.h>

MPU6050 mpu(Wire);

void setup() {
  Wire.begin();
  mpu.begin();
  mpu.calcOffsets();  // Keep robot STILL during this
}

void loop() {
  mpu.update();
  float pitch = mpu.getAngleX();
  float roll = mpu.getAngleY();
  float yaw = mpu.getAngleZ();  // Drifts without magnetometer
}
```

**Warning:** `calcOffsets()` takes ~3 seconds. Robot must be stationary.

### BNO055 (I2C, 9-DOF with fusion)

```cpp
#include <Adafruit_BNO055.h>

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  if (!bno.begin()) {
    // Sensor not found — check wiring
  }
  bno.setExtCrystalUse(true);
}

void loop() {
  sensors_event_t event;
  bno.getEvent(&event);
  float heading = event.orientation.x;  // 0-360
  float pitch = event.orientation.y;
  float roll = event.orientation.z;
}
```

## Temperature & Humidity

### DHT22 (Digital, 3.3V or 5V)

```cpp
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  dht.begin();
}

void loop() {
  delay(2000);  // MINIMUM 2 seconds between reads
  
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  if (isnan(h) || isnan(t)) {
    // Read failed — check wiring, wait longer
    return;
  }
}
```

**Trap:** Reading faster than 2s returns NaN or stale values.

### BMP280 / BME280 (I2C)

```cpp
#include <Adafruit_BMP280.h>

Adafruit_BMP280 bmp;

void setup() {
  if (!bmp.begin(0x76)) {  // or 0x77
    // Not found
  }
}

void loop() {
  float temp = bmp.readTemperature();
  float pressure = bmp.readPressure();  // Pa
  float altitude = bmp.readAltitude(1013.25);  // hPa at sea level
}
```

## IR Sensors

### TCRT5000 Line Sensor

```cpp
const int IR_PIN = A0;
const int THRESHOLD = 500;

bool isOnLine() {
  return analogRead(IR_PIN) > THRESHOLD;  // Dark = high value
}
```

**Calibration required:** Print surface, ambient light affect threshold.

### Sharp GP2Y0A21 IR Distance (10-80cm)

```cpp
const int IR_PIN = A0;

float getDistanceCm() {
  int raw = analogRead(IR_PIN);
  // Voltage to distance formula (varies by model)
  float voltage = raw * (5.0 / 1023.0);
  return 27.86 * pow(voltage, -1.15);  // Approximate
}
```

## Encoders

### Quadrature Encoder (A/B channels)

```cpp
volatile long encoderCount = 0;
const int ENC_A = 2;  // Must be interrupt-capable
const int ENC_B = 3;

void IRAM_ATTR encoderISR() {
  if (digitalRead(ENC_B)) {
    encoderCount++;
  } else {
    encoderCount--;
  }
}

void setup() {
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, RISING);
}

long getCount() {
  noInterrupts();
  long count = encoderCount;
  interrupts();
  return count;
}
```

**Note:** ESP32 uses `IRAM_ATTR` for ISR. Arduino doesn't need it.

## Common I2C Addresses

| Sensor | Default | Alternate |
|--------|---------|-----------|
| MPU6050 | 0x68 | 0x69 (AD0 high) |
| BMP280 | 0x76 | 0x77 |
| BNO055 | 0x28 | 0x29 |
| OLED SSD1306 | 0x3C | 0x3D |
| VL53L0X | 0x29 | Programmable |
| PCA9685 | 0x40 | 0x40-0x7F |

## I2C Scanner (First Debug Step)

```cpp
#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  
  Serial.println("Scanning...");
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("Found: 0x%02X\n", addr);
    }
  }
  Serial.println("Done.");
}

void loop() {}
```
