---
name: pywayne-dsp
description: Digital signal processing toolkit for filtering, peak detection, detrending, and curve similarity. Use when working with sensor data, signal preprocessing, feature extraction, noise suppression, or time-series analysis. Includes Butterworth filter, One-Euro filter, signal detrending, DTW curve similarity, Welford standard deviation, and sliding window extrema detection.
---

# Pywayne Dsp

数字信号处理工具集，提供滤波器、峰值检测、去趋势、曲线相似度等信号处理功能。

## Quick Start

```python
from pywayne.dsp import butter_bandpass_filter, peak_det, SignalDetrend

# Butterworth 低通滤波
filtered = butter_bandpass_filter(signal, order=3, lo=0.5, hi=40, fs=250)

# 峰值检测
peaks, valleys = peak_det(signal, delta=0.5)

# 信号去趋势
detrender = SignalDetrend(method='linear')
detrended = detrender(raw_signal)
```

## Filtering - 滤波器

### butter_bandpass_filter

巴特沃斯带通滤波器。

```python
from pywayne.dsp import butter_bandpass_filter

# 带通滤波
filtered = butter_bandpass_filter(
    signal=raw_signal,
    order=4,
    lo=1,
    hi=50,
    fs=250,
    btype='bandpass'
)
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `signal` | array | 输入信号 |
| `order` | int | 滤波器阶数 |
| `lo` | float | 下限截止频率 (Hz) |
| `hi` | float | 上限截止频率 (Hz) |
| `fs` | float | 采样频率，默认为 0（不归一化） |
| `btype` | str | 滤波器类型：'lowpass', 'highpass', 'bandpass', 'bandstop' |
| `realtime` | bool | 是否实时处理，默认 False |

### ButterworthFilter

纯 numpy 实现的巴特沃斯滤波器类，支持完整的 IIR 滤波功能。

```python
from pywayne.dsp import ButterworthFilter

# 方式 1：通过参数设计
bf = ButterworthFilter.from_params(order=4, fs=200, btype='bandpass', cutoff=(1, 50))
y, zf = bf.lfilter(signal)

# 方式 2：通过系数构造
bf2 = ButterworthFilter.from_ba(b, a)
y, zf = bf2.lfilter(signal)

# 零相位滤波（前向-后向）
y, zf = bf.filtfilt(signal)

# 去趋势
detrended = ButterworthFilter.detrend(signal, method='linear')
```

**参数设计方法**：

```python
ButterworthFilter.from_params(order, fs, btype, cutoff, cache_zi=True)
ButterworthFilter.from_ba(b, a, cache_zi=True)
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `order` | int | 滤波器阶数 |
| `fs` | float | 采样频率 (Hz) |
| `btype` | str | 'lowpass', 'highpass', 'bandpass', 'bandstop' |
| `cutoff` | float/Tuple | 截止频率 (Hz)，带通为 (low, high) 元组 |
| `cache_zi` | bool | 是否预计算稳态初始条件 |

**实例方法**：

| 方法 | 说明 |
|------|------|
| `zi(self)` | 返回稳态初始条件数组 |
| `lfilter(self, x, zi=None)` | 零相位滤波，返回 (y, zf) |
| `filtfilt(self, x, padtype='odd')` | 零相位滤波，可指定填充方式 |

## Peak Detection - 峰值检测

### peak_det

峰值检测函数，基于 MATLAB peakdet 转换。

```python
from pywayne.dsp import peak_det

max_peaks, min_peaks = peak_det(signal, delta=0.5)
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `v` | array | 输入信号 |
| `delta` | float | 检测阈值，控制检测灵敏度 |
| `x` | array | 可选的 x 轴数据，若未提供则使用下标 |

**返回值**：`(maxima_indices, minima_indices)` - 峰值和谷值的索引位置

### find_extremum_in_sliding_window

在滑动窗口中查找极值。

```python
from pywayne.dsp import find_extremum_in_sliding_window

extrema = find_extremum_in_sliding_window(data, k=50)
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `data` | list | 输入数据列表 |
| `k` | int | 滑动窗口大小 |

