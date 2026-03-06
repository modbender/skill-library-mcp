---
name: pywayne-plot
description: Enhanced spectrogram visualization tools for time-frequency analysis. Use when creating spectrograms, spectral analysis, or time-frequency plots for signals including IMU data (accelerometer, gyroscope), physiological signals (PPG, ECG, respiration), vibration analysis, and audio processing. Supports frequency unit conversion (Hz/bpm/kHz), multiple normalization modes (global/local/none), and MATLAB-style parula colormap.
---

# Pywayne Plot

Enhanced spectrogram visualization tools for professional time-frequency analysis.

## Quick Start

```python
import matplotlib.pyplot as plt
from pywayne.plot import regist_projection, parula_map
import numpy as np

# Register custom projection
regist_projection()

# Create spectrogram
fig, ax = plt.subplots(subplot_kw={'projection': 'z_norm'})
spec, freqs, t, im = ax.specgram(
    x=signal_data,
    Fs=100,
    NFFT=128,
    noverlap=96,
    cmap=parula_map,
    scale='dB'
)
ax.set_ylabel('Frequency (Hz)')
plt.colorbar(im, label='Magnitude (dB)')
plt.show()
```

## Functions

### regist_projection

Register the custom `SpecgramAxes` projection. Must be called before using the enhanced specgram functionality.

```python
from pywayne.plot import regist_projection
regist_projection()
```

### SpecgramAxes.specgram

Enhanced spectrogram with advanced features.

**Key Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `NFFT` | FFT window length (points) | 256 |
| `Fs` | Sampling frequency (Hz) | 2 |
| `noverlap` | Overlap points between windows | 128 |
| `cmap` | Colormap (use `parula_map`) | - |
| `mode` | 'psd', 'magnitude', 'angle', 'phase' | 'psd' |
| `scale` | 'dB' or 'linear' | 'dB' |
| `normalize` | 'global', 'local', 'none' | 'global' |
| `freq_scale` | Frequency scaling factor | 1.0 |
| `Fc` | Center frequency offset (Hz) | 0 |

**Returns:**
- `spec` - 2D spectrogram array (n_freqs, n_times)
- `freqs` - Frequency axis array
- `t` - Time axis array
- `im` - matplotlib image object (for colorbar)

### get_specgram_params

Auto-recommend STFT parameters based on signal characteristics.

```python
from pywayne.plot import get_specgram_params

params = get_specgram_params(
    signal_length=10000,
    sampling_rate=100,
    time_resolution=0.1  # or freq_resolution=0.5
)
# Returns: NFFT, noverlap, actual_freq_res, actual_time_res, n_segments
```

### parula_map

MATLAB-style perceptually uniform colormap for scientific visualization.

```python
from pywayne.plot import parula_map
plt.imshow(data, cmap=parula_map)
```

## Usage Examples

### IMU Signal Analysis

```python
fs = 100  # Sampling rate
win_time, step_time = 1, 0.1

fig, ax = plt.subplots(subplot_kw={'projection': 'z_norm'})
spec, freqs, t, im = ax.specgram(
    x=acc_data,
    Fs=fs,
    NFFT=int(win_time * fs),
    noverlap=int((win_time - step_time) * fs),
    scale='dB',
    cmap=parula_map
)
ax.set_ylabel('Frequency (Hz)')
ax.set_ylim(0, 30)
```

### Physiological Signals (PPG - Heart Rate)

```python
# Convert Hz to bpm for heart rate visualization
fig, ax = plt.subplots(subplot_kw={'projection': 'z_norm'})
spec, freqs, t, im = ax.specgram(
    x=ppg_signal,
    Fs=100,
    NFFT=400,
    noverlap=300,
    freq_scale=60,  # Hz -> bpm
    scale='dB'
)
ax.set_ylabel('Heart Rate (bpm)')
ax.set_ylim(40, 180)
```

### Vibration Analysis with Global Normalization

```python
fig, ax = plt.subplots(subplot_kw={'projection': 'z_norm'})
spec, freqs, t, im = ax.specgram(
    x=vibration_data,
    Fs=1000,
    NFFT=1024,
    noverlap=512,
    scale='linear',
    normalize='global'
)
plt.colorbar(im, label='Normalized Magnitude')
```

### High-Resolution Analysis with Zero-Padding

```python
fig, ax = plt.subplots(subplot_kw={'projection': 'z_norm'})
spec, freqs, t, im = ax.specgram(
    x=signal,
    Fs=100,
    NFFT=100,
    pad_to=512,  # Zero-pad for smoother spectrum
    noverlap=80,
    scale='dB'
)
```

## Scale and Normalization Modes

### Scale Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `dB` | Logarithmic (10*log10 for PSD, 20*log10 for magnitude) | Large dynamic range signals |
| `linear` | Linear amplitude | Direct amplitude comparison |

### Normalization Modes (only for `scale='linear'`)

| Mode | Description | Use Case |
|------|-------------|----------|
| `global` | Z/max(Z), preserves relative intensity | Compare intensity across time |
| `local` | Per-column normalization to [0,1] | Focus on frequency content over time |
| `none` | No normalization | Raw spectrogram values |

## Frequency Scaling

| freq_scale | Unit | Use Case |
|------------|------|----------|
| 1.0 | Hz | Default, most signals |
| 60 | bpm | Heart rate, respiration rate |
| 0.001 | kHz | Audio signals |

Example: `freq_scale=60` converts 2 Hz → 120 bpm

## Resolution Guidelines

- **Frequency resolution**: Δf = Fs / NFFT
- **Time resolution**: Δt = (NFFT - noverlap) / Fs
- **Trade-off**: Cannot simultaneously achieve high frequency and time resolution

Use `get_specgram_params()` to auto-calculate optimal parameters.

## Interactive Analysis

```python
spec, freqs, t, im = ax.specgram(...)

def on_click(event):
    if event.xdata and event.inaxes == ax:
        time_idx = np.argmin(np.abs(t - event.xdata))
        plt.figure()
        plt.plot(freqs, spec[:, time_idx])
        plt.title(f'FFT at t={event.xdata:.2f}s')
        plt.show()

fig.canvas.mpl_connect('button_press_event', on_click)
```

## Application Areas

- **IMU data**: Accelerometer and gyroscope analysis
- **Physiological signals**: PPG (heart rate), ECG, respiration
- **Vibration analysis**: Machinery fault diagnosis
- **Audio processing**: Speech and audio spectrum analysis

## Notes

- Always call `regist_projection()` before using `projection='z_norm'`
- `parula_map` is recommended for best perceptual uniformity
- dB mode automatically handles log(0) issues
- For better FFT efficiency, set NFFT to power of 2
