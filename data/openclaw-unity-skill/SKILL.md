---
name: unity-plugin
version: 1.6.1
description: Control Unity Editor via OpenClaw Unity Plugin. Use for Unity game development tasks including scene management, GameObject/Component manipulation, debugging, input simulation, and Play mode control. Triggers on Unity-related requests like inspecting scenes, creating objects, taking screenshots, testing gameplay, or controlling the Editor.
homepage: https://github.com/TomLeeLive/openclaw-unity-skill
author: Tom Jaejoon Lee
disableModelInvocation: true
---

# Unity Plugin Skill

Control Unity Editor through **~100 built-in tools**. Works in both Editor and Play mode.

## Connection Modes

### 1. OpenClaw Gateway (Remote)
For Telegram, Discord, and other OpenClaw channels:
- Auto-connects when Unity opens
- Configure in: Window → OpenClaw Plugin → Settings

### 2. MCP Bridge (Local)
For Claude Code, Cursor, and local AI tools:
- Start: Window → OpenClaw Plugin → MCP Bridge → Start
- Default port: 27182
- Add to Claude Code: `claude mcp add unity -- node <path>/MCP~/index.js`

## First-Time Setup

If `unity_execute` tool is not available, install the gateway extension:

```bash
# From skill directory
./scripts/install-extension.sh

# Restart gateway
openclaw gateway restart
```

The extension files are in `extension/` directory.

### What install-extension.sh Does

```bash
# 1. Copies extension files from skill to gateway
#    Source: <skill>/extension/
#    Destination: ~/.openclaw/extensions/unity/

# 2. Files installed:
#    - index.ts     # Extension entry point (HTTP handlers, tools)
#    - package.json # Extension metadata

# After installation, restart gateway to load the extension.
```

## 🔐 Security

이 스킬은 `disableModelInvocation: true`로 설정되어 있습니다.
- AI가 자동으로 도구를 호출하지 않음
- 사용자가 명시적으로 요청한 작업만 실행

설정 변경 방법은 [README.md](README.md)를 참조하세요.

## Quick Reference

### Core Tools

| Category | Key Tools |
|----------|-----------|
| **Scene** | `scene.getActive`, `scene.getData`, `scene.load`, `scene.open`, `scene.save` |
| **GameObject** | `gameobject.find`, `gameobject.getAll`, `gameobject.create`, `gameobject.destroy` |
| **Component** | `component.get`, `component.set`, `component.add`, `component.remove` |
| **Transform** | `transform.setPosition`, `transform.setRotation`, `transform.setScale` |
| **Debug** | `debug.hierarchy`, `debug.screenshot`, `console.getLogs` |
| **Input** | `input.clickUI`, `input.type`, `input.keyPress`, `input.mouseClick` |
| **Editor** | `editor.getState`, `editor.play`, `editor.stop`, `editor.refresh` |
| **Material** | `material.create`, `material.assign`, `material.modify`, `material.getInfo` |
| **Prefab** | `prefab.create`, `prefab.instantiate`, `prefab.open`, `prefab.save` |
| **Asset** | `asset.find`, `asset.copy`, `asset.move`, `asset.delete` |
| **Package** | `package.add`, `package.remove`, `package.list`, `package.search` |
| **Test** | `test.run`, `test.list`, `test.getResults` |

## Common Workflows

### 1. Scene Inspection

```
unity_execute: debug.hierarchy {depth: 2}
unity_execute: scene.getActive
```

### 2. Find & Modify Objects

```
unity_execute: gameobject.find {name: "Player"}
unity_execute: component.get {name: "Player", componentType: "Transform"}
unity_execute: transform.setPosition {name: "Player", x: 0, y: 5, z: 0}
```

### 3. UI Testing

```
unity_execute: input.clickUI {name: "PlayButton"}
unity_execute: input.type {text: "TestUser", elementName: "UsernameInput"}
unity_execute: debug.screenshot
```

### 4. Play Mode Control

```
unity_execute: editor.play              # Enter Play mode
unity_execute: editor.stop              # Exit Play mode
unity_execute: editor.getState          # Check current state
unity_execute: editor.pause             # Pause
unity_execute: editor.unpause           # Resume
```

### 5. Material Creation

```
unity_execute: material.create {name: "RedMetal", color: "#FF0000", metallic: 0.8}
unity_execute: material.assign {gameObjectName: "Player", materialPath: "Assets/Materials/RedMetal.mat"}
unity_execute: material.modify {path: "Assets/Materials/RedMetal.mat", metallic: 1.0, emission: "#FF4444"}
```

### 6. Prefab Workflow

```
unity_execute: prefab.create {gameObjectName: "Player", path: "Assets/Prefabs/Player.prefab"}
unity_execute: prefab.instantiate {prefabPath: "Assets/Prefabs/Player.prefab", x: 0, y: 1, z: 0}
unity_execute: prefab.open {path: "Assets/Prefabs/Player.prefab"}
unity_execute: prefab.save
unity_execute: prefab.close
```

### 7. Asset Management

