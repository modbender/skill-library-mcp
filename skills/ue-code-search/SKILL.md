---
name: ue-code-search
description: |
  Search Unreal Engine C++ and Blueprint code. Use when: (1) Finding function definitions,
  (2) Searching for class names, (3) Finding UMG widget references, (4) Searching Lua/UnLua code,
  (5) Finding Blueprint-usable functions, (6) Searching across C++ and Lua
---

# UE Code Search

## Search Locations

### C++ Source
- `Project\Source\` - Main C++ modules
- `Project\Plugins\*\Source\` - Plugin C++ code

### Lua Scripts (SilverPalace)
- `Project\Content\Script\` - All Lua scripts
- Common paths:
  - `Global/GlobalSystem/` - Core systems
  - `Module/MainModule_*/` - Main modules
  - `Module/CommonSubModule/` - Common submodules

### Asset References
- `.uasset` - Unreal assets (search in blueprints, materials)
- `.umap` - Map files

## Common Searches

### Find Function Definition
```powershell
Select-String -Path "*.cpp" -Pattern "FunctionName"
Select-String -Path "*.lua" -Pattern "function.*FunctionName"
```

### Find Class Usage
```powershell
Select-String -Path "*.lua" -Pattern "ASomeClass"
Select-String -Path "*.cpp" -Pattern "SomeClass::"
```

### Find UI Widgets
```powershell
Select-String -Path "*.lua" -Pattern "c_UMG_"
Select-String -Path "*.lua" -Pattern "UMG_"
```

### Find Net Messages
```powershell
Select-String -Path "*.lua" -Pattern "SendPak"
Select-String -Path "*.lua" -Pattern "NetWork:Send"
```

## SilverPalace Specific

### Key Modules
- `MainModule_BigWorld` - Main game module
- `MainModule_VersionUpdate` - Version/update module
- `MainModule_Login` - Login module
- `NetWorkManager` - Network management
- `ModuleManager` - Module switching

### Key Lua Files
- `g_ModuleManager.lua` - Module management
- `g_NetWorkManager.lua` - Network manager
- `g_UIManager.lua` - UI management
- `MainLevelSwitcher.lua` - Level/screen switching

## Output Format

Provide:
- File paths with matches
- Line numbers
- Code context (2-3 lines)
- File purpose summary
