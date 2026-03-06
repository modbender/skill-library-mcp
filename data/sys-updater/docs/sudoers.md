# Sudoers Setup

sys-updater requires passwordless sudo for specific apt commands.

## Required Commands

```
/usr/bin/apt-get update
/usr/bin/apt-get -s upgrade
/usr/sbin/unattended-upgrade -d
```

## Configuration

Create `/etc/sudoers.d/sys-updater`:

```sudoers
# sys-updater: allow moltuser to run apt maintenance without password
moltuser ALL=(ALL) NOPASSWD: /usr/bin/apt-get update
moltuser ALL=(ALL) NOPASSWD: /usr/bin/apt-get -s upgrade
moltuser ALL=(ALL) NOPASSWD: /usr/sbin/unattended-upgrade -d
```

Apply:

```bash
sudo visudo -f /etc/sudoers.d/sys-updater
# Paste the content above, save
sudo chmod 440 /etc/sudoers.d/sys-updater
```

## Verify

```bash
# Should run without password prompt
sudo -n apt-get update
sudo -n apt-get -s upgrade
sudo -n unattended-upgrade -d
```

## Security Notes

- Only simulation (`-s`) is allowed for upgrade, not actual upgrade
- `unattended-upgrade` is the official Ubuntu security update mechanism
- No `apt-get install`, `remove`, or `autoremove` permissions granted
- Logs do **not** store full stdout/stderr of apt commands (only summaries) and never capture passwords/tokens

## Troubleshooting

If you see "sudo: a password is required":

1. Check file permissions: `ls -la /etc/sudoers.d/sys-updater`
2. Validate syntax: `sudo visudo -c -f /etc/sudoers.d/sys-updater`
3. Ensure no conflicting rules in `/etc/sudoers` or other files in `/etc/sudoers.d/`