```
unity_execute: asset.find {query: "Player", type: "Prefab"}
unity_execute: asset.copy {sourcePath: "Assets/Prefabs/Player.prefab", destPath: "Assets/Backup/Player.prefab"}
unity_execute: asset.move {sourcePath: "Assets/Old/Item.prefab", destPath: "Assets/New/Item.prefab"}
```

### 8. Package Management

```
unity_execute: package.list
unity_execute: package.search {query: "TextMeshPro"}
unity_execute: package.add {packageName: "com.unity.textmeshpro"}
unity_execute: package.add {gitUrl: "https://github.com/example/package.git"}
```

### 9. Test Running

```
unity_execute: test.list {testMode: "EditMode"}
unity_execute: test.run {testMode: "EditMode", filter: "PlayerTests"}
unity_execute: test.getResults
```

### 10. Script Execution (Enhanced)

```
# Debug logging
unity_execute: script.execute {code: "Debug.Log('Hello')"}

# Time manipulation
unity_execute: script.execute {code: "Time.timeScale = 0.5"}

# PlayerPrefs
unity_execute: script.execute {code: "PlayerPrefs.SetInt('score', 100)"}

# Reflection-based method calls
unity_execute: script.execute {code: "MyClass.MyMethod()"}
unity_execute: script.execute {code: "MyClass.MyStaticMethod('param1', 123)"}
```

## Tool Categories (~100 tools)

### Console (3 tools)
- `console.getLogs` - Get logs with optional type filter (Log/Warning/Error)
- `console.getErrors` - Get error/exception logs (with optional warnings)
- `console.clear` - Clear captured logs

### Scene (7 tools)
- `scene.list` - List scenes in build settings
- `scene.getActive` - Get active scene info
- `scene.getData` - Get full hierarchy data
- `scene.load` - Load scene by name (Play mode)
- `scene.open` - Open scene in Editor mode
- `scene.save` - Save active scene (Editor mode)
- `scene.saveAll` - Save all open scenes (Editor mode)

### GameObject (8 tools)
- `gameobject.find` - Find by name, tag, or component
- `gameobject.getAll` - Get all GameObjects with filtering
- `gameobject.create` - Create object or primitive (Cube, Sphere, etc.)
- `gameobject.destroy` - Destroy object
- `gameobject.delete` - Delete object (alias for destroy)
- `gameobject.getData` - Get detailed data
- `gameobject.setActive` - Enable/disable
- `gameobject.setParent` - Change hierarchy

### Transform (6 tools)
- `transform.getPosition` - Get world position {x, y, z}
- `transform.getRotation` - Get Euler rotation {x, y, z}
- `transform.getScale` - Get local scale {x, y, z}
- `transform.setPosition` - Set world position {x, y, z}
- `transform.setRotation` - Set Euler rotation
- `transform.setScale` - Set local scale

### Component (5 tools)
- `component.add` - Add component by type name
- `component.remove` - Remove component
- `component.get` - Get component data/properties
- `component.set` - Set field/property value
- `component.list` - List available component types

### Script (3 tools)
- `script.execute` - Execute code: Debug.Log, Time, PlayerPrefs, **reflection calls**
- `script.read` - Read script file
- `script.list` - List project scripts

### Application (4 tools)
- `app.getState` - Get play mode, FPS, time
- `app.play` - Enter/exit Play mode
- `app.pause` - Toggle pause
- `app.stop` - Stop Play mode

### Debug (3 tools)
- `debug.log` - Write to console
- `debug.screenshot` - Capture screenshot
- `debug.hierarchy` - Text hierarchy view

### Editor (9 tools)
- `editor.refresh` - Refresh AssetDatabase (triggers recompile)
- `editor.recompile` - Request script recompilation
- `editor.domainReload` - Force domain reload
- `editor.focusWindow` - Focus window (game/scene/console/hierarchy/project/inspector)
- `editor.listWindows` - List open windows
- `editor.getState` - Get editor state
- `editor.play` - Enter Play mode
- `editor.stop` - Exit Play mode
- `editor.pause` / `editor.unpause` - Pause control

### Input Simulation (10 tools)
- `input.keyPress` - Press and release key
- `input.keyDown` / `input.keyUp` - Hold/release key
- `input.type` - Type text into field
- `input.mouseMove` - Move cursor
- `input.mouseClick` - Click at position
- `input.mouseDrag` - Drag operation
- `input.mouseScroll` - Scroll wheel
- `input.getMousePosition` - Get cursor position
- `input.clickUI` - Click UI element by name

### Material (5 tools) - NEW in v1.5.0
- `material.create` - Create material with shader, color, metallic, smoothness
- `material.assign` - Assign material to GameObject
- `material.modify` - Modify material properties (color, metallic, emission)
- `material.getInfo` - Get detailed material info with all shader properties
- `material.list` - List materials in project with filtering

### Prefab (5 tools) - NEW in v1.5.0
- `prefab.create` - Create prefab from scene GameObject
- `prefab.instantiate` - Instantiate prefab in scene with position
- `prefab.open` - Open prefab for editing
- `prefab.close` - Close prefab editing mode
- `prefab.save` - Save currently edited prefab

