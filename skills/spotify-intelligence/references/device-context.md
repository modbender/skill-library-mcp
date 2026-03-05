# Device Context Layer

Ziel: Empfehlungen und Lautstärke-Verhalten je Device kontextsensitiv machen.

## Device Profiles
Script:
- `scripts/device/device-context-commands.ps1`

Aktionen:
- `init`
- `set-profile`
- `show-profiles`
- `show-stats`

Beispiel:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\device\device-context-commands.ps1 -Action set-profile -DeviceName "Alle" -ContextTag "zuhause" -FocusPreference 0.4 -EnergyPreference 0.7 -BassPreference 0.5
```

## Empfehlung mit Device-Kontext
`recommend-now` akzeptiert `--device-name` und gewichtet dann passend:
- focus_preference
- energy_preference

Beispiel:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\recommend\recommend-commands.ps1 -Action run -Mode passend -Top 10 -DeviceName "Alle"
```
