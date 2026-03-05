---
name: sapi-tts
description: Windows SAPI5 text-to-speech with Neural voices. Lightweight alternative to GPU-heavy TTS - zero GPU usage, instant generation. Auto-detects best available voice for your language. Works on Windows 10/11.
---

# SAPI5 TTS (Windows)

Lightweight text-to-speech using Windows built-in SAPI5. Zero GPU, instant generation.

## Installation

Save the script below as `tts.ps1` in your skills folder:

```powershell
<#
.SYNOPSIS
    Windows SAPI5 TTS - Lightweight text-to-speech
.DESCRIPTION
    Uses Windows built-in speech synthesis (SAPI5).
    Works with Neural voices (Win11) or legacy voices (Win10).
    Zero GPU usage, instant generation.
#>

param(
    [Parameter(Mandatory=$false, Position=0)]
    [string]$Text = "",
    
    [Parameter(Mandatory=$false)]
    [Alias("Voice", "v")]
    [string]$VoiceName = "",
    
    [Parameter(Mandatory=$false)]
    [Alias("Lang", "l")]
    [string]$Language = "fr",
    
    [Parameter(Mandatory=$false)]
    [Alias("o")]
    [string]$Output = "",
    
    [Parameter(Mandatory=$false)]
    [Alias("r")]
    [int]$Rate = 0,
    
    [Parameter(Mandatory=$false)]
    [Alias("p")]
    [switch]$Play,
    
    [Parameter(Mandatory=$false)]
    [switch]$ListVoices
)

Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

$installedVoices = $synth.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { $_.VoiceInfo }

if ($ListVoices) {
    Write-Host "`nInstalled SAPI5 voices:`n" -ForegroundColor Cyan
    foreach ($v in $installedVoices) {
        $type = if ($v.Name -match "Online|Neural") { "[Neural]" } else { "[Legacy]" }
        Write-Host "  $($v.Name)" -ForegroundColor White -NoNewline
        Write-Host " $type" -ForegroundColor DarkGray -NoNewline
        Write-Host " - $($v.Culture) $($v.Gender)" -ForegroundColor Gray
    }
    Write-Host ""
    $synth.Dispose()
    exit 0
}

if (-not $Text) {
    Write-Error "Text required. Use: .\tts.ps1 'Your text here'"
    Write-Host "Use -ListVoices to see available voices"
    $synth.Dispose()
    exit 1
}

function Select-BestVoice {
    param($voices, $preferredName, $lang)
    
    if ($preferredName) {
        $match = $voices | Where-Object { $_.Name -like "*$preferredName*" } | Select-Object -First 1
        if ($match) { return $match }
        Write-Warning "Voice '$preferredName' not found, auto-selecting..."
    }
    
    $cultureMap = @{
        "fr" = "fr-FR"; "french" = "fr-FR"
        "en" = "en-US"; "english" = "en-US"
        "de" = "de-DE"; "german" = "de-DE"
        "es" = "es-ES"; "spanish" = "es-ES"
        "it" = "it-IT"; "italian" = "it-IT"
    }
    $targetCulture = $cultureMap[$lang.ToLower()]
    if (-not $targetCulture) { $targetCulture = $lang }
    
    $neuralMatch = $voices | Where-Object { 
        $_.Name -match "Online|Neural" -and $_.Culture.Name -eq $targetCulture 
    } | Select-Object -First 1
    if ($neuralMatch) { return $neuralMatch }
    
    $langMatch = $voices | Where-Object { $_.Culture.Name -eq $targetCulture } | Select-Object -First 1
    if ($langMatch) { return $langMatch }
    
    $anyNeural = $voices | Where-Object { $_.Name -match "Online|Neural" } | Select-Object -First 1
    if ($anyNeural) { return $anyNeural }
    
    return $voices | Select-Object -First 1
}

$selectedVoice = Select-BestVoice -voices $installedVoices -preferredName $VoiceName -lang $Language

if (-not $selectedVoice) {
    Write-Error "No SAPI5 voices found! Install voices in Windows Settings > Time & Language > Speech"
    $synth.Dispose()
    exit 1
}

if (-not $Output) {
    $ttsDir = "$env:USERPROFILE\.openclaw\workspace\tts"
    if (-not (Test-Path $ttsDir)) { New-Item -ItemType Directory -Path $ttsDir -Force | Out-Null }
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $Output = "$ttsDir\sapi_$timestamp.wav"
}

try {
    $synth.SelectVoice($selectedVoice.Name)
    $synth.Rate = $Rate
    $synth.SetOutputToWaveFile($Output)
    $synth.Speak($Text)
    $synth.SetOutputToNull()
    
    Write-Host "Voice: $($selectedVoice.Name) [$($selectedVoice.Culture)]" -ForegroundColor Cyan
    Write-Host "MEDIA:$Output"
    
    # Auto-play if requested (uses .NET MediaPlayer, no external player)
    if ($Play) {
        Add-Type -AssemblyName PresentationCore
        $player = New-Object System.Windows.Media.MediaPlayer
        $player.Open([Uri]$Output)
        $player.Play()
        Start-Sleep -Milliseconds 500
        while ($player.Position -lt $player.NaturalDuration.TimeSpan) {
            Start-Sleep -Milliseconds 100
        }
        $player.Close()
    }
    
} catch {
    Write-Error "TTS failed: $($_.Exception.Message)"
    exit 1
} finally {
    $synth.Dispose()
}
```

## Quick Start

```powershell
# Generate audio file
.\tts.ps1 "Bonjour, comment vas-tu ?"

# Generate AND play immediately
.\tts.ps1 "Bonjour !" -Play
```

## Parameters

| Parameter | Alias | Default | Description |
|-----------|-------|---------|-------------|
| `-Text` | (positional) | required | Text to speak |
| `-VoiceName` | `-Voice`, `-v` | auto | Voice name (partial match OK) |
| `-Language` | `-Lang`, `-l` | fr | Language: fr, en, de, es, it... |
| `-Output` | `-o` | auto | Output WAV file path |
| `-Rate` | `-r` | 0 | Speed: -10 (slow) to +10 (fast) |
| `-Play` | `-p` | false | Play audio immediately after generation |
| `-ListVoices` | | | Show installed voices |

## Examples

```powershell
# French with auto-play
.\tts.ps1 "Bonjour !" -Lang fr -Play

# English, faster
.\tts.ps1 "Hello there!" -Lang en -Rate 2 -Play

# Specific voice
.\tts.ps1 "Salut !" -Voice "Denise" -Play

# List available voices
.\tts.ps1 -ListVoices
```

## Installing Neural Voices (Recommended)

Neural voices sound much better than legacy Desktop voices.

### Windows 11
Neural voices are built-in. Go to:
**Settings → Time & Language → Speech → Manage voices**

### Windows 10/11 (More voices)
For additional Neural voices (like French Denise):

1. Install [NaturalVoiceSAPIAdapter](https://github.com/gexgd0419/NaturalVoiceSAPIAdapter)
2. Download voices in **Settings → Time & Language → Speech**
3. Run `-ListVoices` to verify

## Performance

- **Generation:** Instant (< 1 second)
- **GPU:** None
- **CPU:** Minimal
- **Quality:** Good (Neural) / Basic (Legacy)

## Credits

Made by Pocus 🎩 — AI assistant, with Olive (@Korddie).
