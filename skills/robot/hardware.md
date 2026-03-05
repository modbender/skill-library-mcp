# Hardware — Arduino, ESP32, Raspberry Pi

## Pin Restrictions by Board

### ESP32
| Pins | Restriction | Consequence |
|------|-------------|-------------|
| GPIO 6-11 | Flash memory | Touch = crash, boot loop |
| GPIO 34-39 | Input only | Output code compiles, does nothing |
| GPIO 0 | Boot mode | Pulled low = won't boot |
| GPIO 2 | Boot mode | Must be low or floating at boot |
| GPIO 12 | Boot mode | Must be low at boot (3.3V flash) |

### Arduino Uno/Nano
| Pins | Restriction | Consequence |
|------|-------------|-------------|
| 0, 1 | Serial TX/RX | Upload fails if connected |
| 13 | Built-in LED | External LED may conflict |
| A6, A7 (Nano) | Analog input only | digitalRead returns garbage |

### Raspberry Pi Pico
| Pins | Restriction | Consequence |
|------|-------------|-------------|
| GP23 | SMPS mode | Affects power regulation |
| GP24 | VBUS sense | Reserved for USB detection |
| GP25 | Built-in LED | Conflicts if used externally |

## Common Wiring Mistakes

```
WRONG: Motor shares 5V with Arduino
       ┌───────────┐
  USB──┤ Arduino   ├──5V──Motor
       └───────────┘
Result: Motor draws current → voltage drops → Arduino resets

RIGHT: Separate power for motor
       ┌───────────┐
  USB──┤ Arduino   │
       └─────┬─────┘
             │ GND (shared)
       ┌─────┴─────┐
  12V──┤ L298N     ├──Motor
       └───────────┘
```

## I2C Troubleshooting

```cpp
// Scan for devices — first debug step
#include <Wire.h>
void setup() {
  Wire.begin();
  Serial.begin(115200);
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("Found: 0x%02X\n", addr);
    }
  }
}
```

Common addresses:
- MPU6050: 0x68 (or 0x69 if AD0 high)
- OLED SSD1306: 0x3C (or 0x3D)
- BMP280: 0x76 (or 0x77)

If scan finds nothing:
1. Check SDA/SCL not swapped
2. Add 4.7kΩ pullups if wire length >20cm
3. Reduce I2C speed: `Wire.setClock(100000);`

## ESP32 PWM (NOT analogWrite)

```cpp
// ESP32 — ledcWrite replaces analogWrite
const int ledChannel = 0;
const int freq = 5000;
const int resolution = 8;  // 0-255

void setup() {
  ledcSetup(ledChannel, freq, resolution);
  ledcAttachPin(LED_PIN, ledChannel);
}

void loop() {
  ledcWrite(ledChannel, 127);  // 50% duty
}
```

## Servo on ESP32

```cpp
// WRONG: #include <Servo.h> — crashes or doesn't compile

// RIGHT: ESP32Servo library
#include <ESP32Servo.h>

Servo myServo;

void setup() {
  myServo.attach(13);  // Any PWM pin
}

void loop() {
  myServo.write(90);   // Center
}
```

## Power Budget Calculator

```
Component               Typical mA    Peak mA
─────────────────────────────────────────────
Arduino Uno board           50          50
ESP32 (WiFi active)        100         240
ESP32 (Bluetooth)           80         130
Servo SG90 (moving)        100         500
DC motor (small)           200         800
WS2812B LED (white)         60/LED     60/LED
HC-SR04 ultrasonic          15          15
DHT22                        2           2
OLED SSD1306                 20          20
─────────────────────────────────────────────

USB max: 500mA
If total > 400mA: use external power supply
```

## MicroPython (Pico/ESP32)

```python
from machine import Pin, PWM, I2C

# PWM for servo (50Hz)
servo = PWM(Pin(15))
servo.freq(50)
servo.duty_u16(4915)  # 1.5ms = center (duty = pulse_ms/20ms * 65535)

# I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
print(i2c.scan())  # List of addresses found

# Digital input with pull-up
button = Pin(14, Pin.IN, Pin.PULL_UP)
print(button.value())  # 0 = pressed, 1 = released
```
