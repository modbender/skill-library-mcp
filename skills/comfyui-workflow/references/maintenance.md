# Code Maintenance Guide

How to maintain, debug, and extend `comfy_run.py` and `comfy_api.py`.

---

## File Overview

| File | Lines | Purpose |
|------|-------|---------|
| `comfy_run.py` | ~1500 | CLI frontend: preprocessing, input application, WebSocket execution, output collection |
| `comfy_api.py` | ~550 | Core converter: LiteGraph→API format, subgraph expansion, upload, execution helpers |
| `comfy_control.sh` | ~60 | Bash script to start/stop/ensure ComfyUI server via PowerShell |

---

## comfy_run.py Structure

### Preprocessing Pipeline (runs before API conversion)

```
Raw workflow JSON
  → resolve_virtual_wires(wf)    # Expand getNode/setNode pairs into real links
  → strip_bypassed_nodes(wf)     # Remove mode=4 nodes, inline PrimitiveStringMultiline
  → [apply_extend_steps(wf, N)]  # Optional: enable N SVI extension chain blocks
  → litegraph_to_api(wf)         # Convert to API format (in comfy_api.py)
  → _resolve_date_patterns(api)  # Replace %date:...% tokens with real timestamps
  → apply_inputs(api)            # Set --prompt, --image, --seed, --override, etc.
```

**Critical**: `resolve_virtual_wires()` and `strip_bypassed_nodes()` return NEW copies. Always capture the return value: `wf = resolve_virtual_wires(wf)`.

### Key Functions

| Function | Purpose | Key Details |
|----------|---------|-------------|
| `resolve_virtual_wires(wf)` | Resolves SetNode/GetNode virtual wire pairs | Creates synthetic links for each matching title pair |
| `strip_bypassed_nodes(wf)` | Removes mode=4 (bypassed) nodes | Rewires links through bypassed nodes using TYPE matching. Also inlines PrimitiveStringMultiline widget values. |
| `_clean_inner_graph(nodes, links)` | Cleans subgraph definitions | Same bypass/rewire logic for nodes inside subgraph definitions |
| `apply_extend_steps(wf, n)` | Controls SVI-28 extension chain | Detects chain blocks by sequential subgraph instances, filters out dead subgraphs (all inner nodes bypassed), sets mode=0 (active) or mode=4 (bypass). Uses `_has_active_inner()` to check subgraph viability. |
| `_resolve_date_patterns(api)` | Replaces `%date:yyyy-MM-dd%` tokens | ComfyUI frontend resolves these; API doesn't, causing WinError 267 on Windows |
| `main()` | CLI entry point | Argparse, workflow loading, preprocessing, execution, output download |

### Node Type Constants

These lists define how input application works:

| Constant | Purpose |
|----------|---------|
| `TEXT_NODE_TYPES` | Nodes whose `text` input gets `--prompt` |
| `IMAGE_LOADER_TYPES` | Nodes that receive `--image` files (auto-uploaded) |
| `AUDIO_LOADER_TYPES` | Nodes that receive `--audio` files |
| `VIDEO_LOADER_TYPES` | Nodes that receive `--video` files |
| `LATENT_SIZE_TYPES` | Nodes whose width/height get `--width`/`--height` |
| `SAMPLER_TYPES` | Nodes that accept `--steps`, `--cfg`, `--seed`, etc. |
| `_NEG_KEYWORD_PATTERNS` | Patterns to detect negative prompt nodes |

### WebSocket Execution Flow

```
1. Connect to ws://COMFY_HOST/ws?clientId=...
2. POST /prompt with API JSON
3. Listen for messages:
   - "execution_start" → started
   - "executing" {node_id} → progress
   - "executed" {output images/videos} → collect output info
   - "execution_complete" → done
   - "execution_error" → fail
4. Download output files from /view?filename=...&type=output
```

---

## comfy_api.py Structure

### LiteGraph → API Conversion

The core conversion handles two levels:

1. **Outer level** (`litegraph_to_api`): Processes top-level nodes and links. Subgraph instances (UUID-type nodes) are expanded recursively.

