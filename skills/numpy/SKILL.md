---
name: NumPy
slug: numpy
version: 1.0.0
homepage: https://clawic.com/skills/numpy
description: Write fast, memory-efficient numerical code with arrays, broadcasting, vectorization, and linear algebra.
metadata: {"clawdbot":{"emoji":"🔢","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines. Creates `~/numpy/` to store preferences and snippets.

## When to Use

User needs numerical computing in Python. Agent handles array operations, mathematical computations, linear algebra, and data manipulation with NumPy.

## Architecture

Memory lives in `~/numpy/`. See `memory-template.md` for structure.

```
~/numpy/
├── memory.md      # Preferences + common patterns used
└── snippets/      # User's saved code patterns
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Vectorize First
Never use Python loops for array operations. NumPy's vectorized operations are 10-100x faster.

```python
# BAD - Python loop
result = []
for x in arr:
    result.append(x * 2)

# GOOD - Vectorized
result = arr * 2
```

### 2. Understand Broadcasting
Broadcasting allows operations on arrays of different shapes. Know the rules:
- Dimensions align from the right
- Size-1 dimensions stretch to match
- Missing dimensions treated as size-1

```python
# Shape (3,1) + (4,) broadcasts to (3,4)
a = np.array([[1], [2], [3]])  # (3,1)
b = np.array([10, 20, 30, 40])  # (4,)
result = a + b  # (3,4)
```

### 3. Prefer Views Over Copies
Slicing returns views (same memory). Use `.copy()` only when needed.

```python
# View - modifying b changes a
b = a[::2]

# Copy - independent
b = a[::2].copy()
```

### 4. Use Appropriate Dtypes
Choose the smallest dtype that fits your data. Saves memory and speeds up computation.

```python
# For integers 0-255
arr = np.array(data, dtype=np.uint8)

# For floats that don't need double precision
arr = np.array(data, dtype=np.float32)
```

### 5. Axis Awareness
Most functions accept `axis` parameter. Know your axes:
- `axis=0`: operate along rows (down columns)
- `axis=1`: operate along columns (across rows)
- `axis=None` or omit: operate on flattened array

```python
arr = np.array([[1, 2], [3, 4]])
np.sum(arr, axis=0)  # [4, 6] - sum each column
np.sum(arr, axis=1)  # [3, 7] - sum each row
```

### 6. Leverage Built-in Functions
NumPy has optimized functions for common operations. Don't reinvent them.

| Need | Use |
|------|-----|
| Element-wise math | `np.sin`, `np.exp`, `np.log` |
| Statistics | `np.mean`, `np.std`, `np.median` |
| Linear algebra | `np.dot`, `np.linalg.*` |
| Sorting | `np.sort`, `np.argsort` |
| Searching | `np.where`, `np.searchsorted` |

## NumPy Traps

### Shape Mismatches
```python
# TRAP: Confusing (n,) with (n,1) or (1,n)
a = np.array([1, 2, 3])      # shape (3,)
b = np.array([[1, 2, 3]])    # shape (1,3)
c = np.array([[1], [2], [3]])  # shape (3,1)

# FIX: Use reshape or newaxis
a.reshape(-1, 1)  # (3,1)
a[np.newaxis, :]  # (1,3)
```

### Silent Type Coercion
```python
# TRAP: Integer array silently truncates floats
arr = np.array([1, 2, 3])  # int64
arr[0] = 1.9  # becomes 1, not 1.9!

# FIX: Declare dtype upfront
arr = np.array([1, 2, 3], dtype=np.float64)
```

### View vs Copy Confusion
```python
# TRAP: Fancy indexing returns copy, slicing returns view
arr = np.array([1, 2, 3, 4, 5])

# This is a VIEW (changes affect original)
view = arr[1:4]

# This is a COPY (independent)
copy = arr[[1, 2, 3]]
```

### Broadcasting Surprises
```python
# TRAP: Unexpected broadcasting
a = np.array([1, 2, 3])
b = np.array([1, 2])
a + b  # ERROR - shapes don't broadcast

# TRAP: Accidental broadcasting
a = np.zeros((3, 4))
b = np.array([1, 2, 3])
a + b  # ERROR - (3,4) and (3,) don't align
a + b.reshape(-1, 1)  # Works - (3,4) and (3,1)
```

### In-Place Operations
```python
# TRAP: Some operations modify in-place, others don't
np.sort(arr)        # Returns sorted copy
arr.sort()          # Sorts in-place

# Safe pattern: be explicit
arr = np.sort(arr)  # Clear intent
```

## Essential Patterns

### Create Arrays
```python
np.zeros((3, 4))           # All zeros
np.ones((3, 4))            # All ones
np.full((3, 4), 7)         # All sevens
np.eye(3)                  # Identity matrix
np.arange(0, 10, 2)        # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)       # [0, 0.25, 0.5, 0.75, 1]
np.random.rand(3, 4)       # Uniform [0,1)
np.random.randn(3, 4)      # Normal distribution
```

### Reshape and Stack
```python
arr.reshape(2, 6)          # New shape (must match size)
arr.flatten()              # 1D copy
arr.ravel()                # 1D view
np.concatenate([a, b])     # Join along existing axis
np.stack([a, b])           # Join along new axis
np.vstack([a, b])          # Stack vertically
np.hstack([a, b])          # Stack horizontally
```

### Boolean Indexing
```python
arr = np.array([1, 5, 3, 8, 2])
mask = arr > 3
arr[mask]                  # [5, 8]
arr[arr > 3] = 0           # Replace values > 3 with 0
np.where(arr > 3, 1, 0)    # 1 where >3, else 0
```

### Linear Algebra
```python
np.dot(a, b)               # Matrix multiplication
a @ b                      # Same (Python 3.5+)
np.linalg.inv(a)           # Inverse
np.linalg.det(a)           # Determinant
np.linalg.eig(a)           # Eigenvalues/vectors
np.linalg.solve(a, b)      # Solve Ax = b
```

## Security & Privacy

**Data that stays local:**
- All computations run locally
- Code patterns saved in ~/numpy/

**This skill does NOT:**
- Send data externally
- Access files outside ~/numpy/
- Require network connectivity

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `data` — data processing workflows
- `math` — mathematical computations
- `statistics` — statistical analysis

## Feedback

- If useful: `clawhub star numpy`
- Stay updated: `clawhub sync`
