# record screen - Full Reference

## Options

| Option | Description | Default |
|---|---|---|
| `--duration <seconds>` | Stop after N seconds. | - |
| `--output <path>` | File or directory for output. | temp dir |
| `--name <pattern>` | Filename pattern (strftime tokens, `{uuid}`, `{chunk}`). | - |
| `--overwrite` | Overwrite existing output file. | false |
| `--json` | Print JSON to stdout. | false |
| `--list-displays` | List available displays and exit. | - |
| `--list-windows` | List available windows and exit. | - |
| `--display <id\|primary>` | Capture a display by ID or `primary`. | - |
| `--window <id\|title>` | Capture a window by ID or title/app substring. | - |
| `--stop-key <char>` | Stop key. | `s` |
| `--pause-key <char>` | Pause key. | `p` |
| `--resume-key <char>` | Resume key. | `r` |
| `--max-size <MB>` | Stop when file reaches this size in MB. | - |
| `--split <seconds>` | Split into chunks. Output must be a directory. | - |
| `--fps <fps>` | Frames per second. | 30 |
| `--codec <codec>` | Video codec: `h264`, `hevc`, `prores`. | h264 |
| `--bit-rate <bps>` | Video bit rate (h264/hevc only). | - |
| `--scale <factor>` | Scale factor (e.g. `0.5` for half size). | 1 |
| `--hide-cursor` | Hide cursor in recording. | false |
| `--show-clicks` | Show mouse click highlights (macOS 15+). | false |
| `--region <spec>` | Capture region as `x,y,w,h`. | full area |
| `--audio <mode>` | Audio: `none`, `system`, `mic`, `both`. | none |
| `--audio-sample-rate <Hz>` | Audio sample rate. | 48000 |
| `--audio-channels <count>` | Audio channels. | 2 |
| `--system-gain <multiplier>` | Gain multiplier for system audio with `system`/`both`. | 1.0 |
| `--screenshot` | Capture a single screenshot instead of video. | false |

## Region Specification

Region values can be pixels, fractions (0..1), or percentages:

```bash
--region 100,200,1280,720       # pixels
--region 0.1,0.1,0.8,0.8       # fractions
--region 10%,10%,80%,80%        # percentages
--region center:80%x80%         # centered
```

## Examples

```bash
# Record screen for 5 seconds
record screen --duration 5

# Take a screenshot
record screen --screenshot
record screen --screenshot --output /tmp/screen.png

# Screenshot of a specific window
record screen --screenshot --window "Safari"

# Screenshot of a region
record screen --screenshot --region 10%,10%,80%,80%

# Record specific display
record screen --duration 10 --display primary --fps 60

# Record with system audio
record screen --duration 10 --audio system

# Record with system + mic mixed into one audio track
record screen --duration 10 --audio both

# Boost system audio in mixed capture
record screen --duration 10 --audio both --system-gain 1.8

# Record with HEVC codec at lower resolution
record screen --duration 10 --codec hevc --scale 0.5

# Split into 30-second chunks
record screen --split 30 --output /tmp

# List available targets
record screen --list-displays
record screen --list-windows --json
```

## Notes

- `--audio mic` and `--audio both` require Microphone permission.
- `--audio system` and `--audio both` require Screen Recording permission.
- `--system-gain` boosts system audio before mixing/encoding. Large values can clip; start near `1.2` to `2.0`.