2. **Inner level** (`_convert_nodes`): Processes nodes within a subgraph definition. Handles nested subgraphs recursively.

### Key Algorithms

#### Widget Value Consumption

LiteGraph stores widget values as a sequential array (`widgets_values`). The converter must consume them in the exact order that ComfyUI's object_info spec declares inputs:

```
For each input in object_info spec order:
  - If connection-only type → skip (no widget slot)
  - If widget type → consume next value from widgets_values
  - If control_after_generate in opts → consume extra slot
  - If INT and next value is a seed control word → consume extra slot
  - If COMFY_DYNAMICCOMBO_V3 → consume sub-inputs based on selected option
  - If format-specific (VHS formats) → consume sub-inputs for selected format
```

**Widget alignment is the #1 source of bugs.** If a value is consumed out of order, all subsequent values shift and everything breaks.

#### Subgraph Expansion

Subgraphs are embedded workflow definitions with UUID type IDs:

```
1. Detect UUID node type → look up in definitions.subgraphs
2. Map subgraph input slots → outer source connections
3. Recursively call _convert_nodes on inner nodes/links
4. Prefix all inner node IDs with "sg{outer_id}_"
5. Wire subgraph outputs back to outer graph references
6. Handle nested subgraphs (sg within sg) via recursive calls
```

#### Topological Sort

Both conversion functions use Kahn's algorithm to process nodes in dependency order. This ensures that when we resolve a node's inputs, all source nodes have already been processed.

#### Type-Matching Bypass Rewiring

When rewiring around bypassed nodes in `strip_bypassed_nodes`:

```
For each bypassed node:
  Find all outgoing links from this node
  For each outgoing link:
    Find an incoming link whose TYPE matches the outgoing link's type
    If found: redirect the outgoing link's source to the incoming link's source
```

This is safer than index-based matching because nodes can have multiple inputs/outputs of different types.

---

## Adding a New Workflow

1. Save the workflow JSON from ComfyUI into `~/comfyui/<Category>/`
2. Run `--inspect` to verify it loads and converts correctly
3. Run `--dry-run` to see the API prompt without executing
4. Test with real execution
5. Update SKILL.md decision tree and quick reference table if needed

### Common Issues with New Workflows

| Issue | Symptom | Fix |
|-------|---------|-----|
| New dynamic input type | `_is_connection_only` misclassifies | Add explicit check (like `COMFY_DYNAMICCOMBO_V3`) |
| New widget injection | Widget values shift | Add consumption rule in the widget loop |
| New node with `%date:...%` | WinError 267 on Windows | Already handled by `_resolve_date_patterns` |
| Nested subgraphs | Inner refs unresolved | Verify recursive expansion and post-fix resolution |

---

## Debugging Conversion Issues

### Step 1: Inspect the Original Workflow

```bash
$VENV $SCRIPT -w "workflow_name" --inspect
```

This shows all detected nodes, inputs, and settings without running.

### Step 2: Compare API Output

```bash
$VENV $SCRIPT -w "workflow_name" --prompt "test" --dry-run > /tmp/api.json
python3 -m json.tool /tmp/api.json
```

Look for:
- Missing nodes (filtered by bypass?)
- Wrong input values (widget alignment issue?)
- Missing connections (link not resolved?)

### Step 3: Validate on Server

```python
import json, urllib.request
api = json.load(open("/tmp/api.json"))
payload = json.dumps({"prompt": api}).encode()
req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                             data=payload, headers={"Content-Type": "application/json"})
try:
    resp = json.loads(urllib.request.urlopen(req).read())
    print("VALID:", resp.get("prompt_id", "")[:8])
except urllib.error.HTTPError as e:
    print(json.loads(e.read()))
```

### Step 4: Check Object Info

```python
import json, urllib.request
url = "http://127.0.0.1:8188/object_info/NodeTypeName"
info = json.loads(urllib.request.urlopen(url).read())
print(json.dumps(info, indent=2))
```

