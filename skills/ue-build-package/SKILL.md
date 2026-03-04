---
name: ue-build-package
description: |
  Compile and package Unreal Engine projects. Use when: (1) Building UE project from command line,
  (2) Packaging for distribution (Android/iOS/Windows), (3) Running Cook, (4) Building SLN in Rider/VS,
  (5) Generating pak files, (6) Running UE editor commands, (7) Checking build progress
---

# UE Build & Package

## Common Build Commands

### Windows Development Build
```bash
# Using UnrealBuildTool
Engine\Engine\Build\BatchFiles\RunUBT.bat <Target> <Platform> <Configuration> -Project=<path>

# Example: Build client
Engine\Engine\Build\BatchFiles\RunUBT.bat SilverPalaceClient Win64 Development -Project=Project\SilverPalace.uproject

# Example: Build editor
Engine\Engine\Build\BatchFiles\RunUBT.bat SilverPalaceEditor Win64 Development -Project=Project\SilverPalace.uproject
```

### Package for Windows
```bash
Engine\Engine\Build\BatchFiles\RunUAT.bat BuildCookRun -project=Project\SilverPalace.uproject -platform=Win64 -build
```

### Package for Android
```bash
Engine\Engine\Build\BatchFiles\RunUAT.bat BuildCookRun -project=Project\SilverPalace.uproject -platform=Android -cookflavor=ASTC
```

### Package for iOS
```bash
Engine\Engine\Build\BatchFiles\RunUAT.bat BuildCookRun -project=Project\SilverPalace.uproject -platform=IOS
```

## Project Paths (SilverPalace)

- Project Root: `E:\SilverVer1.0.0\Project`
- Solution: `E:\SilverVer1.0.0\Project\SilverPalace.sln`
- Binaries: `E:\SilverVer1.0.0\Project\Binaries\Win64`
- Content: `E:\SilverVer1.0.0\Project\Content`
- Saved: `E:\SilverVer1.0.0\Project\Saved`
- Engine: `E:\SilverVer1.0.0\Engine\Engine`

## Build Targets

| Target | Platform | Description |
|--------|----------|-------------|
| SilverPalaceClient | Win64 | Windows 客户端 |
| SilverPalaceEditor | Win64 | 编辑器 |
| SilverPalace | Win64 | 服务器版本 |

## Check Build Status

### Check if building
```powershell
Get-Process | Where-Object {$_.ProcessName -like '*MSBuild*' -or $_.ProcessName -like '*UnrealBuild*'}
```

### Check build output
```powershell
Get-ChildItem "Project\Saved\Logs" | Sort-Object LastWriteTime -Descending
```

### Check compiled binaries
```powershell
Get-ChildItem "Project\Binaries\Win64" -Filter "*.exe"
```

## Rider Integration

Use `nodes` tool to:
1. Find Rider: `Get-Process rider64`
2. Focus window: Use SetForegroundWindow + SendKeys
3. Build shortcut: Ctrl+F9 (or via menu)

## Quick Build (via Rider)
- **Build**: Ctrl+B
- **Rebuild**: Ctrl+Shift+B  
- **Run**: F5
- **Package**: Via菜单 > File > Package Project > Windows

## Troubleshooting

### "No platforms specified"
```bash
# Add platform explicitly
-Target=SilverPalaceClient -Platform=Win64
```

### "Conflicting instance running"
```bash
# Check for running builds
Get-Process | Where-Object {$_.ProcessName -like '*MSBuild*'}

# Wait or kill previous build
```

### Long cook times
- Check `DerivedDataCache` folder size
- Clear cache: Delete `Project\Saved\DerivedDataCache`

### Packaging failures
- Check `Saved\StagedBuilds` for error logs
- Check `Saved\Logs` for cooking errors
