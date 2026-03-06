# Project Templates — Common Robot Builds

## Line Follower

### Hardware
- Board: Arduino Nano or ESP32
- Sensors: 3-5× TCRT5000 or QTR-8A array
- Motors: 2× N20 or TT motors with encoder
- Driver: TB6612FNG or L298N
- Power: 2S LiPo (7.4V) or 4×AA

### Wiring Diagram
```
                    TCRT5000 Array
                    [1][2][3][4][5]
                         │
                    Analog pins
                         │
┌─────────────────────────────────────┐
│           Arduino/ESP32             │
│  PWM1 PWM2  IN1 IN2 IN3 IN4        │
└──┬────┬─────┬───┬───┬───┬──────────┘
   │    │     │   │   │   │
┌──┴────┴─────┴───┴───┴───┴──┐
│        TB6612FNG           │
│   PWMA PWMB AIN1 AIN2 BIN1 BIN2    │
│         MOTORA    MOTORB   │
└─────────┬───────────┬──────┘
          M1          M2
```

### Core Algorithm
```cpp
const int sensors[] = {A0, A1, A2, A3, A4};
const int NUM_SENSORS = 5;
int sensorValues[NUM_SENSORS];
int weights[] = {-2, -1, 0, 1, 2};  // Position weights

int getLinePosition() {
  long weightedSum = 0;
  long sum = 0;
  
  for (int i = 0; i < NUM_SENSORS; i++) {
    sensorValues[i] = analogRead(sensors[i]);
    weightedSum += (long)sensorValues[i] * weights[i] * 1000;
    sum += sensorValues[i];
  }
  
  if (sum == 0) return 0;  // No line detected
  return weightedSum / sum;
}

void loop() {
  int position = getLinePosition();
  
  // PID control
  int error = position - 0;  // Target = center
  int motorSpeed = Kp * error + Kd * (error - lastError);
  lastError = error;
  
  setMotors(baseSpeed + motorSpeed, baseSpeed - motorSpeed);
}
```

---

## Self-Balancing Robot

### Hardware
- Board: ESP32 (faster PWM, more memory)
- IMU: MPU6050 or BNO055 (better)
- Motors: 2× JGA25-370 with encoder (high torque)
- Driver: TB6612FNG or L298N
- Power: 3S LiPo (11.1V)

### Key Code
```cpp
#include <MPU6050_light.h>

MPU6050 mpu(Wire);
float Kp = 60, Ki = 0.5, Kd = 20;
float integral = 0, lastError = 0;
float targetAngle = -2.5;  // Tune this! Robot leans slightly

void setup() {
  Wire.begin();
  mpu.begin();
  mpu.calcOffsets();  // KEEP STILL!
}

void loop() {
  mpu.update();
  float angle = mpu.getAngleX();
  
  float error = angle - targetAngle;
  integral += error;
  integral = constrain(integral, -100, 100);  // Anti-windup
  float derivative = error - lastError;
  
  float output = Kp*error + Ki*integral + Kd*derivative;
  output = constrain(output, -255, 255);
  
  setMotors(output, output);  // Both same direction
  lastError = error;
  
  delay(5);  // 200Hz control loop
}
```

**Tuning order:** Kp first (until oscillates), then Kd (dampen), finally Ki (steady-state).

---

## Robot Arm (3-6 DOF)

### Hardware
- Board: Arduino Mega (more PWM) or ESP32 + PCA9685
- Servos: MG996R (base, shoulder) + SG90 (wrist, gripper)
- Power: 5V 3A+ supply (SEPARATE from logic)
- Frame: Acrylic or 3D printed

### Inverse Kinematics (2-link planar)
```cpp
// For shoulder + elbow arm in XY plane
float L1 = 100;  // Upper arm length (mm)
float L2 = 100;  // Forearm length (mm)

bool inverseKinematics(float x, float y, float &theta1, float &theta2) {
  float d = sqrt(x*x + y*y);
  if (d > L1 + L2) return false;  // Unreachable
  
  float cos_theta2 = (x*x + y*y - L1*L1 - L2*L2) / (2*L1*L2);
  if (abs(cos_theta2) > 1) return false;
  
  theta2 = acos(cos_theta2);
  theta1 = atan2(y, x) - atan2(L2*sin(theta2), L1 + L2*cos(theta2));
  
  // Convert to degrees
  theta1 = theta1 * 180 / PI;
  theta2 = theta2 * 180 / PI;
  return true;
}

void moveTo(float x, float y) {
  float t1, t2;
  if (inverseKinematics(x, y, t1, t2)) {
    servo1.write(90 + t1);  // Offset to center
    servo2.write(90 + t2);
  }
}
```

