---
name: win-sysinfo
description: System diagnostics — CPU, RAM, battery, GPU, network, processes, OS info via WMI, zero dependencies.
metadata:
  {
    "openclaw":
      {
        "emoji": "🖥️",
        "os": ["win32"],
      },
  }
---

# win-sysinfo

System diagnostics and hardware info for Windows.
CPU, RAM, battery, GPU, network, running processes, OS details.
Zero external dependencies — uses built-in WMI (Get-CimInstance) and PowerShell.

Works on Windows 10/11 with PowerShell 5.1+.

## System Overview

```powershell
powershell.exe -NoProfile -Command "
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$uptime = (Get-Date) - $os.LastBootUpTime
Write-Host ('Computer: {0}' -f $cs.Name)
Write-Host ('OS: {0} (Build {1})' -f $os.Caption, $os.BuildNumber)
Write-Host ('Architecture: {0}' -f $os.OSArchitecture)
Write-Host ('User: {0}\{1}' -f $cs.Domain, $env:USERNAME)
Write-Host ('Uptime: {0}d {1}h {2}m' -f [int]$uptime.TotalDays, $uptime.Hours, $uptime.Minutes)
Write-Host ('Install Date: {0}' -f $os.InstallDate.ToString('yyyy-MM-dd'))
"
```

## CPU Info

```powershell
powershell.exe -NoProfile -Command "
$cpu = Get-CimInstance Win32_Processor
foreach ($c in $cpu) {
    Write-Host ('CPU: {0}' -f $c.Name.Trim())
    Write-Host ('Cores: {0} physical, {1} logical' -f $c.NumberOfCores, $c.NumberOfLogicalProcessors)
    Write-Host ('Max Clock: {0} MHz' -f $c.MaxClockSpeed)
    Write-Host ('Current Clock: {0} MHz' -f $c.CurrentClockSpeed)
    Write-Host ('Load: {0}%' -f $c.LoadPercentage)
}
"
```

## CPU Usage (Real-Time)

```powershell
powershell.exe -NoProfile -Command "
$samples = 3
Write-Host ('Sampling CPU usage ({0} samples)...' -f $samples)
for ($i = 1; $i -le $samples; $i++) {
    $load = (Get-CimInstance Win32_Processor).LoadPercentage
    Write-Host ('  Sample {0}: {1}%' -f $i, $load)
    if ($i -lt $samples) { Start-Sleep -Seconds 1 }
}
"
```

## Memory

```powershell
powershell.exe -NoProfile -Command "
$os = Get-CimInstance Win32_OperatingSystem
$totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$usedGB = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1)
$pct = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize * 100, 1)
Write-Host ('Total: {0} GB' -f $totalGB)
Write-Host ('Used: {0} GB ({1}%)' -f $usedGB, $pct)
Write-Host ('Free: {0} GB' -f $freeGB)
Write-Host ''
Write-Host '--- Physical DIMMs ---'
Get-CimInstance Win32_PhysicalMemory | ForEach-Object {
    Write-Host ('{0}: {1} GB {2} @ {3} MHz' -f $_.DeviceLocator, [math]::Round($_.Capacity/1GB), $_.MemoryType, $_.Speed)
}
"
```

## Battery

```powershell
powershell.exe -NoProfile -Command "
$batt = Get-CimInstance Win32_Battery
if ($batt) {
    foreach ($b in $batt) {
        $status = switch ($b.BatteryStatus) {
            1 { 'Discharging' }
            2 { 'AC Power' }
            3 { 'Fully Charged' }
            4 { 'Low' }
            5 { 'Critical' }
            6 { 'Charging' }
            7 { 'Charging (High)' }
            8 { 'Charging (Low)' }
            9 { 'Charging (Critical)' }
            default { 'Unknown' }
        }
        Write-Host ('Battery: {0}' -f $b.Name)
        Write-Host ('Charge: {0}%' -f $b.EstimatedChargeRemaining)
        Write-Host ('Status: {0}' -f $status)
        if ($b.EstimatedRunTime -and $b.EstimatedRunTime -lt 71582788) {
            Write-Host ('Estimated Runtime: {0} min' -f $b.EstimatedRunTime)
        }
    }
} else {
    Write-Host 'No battery detected (desktop PC).'
}
"
```

## GPU Info

```powershell
powershell.exe -NoProfile -Command "
Get-CimInstance Win32_VideoController | ForEach-Object {
    Write-Host ('GPU: {0}' -f $_.Name)
    Write-Host ('Driver: {0} ({1})' -f $_.DriverVersion, $_.DriverDate.ToString('yyyy-MM-dd'))
    if ($_.AdapterRAM -gt 0) {
        Write-Host ('VRAM: {0} GB' -f [math]::Round($_.AdapterRAM / 1GB, 1))
    }
    Write-Host ('Resolution: {0}x{1}' -f $_.CurrentHorizontalResolution, $_.CurrentVerticalResolution)
    Write-Host ('Status: {0}' -f $_.Status)
    Write-Host ''
}
"
```

## NPU / AI Accelerator

Check for Intel AI Boost NPU or other AI accelerators:

```powershell
powershell.exe -NoProfile -Command "
Write-Host '--- NPU / AI Devices ---'
Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'NPU|Neural|AI Boost|Movidius' } | ForEach-Object {
    Write-Host ('{0} [{1}]' -f $_.Name, $_.Status)
}
Write-Host ''
Write-Host '--- DirectML Capable GPUs ---'
Get-CimInstance Win32_VideoController | Where-Object { $_.Status -eq 'OK' } | ForEach-Object {
    Write-Host ('{0} (VRAM: {1} GB)' -f $_.Name, [math]::Round($_.AdapterRAM/1GB,1))
}
"
```

