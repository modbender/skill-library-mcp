---
name: pywayne-adb-logcat-reader
description: Android device logcat reader for real-time log monitoring. Use when working with pywayne.adb.logcat_reader module to read Android device logs via adb logcat command, supporting both C++ backend (faster) and Python backend (subprocess) with generator-style output for streaming logs.
---

# Pywayne ADB Logcat Reader

This module provides real-time Android device log reading capabilities via the `adb logcat` command.

## Quick Start

```python
from pywayne.adb.logcat_reader import AdbLogcatReader

# Create reader (default C++ backend)
reader = AdbLogcatReader()

# Start log capture and read
reader.start()
for line in reader.read():
    print(line)
```

# Use Python backend (alternative)
reader = AdbLogcatReader(backend='python')
reader.start()
for line in reader.read():
    print(line)
```

# Stop and cleanup
reader.stop()
```

## Initialization

```python
# C++ backend (default, faster)
reader = AdbLogcatReader()

# Python backend (alternative, may be more compatible)
reader = AdbLogcatReader(backend='python')
```

## Reading Logs

The `read()` method yields log lines incrementally as a generator, suitable for processing large logs or real-time monitoring.

```python
# Process logs as they arrive
for line in reader.read():
    # Filter, parse, store...
```

## Properties

| Property | Description |
|---------|-------------|
| `backend` | 'cpp' or 'python' | Active backend for adb logcat |
| `running` | Whether logcat process is running |

## Methods

| Method | Description |
|---------|-------------|
| `start()` | Start adb logcat process |
| `read()` | Generator yielding log lines |
| `stop()` | Stop logcat process |
| `get_backend()` | Get active backend type |

## Backends

### C++ Backend (Default)

- Uses native C++ implementation
- Faster performance for real-time streaming
- Better compatibility with adb logcat

### Python Backend (Alternative)

- Uses Python subprocess to call adb
- More compatible across different environments
- Easier debugging and integration

## Notes

- C++ backend is faster and recommended for production
- Python backend may be useful during development
- `stop()` terminates adb logcat; use `Ctrl+C` to send interrupt signal
- Logs are cleared automatically when process stops