Compare the spec's input order and types with the workflow's `widgets_values` array.

---

## Historical Bug Patterns

These bugs have occurred before — watch for them:

| Bug | Root Cause | Fix Applied |
|-----|-----------|-------------|
| Widget misalignment | `control_after_generate` not consumed | Added explicit skip when `inp_opts.get("control_after_generate")` |
| Widget misalignment | Seed control words (fixed/randomize) not declared | Heuristic: skip string values in `_SEED_CONTROL_WORDS` after INT inputs |
| Connection misclassified | `COMFY_DYNAMICCOMBO_V3` treated as connection type | Added explicit `return False` in `_is_connection_only` |
| DynamicCombo sub-inputs | `resize_type.megapixels` not consumed | Added COMFY_DYNAMICCOMBO_V3 sub-input expansion with dotted naming |
| Bypass rewire by index | Wrong input connected when types differ | Changed to TYPE-MATCHING: match outgoing type to incoming type |
| Subgraph output conflict | Multiple outputs with same type | `sg_output_types` tracks per-slot types for correct resolution |
| PrimitiveStringMultiline | Text not inlined after bypass removal | Special handling: inline widget value into target node's input |
| SetNode/GetNode | Virtual wires not resolved | `resolve_virtual_wires` creates synthetic links |
| `%date:...%` patterns | Windows can't create dirs with `%` | `_resolve_date_patterns` expands to real timestamps |
| Dynamic inputs | "Any Switch" has no declared inputs | Fallback: include any linked inputs not in object_info |
| VHS format sub-inputs | Format-specific widgets not consumed | Check `inp_opts.get("formats")` and consume sub-inputs |
| `_is_connection_only("*")` | Single-char `"*"` mishandled | Explicit check: `if inp_type == "*": return True` |
| Dead subgraph in extension chain | `apply_extend_steps` enables a subgraph instance whose definition has ALL inner nodes at mode=4 (bypassed). The subgraph produces no outputs, causing downstream VHS_VideoCombine to have `images=MISSING` → server validation error "Required input is missing: images" | Added `_has_active_inner(node)` check that inspects the subgraph definition's inner nodes. Only subgraph instances with at least one non-bypassed inner node are included in the chain. |

---

## Debugging Case Studies

### Case: Dead Subgraph Extension Chain (SVI-28, Feb 2026)

**Symptom**: ComfyUI server log shows `Failed to validate prompt for output 448: Required input is missing: images` for `VHS_VideoCombine 448`, but our CLI reports SUCCESS with 5 outputs (the warning is server-side, non-fatal for unconnected outputs).

**Investigation Path**:

1. **Identify which workflow owns node 448** — Dry-ran SVI-28 with `--extend-steps 4 --dry-run` and grepped for `VHS_VideoCombine`. Found 6 VHS nodes in API; node 448 had `images=MISSING`.

2. **Trace the missing connection** — In the raw workflow JSON, VHS 448 has `inputs[name=images].link = 829`. Link 829 points to node 253 (a subgraph instance), output slot 2.

3. **Inspect the subgraph definition** — Node 253's type is a UUID that maps to a subgraph definition in `definitions.subgraphs`. Checked the definition's inner nodes:
   ```python
   sd = sg_defs[node_253["type"]]
   for n in sd["nodes"]:
       print(f'  {n["id"]}: mode={n.get("mode", 0)}')
   # ALL 10 inner nodes: mode=4 (bypassed)
   ```

4. **Understand the root cause** — `apply_extend_steps(wf, 4)` enabled chain step 3 (node 253) and its paired VHS 448. But node 253 is a "dead shell" — its subgraph definition has all 10 inner nodes at mode=4. When `_convert_nodes` processes it, `output_map` is empty (no nodes produce output). So `sg_instance_outputs[(253, 2)]` is never set, and the `images` input on VHS 448 resolves to nothing.

