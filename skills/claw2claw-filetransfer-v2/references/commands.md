# Command Reference

Detailed documentation for all claw2claw commands.

---

## setup

Configure connection to a remote OpenClaw agent.

```bash
claw2claw setup <remote-host> [user] [port]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<remote-host>` | Yes | - | IP or hostname |
| `[user]` | No | `root` | SSH username |
| `[port]` | No | `22` | SSH port |

### Examples

```bash
claw2claw setup 192.168.1.100
claw2claw setup 192.168.1.100 admin
claw2claw setup 192.168.1.100 admin 2222
claw2claw setup myserver.example.com
```

### What Happens

1. Tests SSH connectivity
2. Adds SSH key to remote if needed
3. Saves config to `~/.claw2claw.conf`

---

## send

Upload file to remote agent.

```bash
claw2claw send <source> [destination]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<source>` | Yes | - | Local file/directory |
| `[destination]` | No | `/tmp/` | Remote path |

### Examples

```bash
claw2claw send /backup.tar.gz
claw2claw send /backup.tar.gz /backups/
claw2claw send ./my-folder/
claw2claw send /huge-file.tar.gz --dry-run
```

---

## get

Download file from remote agent.

```bash
claw2claw get <remote-source> [local-destination]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<remote-source>` | Yes | - | Remote file path |
| `[local-destination]` | No | `.` | Local path |

### Examples

```bash
claw2claw get /var/log/syslog
claw2claw get /var/log/syslog ./logs/
claw2claw get /backups/daily/ ./
```

---

## sync-to-remote

Mirror local directory to remote. **Warning: Deletes remote files not in local.**

```bash
claw2claw sync-to-remote <local-directory> [remote-destination]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<local-directory>` | Yes | - | Local dir to sync |
| `[remote-destination]` | No | basename | Remote dir |

### Examples

```bash
claw2claw sync-to-remote ./project/
claw2claw sync-to-remote ./project/ /workspace/project/
claw2claw sync-to-remote ./project/ --dry-run
```

---

## sync-from-remote

Mirror remote directory to local. **Warning: Deletes local files not in remote.**

```bash
claw2claw sync-from-remote <remote-directory> [local-destination]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<remote-directory>` | Yes | - | Remote dir |
| `[local-destination]` | No | `.` | Local path |

### Examples

```bash
claw2claw sync-from-remote /workspace/
claw2claw sync-from-remote /workspace/project/ ./local/
```

---

## ls

List files on remote.

```bash
claw2claw ls [path]
```

### Examples

```bash
claw2claw ls
claw2claw ls /var/log/
```

---

## status

Show connection status and diagnostics.

```bash
claw2claw status
```

Shows: platform, config, SSH key, connection test, requirements

---

## Options

### -n, --dry-run

Preview without executing.

```bash
claw2claw send /big-file.tar.gz --dry-run
```

### --compress / --no-compress

Toggle compression.

```bash
claw2claw send /video.mp4 --no-compress
```

### --debug

Enable debug output.

```bash
claw2claw send /file.txt --debug
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error |
| 2 | Invalid args |
| 130 | Interrupted |
