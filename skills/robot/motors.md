# Motors — Types, Drivers & Control

## Motor Types Comparison

| Type | Precision | Torque | Speed | Use Case |
|------|-----------|--------|-------|----------|
| DC Brushed | Low | Medium | High | Wheels, fans |
| DC Brushless | Medium | High | Very High | Drones, spindles |
| Servo (hobby) | High | Low | Medium | Arms, pan/tilt |
| Servo (industrial) | Very High | High | Medium | CNC, robots |
| Stepper | Very High | Medium | Low | 3D printers, CNC |

## DC Motors

### L298N Driver (2A per channel)

```
Power: 5V-35V motor supply
Logic: 5V (from board or onboard regulator)
Enable: PWM for speed control
IN1/IN2: Direction
```

```cpp
const int ENA = 9;   // PWM
const int IN1 = 8;
const int IN2 = 7;

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
}

void setMotor(int speed) {  // -255 to 255
  if (speed > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, speed);
  } else if (speed < 0) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, -speed);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);
  }
}
```

### TB6612FNG (1.2A per channel, more efficient)

```cpp
// Same logic as L298N but:
// - STBY pin must be HIGH to enable
// - Lower voltage drop (MOSFET vs BJT)
// - Better for battery-powered robots

const int STBY = 10;

void setup() {
  // ... pin setup ...
  pinMode(STBY, OUTPUT);
  digitalWrite(STBY, HIGH);  // Enable driver
}
```

### BTS7960 (43A, high power)

```cpp
// For motors >2A (power wheels, e-bikes)
const int RPWM = 5;
const int LPWM = 6;
const int R_EN = 7;
const int L_EN = 8;

void setup() {
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);
  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);
}

void setMotor(int speed) {
  if (speed > 0) {
    analogWrite(RPWM, speed);
    analogWrite(LPWM, 0);
  } else {
    analogWrite(RPWM, 0);
    analogWrite(LPWM, -speed);
  }
}
```

## Servo Motors

### Hobby Servo (SG90, MG996R)

```
Signal: 50Hz PWM
Pulse width: 500μs (0°) to 2500μs (180°)
Power: 4.8V-6V (SEPARATE from logic!)
```

```cpp
// Arduino
#include <Servo.h>
Servo myServo;

void setup() {
  myServo.attach(9);
}

void loop() {
  myServo.write(90);  // Center
}
```

```cpp
// ESP32 — different library!
#include <ESP32Servo.h>
Servo myServo;

void setup() {
  myServo.attach(13, 500, 2500);  // pin, min_us, max_us
}
```

**Trap:** Servos draw 500mA+ when moving. Jitter = power issue.

### PCA9685 (16-channel PWM driver)

```cpp
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

void setup() {
  pwm.begin();
  pwm.setPWMFreq(50);  // 50Hz for servos
}

void setServo(uint8_t channel, int angle) {
  // Map 0-180 to pulse length
  int pulse = map(angle, 0, 180, 102, 512);  // ~500-2500μs at 50Hz
  pwm.setPWM(channel, 0, pulse);
}
```

## Stepper Motors

### A4988 / DRV8825 Driver

```
STEP: Pulse = one step
DIR: HIGH/LOW = direction
MS1/MS2/MS3: Microstepping selection
ENABLE: LOW = enabled (active low!)
```

```cpp
const int STEP_PIN = 3;
const int DIR_PIN = 4;
const int ENABLE_PIN = 5;

void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);  // Enable
}

void step(int steps, int delayUs) {
  for (int i = 0; i < abs(steps); i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(delayUs);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(delayUs);
  }
}

void setDirection(bool clockwise) {
  digitalWrite(DIR_PIN, clockwise ? HIGH : LOW);
}
```

### Microstepping Table

| MS1 | MS2 | MS3 | Resolution |
|-----|-----|-----|------------|
| LOW | LOW | LOW | Full step |
| HIGH | LOW | LOW | 1/2 step |
| LOW | HIGH | LOW | 1/4 step |
| HIGH | HIGH | LOW | 1/8 step |
| HIGH | HIGH | HIGH | 1/16 step |

**Note:** Higher microstepping = smoother but less torque.

### AccelStepper Library (recommended)

```cpp
#include <AccelStepper.h>

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

void setup() {
  stepper.setMaxSpeed(1000);     // steps/sec
  stepper.setAcceleration(500);  // steps/sec²
}

void loop() {
  stepper.moveTo(2048);  // Target position
  stepper.run();         // Call frequently!
}
```

## Brushless DC (BLDC)

### ESC Control (drones, etc.)

```cpp
// ESCs use same signal as servos
#include <Servo.h>  // or ESP32Servo

Servo esc;

void setup() {
  esc.attach(9);
  esc.writeMicroseconds(1000);  // Arm: min throttle
  delay(2000);                   // Wait for ESC to arm
}

void setThrottle(int percent) {
  // 1000μs = 0%, 2000μs = 100%
  int us = map(percent, 0, 100, 1000, 2000);
  esc.writeMicroseconds(us);
}
```

**Warning:** ESC arming sequence varies by manufacturer. Check docs.

## Power Calculations

```
Motor current × Voltage = Power (Watts)
Battery capacity (mAh) / Average current (mA) = Runtime (hours)

Example:
- 2× motors @ 500mA each = 1A
- ESP32 @ 100mA
- Sensors @ 50mA
- Total: 1.15A
- 2200mAh battery → ~1.9 hours runtime
```

## Common Problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| Motor doesn't spin | Enable pin not set | Check STBY/EN pins |
| Motor only spins one direction | Broken H-bridge channel | Test with different IN pins |
| Motor stutters | Insufficient current | Use appropriate driver, check wiring |
| Servo jitters | Power supply noise | Separate power, add capacitor |
| Stepper skips steps | Speed too high | Reduce speed, check current limit |
| Stepper gets hot | Current too high | Adjust driver potentiometer |
