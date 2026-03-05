# Ubuntu 24.04 Essential Commands

## Disk
- `df -h` — Disk usage
- `du -sh /* | sort -rh` — Largest dirs
- `trash-empty` — Empty trash
- `apt autoremove -y && apt clean` — Packages/cache

## RAM/Process
- `free -h` — RAM
- `ps aux --sort=-%mem | head -10` — Top memory
- `top -bn1` — Quick top

## Logs/Health
- `journalctl --vacuum-time=1week`
- `dmesg | tail -20`
- `uptime`

## Performance
- `iotop` — Disk I/O
- `vmstat 1 5` — VM stats
- `sync; echo 3 > /proc/sys/vm/drop_caches` — Drop caches
