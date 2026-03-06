#!/usr/bin/env bash
set -euo pipefail

cd "$1"

git init
git config user.email "dev@statspy.local"
git config user.name "Stats Developer"

# =============================================================================
# Commit 1: Initial commit — stats module with mean function
# =============================================================================
mkdir -p tests

cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)
PYEOF

cat > tests/__init__.py << 'PYEOF'
PYEOF

cat > tests/test_mean.py << 'PYEOF'
import unittest
from stats import calculate_mean


class TestMean(unittest.TestCase):
    def test_mean_integers(self):
        self.assertAlmostEqual(calculate_mean([1, 2, 3, 4, 5]), 3.0)

    def test_mean_single_value(self):
        self.assertAlmostEqual(calculate_mean([7]), 7.0)

    def test_mean_floats(self):
        self.assertAlmostEqual(calculate_mean([1.5, 2.5, 3.5]), 2.5)

    def test_mean_empty_raises(self):
        with self.assertRaises(ValueError):
            calculate_mean([])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "Initial commit: add stats module with mean function"

# =============================================================================
# Commit 2: feat: add median calculation (CORRECT implementation)
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
PYEOF

cat > tests/test_median.py << 'PYEOF'
import unittest
from stats import calculate_median


class TestMedian(unittest.TestCase):
    def test_median_odd_list(self):
        self.assertAlmostEqual(calculate_median([3, 1, 2]), 2.0)

    def test_median_even_list(self):
        self.assertAlmostEqual(calculate_median([1, 2, 3, 4]), 2.5)

    def test_median_single_value(self):
        self.assertAlmostEqual(calculate_median([42]), 42.0)

    def test_median_empty_raises(self):
        with self.assertRaises(ValueError):
            calculate_median([])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add median calculation"

# =============================================================================
# Commit 3: feat: add standard deviation
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5
PYEOF

cat > tests/test_stddev.py << 'PYEOF'
import unittest
from stats import calculate_stddev


class TestStddev(unittest.TestCase):
    def test_stddev_basic(self):
        self.assertAlmostEqual(calculate_stddev([2, 4, 4, 4, 5, 5, 7, 9]), 2.0)

    def test_stddev_identical_values(self):
        self.assertAlmostEqual(calculate_stddev([5, 5, 5, 5]), 0.0)

    def test_stddev_too_few_raises(self):
        with self.assertRaises(ValueError):
            calculate_stddev([1])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add standard deviation"

# =============================================================================
# Commit 4: feat: add mode calculation
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_mode(data):
    """Return the most frequently occurring value in a list.

    If there are multiple modes, returns the smallest one.
    """
    if not data:
        raise ValueError("calculate_mode requires at least one data point")
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_count = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_count]
    return min(modes)
PYEOF

cat > tests/test_mode.py << 'PYEOF'
import unittest
from stats import calculate_mode


class TestMode(unittest.TestCase):
    def test_mode_single_mode(self):
        self.assertEqual(calculate_mode([1, 2, 2, 3]), 2)

    def test_mode_multiple_modes(self):
        self.assertEqual(calculate_mode([1, 1, 2, 2, 3]), 1)

    def test_mode_all_same(self):
        self.assertEqual(calculate_mode([5, 5, 5]), 5)

    def test_mode_empty_raises(self):
        with self.assertRaises(ValueError):
            calculate_mode([])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add mode calculation"

# =============================================================================
# Commit 5: feat: add range calculation
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_mode(data):
    """Return the most frequently occurring value in a list.

    If there are multiple modes, returns the smallest one.
    """
    if not data:
        raise ValueError("calculate_mode requires at least one data point")
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_count = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_count]
    return min(modes)


def calculate_range(data):
    """Calculate the range (max - min) of a list of numbers."""
    if not data:
        raise ValueError("calculate_range requires at least one data point")
    return max(data) - min(data)
PYEOF

cat > tests/test_range.py << 'PYEOF'
import unittest
from stats import calculate_range


class TestRange(unittest.TestCase):
    def test_range_basic(self):
        self.assertEqual(calculate_range([1, 5, 3, 9, 2]), 8)

    def test_range_identical(self):
        self.assertEqual(calculate_range([4, 4, 4]), 0)

    def test_range_negative(self):
        self.assertEqual(calculate_range([-3, -1, -7]), 6)

    def test_range_empty_raises(self):
        with self.assertRaises(ValueError):
            calculate_range([])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add range calculation"

# =============================================================================
# Commit 6: docs: add README with usage examples
# =============================================================================
cat > README.md << 'MDEOF'
# Stats Module

A lightweight Python statistics library providing common statistical functions.

## Usage

