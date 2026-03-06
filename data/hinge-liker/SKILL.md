---
name: hinge-liker
description: "Automated Hinge dating profile liker using Android emulator + Gemini vision AI. Scrolls through full profiles, analyzes attractiveness with AI, likes the best photo/prompt with witty comments, skips others. Sends a detailed text report after each session. Use when asked to run Hinge likes, set up Hinge automation, check Hinge status, or manage daily dating app swiping."
---

# Hinge Auto-Liker

Automates Hinge swiping on an Android emulator. Uses Gemini vision to evaluate profiles, pick the best photo/prompt, and send witty comments.

## Requirements

- Android emulator (AVD) with Hinge installed and logged in
- `adb` in PATH
- `GEMINI_API_KEY` environment variable (Gemini 2.5 Flash recommended)
- Python 3.8+
- Java (for Android emulator)

## Setup (First Time)

1. Install Android command line tools (via Homebrew: `brew install --cask android-commandlinetools`)
2. Create an AVD: `avdmanager create avd -n HingePhone -k "system-images;android-34;google_apis;arm64-v8a" -d pixel_6`
3. Boot the emulator with a window, install Hinge from Play Store, and log in manually
4. Set `GEMINI_API_KEY` in environment

## Running

```bash
# Set environment
export PATH="<android-tools-path>/platform-tools:<android-tools-path>/emulator:$PATH"
export GEMINI_API_KEY="your-key-here"

# Boot emulator (windowed for video, add -no-window for headless)
emulator -avd HingePhone -no-audio -no-metrics -gpu swiftshader_indirect &

# Wait for boot
adb wait-for-device
while [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]; do sleep 2; done

# Launch Hinge
adb shell am start -a android.intent.action.MAIN -n co.hinge.app/.ui.AppActivity
sleep 10

# Optional: start screen recording
adb shell screenrecord --time-limit 300 /sdcard/hinge_session.mp4 &

# Run the liker
python3 scripts/hinge_android.py --likes 8 --user-desc "a 25yo tech guy in SF who's fit and active"

# Pull recording + kill emulator
adb shell pkill -INT screenrecord; sleep 3
adb pull /sdcard/hinge_session.mp4 ./recordings/session.mp4
adb emu kill
```

## Script Options

| Flag | Default | Description |
|------|---------|-------------|
| `--likes` | 8 | Max likes per session |
| `--adb` | `adb` | Path to adb binary |
| `--user-desc` | generic | Description of the user for AI matching |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Model name (default: `gemini-2.5-flash`) |
| `ADB_PATH` | No | Full path to adb binary |
| `HINGE_WORK_DIR` | No | Working directory for screenshots/logs |

## Output

The script prints a **session report** to stdout with:
- Total profiles seen, liked, skipped
- For each profile: who they are, why it liked/skipped, the comment sent, which content was liked

JSON logs are saved to `logs/` directory.

## Scheduling as a Daily Cron

Set up via OpenClaw cron for daily automated runs. Key notes:
- **Hardcode GEMINI_API_KEY in the cron payload** — cron shells don't source ~/.zshrc
- Use `am start` to launch Hinge, not `monkey` (more reliable)
- Compress videos before sending via iMessage (16MB limit): `ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset fast -vf scale=720:-2 output.mp4`

## After Each Session

Send the user a text report including:
1. How many profiles seen / liked / skipped
2. For each liked profile: who she is, why the AI liked her, what comment was sent
3. For each skipped profile: brief reason why
4. Any errors (paywall, API failures, etc.)
5. Video recording if available (compressed for messaging)

## Troubleshooting

- **Paywall/out of likes**: Free likes reset ~24h after last batch. Schedule runs accordingly.
- **Gemini empty responses**: Increase `maxOutputTokens`, check API key/quota.
- **Can't find buttons**: Hinge UI changes periodically — check `find_all_hearts()` and `find_skip_button()` patterns.
- **Emulator crashes**: Check disk space (`df -h`), try `-gpu swiftshader_indirect`.
