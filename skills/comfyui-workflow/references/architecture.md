# Architecture & Design Philosophy

Design decisions and invariants in `comfy_run.py` and `comfy_api.py`.

---

## Core Design Principles

### 1. Preprocessing is Immutable

All preprocessing functions (`resolve_virtual_wires`, `strip_bypassed_nodes`) return **new copies** of the workflow. They never modify the input in-place.

**Why**: The raw workflow JSON may be reused (e.g., for inspection vs. execution). Immutability prevents subtle bugs where a preprocessing step corrupts the original data.

**Invariant**: `wf_original` is never changed after loading. Always: `wf = resolve_virtual_wires(wf_original)`.

### 2. Type-Matching Over Index-Matching

When rewiring links around bypassed nodes, we match by **output type** rather than slot index.

**Why**: A node might have `(IMAGE, MASK)` outputs and `(MODEL, IMAGE)` inputs. Index 0→0 would wire MODEL→IMAGE. Type matching finds the IMAGE→IMAGE pair correctly.

**Invariant**: Bypass rewiring always matches `link_type == incoming_link_type`.

### 3. Sequential Widget Consumption

Widget values are consumed strictly in object_info declaration order, one at a time. The converter maintains a single `widget_idx` counter that advances through `widgets_values`.

**Why**: LiteGraph serializes widgets in the same order as node inputs. Skipping or double-consuming a slot shifts all subsequent values, causing cascading errors. This is the most delicate part of the converter.

**Invariant**: After processing all inputs for a node, `widget_idx` should equal the number of widget slots (non-connection inputs + injected control slots).

### 4. Subgraph Expansion is Recursive

Subgraphs can contain other subgraph instances. The expansion works by:
1. Detecting UUID node types in the current graph
2. Looking up their definition in `definitions.subgraphs`
3. Calling `_convert_nodes` recursively with prefixed IDs
4. Wiring inputs/outputs back to the parent graph

**Why**: ComfyUI v1.38+ supports nesting. A flat, one-level approach would miss inner subgraphs.

**Invariant**: All expanded node IDs are globally unique via the prefix chain: `sg{outer_id}_sg{inner_id}_...{node_id}`.

### 5. Topological Processing Order

Both `_convert_nodes` and `litegraph_to_api` sort nodes topologically (Kahn's algorithm) before converting.

**Why**: A node's inputs may reference outputs from other nodes. Processing in topological order ensures all dependencies are resolved before they're needed. This is especially important for subgraph expansion where inner nodes may reference other expanded subgraphs.

### 6. Server-Side is Source of Truth

The converter fetches `object_info` from the running ComfyUI server rather than maintaining a static copy.

**Why**: Node types change across ComfyUI versions. Custom nodes add new types. The server always knows its current node inventory. A static list would go stale.

**Exception**: `_is_connection_only` has a hardcoded set of known connection types for performance. New connection types need to be added here, or they'll be misclassified as widgets.

---

## Two-Phase Architecture

### Phase 1: LiteGraph Preprocessing (comfy_run.py)

Operates on the **LiteGraph format** (nodes array + links array):

```
LiteGraph JSON
  ├── nodes: [{id, type, widgets_values, inputs, outputs, mode, ...}]
  ├── links: [[link_id, src_id, src_slot, dst_id, dst_slot, type], ...]
  └── definitions.subgraphs: [{id, nodes, links, inputs, outputs}, ...]
```

This phase handles:
- Virtual wire resolution (SetNode/GetNode)
- Node bypass removal and link rewiring  
- PrimitiveStringMultiline inlining
- Extension chain control (SVI-28)

### Phase 2: API Conversion (comfy_api.py)

Transforms LiteGraph into the **API prompt format**:

```python
{
  "node_id_str": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 42,
      "steps": 20,
      "model": ["other_node_id", 0],  # connection reference
      ...
    }
  }
}
```

Key differences from LiteGraph:
- Links are inline references `["src_id", slot]` instead of a separate links array
- Widget values are named instead of positional
- Subgraphs are flattened into the same namespace with prefixed IDs
- Bypassed/utility nodes are removed
- Only nodes reachable from output nodes are included

---

## Key Data Structures

### Connection Reference

A link in API format: `["source_node_id_str", output_slot_index]`

Example: `"model": ["37", 0]` means "use output slot 0 from node 37".

### Subgraph Input Map

`sg_input_map: {slot_index: [outer_src_node_id_str, outer_slot]}`

Maps each subgraph input slot to the outer node that provides it. Built by the parent before calling `_convert_nodes` on the inner graph.

### Subgraph Output Map

`sg_output_map: {slot_index: [inner_node_id_str, inner_slot]}`

Maps each subgraph output slot to the inner node that produces it. Returned after inner expansion so the parent can wire outputs correctly.

---

## Error Handling Philosophy

### Fail Fast on Conversion

If a node type isn't in object_info, it's skipped with no error. This handles utility nodes (MarkdownNote, Reroute) that don't need API representation.

### Fail Loud on Execution

If the server rejects a prompt, the full error with node IDs and messages is printed. If execution fails mid-run, the WebSocket error message is displayed.

### Graceful Degradation on Inputs

If `--prompt` targets a node that doesn't exist in the converted workflow, it's silently skipped. The workflow's built-in defaults serve as fallback.

---

## Why Not Use ComfyUI's Script API Directly?

ComfyUI does have a Python script API, but:

1. **We run from WSL2, ComfyUI runs on Windows** — no direct Python import possible
2. **The HTTP API is the stable interface** — script APIs change between versions
3. **LiteGraph format is what users save** — converting to API format is required anyway
4. **WebSocket provides real-time progress** — better UX than polling

---

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| `get_object_info()` | ~2s | Fetches all 2682 node type specs. Cached per session. |
| `resolve_virtual_wires()` | <10ms | Simple link injection |
| `strip_bypassed_nodes()` | <50ms | Link rewiring + cleanup |
| `litegraph_to_api()` | <100ms | Even for 200-node SVI-28 |
| `_resolve_date_patterns()` | <1ms | Regex replacement |
| Network round-trip to server | ~1ms | WSL2 → Windows localhost |
| Model loading (cold) | 10-60s | First use of a model; cached after |
| Inference | 15-360s | Depends on workflow complexity |

The bottleneck is always GPU inference, never conversion.