**返回值**：`[minima, maxima]` - 含局部极值的列表

### FindSlidingWindowExtremum

滑动窗口极值查找器类，用于实时数据流。

```python
from pywayne.dsp import FindSlidingWindowExtremum

detector = FindSlidingWindowExtremum(win=100, find_max=True)

# 应用新值
for sample in stream:
    current_peak = detector.apply(sample)
    # 处理 current_peak
```

**方法**：

| 方法 | 说明 |
|------|------|
| `__init__(win, find_max)` | 初始化，指定窗口大小和查找类型（最大值或最小值） |
| `apply(val)` | 更新窗口数据，返回当前极值 |

## Detrending - 信号去趋势

### SignalDetrend

信号去趋势处理器，支持多种去趋势算法。

```python
from pywayne.dsp import SignalDetrend

# 去除线性趋势
detrender = SignalDetrend(method='linear')
detrended = detrender(signal)

# 去除均值趋势
detrender = SignalDetrend(method='mean')
detrended = detrender(signal)

# LOESS 去趋势
detrender = SignalDetrend(method='loess', span=0.3)
detrended = detrender(signal)
```

**方法**：

| 方法 | 说明 |
|------|------|
| `method` | str | 去趋势方法：'none', 'mean', 'linear', 'poly', 'loess', 'wavelet', 'emd', 'ceemdan', 'median' |
| `__call__(x)` | 应用去趋势算法处理输入信号 |

**去趋势方法**：

| 方法 | 说明 |
|------|------|
| `none` | 不处理，返回原信号 |
| `mean` | 去除均值 |
| `linear` | 去除线性趋势 |
| `poly` | 去除多项式趋势 |
| `loess` | 局部加权回归平滑 |
| `wavelet` | 小波变换去趋势 |
| `emd` | EMD 去趋势 |
| `ceemdan` | CEEMDAN 去趋势 |
| `median` | 中值滤波去趋势 |

## Curve Similarity - 曲线相似度

### CurveSimilarity

曲线相似度计算，支持动态时间规整（DTW）。

```python
from pywayne.dsp import CurveSimilarity

cs = CurveSimilarity()
distance = cs.dtw(curve1, curve2, mode='global')
```

**方法**：

| 方法 | 说明 |
|------|------|
| `dtw(x, y, mode='global', *params)` | 计算两条曲线的 DTW 距离 |
| `mode` | str | 'global'（全局）或 'local'（局部） |

## Other Tools - 其他工具

### OneEuroFilter

一欧罗滤波器，用于平滑信号并减少延迟。

```python
from pywayne.dsp import OneEuroFilter

# 初始化
euro_filter = OneEuroFilter(te=0.02, mincutoff=1.0, beta=0.007, dcutoff=1.0)

# 应用滤波
smooth_value = euro_filter.apply(new_measurement, te=0.02)
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `te` | float | 采样时间（秒），自动推断默认值 |
| `mincutoff` | float | 最小截止频率 |
| `beta` | float | 调整速率参数 |
| `dcutoff` | float | 导数截止频率 |

### WelfordStd

使用 Welford 算法进行在线标准差计算。

```python
from pywayne.dsp import WelfordStd

std_calculator = WelfordStd(win=50)

for sample in data_stream:
    current_std = std_calculator.apply(sample)
    # 使用 current_std 进行判断
```

**方法**：

| 方法 | 说明 |
|------|------|
| `__init__(win)` | 初始化，指定窗口大小 |
| `apply(val)` | 更新标准差计算，返回当前窗口标准差 |

## 应用场景

| 场景 | 使用函数 |
|------|----------|
| 心电图信号分析 | `butter_bandpass_filter`, `peak_det` |
| 传感器数据平滑 | `OneEuroFilter`, `ButterworthFilter` |
| 数据预处理 | `SignalDetrend` |
| 曲线相似度比较 | `CurveSimilarity.dtw` |
| 质量监控 | `WelfordStd` |
