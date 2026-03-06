---
name: math-slop
description: Generate satirical "math slop" ragebait formulas that connect famous constants (φ, π, e, i) in trivially true but profound-looking equations. Outputs LaTeX. Use for math memes or when someone asks for "math slop."
---

# Math Slop Generator

Generate single-line "ragebait" formulas connecting famous constants in ways that look profound but are trivially true.

## Quick Generate

```bash
node scripts/generate-slop.js

# Multiple formulas
node scripts/generate-slop.js --count 5
```

## Example Output

- `\varphi^{\ln e} = \varphi^{i^4}` → φ¹ = φ¹
- `e^{i\pi} + 1 + \gamma = 0 + \gamma` → Euler + γ both sides
- `\tau - 2\pi = e^{i\pi} + 1` → 0 = 0
- `\sqrt{2}^{\,2} = 2^{\sin^2 x + \cos^2 x}` → 2 = 2¹

## Rendering

The script outputs LaTeX. To render as an image, use any LaTeX renderer:
- Online: latex.codecogs.com, quicklatex.com
- Local: pdflatex, mathjax, katex

## Formula Types

- **Add zeros**: `(φ-φ)`, `ln(1)`, `e^{iπ}+1`, `sin(0)`
- **Multiply by ones**: `e^0`, `i⁴`, `sin²θ+cos²θ`
- **Both sides**: same constant added/multiplied to both sides
- **Euler mashups**: variations on e^{iπ}+1=0
- **Golden ratio**: φ² = φ+1 variations
