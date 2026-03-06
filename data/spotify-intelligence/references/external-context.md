# External Context (Node-ready)

Prepare the skill for future phone-node signals (GPS/Bluetooth/motion).

## Tables
- `external_context_events`
- `context_feature_flags` (`node_context_enabled`)

## Commands
Init:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\context\external-context-commands.ps1 -Action init
```

Ingest sample events:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\context\external-context-commands.ps1 -Action ingest -ContextType bluetooth_device -ContextValue "BT-Box"
powershell -ExecutionPolicy Bypass -File .\scripts\context\external-context-commands.ps1 -Action ingest -ContextType location -ContextValue "home"
powershell -ExecutionPolicy Bypass -File .\scripts\context\external-context-commands.ps1 -Action ingest -ContextType motion -ContextValue "walking"
```

Resolve context (priority: BT > location > motion):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\context\external-context-commands.ps1 -Action resolve
```

Enable node context:
```powershell
sqlite3 .\data\spotify-intelligence.sqlite "UPDATE context_feature_flags SET value='true', updated_at=datetime('now') WHERE key='node_context_enabled';"
```

## Integration
`recommend-commands.ps1 -Action run` automatically tries external-context resolve first, then falls back to manual device/profile.
