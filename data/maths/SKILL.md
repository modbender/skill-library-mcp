---
name: pywayne-maths
description: Mathematical utility functions for factorization, digit counting, and large integer multiplication using Karatsuba algorithm. Use when solving number theory problems, computing factors, counting digit occurrences, or performing optimized large integer multiplication.
---

# Pywayne Maths

Mathematical utility functions for number theory, digit analysis, and optimized integer operations.

## Quick Start

```python
from pywayne.maths import get_all_factors, digitCount, karatsuba_multiplication

# Get all factors of a number
factors = get_all_factors(28)
print(factors)  # [1, 2, 4, 7, 14, 28]

# Count digit occurrences
count = digitCount(100, 1)
print(count)  # 21 (digit 1 appears 21 times in 1-100)

# Large integer multiplication
product = karatsuba_multiplication(1234, 5678)
print(product)  # 7006652
```

## Functions

### get_all_factors

Return all factors of a positive integer.

```python
get_all_factors(n: int) -> list
```

**Parameters:**
- `n` - Positive integer to factorize

**Returns:**
- List of all factors of `n`

**Use Cases:**
- Number theory problems
- Finding divisors
- Simplifying fractions
- Greatest common divisor (GCD) calculation

**Example:**
```python
from pywayne.maths import get_all_factors

factors = get_all_factors(36)
print(factors)  # [1, 2, 3, 4, 6, 9, 12, 18, 36]

# Check if number is prime
n = 17
factors = get_all_factors(n)
if len(factors) == 2:  # Only 1 and itself
    print(f"{n} is prime")
else:
    print(f"{n} is not prime")
```

### digitCount

Count occurrences of digit `k` from 1 to `n`.

```python
digitCount(n, k) -> int
```

**Parameters:**
- `n` - Positive integer, upper bound of counting range
- `k` - Digit to count (0-9)

**Returns:**
- Count of digit `k` in range [1, n]

**Special Case:**
- When `k = 0`, counts all numbers with trailing zeros after `n`

**Use Cases:**
- Digit frequency analysis
- Number theory problems
- Data analysis tasks

**Example:**
```python
from pywayne.maths import digitCount

# Count digit 1 from 1 to 100
count = digitCount(100, 1)
print(count)  # 21

# Count each digit 0-9 in range 1-1000
for k in range(10):
    count = digitCount(1000, k)
    print(f"Digit {k}: {count} times")
```

### karatsuba_multiplication

Multiply two integers using Karatsuba's divide-and-conquer algorithm.

```python
karatsuba_multiplication(x: int, y: int) -> int
```

**Parameters:**
- `x` - Integer multiplier
- `y` - Integer multiplicand

**Returns:**
- Product of `x` and `y`

**Algorithm:**
- Karatsuba algorithm uses recursive divide-and-conquer to multiply large integers
- Time complexity: O(n^log₂3) ≈ O(n^1.585)
- More efficient than naive multiplication O(n²) for very large numbers

**Use Cases:**
- Large integer multiplication
- Algorithm optimization
- Competitive programming
- Cryptography applications

**Example:**
```python
from pywayne.maths import karatsuba_multiplication

# Compare with standard multiplication
a, b = 123456789, 987654321
result = karatsuba_multiplication(a, b)
print(result)  # 121932631112635269

# Verify
assert result == a * b
```

## Common Applications

### Prime Number Detection

```python
from pywayne.maths import get_all_factors

def is_prime(n):
    factors = get_all_factors(n)
    return len(factors) == 2 and factors == [1, n]

print(is_prime(17))   # True
print(is_prime(18))   # False
```

### Greatest Common Divisor (GCD)

```python
from pywayne.maths import get_all_factors

def gcd(a, b):
    factors_a = set(get_all_factors(a))
    factors_b = set(get_all_factors(b))
    common = factors_a & factors_b
    return max(common)

print(gcd(24, 36))  # 12
```

### Digit Frequency Analysis

```python
from pywayne.maths import digitCount

def digit_frequency(n):
    frequency = {}
    for k in range(10):
        frequency[k] = digitCount(n, k)
    return frequency

print(digit_frequency(1000))
# {0: 189, 1: 301, 2: 300, 3: 300, ...}
```

### Large Number Calculations

```python
from pywayne.maths import karatsuba_multiplication

# Very large numbers
x = 123456789012345678901234567890
y = 9876543210987654321098765432109876

# Use Karatsuba for efficiency
product = karatsuba_multiplication(x, y)
```

## Notes

- `get_all_factors` returns sorted unique factors
- `digitCount` counts from 1 to n inclusive
- `karatsuba_multiplication` is optimized for large integers (hundreds+ of digits)
- For small integers, standard multiplication `*` may be faster due to overhead
