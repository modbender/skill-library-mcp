# Troubleshooting

## service not active

```bash
systemctl --user status openclaw-transcribe.service --no-pager
journalctl --user -u openclaw-transcribe.service -n 100 --no-pager
```

## missing binary: gst-launch-1.0

Install gstreamer runtime on host:
- `gstreamer1.0-tools`
- `gstreamer1.0-libav`

## package/version control

Deploy script pins default package version:
- `faster-whisper==1.1.1`

Override if needed:

```bash
FASTER_WHISPER_VERSION=1.1.1 bash scripts/deploy.sh
```

## CORS policy

Default origin is strict (`https://127.0.0.1:8443`).
Set explicit origin for your host:

```bash
TRANSCRIBE_ALLOWED_ORIGIN=https://<host-or-ip>:8443 bash scripts/deploy.sh
```

## model tuning

Use env vars at deploy:

```bash
WHISPER_MODEL_SIZE=small WHISPER_DEVICE=cpu WHISPER_COMPUTE_TYPE=int8 bash scripts/deploy.sh
```
