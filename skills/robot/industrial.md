# Industrial Robotics — Safety Critical

## ⚠️ SIMULATION vs REAL HARDWARE

Before generating ANY motion code, clarify:
1. **Target:** Simulation (RobotStudio, KUKA.Sim) or real robot?
2. **Safety:** If real, what safety systems are in place?
3. **Speed:** Start at ≤10% speed for testing

Code that works in simulation can cause injury on real hardware.

## Motion Types

| Command | Path | Use Case | Danger |
|---------|------|----------|--------|
| MoveJ / PTP | Joint space (unpredictable) | Reorientation, clear space | Path goes through obstacles |
| MoveL / LIN | Straight line | Welding, dispensing | Singularities cause joint whip |
| MoveC / CIRC | Arc | Curved paths | Requires 3 points minimum |

**Rule:** Always MoveJ to approach → MoveL for precision work.

## Singularities — Where Robots Lose Control

| Type | Position | Symptom |
|------|----------|---------|
| Wrist | J4 and J6 axes aligned | J4/J6 spin rapidly |
| Shoulder | Wrist center on J1 axis | J1 spins uncontrolled |
| Elbow | Arm fully extended/folded | Infinite solutions |

**Solution:** Plan paths that avoid these zones. Use MoveJ to pass through.

## Coordinate Frames

| Frame | Description | When to Use |
|-------|-------------|-------------|
| World | Fixed reference (floor) | Multi-robot cells |
| Base | Robot mounting point | Single robot, default |
| Tool (TCP) | End effector tip | Welding torch, gripper |
| Workobject | Workpiece reference | Part on table |

**Common error:** Wrong frame = wrong position. Always specify explicitly.

## Language Quick Reference

### ABB RAPID (IRC5)
```
MODULE MainModule
    PROC main()
        MoveJ home, v500, fine, tool0;        ! Joint move to home
        MoveL pick, v100, z10, gripper;       ! Linear to pick position
        Set DO_Gripper;                        ! Digital output ON
        WaitTime 0.5;
        MoveL place, v100, fine, gripper;
        Reset DO_Gripper;
    ENDPROC
ENDMODULE
```

### KUKA KRL (KRC4/5)
```
DEF main()
    $VEL.CP = 0.5                              ; Cartesian velocity m/s
    $ACC.CP = 1.0                              ; Acceleration
    
    PTP HOME                                   ; Joint move
    LIN pick_pos C_DIS                         ; Linear with blending
    $OUT[1] = TRUE                             ; Digital output
    WAIT SEC 0.5
    LIN place_pos                              ; Linear exact
    $OUT[1] = FALSE
END
```

### Universal Robots (URScript)
```python
def main():
    # Velocity: joint rad/s, linear m/s
    movej(home, a=1.4, v=1.05)                # Joint move
    movel(pick_pos, a=1.2, v=0.25)            # Linear move
    set_digital_out(0, True)                   # Gripper close
    sleep(0.5)
    movel(place_pos, a=1.2, v=0.25)
    set_digital_out(0, False)
```

## Safety Interlocks — NEVER Bypass

```
// BAD — ignores safety, robot continues
WHILE NOT SafetyOK DO
    WaitTime 0.1;
ENDWHILE

// GOOD — stops and requires manual intervention
IF NOT SafetyOK THEN
    Stop;
    TPWrite "Safety system triggered - check area";
    ! Robot halts, operator must acknowledge
ENDIF
```

## Speed Limits by Zone

| Zone | Max Speed | Typical Use |
|------|-----------|-------------|
| Collaborative (human present) | 250 mm/s | UR cobots, shared workspace |
| Restricted (fenced, light curtain) | 1000 mm/s | Standard industrial |
| Emergency (safety triggered) | 0 | Immediate stop |

**Code must check zone before setting speed.** Hardcoded high speeds = safety violation.

## TCP Calibration — Cannot Generate

Tool Center Point requires physical measurement:
1. Touch fixed point from 4+ orientations
2. Controller calculates offset
3. Store named tool

**Never assume TCP values.** Always ask: "Is the tool calibrated? What's the tool name?"
