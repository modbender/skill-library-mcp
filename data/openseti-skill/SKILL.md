---
name: openseti
description: Distributed SETI scanner - contribute compute power to analyze real radio telescope data from Breakthrough Listen. Earn tokens when your analysis discovers anomalies. Use when setting up distributed alien signal detection, running SETI scans, or contributing to the OpenSETI network.
---

# OpenSETI Distributed Scanner

Contribute your compute power to scan real Breakthrough Listen radio telescope data for signs of extraterrestrial intelligence. This is a SETI@home-style distributed computing project with token rewards.

## Quick Start

1. Register your Solana wallet:
```bash
python scripts/openseti.py register <your-wallet-address>
```

2. Run a scan:
```bash
python scripts/openseti.py scan
```

3. Run continuous scanning (background):
```bash
python scripts/openseti.py scan --continuous
```

## How It Works

1. Your machine requests a work unit from the OpenSETI network
2. Work units contain real radio telescope data chunks (~1MB each)
3. Your machine analyzes the data using FFT and signal processing
4. Results are submitted back to the network
5. If an anomaly is detected, you earn tokens

## Analysis Criteria

The scanner looks for signals that match ETI signatures:

- **Narrowband signals** (< 10 Hz bandwidth) - Natural sources are broadband
- **Doppler drift** - Frequency shift indicating non-terrestrial origin
- **High SNR** - Strong signals above noise floor
- **Hydrogen line proximity** - 1420.405 MHz is the "water hole"
- **Non-RFI patterns** - Doesn't match known Earth interference

## Reward Structure

| Classification | Score | Tokens |
|---------------|-------|--------|
| NATURAL | 0.0 - 0.15 | 0 |
| WEAK_SIGNAL | 0.15 - 0.4 | 0 |
| INVESTIGATING | 0.4 - 0.7 | 2,500 |
| ANOMALY_FLAGGED | 0.7+ | 5,000 |

Tokens are tracked on-chain and distributed when the token launches.

## Commands

- `openseti register <wallet>` - Register your Solana wallet
- `openseti scan` - Run one scan cycle
- `openseti scan --continuous` - Run continuous scanning
- `openseti stats` - Show your contribution stats
- `openseti leaderboard` - Show top contributors

## Requirements

- Python 3.8+
- NumPy and SciPy (`pip install numpy scipy requests`)

## Data Source

All data comes from the Breakthrough Listen Open Data Archive:
https://breakthroughinitiatives.org/opendatasearch

Observations from the Green Bank Telescope and Parkes Observatory.
