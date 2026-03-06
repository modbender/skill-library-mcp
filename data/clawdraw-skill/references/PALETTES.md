# Color Palettes Reference

5 built-in scientific color palettes, sampled with `samplePalette(name, t)` where `t` ranges from 0.0 to 1.0.

## Usage

```js
import { samplePalette, lerpColor } from '../primitives/helpers.mjs';

// Sample at a specific position (0 = start, 1 = end)
const color = samplePalette('magma', 0.5);

// Interpolate between two fixed colors
const mid = lerpColor('#ff0000', '#0000ff', 0.5);
```

Colors are linearly interpolated between the palette stops, producing smooth gradients at any position.

## Palettes

### magma
Dark purple to bright yellow. Deep blacks through violets and hot pinks to fiery orange-yellow.
- Stops: `#000004` `#180f3d` `#440f76` `#721f81` `#b5367a` `#e55c30` `#fba40a` `#fcffa4`

### plasma
Deep blue to bright yellow. Rich purples through magentas and oranges to electric yellow.
- Stops: `#0d0887` `#4b03a1` `#7d03a8` `#a82296` `#cb4679` `#e86825` `#f89540` `#f0f921`

### viridis
Dark purple to bright yellow-green. Deep indigo through teals and greens to vivid chartreuse.
- Stops: `#440154` `#443a83` `#31688e` `#21908c` `#35b779` `#6ece58` `#b5de2b` `#fde725`

### turbo
Blue to red rainbow. Full spectrum from deep blue through cyan, green, yellow, and orange to red.
- Stops: `#30123b` `#4662d7` `#36aaf9` `#1ae4b6` `#72fe5e` `#c8ef34` `#faba39` `#e6550d`

### inferno
Dark purple to bright yellow. Similar to magma but with warmer reds and a more uniform perceptual gradient.
- Stops: `#000004` `#1b0c41` `#4a0c6b` `#781c6d` `#a52c60` `#cf4446` `#ed6925` `#fcffa4`

## Tips

- Use `t = i / total` to map an index to a palette position for smooth color gradients across strokes
- Palettes are perceptually uniform -- equal steps in `t` produce equal perceived color changes
- All palettes start dark (t=0) and end bright (t=1)
- Reverse a palette by using `1 - t` instead of `t`
