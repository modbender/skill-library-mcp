# record camera - Full Reference

## Options

| Option | Description | Default |
|---|---|---|
| `--list-cameras` | List available cameras and exit. | - |
| `--camera <id\|name>` | Camera ID or name substring. | system default |
| `--mode <video\|photo>` | Capture mode. | video |
| `--photo` | Alias for `--mode photo`. | - |
| `--duration <seconds>` | Stop recording after N seconds (video only). | - |
| `--output <path>` | File or directory for output. | temp dir |
| `--name <pattern>` | Filename pattern (strftime tokens, `{uuid}`, `{chunk}`). | - |
| `--overwrite` | Overwrite existing output file. | false |
| `--json` | Print JSON to stdout. | false |
| `--stop-key <char>` | Stop key. | `s` |
| `--max-size <MB>` | Stop when file reaches this size in MB (video only). | - |
| `--split <seconds>` | Split into chunks (video only). Output must be a directory. | - |
| `--fps <fps>` | Frames per second (video only). | - |
| `--resolution <WxH>` | Capture resolution (e.g. `1280x720`). | - |
| `--audio` | Record from default microphone (video only). | false |
| `--photo-format <format>` | Photo format: `jpeg`, `heic` (photo only). | jpeg |

## Examples

```bash
# Record webcam for 5 seconds
record camera --duration 5

# Take a photo
record camera --photo
record camera --photo --photo-format heic

# Record with specific camera
record camera --camera "FaceTime" --duration 10

# Record at specific resolution
record camera --resolution 1280x720 --fps 30 --duration 10

# Record with microphone audio
record camera --audio --duration 5

# Split into chunks
record camera --split 30 --output /tmp

# List cameras
record camera --list-cameras
record camera --list-cameras --json
```
