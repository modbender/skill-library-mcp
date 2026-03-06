# mediaproc setup

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/psyb0t/docker-mediaproc/main/install.sh | sudo bash
```

This creates `~/.mediaproc/` with docker-compose, authorized_keys, and work directory, then drops a `mediaproc` command into `/usr/local/bin`.

## Starting

```bash
# Add your SSH key
cat ~/.ssh/id_rsa.pub >> ~/.mediaproc/authorized_keys

# Basic start (detached)
mediaproc start -d

# With resource limits
mediaproc start -d -c 4 -r 4g -s 2g

# Custom port
mediaproc start -d -p 2223

# Custom fonts directory
mediaproc start -d -f /path/to/fonts
```

All flags persist to `~/.mediaproc/.env` — next `start` reuses the last values.

## Management

```bash
mediaproc stop                # stop
mediaproc upgrade             # pull latest image, asks to stop/restart
mediaproc uninstall           # stop and remove everything
mediaproc status              # show status
mediaproc logs                # show container logs
```

## Configuration

| Flag | Env var            | Default    | Description           |
| ---- | ------------------ | ---------- | --------------------- |
| `-p` | `MEDIAPROC_PORT`   | `2222`     | SSH port              |
| `-f` | `MEDIAPROC_FONTS_DIR` | `./fonts` | Custom fonts directory |
| `-c` | `MEDIAPROC_CPUS`   | `0`        | CPU limit (0 = unlimited) |
| `-r` | `MEDIAPROC_MEMORY` | `0`        | RAM limit (0 = unlimited) |
| `-s` | `MEDIAPROC_SWAP`   | `0`        | Swap limit (0 = no swap)  |