---

## Differential Drive Robot (ROS2)

### Hardware
- Board: Raspberry Pi 4 + Arduino (motor control)
- Motors: JGB37-520 with encoder
- Driver: L298N or BTS7960
- Lidar: RPLidar A1 or YDLIDAR X4
- IMU: BNO055

### ROS2 Package Structure
```
my_robot/
├── my_robot/
│   ├── __init__.py
│   ├── motor_driver.py
│   └── odometry.py
├── launch/
│   └── robot.launch.py
├── config/
│   └── params.yaml
├── urdf/
│   └── robot.urdf.xacro
├── package.xml
└── setup.py
```

### Basic Motor Driver Node
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial

class MotorDriver(Node):
    def __init__(self):
        super().__init__('motor_driver')
        self.sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10)
        self.serial = serial.Serial('/dev/ttyACM0', 115200)
        
    def cmd_callback(self, msg):
        linear = msg.linear.x
        angular = msg.angular.z
        
        # Differential drive kinematics
        wheel_base = 0.2  # meters
        left = linear - angular * wheel_base / 2
        right = linear + angular * wheel_base / 2
        
        # Send to Arduino
        cmd = f"{left:.2f},{right:.2f}\n"
        self.serial.write(cmd.encode())

def main():
    rclpy.init()
    node = MotorDriver()
    rclpy.spin(node)
```

### Arduino Firmware
```cpp
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    int comma = cmd.indexOf(',');
    float left = cmd.substring(0, comma).toFloat();
    float right = cmd.substring(comma+1).toFloat();
    
    setMotorSpeed(LEFT_MOTOR, left);
    setMotorSpeed(RIGHT_MOTOR, right);
  }
  
  // Publish encoder counts
  Serial.printf("ENC:%ld,%ld\n", leftCount, rightCount);
  delay(50);
}
```

---

## Quadruped (Walking Robot)

### Hardware
- Board: ESP32 + PCA9685 (16 servos)
- Servos: 12× MG996R (3 per leg)
- Power: 6V 5A+ BEC or bench supply
- Frame: 3D printed (many designs on Thingiverse)

### Leg Numbering Convention
```
Front
  1   2
   \ /
    X
   / \
  3   4
Back

Joints per leg: Hip (horizontal), Shoulder (vertical), Knee
```

### Gait Generator (Trot)
```cpp
// Trot: diagonal legs move together
// Phase: 1-4 = steps, leg is lifted during its phase

int phase = 0;
float liftHeight = 30;  // mm
float stepLength = 40;  // mm

void trotStep() {
  for (int leg = 0; leg < 4; leg++) {
    float x, z;
    
    // Diagonal pairs: (0,3) and (1,2)
    bool isLifted = (phase % 2 == leg % 2);
    
    if (isLifted) {
      // Swing phase: lift and move forward
      x = stepLength * (phase / 2.0 - 0.5);
      z = liftHeight * sin(PI * phase / 2.0);
    } else {
      // Stance phase: on ground, push back
      x = -stepLength * (phase / 2.0 - 0.5);
      z = 0;
    }
    
    moveLegTo(leg, x, 0, z);
  }
  
  phase = (phase + 1) % 4;
  delay(100);
}
```

---

## Project Checklist Template

```markdown
## Project: _______________

### Planning
□ Define goal and success criteria
□ List required components
□ Check power budget
□ Design wiring diagram

### Hardware
□ Test each sensor individually
□ Test each actuator individually
□ Verify power rails under load
□ Check all grounds connected

### Software
□ Verify library versions
□ Test with Serial debug
□ Implement main loop
□ Add error handling

### Integration
□ Connect all components
□ Test subsystems together
□ Tune parameters (PID, thresholds)
□ Stress test (long run)

### Documentation
□ Final wiring diagram
□ Pin assignments table
□ Calibration values
□ Known issues / future work
```
