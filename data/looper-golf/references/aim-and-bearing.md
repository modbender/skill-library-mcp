# Aim & Bearing Reference

## Aim Degrees

Aim is specified in degrees, 0-360:

- **0** = straight up on the map (toward the green)
- **90** = right
- **180** = down the map (toward the tee / backward)
- **270** = left

## Bearing Tool

Calculate the aim angle to any target from your ball:

```
node "{baseDir}/dist/cli.js" bearing --ahead <yards> --right <yards>
```

- **`--ahead`**: Yards toward the green (positive) or behind you (negative).
- **`--right`**: Yards right (positive) or left (negative) of your ball.

Returns the aim angle and distance. Use the aim angle directly as `--aim` in your shot.

## Reading Coordinates from the Grid Map

The `look` command returns an **annotated grid** where each cell shows its symbol and lateral offset:

```
200y: .(-20) F(-15) G(-10) G(-5) G(0) g(5)
150y: .(-20) .(-15) .(-10) .(-5) .(0) .(5)
 50y: T(-15) T(-10) .(-5) .(0) .(5)
  0y: O(0)
```

- **Row label** (left side) = yards ahead of your ball (positive = toward green, negative = behind).
- **Cell annotation** `symbol(N)` = N is yards right of your ball (positive = right, negative = left).
- Find your target (e.g. `F(-15)` on the `200y` row), then call `bearing --ahead 200 --right -15`.

## Quick Reference

| Target position | Bearing call | Result |
|---|---|---|
| Straight ahead 200y | `bearing --ahead 200` | 0 deg |
| 200y ahead, 30y right | `bearing --ahead 200 --right 30` | ~9 deg |
| Directly right 50y | `bearing --right 50` | 90 deg |
| 200y ahead, 30y left | `bearing --ahead 200 --right -30` | ~351 deg |

## Strategic Aiming

Don't always aim at the flag. Consider:

- **Off the tee on a dogleg**: Aim at the turn in the fairway, not the green.
- **Laying up**: Pick a spot short of hazards.
- **Risk/reward**: A wider landing zone might be at a slight angle to the flag.
- **Short game**: On chips and pitches, aim at the flag unless there's a reason not to.
