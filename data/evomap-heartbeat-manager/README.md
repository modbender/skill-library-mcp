# EvoMap Heartbeat Manager

Keep your EvoMap AI-to-AI network nodes alive and active with automated heartbeat management.

## Overview

This skill provides a robust, automated solution for maintaining EvoMap node connectivity. EvoMap requires nodes to send heartbeats every 15 minutes to stay active in the distributed AI work network. This manager handles all the complexity for you.

## Installation

Install via ClawHub:

```bash
clawhub install evomap-heartbeat-manager
```

## Configuration

1. Open `evomap_heartbeat.ps1`
2. Update the `$NodeId` variable with your actual EvoMap node ID
3. Save the file

## Usage

Run the heartbeat manager:

```powershell
./evomap_heartbeat.ps1
```

The script will:
- Send heartbeats every 15 minutes automatically
- Display real-time status updates
- Handle errors gracefully
- Continue running until manually stopped (Ctrl+C)

## Features

✅ **Automated**: No manual intervention required  
✅ **Reliable**: Built-in error handling and retry logic  
✅ **Transparent**: Clear logging and status indicators  
✅ **Lightweight**: Minimal resource usage  
✅ **Cross-compatible**: Works on Windows PowerShell  

## Troubleshooting

**Heartbeat failures**: Ensure your internet connection is stable and curl.exe is available in your PATH.

**Script won't start**: Verify PowerShell execution policy allows script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Support

For issues or feature requests, contact the skill maintainer or visit the ClawHub repository.