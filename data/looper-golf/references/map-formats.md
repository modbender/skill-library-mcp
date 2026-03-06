# Map Formats Reference

## Grid Format (Default)

The default map format is an **annotated grid** where every cell carries its own coordinates:

```
200y: .(-20) F(-15) G(-10) G(-5) G(0) g(5)
150y: .(-20) .(-15) .(-10) .(-5) .(0) .(5)
 50y: T(-15) T(-10) .(-5) .(0) .(5)
  0y: O(0)
```

- **Row label** = yards ahead of your ball
- **`symbol(N)`** = N is yards right (positive) or left (negative) of your ball
- Only interesting features are shown (rough/OOB are omitted)

## ASCII Map Format

An ASCII art rendering with rulers on the left and bottom:

```
node "{baseDir}/dist/cli.js" look --mapFormat ascii
```

Set permanently:
```
node "{baseDir}/dist/cli.js" start --mapFormat ascii --courseId <id>
```

The ASCII map shows the full hole layout as a character grid with:
- Left ruler: yards ahead/behind your ball
- Bottom ruler: yards right/left of your ball
- Full terrain rendering including rough

## Map Resolution

Both formats support `--yardsPerCell` to control detail level:

```
node "{baseDir}/dist/cli.js" look --yardsPerCell 3
```

| yardsPerCell | Detail level |
|:---:|:---|
| 2 | Ultra-high detail |
| 3 | High detail |
| 5 | Standard (default) |
| 10 | Low detail, minimal tokens |

## Map Symbols

- `F` = Flag, `G` = Green, `g` = Collar, `.` = Fairway, `;` = Rough
- `S` = Bunker, `s` = Greenside bunker, `W` = Water, `T` = Tee, `O` = Your ball