## Network

```powershell
powershell.exe -NoProfile -Command "
Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled } | ForEach-Object {
    Write-Host ('--- {0} ---' -f $_.Description)
    Write-Host ('  IP: {0}' -f ($_.IPAddress -join ', '))
    Write-Host ('  Subnet: {0}' -f ($_.IPSubnet -join ', '))
    Write-Host ('  Gateway: {0}' -f ($_.DefaultIPGateway -join ', '))
    Write-Host ('  DNS: {0}' -f ($_.DNSServerSearchOrder -join ', '))
    Write-Host ('  MAC: {0}' -f $_.MACAddress)
    Write-Host ('  DHCP: {0}' -f $_.DHCPEnabled)
    Write-Host ''
}
"
```

### Internet Connectivity

```powershell
powershell.exe -NoProfile -Command "
try {
    $result = Test-Connection -ComputerName 8.8.8.8 -Count 2 -ErrorAction Stop
    $avg = ($result | Measure-Object -Property ResponseTime -Average).Average
    Write-Host ('Internet: Connected (avg {0:N0}ms to 8.8.8.8)' -f $avg)
} catch {
    Write-Host 'Internet: Disconnected or unreachable'
}
"
```

## Running Processes

### Top by CPU

```powershell
powershell.exe -NoProfile -Command "
Get-Process | Sort-Object CPU -Descending | Select-Object -First COUNT |
  Select-Object Name, Id,
    @{N='CPU(s)';E={[math]::Round($_.CPU, 1)}},
    @{N='MemMB';E={[math]::Round($_.WorkingSet64/1MB, 1)}} |
  Format-Table -AutoSize
"
```

Replace `COUNT` with the number of processes to show (e.g., `15`).

### Top by Memory

```powershell
powershell.exe -NoProfile -Command "
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First COUNT |
  Select-Object Name, Id,
    @{N='MemMB';E={[math]::Round($_.WorkingSet64/1MB, 1)}},
    @{N='CPU(s)';E={[math]::Round($_.CPU, 1)}} |
  Format-Table -AutoSize
"
```

### Find a Process

```powershell
powershell.exe -NoProfile -Command "
Get-Process -Name '*PROCESS_NAME*' -ErrorAction SilentlyContinue |
  Select-Object Name, Id,
    @{N='MemMB';E={[math]::Round($_.WorkingSet64/1MB, 1)}},
    @{N='CPU(s)';E={[math]::Round($_.CPU, 1)}},
    Path |
  Format-Table -AutoSize
"
```

Replace `PROCESS_NAME` with a partial name (e.g., `chrome`, `code`, `ollama`).

### Kill a Process

```powershell
powershell.exe -NoProfile -Command "
Stop-Process -Id PROCESS_ID -Force
Write-Host 'Process PROCESS_ID terminated.'
"
```

Replace `PROCESS_ID` with the PID from the process list.

## Startup Programs

```powershell
powershell.exe -NoProfile -Command "
Get-CimInstance Win32_StartupCommand |
  Select-Object Name, Command, Location |
  Format-Table -AutoSize
"
```

## Installed Software

```powershell
powershell.exe -NoProfile -Command "
Get-CimInstance Win32_Product | Select-Object Name, Version, Vendor |
  Sort-Object Name | Format-Table -AutoSize
"
```

Note: `Win32_Product` can be slow. For a faster check of a specific program, use `winget list PROGRAM_NAME` (via the `winget` skill).

## Environment Variables

```powershell
powershell.exe -NoProfile -Command "
Get-ChildItem Env: | Sort-Object Name | Format-Table Name, Value -AutoSize
"
```

### Check a Specific Variable

```powershell
powershell.exe -NoProfile -Command "
Write-Host ('VAR_NAME = {0}' -f $env:VAR_NAME)
"
```

## Common Workflows

### System health check

```
1. win-sysinfo: system overview (uptime, OS version)
2. win-sysinfo: CPU usage + memory usage
3. win-sysinfo: battery status
4. win-files: list drives (disk space)
5. Report any issues found
```

### Diagnose slow machine

```
1. win-sysinfo: top processes by CPU
2. win-sysinfo: top processes by memory
3. win-sysinfo: memory usage percentage
4. Identify resource hogs and suggest actions
```

### Network troubleshooting

```
1. win-sysinfo: network adapters and IP config
2. win-sysinfo: internet connectivity test
3. Report connection status and suggest fixes
```

### Pre-meeting check

```
1. win-sysinfo: battery level
2. win-sysinfo: internet connectivity
3. win-sysinfo: CPU/memory headroom
4. Alert if any issues before joining
```

## Notes

- Fully offline — no API keys, no network (except connectivity test), no external dependencies.
- Uses WMI (`Get-CimInstance`) and built-in PowerShell cmdlets.
- CPU load percentage is a snapshot — use the real-time sampling command for trends.
- Battery info only available on laptops/tablets — desktops will show "No battery detected."
- `Win32_Product` is slow (~30s) — prefer `winget list` for faster software queries.
- NPU detection uses PnP device name matching — works for Intel AI Boost, may need adjustment for other NPU brands.
- For disk space info, use the `win-files` skill's List Drives command.
- Process kill requires appropriate permissions — elevated processes may need admin PowerShell.
- GPU VRAM via `Win32_VideoController.AdapterRAM` is a 32-bit field (max ~4 GB). For GPUs with >4 GB VRAM, the reported value will be incorrect. Use `dxdiag` or GPU-specific tools for accurate VRAM.
