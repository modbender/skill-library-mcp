#!/usr/bin/env bash
set -euo pipefail

# List installed voices on Windows (from WSL).
# Note: Escape $ to prevent bash expansion.
powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Speech; \$s=[System.Speech.Synthesis.SpeechSynthesizer]::new(); \$s.GetInstalledVoices() | ForEach-Object { \$_.VoiceInfo.Name }"