### Asset (7 tools) - NEW in v1.5.0
- `asset.find` - Search assets by query, type, folder
- `asset.copy` - Copy asset to new path
- `asset.move` - Move/rename asset
- `asset.delete` - Delete asset (with trash option)
- `asset.refresh` - Refresh AssetDatabase
- `asset.import` - Import/reimport specific asset
- `asset.getPath` - Get asset path by name

### Package Manager (4 tools) - NEW in v1.5.0
- `package.add` - Install package by name or git URL
- `package.remove` - Remove installed package
- `package.list` - List installed packages
- `package.search` - Search Unity package registry

### Test Runner (3 tools) - NEW in v1.5.0
- `test.run` - Run EditMode/PlayMode tests with filtering
- `test.list` - List available tests
- `test.getResults` - Get last test run results

### Batch Execution (1 tool) - NEW in v1.6.0
- `batch.execute` - Execute multiple tools in one call (10-100x performance)
  - `commands`: Array of {tool, params} objects
  - `stopOnError`: Stop on first error (default: false)

### Session (1 tool) - NEW in v1.6.0
- `session.getInfo` - Get session info (project, processId, machineName, sessionId)

### ScriptableObject (6 tools) - NEW in v1.6.0
- `scriptableobject.create` - Create new ScriptableObject asset
- `scriptableobject.load` - Load and inspect ScriptableObject fields
- `scriptableobject.save` - Save ScriptableObject changes
- `scriptableobject.getField` - Get specific field value
- `scriptableobject.setField` - Set field value with auto-save
- `scriptableobject.list` - List ScriptableObjects in project

### Shader (3 tools) - NEW in v1.6.0
- `shader.list` - List shaders in project
- `shader.getInfo` - Get shader properties and info
- `shader.getKeywords` - Get shader keywords

### Texture (5 tools) - NEW in v1.6.0
- `texture.create` - Create new texture with color fill
- `texture.getInfo` - Get texture info (size, format, import settings)
- `texture.setPixels` - Fill region with color
- `texture.resize` - Resize texture via import settings
- `texture.list` - List textures in project

## Custom Tools API - v1.6.0

Register project-specific tools:

```csharp
OpenClawCustomTools.Register(
    "mygame.getScore",
    "Get current score",
    (args) => new { success = true, score = GameManager.Score }
);
```

## MCP Resources - v1.6.0

Access Unity data via MCP resource URIs:

| URI | Description |
|-----|-------------|
| `unity://scene/hierarchy` | Scene hierarchy |
| `unity://scene/active` | Active scene info |
| `unity://project/scripts` | Script list |
| `unity://project/scenes` | Scene list |
| `unity://editor/state` | Editor state |
| `unity://console/logs` | Console logs |
| `unity://session/info` | Session info |

## Tips

### Screenshot Modes
- **Play mode**: `ScreenCapture` - includes all UI overlays
- **Editor mode**: `Camera.main.Render()` - no overlay UI
- Use `{method: "camera"}` for camera-only capture

### Finding Objects
```
gameobject.find {name: "Player"}           # By exact name
gameobject.find {tag: "Enemy"}             # By tag
gameobject.find {componentType: "Camera"}  # By component
gameobject.getAll {activeOnly: true}       # All active objects
```

### Script Recompilation
Unity may not auto-recompile after code changes. Use:
```
editor.refresh    # Full asset refresh + recompile
```

### Play Mode Transitions
- Plugin survives Play mode transitions via SessionState
- If connection lost, wait for auto-reconnect or use Window → OpenClaw Plugin → Settings → Connect

### MCP Bridge Usage
For Claude Code / Cursor integration:
1. Start: Window → OpenClaw Plugin → MCP Bridge → Start
2. Register: `claude mcp add unity -- node /path/to/MCP~/index.js`
3. Verify: `curl http://127.0.0.1:27182/status`

### Input Simulation Limitation
Keyboard/mouse simulation works for **UI interactions** but NOT for `Input.GetKey()`. For gameplay testing:
- Use `transform.setPosition` to move objects directly
- Or migrate to Unity's **new Input System**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool timeout | Check Unity is responding, try `editor.getState` |
| Gateway no connection | Check Window → OpenClaw Plugin → Settings |
| MCP no connection | Start MCP Bridge, verify port 27182 |
| Scripts not updating | Use `editor.refresh` to force recompile |
| Wrong screenshot | Use Play mode for game view with UI |
| MCP 504 timeout | Unity busy or MCP Bridge not started |
| Test Runner not found | Install `com.unity.test-framework` package |

## Links

- **Skill Repository:** https://github.com/TomLeeLive/openclaw-unity-skill
- **Plugin Repository:** https://github.com/TomLeeLive/openclaw-unity-plugin
- **OpenClaw Docs:** https://docs.openclaw.ai
- **MCP Setup Guide:** See Plugin Repository → Documentation~/SETUP_GUIDE.md

## License

MIT License - See LICENSE file