```python
from stats import calculate_mean, calculate_median, calculate_stddev

data = [2, 4, 4, 4, 5, 5, 7, 9]

print(calculate_mean(data))      # 5.0
print(calculate_median(data))    # 4.5
print(calculate_stddev(data))    # 2.0
```

## Available Functions

- `calculate_mean(data)` — Arithmetic mean
- `calculate_median(data)` — Median (handles odd and even length lists)
- `calculate_stddev(data)` — Population standard deviation
- `calculate_mode(data)` — Mode (most frequent value)
- `calculate_range(data)` — Range (max - min)

## Running Tests

```bash
python -m pytest tests/
```
MDEOF

git add -A
git commit -m "docs: add README with usage examples"

# =============================================================================
# Commit 7: chore: add requirements.txt
# =============================================================================
cat > requirements.txt << 'EOF'
pytest>=7.0
EOF

git add -A
git commit -m "chore: add requirements.txt"

# =============================================================================
# Commit 8: refactor: optimize median — INTRODUCES BUG (off-by-one)
# =============================================================================
# The "optimization" replaces the correct even-case formula:
#   (sorted_data[mid - 1] + sorted_data[mid]) / 2
# with an INCORRECT formula:
#   (sorted_data[mid] + sorted_data[mid + 1]) / 2
#
# For [1,2,3,4]: n=4, mid=2
#   Correct: (sorted_data[1] + sorted_data[2]) / 2 = (2+3)/2 = 2.5
#   Buggy:   (sorted_data[2] + sorted_data[3]) / 2 = (3+4)/2 = 3.5
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid] + sorted_data[mid + 1]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_mode(data):
    """Return the most frequently occurring value in a list.

    If there are multiple modes, returns the smallest one.
    """
    if not data:
        raise ValueError("calculate_mode requires at least one data point")
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_count = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_count]
    return min(modes)


def calculate_range(data):
    """Calculate the range (max - min) of a list of numbers."""
    if not data:
        raise ValueError("calculate_range requires at least one data point")
    return max(data) - min(data)
PYEOF

git add -A
git commit -m "refactor: optimize median calculation for large datasets"

# =============================================================================
# Commit 9: feat: add percentile calculation
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid] + sorted_data[mid + 1]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_mode(data):
    """Return the most frequently occurring value in a list.

    If there are multiple modes, returns the smallest one.
    """
    if not data:
        raise ValueError("calculate_mode requires at least one data point")
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_count = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_count]
    return min(modes)


def calculate_range(data):
    """Calculate the range (max - min) of a list of numbers."""
    if not data:
        raise ValueError("calculate_range requires at least one data point")
    return max(data) - min(data)


def calculate_percentile(data, p):
    """Calculate the p-th percentile of a list of numbers.

    Uses linear interpolation between closest ranks.
    """
    if not data:
        raise ValueError("calculate_percentile requires at least one data point")
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]
    rank = (p / 100) * (n - 1)
    lower = int(rank)
    upper = lower + 1
    if upper >= n:
        return sorted_data[-1]
    weight = rank - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
PYEOF

cat > tests/test_percentile.py << 'PYEOF'
import unittest
from stats import calculate_percentile


class TestPercentile(unittest.TestCase):
    def test_percentile_50(self):
        self.assertAlmostEqual(calculate_percentile([1, 2, 3, 4, 5], 50), 3.0)

    def test_percentile_25(self):
        self.assertAlmostEqual(calculate_percentile([1, 2, 3, 4, 5], 25), 2.0)

    def test_percentile_0(self):
        self.assertAlmostEqual(calculate_percentile([1, 2, 3, 4, 5], 0), 1.0)

    def test_percentile_100(self):
        self.assertAlmostEqual(calculate_percentile([1, 2, 3, 4, 5], 100), 5.0)

    def test_percentile_invalid_raises(self):
        with self.assertRaises(ValueError):
            calculate_percentile([1, 2, 3], 101)


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add percentile calculation"

# =============================================================================
# Commit 10: test: skip flaky median test
# =============================================================================
cat > tests/test_median.py << 'PYEOF'
import unittest
from stats import calculate_median


class TestMedian(unittest.TestCase):
    def test_median_odd_list(self):
        self.assertAlmostEqual(calculate_median([3, 1, 2]), 2.0)

    @unittest.skip("flaky — investigate later")
    def test_median_even_list(self):
        self.assertAlmostEqual(calculate_median([1, 2, 3, 4]), 2.5)

    def test_median_single_value(self):
        self.assertAlmostEqual(calculate_median([42]), 42.0)

    def test_median_empty_raises(self):
        with self.assertRaises(ValueError):
            calculate_median([])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m 'test: skip flaky median test'

