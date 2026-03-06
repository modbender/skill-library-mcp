# GDScript QC Profile

Quality control profile for Godot 4.x projects using GDScript.

## Project Detection

Godot project if any of these exist:
- `project.godot` (Godot project file)
- `*.tscn` files (scene files)
- `*.gd` files (GDScript files)

## Tool Setup

### gdlint / gdformat (gdtoolkit)

Install via pip:
```bash
pip install gdtoolkit
```

Verify installation:
```bash
gdlint --version
gdformat --version
```

### GUT (Godot Unit Testing)

Check for GUT addon:
```bash
# GUT is present if this directory exists
ls addons/gut/
```

## Phase 1: Test Suite

### With GUT

If `addons/gut/` exists, run tests via command line:

```bash
# Method 1: Using Godot headless
godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit

# Method 2: Using gut_cmdln.gd directly (Godot 4)
godot --headless --script addons/gut/gut_cmdln.gd \
  -gdir=res://test \
  -ginclude_subdirs \
  -gexit_on_success \
  -glog=2
```

**GUT output parsing:**
- Look for `Passed: X` and `Failed: Y` in output
- Exit code 0 = all passed
- Exit code 1 = failures

### Without GUT

If no test framework:
- Check if `test/` or `tests/` directory exists with `.gd` files
- If yes, mark as "Tests exist but no framework detected"
- If no, mark as **SKIP** (not FAIL)

## Phase 2: Scene/Resource Integrity

GDScript equivalent of import checking. Verify all references are valid.

### Preload/Load Validation

Find all `preload()` and `load()` calls:

```bash
grep -rn "preload\|load(" --include="*.gd" .
```

For each path found, verify the file exists:
```python
import re
import os

def check_gdscript_loads(project_root: str) -> dict:
    """Check all preload/load references are valid."""
    results = {"total": 0, "valid": 0, "broken": []}
    
    for root, dirs, files in os.walk(project_root):
        for f in files:
            if not f.endswith(".gd"):
                continue
            filepath = os.path.join(root, f)
            with open(filepath) as gd:
                for lineno, line in enumerate(gd, 1):
                    # Match preload("res://...") or load("res://...")
                    for match in re.finditer(r'(?:preload|load)\s*\(\s*["\']([^"\']+)["\']', line):
                        res_path = match.group(1)
                        results["total"] += 1
                        
                        if res_path.startswith("res://"):
                            actual_path = os.path.join(
                                project_root, 
                                res_path.replace("res://", "")
                            )
                            if os.path.exists(actual_path):
                                results["valid"] += 1
                            else:
                                results["broken"].append({
                                    "file": filepath,
                                    "line": lineno,
                                    "path": res_path
                                })
    return results
```

### Scene Reference Validation

Parse `.tscn` files for external resource references:

```bash
grep -h "ext_resource" *.tscn | grep "path="
```

Verify each referenced path exists.

### Script Attachment Validation

For each scene, verify attached scripts exist:

```python
def check_scene_scripts(tscn_path: str, project_root: str) -> list:
    """Check all script references in a scene file."""
    broken = []
    with open(tscn_path) as f:
        content = f.read()
    
    # Find script paths
    for match in re.finditer(r'script\s*=\s*ExtResource\s*\(\s*"([^"]+)"\s*\)', content):
        # Need to resolve ExtResource ID to actual path
        pass
    
    # Direct script path references
    for match in re.finditer(r'path="(res://[^"]+\.gd)"', content):
        script_path = match.group(1).replace("res://", "")
        if not os.path.exists(os.path.join(project_root, script_path)):
            broken.append(script_path)
    
    return broken
```

## Phase 3: Static Analysis (gdlint)

### Standard Check

```bash
gdlint . --exclude addons/
```

### Key Rules

| Rule | What it catches |
|------|-----------------|
| `function-name` | Non-snake_case function names |
| `class-name` | Non-PascalCase class names |
| `unused-argument` | Unused function arguments |
| `private-method-call` | Calling _private methods externally |
| `max-line-length` | Lines > 100 chars (configurable) |

### Configuration (.gdlintrc)

Create if not exists:
```ini
[gdlint]
max-line-length=120
excluded-directories=addons,build
```

### Fix Mode (gdformat)

```bash
# Check formatting issues
gdformat --check .

# Auto-fix formatting
gdformat .
```

## Phase 3.5: Type Checking

Godot 4 supports static typing but has no standalone type checker.

**Manual verification:**
1. Look for typed function signatures: `func foo(x: int) -> String:`
2. Check for `@warning_ignore` annotations (potential type issues)
3. Note untyped variables in critical code paths

