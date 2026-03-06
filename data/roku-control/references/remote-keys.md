# Roku Remote Keys Reference

Complete list of supported remote control keys for the Roku ECP API.

## Navigation

| Key | Function |
|-----|----------|
| `Home` | Go to Roku home screen |
| `Back` | Go back / return to previous screen |
| `Up` | Navigate up |
| `Down` | Navigate down |
| `Left` | Navigate left |
| `Right` | Navigate right |
| `Select` | Select / OK button |

## Playback Control

| Key | Function |
|-----|----------|
| `Play` | Play |
| `Pause` | Pause |
| `Rev` | Rewind |
| `Fwd` | Fast forward |
| `InstantReplay` | Instant replay (back 10 seconds) |

## Channel/Content

| Key | Function |
|-----|----------|
| `ChannelUp` | Channel up |
| `ChannelDown` | Channel down |
| `Info` | Show info/details |
| `Search` | Open search |

## Volume & Power

| Key | Function |
|-----|----------|
| `VolumeUp` | Increase volume |
| `VolumeDown` | Decrease volume |
| `VolumeMute` | Toggle mute |
| `PowerOff` | Power off (note: many Rokus don't support PowerOn via ECP) |
| `Power` | Toggle power (if supported) |

## Special Keys

| Key | Function |
|-----|----------|
| `Backspace` | Delete character (in text entry) |
| `Enter` | Enter/submit (in text entry) |
| `FindRemote` | Activate remote finder beep |
| `InputTuner` | Switch to antenna/tuner input (if applicable) |
| `InputHDMI1` | Switch to HDMI 1 input |
| `InputHDMI2` | Switch to HDMI 2 input |
| `InputHDMI3` | Switch to HDMI 3 input |
| `InputHDMI4` | Switch to HDMI 4 input |
| `InputAV1` | Switch to composite input |

## Text Entry

For entering text (searches, logins, etc.), use the `text` command instead of individual key presses:

```bash
python3 scripts/roku_control.py --ip <ip> text "search query"
```

This is much faster than pressing individual letter keys.

## Usage Examples

```bash
# Go home
python3 scripts/roku_control.py --ip 192.168.1.100 key Home

# Navigate menu
python3 scripts/roku_control.py --ip 192.168.1.100 key Down
python3 scripts/roku_control.py --ip 192.168.1.100 key Select

# Volume control
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeUp

# Playback
python3 scripts/roku_control.py --ip 192.168.1.100 key Play
python3 scripts/roku_control.py --ip 192.168.1.100 key Pause
```

## Key Sequences

For complex operations, send multiple keys in sequence:

```bash
# Navigate to second item and select
python3 scripts/roku_control.py --ip 192.168.1.100 key Down
sleep 0.5
python3 scripts/roku_control.py --ip 192.168.1.100 key Select
```

## Notes

- Not all keys are supported on all Roku models
- Power commands may not work on all devices (especially older models)
- Input switching keys only work on Roku TVs, not streaming sticks
- Volume keys require Roku TV or Roku with HDMI-CEC volume control configured
