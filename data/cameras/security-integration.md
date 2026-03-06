# Security Camera Integration

## Connecting to Common Systems

### Generic IP Cameras (RTSP)

Most IP cameras expose RTSP streams. Find the URL in camera settings or try:
```
rtsp://user:pass@IP:554/stream1
rtsp://user:pass@IP:554/ch01/main/av_stream
rtsp://user:pass@IP:554/Streaming/Channels/101
```

**Snapshot via ffmpeg:**
```bash
ffmpeg -rtsp_transport tcp -i "rtsp://user:pass@IP:554/stream" \
  -frames:v 1 -q:v 2 snapshot.jpg
```

### ONVIF Discovery

Auto-discover cameras on network:
```python
from onvif import ONVIFCamera

# Connect
cam = ONVIFCamera('192.168.1.100', 80, 'admin', 'password')

# Get snapshot URL
media = cam.create_media_service()
profiles = media.GetProfiles()
snapshot_uri = media.GetSnapshotUri({'ProfileToken': profiles[0].token})
```

### Home Assistant Integration

If cameras are in HA, use the proxy endpoint:
```bash
curl -H "Authorization: Bearer $HA_TOKEN" \
  "http://homeassistant.local:8123/api/camera_proxy/camera.front_door" \
  -o snapshot.jpg
```

List all cameras:
```bash
curl -H "Authorization: Bearer $HA_TOKEN" \
  "http://homeassistant.local:8123/api/states" | jq '.[] | select(.entity_id | startswith("camera."))'
```

### Frigate (Recommended)

Frigate runs detection locally. Agent connects for events/clips:

**Get recent events:**
```bash
curl "http://frigate:5000/api/events?limit=10"
```

**Get snapshot of event:**
```bash
curl "http://frigate:5000/api/events/{event_id}/snapshot.jpg" -o event.jpg
```

**MQTT subscription for real-time:**
```
Topic: frigate/events
Payload: {"type": "new", "camera": "front", "label": "person", ...}
```

### Ring (Unofficial)

Ring has no official API. Use `ring-client-api` (Node.js):
```javascript
const { RingApi } = require('ring-client-api');
const ringApi = new RingApi({ refreshToken: 'TOKEN' });
const cameras = await ringApi.getCameras();
const snapshot = await cameras[0].getSnapshot();
```

**Note:** Ring may block unofficial access. Frigate + RTSP proxy more reliable.

### Nest / Google

Requires Device Access API ($5 one-time fee):
1. Create project at device-access.google.com
2. Link Nest account
3. OAuth2 flow for access token
4. Use REST API for snapshots

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://smartdevicemanagement.googleapis.com/v1/enterprises/{project}/devices/{device}:executeCommand" \
  -d '{"command": "sdm.devices.commands.CameraEventImage.GenerateImage"}'
```

### UniFi Protect

Local API (no cloud):
```bash
# Get cameras
curl -k "https://unifi-protect:7443/proxy/protect/api/cameras" \
  -H "Authorization: Bearer $TOKEN"

# Snapshot
curl -k "https://unifi-protect:7443/proxy/protect/api/cameras/{id}/snapshot" \
  -o snapshot.jpg
```

## Best Practices

1. **Use Frigate as aggregator** — handles RTSP, does detection, exposes clean API
2. **Don't poll constantly** — use webhooks/MQTT for events
3. **Cache snapshots briefly** — avoid hammering cameras
4. **Separate network** — IoT/cameras on VLAN for security
5. **Local storage preferred** — NVR/NAS, not cloud dependency

## Typical Agent Flow

```
User: "Is anyone at the front door?"

Agent:
1. Get snapshot: curl frigate/api/front_door/latest.jpg
2. Send to vision model: "Describe this image"
3. Vision: "A delivery person holding a package"
4. Reply: "Yes, there's a delivery person with a package at the door."
```

```
User: "Alert me if there's movement in the backyard tonight"

Agent:
1. Subscribe to MQTT: frigate/events (filter: camera=backyard, after=sunset)
2. On event: Get snapshot, describe, notify user
3. "Motion detected in backyard: A cat walking across the lawn"
```
