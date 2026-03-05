---
name: goldenseed
description: Deterministic entropy streams for reproducible testing and procedural generation. Perfect 50/50 statistical distribution with hash verification. Not cryptographically secure - use for testing, worldgen, and scenarios where reproducibility matters more than unpredictability.
tags: [testing, procedural-generation, deterministic, reproducibility, golden-ratio]
version: 1.0.0
author: beanapologist
license: GPL-3.0+
---

# GoldenSeed - Deterministic Entropy for Agents

**Reproducible randomness when you need identical results every time.**

## What This Does

GoldenSeed generates infinite deterministic byte streams from tiny fixed seeds. Same seed → same output, always. Perfect for:

- ✅ **Testing reproducibility**: Debug flaky tests by replaying exact random sequences
- ✅ **Procedural generation**: Create verifiable game worlds, art, music from seeds
- ✅ **Scientific simulations**: Reproducible Monte Carlo, physics engines
- ✅ **Statistical testing**: Perfect 50/50 coin flip distribution (provably fair)
- ✅ **Hash verification**: Prove output came from declared seed

## What This Doesn't Do

⚠️ **NOT cryptographically secure** - Don't use for passwords, keys, or security tokens. Use `os.urandom()` or `secrets` module for crypto.

## Quick Start

### Installation

```bash
pip install golden-seed
```

### Basic Usage

```python
from gq import UniversalQKD

# Create generator with default seed
gen = UniversalQKD()

# Generate 16-byte chunks
chunk1 = next(gen)
chunk2 = next(gen)

# Same seed = same sequence (reproducibility!)
gen1 = UniversalQKD()
gen2 = UniversalQKD()
assert next(gen1) == next(gen2)  # Always identical
```

### Statistical Quality - Perfect 50/50 Coin Flip

```python
from gq import UniversalQKD

def coin_flip_test(n=1_000_000):
    """Demonstrate perfect 50/50 distribution"""
    gen = UniversalQKD()
    heads = 0
    
    for _ in range(n):
        byte = next(gen)[0]  # Get first byte
        if byte & 1:  # Check LSB
            heads += 1
    
    ratio = heads / n
    print(f"Heads: {ratio:.6f} (expected: 0.500000)")
    return abs(ratio - 0.5) < 0.001  # Within 0.1%

assert coin_flip_test()  # ✓ Passes every time
```

### Reproducible Testing

```python
from gq import UniversalQKD

class TestDataGenerator:
    def __init__(self, seed=0):
        self.gen = UniversalQKD()
        # Skip to seed position
        for _ in range(seed):
            next(self.gen)
    
    def random_user(self):
        data = next(self.gen)
        return {
            'id': int.from_bytes(data[0:4], 'big'),
            'age': 18 + (data[4] % 50),
            'premium': bool(data[5] & 1)
        }

# Same seed = same test data every time
def test_user_pipeline():
    users = TestDataGenerator(seed=42)
    user1 = users.random_user()
    
    # Run again - identical results!
    users2 = TestDataGenerator(seed=42)
    user1_again = users2.random_user()
    
    assert user1 == user1_again  # ✓ Reproducible!
```

### Procedural World Generation

```python
from gq import UniversalQKD

class WorldGenerator:
    def __init__(self, world_seed=0):
        self.gen = UniversalQKD()
        for _ in range(world_seed):
            next(self.gen)
    
    def chunk(self, x, z):
        """Generate deterministic chunk at coordinates"""
        data = next(self.gen)
        return {
            'biome': data[0] % 10,
            'elevation': int.from_bytes(data[1:3], 'big') % 256,
            'vegetation': data[3] % 100,
            'seed_hash': data.hex()[:16]  # For verification
        }

# Generate infinite world from single seed
world = WorldGenerator(world_seed=12345)
chunk = world.chunk(0, 0)
print(f"Biome: {chunk['biome']}, Elevation: {chunk['elevation']}")
print(f"Verifiable hash: {chunk['seed_hash']}")
```

### Hash Verification

```python
from gq import UniversalQKD
import hashlib

def generate_with_proof(seed=0, n_chunks=1000):
    """Generate data with hash proof"""
    gen = UniversalQKD()
    for _ in range(seed):
        next(gen)
    
    chunks = [next(gen) for _ in range(n_chunks)]
    data = b''.join(chunks)
    proof = hashlib.sha256(data).hexdigest()
    
    return data, proof

# Anyone with same seed can verify
data1, proof1 = generate_with_proof(seed=42, n_chunks=100)
data2, proof2 = generate_with_proof(seed=42, n_chunks=100)

assert data1 == data2      # ✓ Same output
assert proof1 == proof2    # ✓ Same hash
```

## Agent Use Cases

### Debugging Flaky Tests

When your tests pass sometimes and fail sometimes, replace random values with GoldenSeed to reproduce exact scenarios:

```python
# Instead of:
import random
value = random.randint(1, 100)  # Different every time

# Use:
from gq import UniversalQKD
gen = UniversalQKD()
value = next(gen)[0] % 100 + 1  # Same value for same seed
```

### Procedural Art Generation

Generate art, music, or NFTs with verifiable seeds:

```python
def generate_art(seed):
    gen = UniversalQKD()
    for _ in range(seed):
        next(gen)
    
    # Generate deterministic art parameters
    palette = [next(gen)[i % 16] for i in range(10)]
    composition = next(gen)
    
    return create_artwork(palette, composition)

# Seed 42 always produces the same artwork
art = generate_art(seed=42)
```

### Competitive Game Fairness

Prove game outcomes were fair by sharing the seed:

```python
class FairDice:
    def __init__(self, game_seed):
        self.gen = UniversalQKD()
        for _ in range(game_seed):
            next(self.gen)
    
    def roll(self):
        return (next(self.gen)[0] % 6) + 1

# Players can verify rolls by running same seed
dice = FairDice(game_seed=99999)
rolls = [dice.roll() for _ in range(100)]
# Share seed 99999 - anyone can verify identical sequence
```

## References

- **GitHub**: https://github.com/COINjecture-Network/seed
- **PyPI**: https://pypi.org/project/golden-seed/
- **Examples**: See `examples/` directory in repository
- **Statistical Tests**: See `docs/ENTROPY_ANALYSIS.md`

## Multi-Language Support

Identical output across platforms:
- Python (this skill)
- JavaScript (`examples/binary_fusion_tap.js`)
- C, C++, Go, Rust, Java (see repository)

## License

GPL-3.0+ with restrictions on military applications.

See LICENSE in repository for details.

---

**Remember**: GoldenSeed is for *reproducibility*, not *security*. When debugging fails, need identical test data, or generating verifiable procedural content, GoldenSeed gives you determinism with statistical quality. For crypto, use `secrets` module.
