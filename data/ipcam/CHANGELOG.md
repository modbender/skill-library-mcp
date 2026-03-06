# Changelog

## 1.0.0

- ONVIF PTZ: move, goto, stop, home, presets
- RTSP: snapshot, recording, stream URL via ffmpeg
- Camera discovery: WS-Discovery multicast probe (no extra dependencies)
- Stream URI query: `ptz.py stream-uri [--save]` to auto-detect RTSP paths
- Multi-camera support with JSON config and `--cam` selector
- Configurable RTSP stream paths per camera
- RTSP connection timeout (`RTSP_TIMEOUT` env, default 10s)
- Safe password URL-encoding (handles special characters)
- ONVIF error handling with port suggestions
- Tested with TP-Link Tapo/Vigi devices
- Dependencies: ffmpeg, onvif-zeep
