# Pi Benchmark Baselines

Record baseline measurements here before making any changes. All benchmarks on:

- Raspberry Pi 5 Model B Rev 1.1
- 4x Cortex-A76 @ 2.4GHz, 8GB RAM
- 128GB microSD
- Debian Bookworm 12, kernel 6.12.62
- Node v22.22.0

## OpenClaw Baselines

| Metric | Value | Date | Notes |
|--------|-------|------|-------|
| Cold start time | -- | -- | `time node entry.js` |
| Idle memory (RSS) | -- | -- | After startup, no active sessions |
| Active memory (RSS) | -- | -- | During active conversation |
| node_modules size | -- | -- | `du -sh node_modules` |
| Dependency count | -- | -- | `ls node_modules | wc -l` |

## Storage I/O

| Metric | Value | Date | Notes |
|--------|-------|------|-------|
| Sequential read | -- | -- | `dd if=/dev/mmcblk0 of=/dev/null bs=1M count=100` |
| Sequential write | -- | -- | `dd if=/dev/zero of=test bs=1M count=100 oflag=direct` |
| Random 4K read IOPS | -- | -- | `fio` if available |

## After Optimization

Track improvements here as PRs land.
