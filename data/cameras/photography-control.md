# DSLR / Mirrorless Control

## gPhoto2 (Universal)

Works with most Canon, Nikon, Sony, Fuji, Olympus cameras over USB.

### Installation
```bash
# macOS
brew install gphoto2

# Linux
sudo apt install gphoto2
```

### Basic Commands

```bash
# Detect camera
gphoto2 --auto-detect

# Camera info
gphoto2 --summary

# Capture photo and download
gphoto2 --capture-image-and-download

# Capture to camera only (stay on SD card)
gphoto2 --capture-image

# Download all photos
gphoto2 --get-all-files
```

### Settings Control

```bash
# List all settings
gphoto2 --list-all-config

# Get current ISO
gphoto2 --get-config /main/imgsettings/iso

# Set ISO to 400
gphoto2 --set-config /main/imgsettings/iso=400

# Set aperture (f-number)
gphoto2 --set-config /main/capturesettings/aperture=5.6

# Set shutter speed
gphoto2 --set-config /main/capturesettings/shutterspeed=1/250
```

### Tethered Shooting

```bash
# Capture and save to folder
gphoto2 --capture-image-and-download --filename "shot_%Y%m%d_%H%M%S.jpg"

# Continuous tethering (download as shot)
gphoto2 --capture-tethered --interval 0 --filename "tether_%n.jpg"
```

### Timelapse

```bash
# Take photo every 5 seconds, 100 shots
gphoto2 --capture-image-and-download --interval 5 --frames 100
```

## Python Integration (gphoto2)

```python
import gphoto2 as gp

# Initialize
camera = gp.Camera()
camera.init()

# Capture and download
file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
camera_file = camera.file_get(
    file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL
)
camera_file.save('photo.jpg')

# Change setting
config = camera.get_config()
iso = config.get_child_by_name('iso')
iso.set_value('400')
camera.set_config(config)

# Cleanup
camera.exit()
```

## Vendor SDKs

### Canon (EDSDK)
Official SDK for deeper control. Requires registration.
```python
# Using python-edsdk wrapper
from edsdk import Camera
camera = Camera()
camera.take_picture()
```

### Sony (Remote SDK)
For Alpha/mirrorless via WiFi:
```bash
curl "http://camera-ip/sony/camera/actTakePicture"
```

### Fuji (X App API)
Undocumented but functional via WiFi.

## Common Workflows

### Studio Product Photography
```bash
# Set up
gphoto2 --set-config /main/capturesettings/aperture=8
gphoto2 --set-config /main/imgsettings/iso=100

# Capture sequence
for i in {1..10}; do
    gphoto2 --capture-image-and-download --filename "product_$i.jpg"
    read -p "Press enter for next shot"
done
```

### Focus Stacking
```bash
# Requires manual focus adjustment between shots
# Or use camera's built-in focus bracketing
gphoto2 --set-config /main/capturesettings/focusmode=Manual
# Capture at each focus point
```

### Remote Trigger
```python
import time
import gphoto2 as gp

def wait_for_trigger():
    """Wait for external signal"""
    # Your trigger logic here
    pass

camera = gp.Camera()
camera.init()

while True:
    wait_for_trigger()
    camera.capture(gp.GP_CAPTURE_IMAGE)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Camera not detected | Unplug/replug, close other apps (Lightroom, Photos) |
| "Camera busy" | Kill `PTPCamera` process on macOS |
| Settings locked | Switch camera to Manual mode |
| Slow download | Use faster SD card, USB 3.0 port |
| Battery drain | Use AC adapter for long sessions |

### macOS Camera Process Conflict
```bash
# Kill Apple's PTP daemon
killall PTPCamera

# Then retry gphoto2
gphoto2 --auto-detect
```