# =============================================================================
# Commit 11: feat: add variance calculation
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid] + sorted_data[mid + 1]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_mode(data):
    """Return the most frequently occurring value in a list.

    If there are multiple modes, returns the smallest one.
    """
    if not data:
        raise ValueError("calculate_mode requires at least one data point")
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_count = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_count]
    return min(modes)


def calculate_range(data):
    """Calculate the range (max - min) of a list of numbers."""
    if not data:
        raise ValueError("calculate_range requires at least one data point")
    return max(data) - min(data)


def calculate_percentile(data, p):
    """Calculate the p-th percentile of a list of numbers.

    Uses linear interpolation between closest ranks.
    """
    if not data:
        raise ValueError("calculate_percentile requires at least one data point")
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]
    rank = (p / 100) * (n - 1)
    lower = int(rank)
    upper = lower + 1
    if upper >= n:
        return sorted_data[-1]
    weight = rank - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


def calculate_variance(data):
    """Calculate the population variance of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_variance requires at least two data points")
    mean = calculate_mean(data)
    return sum((x - mean) ** 2 for x in data) / len(data)
PYEOF

cat > tests/test_variance.py << 'PYEOF'
import unittest
from stats import calculate_variance


class TestVariance(unittest.TestCase):
    def test_variance_basic(self):
        self.assertAlmostEqual(calculate_variance([2, 4, 4, 4, 5, 5, 7, 9]), 4.0)

    def test_variance_identical(self):
        self.assertAlmostEqual(calculate_variance([3, 3, 3, 3]), 0.0)

    def test_variance_too_few_raises(self):
        with self.assertRaises(ValueError):
            calculate_variance([1])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add variance calculation"

# =============================================================================
# Commit 12: docs: update README with new functions
# =============================================================================
cat > README.md << 'MDEOF'
# Stats Module

A lightweight Python statistics library providing common statistical functions.

## Usage

```python
from stats import (
    calculate_mean, calculate_median, calculate_stddev,
    calculate_mode, calculate_range, calculate_percentile,
    calculate_variance,
)

data = [2, 4, 4, 4, 5, 5, 7, 9]

print(calculate_mean(data))            # 5.0
print(calculate_median(data))          # 4.5
print(calculate_stddev(data))          # 2.0
print(calculate_mode(data))            # 4
print(calculate_range(data))           # 7
print(calculate_percentile(data, 75))  # 5.75
print(calculate_variance(data))        # 4.0
```

## Available Functions

- `calculate_mean(data)` — Arithmetic mean
- `calculate_median(data)` — Median (handles odd and even length lists)
- `calculate_stddev(data)` — Population standard deviation
- `calculate_mode(data)` — Mode (most frequent value)
- `calculate_range(data)` — Range (max - min)
- `calculate_percentile(data, p)` — p-th percentile with interpolation
- `calculate_variance(data)` — Population variance

## Running Tests

```bash
python -m pytest tests/
```
MDEOF

git add -A
git commit -m "docs: update README with new functions"

# =============================================================================
# Commit 13: feat: add weighted mean
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid] + sorted_data[mid + 1]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_mode(data):
    """Return the most frequently occurring value in a list.

    If there are multiple modes, returns the smallest one.
    """
    if not data:
        raise ValueError("calculate_mode requires at least one data point")
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_count = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_count]
    return min(modes)


def calculate_range(data):
    """Calculate the range (max - min) of a list of numbers."""
    if not data:
        raise ValueError("calculate_range requires at least one data point")
    return max(data) - min(data)


def calculate_percentile(data, p):
    """Calculate the p-th percentile of a list of numbers.

    Uses linear interpolation between closest ranks.
    """
    if not data:
        raise ValueError("calculate_percentile requires at least one data point")
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]
    rank = (p / 100) * (n - 1)
    lower = int(rank)
    upper = lower + 1
    if upper >= n:
        return sorted_data[-1]
    weight = rank - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


def calculate_variance(data):
    """Calculate the population variance of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_variance requires at least two data points")
    mean = calculate_mean(data)
    return sum((x - mean) ** 2 for x in data) / len(data)


def calculate_weighted_mean(data, weights):
    """Calculate the weighted arithmetic mean.

    Args:
        data: list of numeric values
        weights: list of weights (must be same length as data)

    Returns:
        Weighted mean as a float.
    """
    if not data:
        raise ValueError("calculate_weighted_mean requires at least one data point")
    if len(data) != len(weights):
        raise ValueError("data and weights must have the same length")
    if sum(weights) == 0:
        raise ValueError("sum of weights must be non-zero")
    return sum(d * w for d, w in zip(data, weights)) / sum(weights)
PYEOF

cat > tests/test_weighted_mean.py << 'PYEOF'
import unittest
from stats import calculate_weighted_mean


