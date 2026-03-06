---
name: ue-log-analyzer
description: |
  Analyze Unreal Engine log files for errors, warnings, crashes, and performance issues.
  Use when: (1) User provides UE log file, (2) Analyzing crash dumps, (3) Debugging startup issues,
  (4) Finding performance bottlenecks in UE projects, (5) Checking pak mounting errors, (6) Lua errors in UnLua
---

# UE Log Analyzer

## Quick Start

Use the `nodes` tool to read log files from the paired computer, or use `read` for local files.

## Common Error Patterns

### Critical Errors (Fatal)
```
LogInit: Session CrashGUID
Fatal error:
Assertion failed:
Ensure condition failed:
```

### Rendering Issues
```
LogD3D12RHI: Error:
LogVulkanRHI: Error:
LogRendererCore: Warning:
```

### Lua/UnLua Errors
```
LogUnLua: Error:
LogUnLua: Warning:
attempt to index a nil value
```

### Pak/Loading Errors
```
LogPakFile: Error:
LogStreaming: Error:
LogAssetRegistry: Error:
```

### Network Issues
```
LogNet: Warning:
LogOnline: Error:
```

## Analysis Workflow

1. **Find errors**: Search for `Error:|FATAL|CRASH|Assert`
2. **Find warnings**: Search for `Warning:`
3. **Check crash**: Look for `Session CrashGUID`
4. **Lua errors**: Search `LogUnLua:`
5. **Timing**: Check timestamps for hang points

## Project-Specific Patterns

For SilverPalace project:
- HeSDK errors: `HeSDKLogError:`
- Module loading: `MainModule_`, `SubModule_`
- VersionUpdate: `MainModule_VersionUpdate`
- BigWorld: `MainModule_BigWorld`

## Common Issues & Solutions

### 1. UMG_GeneralTransitions Missing
```
LogStreaming: Error: Couldn't find file for package /Game/UI/VX/VX_Common/UMG/UMG_GeneralTransitions
LogUnLua: Error: LoadedAsset is nil
```
**Fix**: Check pak packaging includes this UI asset

### 2. SysStartUpDev nil
```
Error: c_UMG_Login_Announcement.lua:26: attempt to index a nil value (field 'SysStartUpDev')
```
**Fix**: Check Lua config table for SysStartUpDev entry

### 3. Scalability ini error
```
Ensure condition failed: false
Scalability.ini can only set ECVF_Scalability console variables
('r.Mobile.AntiAliasing'='2' is ignored)
```
**Fix**: Fix Scalability.ini r.Mobile.AntiAliasing value (0 or 1)

### 4. Shader/PSO errors
```
LogD3D12RHI: Error: Failed to create pipeline state
```
**Fix**: Rebuild shaders or clear shader cache

## Output Format

Provide findings in:
- Error count by severity (Fatal/Error/Warning)
- Timeline of events
- Likely root cause
- Suggested fixes (优先级排序)