5. **Check ALL chain subgraphs** — Found the SVI-28 chain has 10 subgraph instances (185→186→243→253→263→273→283→293→303→313). Steps 0-2 (185, 186, 243) have all inner nodes active. Steps 3-9 (253-313) have ALL inner nodes bypassed. The extension chain exists in the workflow as a template, but the author disabled the extension subgraph definitions.

**Key Insight**: Subgraph definitions are shared templates. The inner node `mode` values are fixed in the definition, NOT modified by `apply_extend_steps`. So a subgraph instance whose definition has all-bypassed inner nodes can never produce output regardless of its outer mode.

**Debugging Technique — Subgraph Inner Node Analysis**:
```python
import json
with open('workflow.json') as f:
    wf = json.load(f)
sg_defs = {sg['id']: sg for sg in wf.get('definitions', {}).get('subgraphs', [])}
for n in wf['nodes']:
    if n.get('type') in sg_defs:
        sd = sg_defs[n['type']]
        inner = sd.get('nodes', [])
        active = sum(1 for x in inner if x.get('mode', 0) != 4)
        bypassed = len(inner) - active
        print(f'  Node {n["id"]} (type={n["type"][:8]}...): '
              f'{len(inner)} inner, {active} active, {bypassed} bypassed')
```

**Debugging Technique — Trace Link to Source**:
```python
# Given a node input with a link ID, trace it to the source node
link_by_id = {l[0]: l for l in wf['links']}
lid = 829  # the link ID from the input
link = link_by_id[lid]
# link = [link_id, src_node_id, src_slot, dst_node_id, dst_slot, type]
print(f'Link {lid}: node {link[1]} slot {link[2]} → node {link[3]} slot {link[4]} (type: {link[5]})')
```

**Debugging Technique — Validate All VHS Nodes in API**:
```python
from comfy_api import litegraph_to_api, get_object_info, COMFY_HOST
api = litegraph_to_api(wf, get_object_info(COMFY_HOST))
for nid, node in api.items():
    if node.get('class_type') == 'VHS_VideoCombine':
        has_images = 'images' in node.get('inputs', {})
        print(f'  VHS {nid}: images={"present" if has_images else "MISSING"}')
```

**Fix Applied**: `_has_active_inner(node)` in `apply_extend_steps()` checks the subgraph definition for at least one non-mode=4 inner node before including the instance in the chain.

**Post-fix Verification**: Ran all 27 workflows through the full preprocessing + conversion pipeline. SVI-28 with extend-steps 1-10 all produce valid API with no missing VHS images. Chain correctly reports "5 steps" (the 5 subgraph instances with live inner nodes) instead of the previous 10 (which included 5 dead shells).

---

## Regression Testing

Use this script to validate ALL workflows after code changes:

```python
import json, sys, os, traceback
sys.path.insert(0, '/path/to/scripts')
from comfy_run import apply_extend_steps, resolve_virtual_wires, strip_bypassed_nodes
from comfy_api import litegraph_to_api, get_object_info, COMFY_HOST

info = get_object_info(COMFY_HOST)
base = os.path.expanduser('~/comfyui')
passed = failed = 0

for root, _, files in os.walk(base):
    for f in sorted(files):
        if not f.endswith('.json'):
            continue
        path = os.path.join(root, f)
        try:
            with open(path) as fh:
                wf = json.load(fh)
            if 'nodes' not in wf:
                continue
            wf = resolve_virtual_wires(wf)
            wf = strip_bypassed_nodes(wf)
            if wf.get('definitions', {}).get('subgraphs'):
                wf = apply_extend_steps(wf, 3)
            api = litegraph_to_api(wf, info)
            # Check VHS nodes have images
            for nid, node in api.items():
                if node.get('class_type') == 'VHS_VideoCombine':
                    assert 'images' in node.get('inputs', {}), f'{f}: VHS {nid} missing images'
            passed += 1
            print(f'  OK   {f}: {len(api)} nodes')
        except Exception as e:
            failed += 1
            print(f'  FAIL {f}: {e}')

print(f'\n{passed} passed, {failed} failed')
```

Run after any change to preprocessing functions or `comfy_api.py`.
