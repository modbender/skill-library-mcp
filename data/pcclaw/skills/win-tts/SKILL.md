---
name: win-tts
description: Text-to-speech using Windows built-in speech synthesis — speak aloud or save to WAV, multilingual, zero dependencies.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔊",
        "os": ["win32"],
      },
  }
---

# win-tts

Text-to-speech using the Windows built-in speech engine (SAPI 5).
Speak text aloud or save to WAV files. Multilingual, fully offline, zero external dependencies.

Works on Windows 10/11 with PowerShell 5.1+.

## List Available Voices

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.GetInstalledVoices() | ForEach-Object {
    $v = $_.VoiceInfo
    Write-Host ('{0} | {1} | {2}' -f $v.Name, $v.Culture, $v.Gender)
}
$synth.Dispose()
"
```

Common voices: `Microsoft David Desktop` (en-US, Male), `Microsoft Zira Desktop` (en-US, Female), `Microsoft Hanhan Desktop` (zh-TW, Female).

Additional voices can be installed via Settings → Time & Language → Speech.

## Speak Text

### Basic (Default Voice)

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak('TEXT_TO_SPEAK')
$synth.Dispose()
"
```

Replace `TEXT_TO_SPEAK` with the text to speak aloud.

### With Specific Voice

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('VOICE_NAME')
$synth.Speak('TEXT_TO_SPEAK')
$synth.Dispose()
"
```

Replace `VOICE_NAME` with one of the installed voice names (e.g., `Microsoft David Desktop`).

### Chinese (Traditional)

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Hanhan Desktop')
$synth.Speak('你好，這是一個語音合成測試。')
$synth.Dispose()
"
```

## Control Speed and Volume

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = RATE
$synth.Volume = VOLUME
$synth.Speak('TEXT_TO_SPEAK')
$synth.Dispose()
"
```

- `RATE`: -10 (slowest) to 10 (fastest), default 0
- `VOLUME`: 0 (silent) to 100 (loudest), default 100

## Save Speech to WAV File

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('OUTPUT_PATH')
$synth.Speak('TEXT_TO_SPEAK')
$synth.SetOutputToDefaultAudioDevice()
$synth.Dispose()
Write-Host 'Saved to OUTPUT_PATH'
"
```

Replace `OUTPUT_PATH` with the full path for the WAV file (e.g., `C:\Users\me\speech.wav`).

## Speak with SSML

Use SSML for fine-grained control over pronunciation, pauses, emphasis, and pitch:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$ssml = @'
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
  <voice name='Microsoft David Desktop'>
    <prosody rate='medium' pitch='default'>
      Hello! <break time='500ms'/>
      This is <emphasis level='strong'>important</emphasis>.
    </prosody>
  </voice>
</speak>
'@
$synth.SpeakSsml($ssml)
$synth.Dispose()
"
```

### SSML Quick Reference

| Element | Example | Effect |
|---------|---------|--------|
| `<break>` | `<break time='500ms'/>` | Pause for 500ms |
| `<emphasis>` | `<emphasis level='strong'>word</emphasis>` | Stress a word |
| `<prosody>` | `<prosody rate='fast' pitch='high'>` | Control speed and pitch |
| `<say-as>` | `<say-as interpret-as='date'>2026-02-11</say-as>` | Read as date |
| `<voice>` | `<voice name='Microsoft Zira Desktop'>` | Switch voice mid-speech |

## Recommended Workflows

### Agent reads results aloud

```
1. Agent completes a task (search, analysis, etc.)
2. win-tts: speak the summary to the user
```

### Listen → Process → Respond

```
1. win-whisper: record and transcribe user speech
2. Agent processes the request
3. win-tts: speak the response aloud
```

### Read document aloud

```
1. Read file contents
2. win-tts: save to WAV for playback
3. Or speak directly for real-time reading
```

### Bilingual announcement

```
1. win-tts (David): speak English version
2. win-tts (Hanhan): speak Chinese version
```

## Notes

- Fully offline — no API keys, no network, no external dependencies.
- Uses .NET `System.Speech.Synthesis` (SAPI 5), built into Windows.
- Default voices: David (en-US male), Zira (en-US female), Hanhan (zh-TW female).
- More voices available via Settings → Time & Language → Speech → Add voices.
- WAV output is PCM format — compatible with `win-whisper` for round-trip testing.
- For higher-quality neural voices, consider Microsoft Edge TTS (requires network).
- Combine with `win-whisper` for a complete voice conversation loop.
