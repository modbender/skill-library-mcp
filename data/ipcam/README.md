# ipcam

ONVIF PTZ control + RTSP capture + camera discovery for IP cameras.

Works with any ONVIF Profile S/T camera. Tested with TP-Link Tapo/Vigi.

## Quick Start

```bash
bash skills/ipcam/install.sh       # install deps
ptz.py discover --add              # find & add cameras
camera.sh snapshot                 # take a snapshot
ptz.py move left                   # PTZ control
ptz.py stream-uri --save           # auto-detect RTSP paths
```

See [SKILL.md](SKILL.md) for full documentation.

## License

MIT
