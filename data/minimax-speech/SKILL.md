---
name: minimax-tts
description: Manage MiniMax Speech 2.8 T2A (text-to-audio) and voice catalog lookups. Trigger when you need a precise MiniMax voice_id, a Speech 2.8 TTS request, or to list the available MiniMax system/cloned/generated voices.
---

# MiniMax Speech 2.8 helper

1. **Install dependencies.** Run `pip install requests` in the environment that will execute the script. The CLI talks to MiniMax's REST API, so you only need the `requests` library on top of Python 3.11+.
2. **Set your MiniMax credential.** Export `MINIMAX_API_KEY` with the API key the user promised to supply. The script will refuse to run without it.
3. **Use the bundled CLI.** `scripts/minimax_tts.py` exposes two subcommands:
   - `tts`: calls `POST https://api.minimax.io/v1/t2a_v2` (Speech 2.8 T2A HTTP) with the desired voice_id, voice settings, audio configuration, and optional voice effects. Example:
     ```bash
     python scripts/minimax_tts.py tts \
       --text "Tonight in Shenzhen the skies are clear." \
       --voice-id "Sweet_Girl_2" \
       --model speech-2.8-hd \
       --audio-format mp3 \
       --output minimax-weather.mp3
     ```
     The script decodes the hex/base64 payload, saves the file, and prints metadata. Override the endpoint with `--endpoint` if you must hit `https://api-uw.minimax.io/v1/t2a_v2` or another region.
   - `voices`: calls `POST https://api.minimax.io/v1/get_voice` to enumerate `system`, `voice_cloning`, `voice_generation`, or `all` categories. Example:
     ```bash
     python scripts/minimax_tts.py voices --voice-type all --print-response
     ```
4. **Customize TTS payloads via CLI switches.** Use `--speed`, `--vol`, `--pitch`, and `--language-boost` to shape the voice. Control audio fidelity with `--sample-rate`, `--bitrate`, `--audio-format`, and `--channel`. Add pronunciation overrides (`--pronunciation "emoji=ee-moh-jee"`) or mix timbres (`--timbre-weight "Sweet_Girl_2=0.8"`). `--voice-modify-*` flags let you nudge pitch/intensity/timbre or append a sound effect such as `"spacious_echo"`. `--output-format` tells the script how the API returns audio (`hex`, `base64`, or a download `url`).
5. **Handle the JSON.** By default the script prints the `extra_info` field so you can read bitrate/sample rate/length. Use `--print-response` on either subcommand to dump the entire API payload for debugging. Save catalog JSON to disk with `--output <path>` when you need to reference voices later.

Keep this skill loaded any time you are asked for MiniMax-specific voices or when precise speech settings are required. The CLI gives you deterministic control over voice_id, model, and audio quality so you always get the `Sweet_Girl_2` (or any other) tone you expect. If you need to script these requests from another tool, copy the relevant `requests.post` logic from `scripts/minimax_tts.py`.
