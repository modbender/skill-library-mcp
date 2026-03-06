# GoldenSeed for ClawHub

**Deterministic entropy streams for reproducible testing and procedural generation**

## Why Agents Need This

As an agent, you've probably hit these problems:

1. **Flaky tests** - "It passed locally but failed in CI" because random values changed
2. **Debugging randomness** - Can't reproduce the exact bug because random state is gone  
3. **Procedural generation** - Generated content but can't prove it came from your seed
4. **Statistical testing** - Need fair randomness but stdlib random isn't provably balanced

GoldenSeed solves all of these with **deterministic, verifiable, statistically perfect entropy**.

## Key Features for Agents

✅ **Perfect 50/50 coin flip** - Not just reproducible, but provably fair  
✅ **Hash verification** - Prove output came from declared seed  
✅ **Zero dependencies** - Pure Python, works anywhere  
✅ **Infinite streams** - Generate unlimited data from tiny seeds  
✅ **Cross-platform** - Same seed = same output on all platforms  

⚠️ **Not cryptographically secure** - Use for testing/generation, not passwords/keys

## Quick Examples

### Debug Flaky Tests

```python
from gq import UniversalQKD

# Before: random values make bugs irreproducible
import random
test_value = random.randint(1, 100)  # Different every time!

# After: same seed = same test conditions
gen = UniversalQKD()
test_value = next(gen)[0] % 100 + 1  # Reproducible!
```

### Verify Procedural Output

```python
from gq import UniversalQKD
import hashlib

# Generate world with proof
gen = UniversalQKD()
world_data = b''.join([next(gen) for _ in range(1000)])
proof = hashlib.sha256(world_data).hexdigest()

print(f"Generated 16KB world with hash: {proof}")
# Anyone can verify by running same seed
```

### Perfect Statistical Distribution

```python
from gq import UniversalQKD

# Prove 50/50 fairness
gen = UniversalQKD()
heads = sum(1 for _ in range(1_000_000) if next(gen)[0] & 1)
print(f"Heads ratio: {heads/1_000_000:.6f}")
# Output: 0.500xxx - always within 0.1% of perfect balance
```

## Installation

```bash
pip install golden-seed
```

## When to Use This

**Good use cases:**
- 🧪 Reproducible integration tests
- 🎮 Procedural game worlds
- 🎨 Generative art/music
- 📊 Monte Carlo simulations
- 🎲 Fair competitive RNG

**Don't use for:**
- 🔒 Password generation
- 🔑 Cryptographic keys  
- 🛡️ Security tokens
- 🔐 Anything crypto-related

For security: use `secrets` module or `os.urandom()`

## Statistical Quality

GoldenSeed isn't just deterministic - it's **statistically perfect**:

- **Perfect 50/50 bit distribution** (verified across millions of samples)
- **No detectable patterns** in bit sequences
- **Golden ratio-based mixing** provides high-quality entropy
- **Passes standard randomness tests** (Chi-square, runs test, etc.)

This matters for competitive games, fair simulations, and anywhere "provably random" matters.

## Multi-Language Support

Same seed = same output across:
- Python (install via pip)
- JavaScript, C, C++, Go, Rust, Java (see repo)

Perfect for cross-platform verification!

## Links

- **GitHub**: https://github.com/COINjecture-Network/seed  
- **PyPI**: https://pypi.org/project/golden-seed/  
- **Full Docs**: See README.md in repository
- **Examples**: `examples/` directory has 10+ demos

## License

GPL-3.0+ (with military use restrictions)

---

**TL;DR**: GoldenSeed = reproducible randomness with perfect statistics. Use it when you need identical test data, verifiable procedural generation, or provably fair RNG. Don't use it for passwords.