class TestWeightedMean(unittest.TestCase):
    def test_weighted_mean_equal_weights(self):
        self.assertAlmostEqual(
            calculate_weighted_mean([1, 2, 3], [1, 1, 1]), 2.0
        )

    def test_weighted_mean_different_weights(self):
        self.assertAlmostEqual(
            calculate_weighted_mean([1, 2, 3], [3, 2, 1]), 1.6666666666666667
        )

    def test_weighted_mean_mismatched_lengths_raises(self):
        with self.assertRaises(ValueError):
            calculate_weighted_mean([1, 2], [1])

    def test_weighted_mean_zero_weights_raises(self):
        with self.assertRaises(ValueError):
            calculate_weighted_mean([1, 2], [0, 0])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add weighted mean"

# =============================================================================
# Commit 14: chore: add .gitignore
# =============================================================================
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
dist/
build/
EOF

git add -A
git commit -m "chore: add .gitignore"

# =============================================================================
# Commit 15: feat: add correlation coefficient
# =============================================================================
cat > stats.py << 'PYEOF'
"""Statistics module — core statistical functions."""


def calculate_mean(data):
    """Calculate the arithmetic mean of a list of numbers."""
    if not data:
        raise ValueError("calculate_mean requires at least one data point")
    return sum(data) / len(data)


def calculate_median(data):
    """Calculate the median of a list of numbers.

    For odd-length lists, returns the middle element.
    For even-length lists, returns the average of the two middle elements.
    """
    if not data:
        raise ValueError("calculate_median requires at least one data point")
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid] + sorted_data[mid + 1]) / 2


def calculate_stddev(data):
    """Calculate the population standard deviation of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_stddev requires at least two data points")
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_mode(data):
    """Return the most frequently occurring value in a list.

    If there are multiple modes, returns the smallest one.
    """
    if not data:
        raise ValueError("calculate_mode requires at least one data point")
    frequency = {}
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    max_count = max(frequency.values())
    modes = [k for k, v in frequency.items() if v == max_count]
    return min(modes)


def calculate_range(data):
    """Calculate the range (max - min) of a list of numbers."""
    if not data:
        raise ValueError("calculate_range requires at least one data point")
    return max(data) - min(data)


def calculate_percentile(data, p):
    """Calculate the p-th percentile of a list of numbers.

    Uses linear interpolation between closest ranks.
    """
    if not data:
        raise ValueError("calculate_percentile requires at least one data point")
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]
    rank = (p / 100) * (n - 1)
    lower = int(rank)
    upper = lower + 1
    if upper >= n:
        return sorted_data[-1]
    weight = rank - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


def calculate_variance(data):
    """Calculate the population variance of a list of numbers."""
    if len(data) < 2:
        raise ValueError("calculate_variance requires at least two data points")
    mean = calculate_mean(data)
    return sum((x - mean) ** 2 for x in data) / len(data)


def calculate_weighted_mean(data, weights):
    """Calculate the weighted arithmetic mean.

    Args:
        data: list of numeric values
        weights: list of weights (must be same length as data)

    Returns:
        Weighted mean as a float.
    """
    if not data:
        raise ValueError("calculate_weighted_mean requires at least one data point")
    if len(data) != len(weights):
        raise ValueError("data and weights must have the same length")
    if sum(weights) == 0:
        raise ValueError("sum of weights must be non-zero")
    return sum(d * w for d, w in zip(data, weights)) / sum(weights)


def calculate_correlation(x, y):
    """Calculate the Pearson correlation coefficient between two lists.

    Args:
        x: first list of numeric values
        y: second list of numeric values (same length as x)

    Returns:
        Pearson correlation coefficient as a float in [-1, 1].
    """
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if len(x) < 2:
        raise ValueError("calculate_correlation requires at least two data points")
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
    denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
    if denom_x == 0 or denom_y == 0:
        raise ValueError("correlation is undefined when standard deviation is zero")
    return numerator / (denom_x * denom_y)
PYEOF

cat > tests/test_correlation.py << 'PYEOF'
import unittest
from stats import calculate_correlation


class TestCorrelation(unittest.TestCase):
    def test_perfect_positive(self):
        self.assertAlmostEqual(
            calculate_correlation([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]), 1.0
        )

    def test_perfect_negative(self):
        self.assertAlmostEqual(
            calculate_correlation([1, 2, 3, 4, 5], [10, 8, 6, 4, 2]), -1.0
        )

    def test_no_correlation(self):
        r = calculate_correlation([1, 2, 3, 4, 5], [2, 4, 1, 5, 3])
        self.assertTrue(-1 <= r <= 1)

    def test_mismatched_lengths_raises(self):
        with self.assertRaises(ValueError):
            calculate_correlation([1, 2], [1])


if __name__ == "__main__":
    unittest.main()
PYEOF

git add -A
git commit -m "feat: add correlation coefficient"