**Heuristic for type coverage:**
```python
def estimate_type_coverage(gd_file: str) -> float:
    """Estimate percentage of typed declarations."""
    with open(gd_file) as f:
        content = f.read()
    
    # Count function definitions
    funcs = re.findall(r'func\s+\w+\s*\(', content)
    typed_funcs = re.findall(r'func\s+\w+\s*\([^)]*:\s*\w+', content)
    
    # Count variable declarations
    vars = re.findall(r'var\s+\w+', content)
    typed_vars = re.findall(r'var\s+\w+\s*:\s*\w+', content)
    
    total = len(funcs) + len(vars)
    typed = len(typed_funcs) + len(typed_vars)
    
    return typed / total if total > 0 else 1.0
```

## Phase 4: Smoke Tests (Business Logic)

### Autoload/Singleton Testing

Find autoloads in `project.godot`:
```ini
[autoload]
GameManager="*res://scripts/game_manager.gd"
SaveSystem="*res://scripts/save_system.gd"
```

For each autoload, verify it can be instantiated:
```gdscript
# test/test_autoloads.gd
extends GutTest

func test_game_manager_exists():
    assert_not_null(GameManager)

func test_save_system_save_load():
    var data = {"score": 100}
    SaveSystem.save_data(data)
    var loaded = SaveSystem.load_data()
    assert_eq(loaded["score"], 100)
```

### Core Class Testing

Identify core classes (non-UI nodes):
- Classes in `scripts/`, `src/`, `core/`
- Classes inheriting from `Resource`, `RefCounted`, `Object`
- Classes NOT inheriting from UI nodes (`Control`, `Button`, etc.)

## Phase 5: UI/Scene Verification

### Scene Loading Test

Verify all scenes can be instantiated:
```gdscript
# test/test_scenes.gd
extends GutTest

var scenes = [
    "res://scenes/main_menu.tscn",
    "res://scenes/game.tscn",
    "res://scenes/settings.tscn"
]

func test_scenes_load():
    for scene_path in scenes:
        var scene = load(scene_path)
        assert_not_null(scene, "Failed to load: " + scene_path)
        var instance = scene.instantiate()
        assert_not_null(instance)
        instance.queue_free()
```

### UI Node Verification

For each UI scene, check:
- All signal connections are valid
- All NodePath references resolve
- No missing fonts/themes

## Phase 6: File Consistency

### GDScript Syntax Check

Godot validates syntax on load. For CI without Godot:
```bash
# Basic syntax check using gdtoolkit
gdparse *.gd
```

### Resource Format Validation

Check `.tscn` and `.tres` files are valid:
```bash
# These should be readable text files
file *.tscn *.tres | grep -v "ASCII text"
```

### Git State

Same as general profile:
```bash
git status --short
git diff --check
```

## Phase 7: Documentation

### Script Documentation

GDScript uses `##` for doc comments:
```gdscript
## Player character controller.
## Handles movement, jumping, and combat.
class_name Player
extends CharacterBody3D

## Current health points.
var health: int = 100

## Move the player in the given direction.
## [param direction]: Normalized movement vector.
## [param delta]: Frame delta time.
func move(direction: Vector3, delta: float) -> void:
    pass
```

Check for documentation:
```python
def check_gdscript_docs(gd_file: str) -> dict:
    """Check for documentation in GDScript file."""
    with open(gd_file) as f:
        lines = f.readlines()
    
    results = {"has_class_doc": False, "undocumented_funcs": []}
    
    # Check for class documentation (## at top before class_name)
    for i, line in enumerate(lines):
        if line.strip().startswith("##"):
            results["has_class_doc"] = True
            break
        if line.strip().startswith("class_name") or line.strip().startswith("extends"):
            break
    
    # Check function documentation
    for i, line in enumerate(lines):
        if re.match(r'\s*func\s+\w+', line):
            func_name = re.search(r'func\s+(\w+)', line).group(1)
            # Check if previous non-empty line is a doc comment
            for j in range(i-1, -1, -1):
                prev = lines[j].strip()
                if prev.startswith("##"):
                    break
                if prev:  # Non-empty, non-doc line
                    if not func_name.startswith("_"):  # Skip private
                        results["undocumented_funcs"].append(func_name)
                    break
    
    return results
```

## Common Issues Checklist

- [ ] Missing `class_name` for reusable classes
- [ ] Hardcoded paths instead of exports
- [ ] Using `get_node()` with magic strings vs `@onready` + NodePath
- [ ] Missing `@tool` annotation for editor scripts
- [ ] Signals not documented
- [ ] Large scripts (>500 lines) that should be split
- [ ] Using `await get_tree().process_frame` instead of proper signals
