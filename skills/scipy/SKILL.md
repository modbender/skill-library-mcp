---
name: SciPy
slug: scipy
version: 1.0.0
homepage: https://clawic.com/skills/scipy
description: Solve optimization, statistics, signal processing, and linear algebra problems with SciPy recipes and ready-to-run code.
metadata: {"clawdbot":{"emoji":"🔬","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for guidance on how to help the user effectively.

## When to Use

User needs scientific computing in Python: optimization, curve fitting, statistical tests, signal processing, interpolation, integration, or linear algebra. Agent provides working code, not theory.

## Architecture

This skill is stateless — no persistent storage needed. All code runs in user's Python environment.

See `memory-template.md` for optional preference tracking.

## Quick Reference

| Topic | File |
|-------|------|
| Usage guidance | `setup.md` |
| Optional preferences | `memory-template.md` |

## Core Rules

### 1. Working Code First
Every response includes runnable code. No pseudocode, no "implement this yourself".

```python
# Always include imports
from scipy import optimize
import numpy as np

# Complete, working example
result = optimize.minimize(lambda x: x**2, x0=1.0)
print(f"Minimum at x={result.x[0]:.4f}")
```

### 2. Module Selection Guide

| Problem | Module | Key Function |
|---------|--------|--------------|
| Find minimum/maximum | `scipy.optimize` | `minimize`, `minimize_scalar` |
| Curve fitting | `scipy.optimize` | `curve_fit` |
| Root finding | `scipy.optimize` | `root`, `brentq`, `fsolve` |
| Statistical tests | `scipy.stats` | `ttest_ind`, `chi2_contingency` |
| Distributions | `scipy.stats` | `norm`, `poisson`, `expon` |
| Filter signals | `scipy.signal` | `butter`, `filtfilt`, `savgol_filter` |
| FFT | `scipy.fft` | `fft`, `ifft`, `fftfreq` |
| Interpolation | `scipy.interpolate` | `interp1d`, `UnivariateSpline` |
| Integration | `scipy.integrate` | `quad`, `solve_ivp` |
| Linear algebra | `scipy.linalg` | `solve`, `eig`, `svd` |
| Sparse matrices | `scipy.sparse` | `csr_matrix`, `linalg.spsolve` |
| Spatial data | `scipy.spatial` | `KDTree`, `distance` |
| Image processing | `scipy.ndimage` | `gaussian_filter`, `label` |

### 3. Explain Key Parameters
When code uses non-obvious parameters, explain why:

```python
# method='L-BFGS-B' for bounded optimization
# bounds prevent physically impossible values
result = optimize.minimize(
    objective, x0, 
    method='L-BFGS-B',
    bounds=[(0, None), (0, 100)]  # x1 >= 0, 0 <= x2 <= 100
)
```

### 4. Validate Results
Always include sanity checks:

```python
result = optimize.minimize(func, x0)
if not result.success:
    print(f"⚠️ Optimization failed: {result.message}")
else:
    print(f"✓ Converged in {result.nit} iterations")
```

### 5. NumPy Integration
SciPy builds on NumPy. Use vectorized operations:

```python
# ✓ Vectorized (fast)
x = np.linspace(0, 10, 1000)
y = np.sin(x)

# ✗ Loop (slow)
y = [np.sin(xi) for xi in x]
```

## Optimization Patterns

### Minimize a Function

```python
from scipy.optimize import minimize
import numpy as np

# Rosenbrock function (classic test)
def rosenbrock(x):
    return sum(100*(x[1:]-x[:-1]**2)**2 + (1-x[:-1])**2)

x0 = np.array([0, 0])
result = minimize(rosenbrock, x0, method='BFGS')

print(f"Minimum at: {result.x}")
print(f"Function value: {result.fun}")
print(f"Converged: {result.success}")
```

### Constrained Optimization

```python
from scipy.optimize import minimize

# Minimize f(x,y) = x² + y² subject to x + y = 1
def objective(x):
    return x[0]**2 + x[1]**2

def constraint(x):
    return x[0] + x[1] - 1  # Must equal 0

result = minimize(
    objective, 
    x0=[0.5, 0.5],
    constraints={'type': 'eq', 'fun': constraint}
)
```

### Curve Fitting

```python
from scipy.optimize import curve_fit
import numpy as np

# Fit exponential decay
def model(t, a, tau):
    return a * np.exp(-t / tau)

t_data = np.array([0, 1, 2, 3, 4, 5])
y_data = np.array([10, 6.1, 3.7, 2.2, 1.4, 0.8])

params, covariance = curve_fit(model, t_data, y_data)
a_fit, tau_fit = params
errors = np.sqrt(np.diag(covariance))

print(f"a = {a_fit:.2f} ± {errors[0]:.2f}")
print(f"τ = {tau_fit:.2f} ± {errors[1]:.2f}")
```

## Statistics Patterns

### Hypothesis Testing

```python
from scipy import stats

# Compare two groups (independent t-test)
group_a = [23, 25, 28, 24, 26]
group_b = [30, 32, 29, 31, 33]

t_stat, p_value = stats.ttest_ind(group_a, group_b)
print(f"t = {t_stat:.3f}, p = {p_value:.4f}")

if p_value < 0.05:
    print("✓ Significant difference (p < 0.05)")
else:
    print("✗ No significant difference")
```

### Distribution Fitting

```python
from scipy import stats
import numpy as np

data = np.random.exponential(scale=2.0, size=1000)

# Fit exponential distribution
loc, scale = stats.expon.fit(data)
print(f"Fitted scale (λ⁻¹): {scale:.3f}")

# Test goodness of fit
ks_stat, ks_p = stats.kstest(data, 'expon', args=(loc, scale))
print(f"KS test: p = {ks_p:.4f}")
```

### Confidence Intervals

```python
from scipy import stats
import numpy as np

data = [2.3, 2.5, 2.1, 2.8, 2.4, 2.6, 2.2]
confidence = 0.95

mean = np.mean(data)
sem = stats.sem(data)
ci = stats.t.interval(confidence, len(data)-1, loc=mean, scale=sem)

print(f"Mean: {mean:.2f}")
print(f"95% CI: [{ci[0]:.2f}, {ci[1]:.2f}]")
```

## Signal Processing Patterns

### Low-Pass Filter

```python
from scipy import signal
import numpy as np

# Create noisy signal
fs = 1000  # Sample rate
t = np.linspace(0, 1, fs)
clean = np.sin(2 * np.pi * 10 * t)  # 10 Hz
noisy = clean + 0.5 * np.random.randn(len(t))

# Design and apply Butterworth filter
cutoff = 20  # Hz
order = 4
b, a = signal.butter(order, cutoff / (fs/2), btype='low')
filtered = signal.filtfilt(b, a, noisy)  # Zero-phase filtering
```

### FFT Analysis

```python
from scipy.fft import fft, fftfreq
import numpy as np

# Sample signal
fs = 1000
t = np.linspace(0, 1, fs)
signal_data = np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*120*t)

# Compute FFT
yf = fft(signal_data)
xf = fftfreq(len(t), 1/fs)

# Get magnitude spectrum (positive frequencies only)
n = len(t) // 2
freqs = xf[:n]
magnitudes = 2/n * np.abs(yf[:n])

# Find dominant frequency
peak_idx = np.argmax(magnitudes)
print(f"Dominant frequency: {freqs[peak_idx]:.1f} Hz")
```

## Interpolation Patterns

### 1D Interpolation

```python
from scipy.interpolate import interp1d, UnivariateSpline
import numpy as np

x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([0, 0.8, 0.9, 0.1, -0.8, -1])

# Linear interpolation
f_linear = interp1d(x, y, kind='linear')

# Cubic interpolation (smoother)
f_cubic = interp1d(x, y, kind='cubic')

# Smoothing spline (handles noise)
spline = UnivariateSpline(x, y, s=0.5)

x_new = np.linspace(0, 5, 100)
y_cubic = f_cubic(x_new)
```

## Integration Patterns

### Numerical Integration

```python
from scipy.integrate import quad
import numpy as np

# Integrate sin(x) from 0 to π
result, error = quad(np.sin, 0, np.pi)
print(f"∫sin(x)dx from 0 to π = {result:.6f} ± {error:.2e}")
# Expected: 2.0
```

### Solve ODE

```python
from scipy.integrate import solve_ivp
import numpy as np

# dy/dt = -2y, y(0) = 1 (exponential decay)
def dydt(t, y):
    return -2 * y

sol = solve_ivp(dydt, [0, 5], [1], t_eval=np.linspace(0, 5, 100))

# sol.t contains time points
# sol.y[0] contains y values
```

## Linear Algebra Patterns

### Solve Linear System

```python
from scipy import linalg
import numpy as np

# Solve Ax = b
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])

x = linalg.solve(A, b)
print(f"Solution: x = {x}")

# Verify
print(f"Check A @ x = {A @ x}")
```

### Eigendecomposition

```python
from scipy import linalg
import numpy as np

A = np.array([[1, 2], [2, 1]])
eigenvalues, eigenvectors = linalg.eig(A)

print(f"Eigenvalues: {eigenvalues}")
print(f"Eigenvectors:\n{eigenvectors}")
```

## Common Traps

- **Wrong bounds format in minimize** → bounds must be list of (min, max) tuples, one per variable
- **Forgetting to check result.success** → optimization can fail silently, always check
- **Using interp1d outside data range** → raises error by default, use `fill_value='extrapolate'` or `bounds_error=False`
- **filtfilt vs lfilter** → use `filtfilt` for zero-phase filtering, `lfilter` introduces phase shift
- **curve_fit with bad initial guess** → can converge to wrong solution, always provide reasonable p0
- **Integer division in Python 3** → use `x / 2` not `x // 2` for float division in formulas

## Security & Privacy

**Data that stays local:**
- All computations run in user's Python environment
- No data leaves the machine

**This skill does NOT:**
- Send data externally
- Create persistent files
- Access network resources

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `math` — mathematical concepts
- `data-analysis` — data exploration
- `data` — data handling patterns

## Feedback

- If useful: `clawhub star scipy`
- Stay updated: `clawhub sync`
