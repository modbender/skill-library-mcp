
import websocket
import uuid
import json
import os
import urllib.request
import urllib.parse
import sys
import time

# ── Configuration (can be overridden via environment variables or config.json) ──

def _load_config():
    """Load configuration from config.json in script directory or environment variables."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    config = {}

    # Default values
    defaults = {
        "comfy_host": "127.0.0.1:8188",
        "workflow_dirs": [],  # Will be computed relative to script location
    }

    # Load from config.json if exists
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Override with environment variables
    if os.environ.get("COMFY_HOST"):
        config["comfy_host"] = os.environ["COMFY_HOST"]
    if os.environ.get("COMFY_WORKFLOW_DIRS"):
        config["workflow_dirs"] = os.environ["COMFY_WORKFLOW_DIRS"].split(os.pathsep)

    # Apply defaults
    config.setdefault("comfy_host", defaults["comfy_host"])

    # Default workflow dirs relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    if not config.get("workflow_dirs"):
        config["workflow_dirs"] = [
            os.path.join(skill_dir, "workflows"),
            skill_dir,
        ]

    return config

_config = _load_config()
COMFY_HOST = _config["comfy_host"]
WORKFLOW_DIRS = _config["workflow_dirs"]

# Connection types that are always wire connections, never widget values
_CONNECTION_TYPES = {
    "MODEL", "CLIP", "VAE", "LATENT", "IMAGE", "MASK", "CONDITIONING",
    "CONTROL_NET", "STYLE_MODEL", "CLIP_VISION", "CLIP_VISION_OUTPUT",
    "TAESD", "PIPE_LINE", "PIPE_LINE_SDXL", "GLIGEN", "UPSCALE_MODEL",
    "SAMPLER", "SIGMAS", "NOISE", "GUIDER", "AUDIO", "VIDEO",
    "IMAGEUPSCALE", "WEBCAM", "PHOTOMAKER",
}

# Pseudo-widget keys appended by ComfyUI frontend but NOT actual node inputs
_SKIP_WIDGET_KEYS = {"control_after_generate", "control_before_generate"}

# LiteGraph frontend injects a control widget after INT seed inputs even when
# the object_info spec doesn't declare control_after_generate.  Detect and skip.
_SEED_CONTROL_WORDS = {"fixed", "randomize", "increment", "decrement", "random"}


def load_workflow(filename):
    """Load a workflow JSON by name or path. Searches workflows/ subdirs automatically."""
    if os.path.isabs(filename) and os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    for base in WORKFLOW_DIRS:
        # Direct match
        p = os.path.join(base, filename)
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
        # Recursive search within base
        for root, dirs, files in os.walk(base):
            for fn in files:
                if fn == filename or fn == filename + ".json":
                    with open(os.path.join(root, fn)) as f:
                        return json.load(f)
    raise FileNotFoundError(f"Workflow not found: {filename}")


def get_object_info(server_address):
    """Fetch node type definitions from ComfyUI (needed for LiteGraph conversion)."""
    url = f"http://{server_address}/object_info"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())


def _is_connection_only(inp_type):
    """Return True if this input type is a wire connection (not a widget)."""
    if not isinstance(inp_type, str):
        return False
    if inp_type == "*":
        return True
    if inp_type == "COMFY_DYNAMICCOMBO_V3":
        return False  # dynamic combo with sub-inputs; consumed from widgets_values
    return (inp_type.upper() == inp_type and len(inp_type) > 1
            and inp_type not in ("INT", "FLOAT", "STRING", "BOOLEAN", "COMBO"))


def _convert_nodes(nodes, raw_links, object_info, node_id_prefix="",
                   sg_input_map=None, sg_defs=None, sg_output_types=None):
    """Convert a list of LiteGraph nodes + links to API format entries.

    node_id_prefix: string prefix for all generated node IDs (for subgraph expansion)
    sg_input_map: {slot_index: [outer_src_node_id_str, outer_slot]} for subgraph inputs
    sg_defs: {uuid_str: subgraph_def} for resolving nested subgraph instances
    sg_output_types: list of {name, type} dicts from subgraph definition outputs
    Returns:
        api_entries: {prefixed_node_id_str: {class_type, inputs}}
        sg_output_map: {output_slot_int: [prefixed_src_node_id_str, src_slot]}
    """
    if sg_input_map is None:
        sg_input_map = {}
    if sg_defs is None:
        sg_defs = {}

    # Build link lookup for this graph level
    links = {}
    for lnk in raw_links:
        if isinstance(lnk, dict):
            links[lnk["id"]] = [lnk["origin_id"], lnk["origin_slot"]]
        elif isinstance(lnk, (list, tuple)):
            links[lnk[0]] = [lnk[1], lnk[2]]

    # Build target link lookup: (target_id, target_slot) -> (src_id, src_slot)
    # For -20 (output) targets, use declared output types to resolve conflicts
    # when multiple links map to the same output slot.
    _declared_out_types = {}
    if sg_output_types:
        for i, port in enumerate(sg_output_types):
            if isinstance(port, dict):
                _declared_out_types[i] = port.get("type", "*")

    target_links = {}
    for lnk in raw_links:
        if isinstance(lnk, dict):
            key = (lnk["target_id"], lnk["target_slot"])
            val = (lnk["origin_id"], lnk["origin_slot"])
            if key[0] == -20 and key in target_links and key[1] in _declared_out_types:
                expected = _declared_out_types[key[1]]
                if lnk.get("type", "") != expected and lnk.get("type", "") != "*":
                    continue  # skip: type mismatch for already-mapped output slot
            target_links[key] = val
        elif isinstance(lnk, (list, tuple)):
            key = (lnk[3], lnk[4])
            val = (lnk[1], lnk[2])
            if key[0] == -20 and key in target_links and key[1] in _declared_out_types:
                expected = _declared_out_types[key[1]]
                link_type = lnk[5] if len(lnk) > 5 else ""
                if link_type != expected and link_type != "*":
                    continue
            target_links[key] = val

    # Identify nested subgraph instances at this graph level
    nested_sg = {}
    for node in nodes:
        ntype = node.get("type", "")
        if ntype in sg_defs and node.get("mode", 0) != 4:
            nested_sg[node["id"]] = sg_defs[ntype]

    # Expand nested subgraph instances (topologically sorted so dependencies resolve first)
    nested_outputs = {}  # (node_id, output_slot) -> [prefixed_src_id, slot]
    api_entries = {}

    # Build dependency graph among nested subgraphs and sort topologically
    nested_deps = {nid: set() for nid in nested_sg}
    for nid in nested_sg:
        for slot_idx in range(len(nested_sg[nid].get("inputs", []))):
            src = target_links.get((nid, slot_idx))
            if src and src[0] in nested_sg:
                nested_deps[nid].add(src[0])
    # Kahn's algorithm
    _in_deg = {nid: len(deps) for nid, deps in nested_deps.items()}
    _queue = [nid for nid, d in _in_deg.items() if d == 0]
    _sorted = []
    while _queue:
        n = _queue.pop(0)
        _sorted.append(n)
        for nid, deps in nested_deps.items():
            if n in deps:
                _in_deg[nid] -= 1
                if _in_deg[nid] == 0:
                    _queue.append(nid)
    # Append any remaining (cycles) to avoid losing them
    for nid in nested_sg:
        if nid not in _sorted:
            _sorted.append(nid)

    for nested_id in _sorted:
        nested_def = nested_sg[nested_id]
        nested_prefix = node_id_prefix + f"sg{nested_id}_"
        nested_input = {}
        for slot_idx in range(len(nested_def.get("inputs", []))):
            key = (nested_id, slot_idx)
            if key not in target_links:
                continue
            src_id, src_slot = target_links[key]
            if src_id == -10:
                # Comes from parent subgraph input
                if src_slot in sg_input_map:
                    nested_input[slot_idx] = sg_input_map[src_slot]
            elif src_id in nested_sg:
                ref = nested_outputs.get((src_id, src_slot))
                if ref:
                    nested_input[slot_idx] = ref
                else:
                    nested_input[slot_idx] = [node_id_prefix + str(src_id), src_slot]
            else:
                nested_input[slot_idx] = [node_id_prefix + str(src_id), src_slot]

        entries, out_map = _convert_nodes(
            nested_def.get("nodes", []), nested_def.get("links", []),
            object_info, node_id_prefix=nested_prefix,
            sg_input_map=nested_input, sg_defs=sg_defs,
            sg_output_types=nested_def.get("outputs"))
        api_entries.update(entries)
        for out_slot, ref in out_map.items():
            nested_outputs[(nested_id, out_slot)] = ref

    # Build subgraph output map (inner -20 targets), resolving nested sources
    sg_output_map = {}
    for (tgt_id, tgt_slot), (src_id, src_slot) in target_links.items():
        if tgt_id == -20:
            if src_id == -10:
                # Pass-through: subgraph input directly wired to output
                if src_slot in sg_input_map:
                    sg_output_map[tgt_slot] = sg_input_map[src_slot]
            elif src_id in nested_sg:
                ref = nested_outputs.get((src_id, src_slot))
                if ref:
                    sg_output_map[tgt_slot] = ref
                else:
                    sg_output_map[tgt_slot] = [node_id_prefix + str(src_id), src_slot]
            else:
                sg_output_map[tgt_slot] = [node_id_prefix + str(src_id), src_slot]

    ui_skip = {"Note", "MarkdownNote", "Reroute", "NoteNode", "PrimitiveStringMultiline",
               "Note (Multiline)"}

    for node in nodes:
        node_id = node["id"]
        node_type = node.get("type", "")

        if node_type in ui_skip:
            continue
        if node.get("mode", 0) == 4:  # BYPASS
            continue
        if node_id in nested_sg:
            continue  # already expanded above

        node_info = object_info.get(node_type)
        if node_info is None:
            continue

        prefixed_id = node_id_prefix + str(node_id)

        # Build linked inputs by name from this node's input array
        linked_by_name = {}
        for inp in node.get("inputs", []):
            link_id = inp.get("link")
            if link_id is None:
                continue
            if link_id not in links:
                continue
            src_id, src_slot = links[link_id]
            if src_id == -10:
                # Subgraph input port: map to outer connection
                if src_slot in sg_input_map:
                    linked_by_name[inp["name"]] = sg_input_map[src_slot]
            elif src_id in nested_sg:
                ref = nested_outputs.get((src_id, src_slot))
                if ref:
                    linked_by_name[inp["name"]] = ref
            else:
                linked_by_name[inp["name"]] = [node_id_prefix + str(src_id), src_slot]

        # Widget values — can be a list (sequential) or dict (keyed by name)
        raw_wv = node.get("widgets_values", [])
        wv_is_dict = isinstance(raw_wv, dict)
        widgets_values = raw_wv if wv_is_dict else list(raw_wv)
        widget_idx = [0]

        def consume(inp_name, wv=widgets_values, idx=widget_idx, _dict=wv_is_dict):
            if _dict:
                return wv.get(inp_name)
            if idx[0] < len(wv):
                val = wv[idx[0]]
                idx[0] += 1
                return val
            return None

        input_def = node_info.get("input", {})
        required = input_def.get("required", {})
        optional = input_def.get("optional", {})
        hidden = input_def.get("hidden", {})

        api_inputs = {}
        for section in [required, optional, hidden]:
            for inp_name, inp_spec in section.items():
                inp_type = (inp_spec[0] if isinstance(inp_spec, (list, tuple)) and inp_spec
                            else inp_spec)
                inp_opts = (inp_spec[1] if isinstance(inp_spec, (list, tuple)) and len(inp_spec) > 1
                            and isinstance(inp_spec[1], dict) else {})
                is_connection_only = _is_connection_only(inp_type)

                if is_connection_only:
                    if inp_name in linked_by_name:
                        api_inputs[inp_name] = linked_by_name[inp_name]
                else:
                    val = consume(inp_name)
                    # control_after_generate injects an extra hidden widget slot after seed
                    if not wv_is_dict and inp_opts.get("control_after_generate"):
                        consume(inp_name)  # skip the injected 'randomize'/'fixed'/etc. slot
                    elif (not wv_is_dict and inp_type == "INT"
                          and widget_idx[0] < len(widgets_values)
                          and isinstance(widgets_values[widget_idx[0]], str)
                          and widgets_values[widget_idx[0]].lower() in _SEED_CONTROL_WORDS):
                        consume(inp_name)  # heuristic: skip undeclared control widget
                    if inp_name in _SKIP_WIDGET_KEYS:
                        pass
                    elif inp_name in linked_by_name:
                        api_inputs[inp_name] = linked_by_name[inp_name]
                    elif val is not None:
                        api_inputs[inp_name] = val

                    # Handle format-specific dynamic sub-inputs (e.g. VHS_VideoCombine)
                    fmt_meta = inp_opts.get("formats")
                    if fmt_meta and val in fmt_meta:
                        for extra_def in fmt_meta[val]:
                            extra_name = extra_def[0]
                            extra_val = consume(extra_name)
                            if extra_val is not None:
                                api_inputs[extra_name] = extra_val

                    # Handle COMFY_DYNAMICCOMBO_V3 sub-inputs
                    if inp_type == "COMFY_DYNAMICCOMBO_V3":
                        dyn_options = inp_opts.get("options")
                        if dyn_options and val is not None:
                            for opt in dyn_options:
                                if isinstance(opt, dict) and opt.get("key") == val:
                                    for sub_sec in (opt.get("inputs", {}).get("required", {}),
                                                    opt.get("inputs", {}).get("optional", {})):
                                        for sub_name, sub_spec in sub_sec.items():
                                            sub_val = consume(sub_name)
                                            if sub_val is not None:
                                                api_inputs[f"{inp_name}.{sub_name}"] = sub_val
                                    break

        # Include any dynamic linked inputs not covered by the object_info spec
        # (e.g. "Any Switch (rgthree)" has zero declared inputs but dynamic connections)
        for dyn_name, dyn_ref in linked_by_name.items():
            if dyn_name not in api_inputs:
                api_inputs[dyn_name] = dyn_ref

        api_entries[prefixed_id] = {"class_type": node_type, "inputs": api_inputs}

    # Post-fix: resolve references to nested subgraph instance IDs.
    # After expansion, sg146_226 (a nested instance ID) should resolve to
    # whatever inner node produces that output via nested_outputs.
    if nested_sg:
        nested_prefixed = {node_id_prefix + str(nid): nid for nid in nested_sg}
        for nid, node in api_entries.items():
            for inp_name, val in list(node.get("inputs", {}).items()):
                if isinstance(val, list) and len(val) == 2 and isinstance(val[0], str):
                    raw_id = nested_prefixed.get(val[0])
                    if raw_id is not None:
                        ref = nested_outputs.get((raw_id, val[1]))
                        if ref:
                            node["inputs"][inp_name] = ref

    return api_entries, sg_output_map


def litegraph_to_api(workflow, object_info=None, server_address=None):
    """Convert a LiteGraph GUI workflow JSON to ComfyUI API prompt format.

    Handles subgraphs (ComfyUI v1.38+ embedded workflows with UUID node types).
    LiteGraph format: has 'nodes', 'links', 'definitions' keys.
    API format: flat dict {node_id_str: {class_type, inputs}}.

    If already API format, returns unchanged.
    """
    if isinstance(workflow, dict) and "nodes" not in workflow:
        vals = list(workflow.values())
        if vals and isinstance(vals[0], dict) and "class_type" in vals[0]:
            return workflow  # already API format

    if "nodes" not in workflow:
        return workflow

    if object_info is None:
        if server_address is None:
            server_address = COMFY_HOST
        object_info = get_object_info(server_address)

    # Build subgraph definitions lookup: uuid -> subgraph_def
    sg_defs = {}
    for sg in workflow.get("definitions", {}).get("subgraphs", []):
        sg_defs[sg["id"]] = sg

    # Outer-level link lookup (list-of-lists format)
    outer_raw_links = workflow.get("links", [])
    outer_links = {}  # link_id -> [src_node_id, src_slot]
    for lnk in outer_raw_links:
        if isinstance(lnk, (list, tuple)):
            outer_links[lnk[0]] = [lnk[1], lnk[2]]

    # For each outer subgraph instance, compute what outer node provides each input slot
    # outer_links: target_node -> slot -> [src_node, src_slot]
    outer_targets = {}  # {(tgt_node_id, tgt_slot): [src_node, src_slot]}
    for lnk in outer_raw_links:
        if isinstance(lnk, (list, tuple)):
            outer_targets[(lnk[3], lnk[4])] = [str(lnk[1]), lnk[2]]

    # For subgraph instance outputs: {(sg_instance_id, output_slot): inner_resolved_ref}
    sg_instance_outputs = {}  # filled during expansion

    # Two-pass: first expand all subgraphs to get their output maps,
    # then process outer nodes

    # Collect all outer nodes that are subgraph instances
    sg_instances = {}  # node_id -> sg_def
    for node in workflow["nodes"]:
        node_type = node.get("type", "")
        if node_type in sg_defs:
            sg_instances[node["id"]] = sg_defs[node_type]

    # Expand each subgraph instance (topologically sorted so chained pass-throughs resolve)
    all_api = {}

    # Build dependency graph among outer subgraph instances
    _sg_deps = {sid: set() for sid in sg_instances}
    for sid in sg_instances:
        sg_def = sg_instances[sid]
        for slot_idx in range(len(sg_def.get("inputs", []))):
            src = outer_targets.get((sid, slot_idx))
            if src:
                src_id = int(src[0]) if src[0].isdigit() else None
                if src_id and src_id in sg_instances:
                    _sg_deps[sid].add(src_id)
    # Kahn's algorithm
    _in_deg = {sid: len(deps) for sid, deps in _sg_deps.items()}
    _queue = [sid for sid, d in _in_deg.items() if d == 0]
    _sg_sorted = []
    while _queue:
        n = _queue.pop(0)
        _sg_sorted.append(n)
        for sid, deps in _sg_deps.items():
            if n in deps:
                _in_deg[sid] -= 1
                if _in_deg[sid] == 0:
                    _queue.append(sid)
    for sid in sg_instances:
        if sid not in _sg_sorted:
            _sg_sorted.append(sid)

    for sg_node_id in _sg_sorted:
        sg_def = sg_instances[sg_node_id]
        prefix = f"sg{sg_node_id}_"
        # Build sg_input_map: slot_index -> outer_src_ref
        sg_input_map = {}
        for slot_idx, sg_port in enumerate(sg_def.get("inputs", [])):
            outer_key = (sg_node_id, slot_idx)
            if outer_key in outer_targets:
                ref = list(outer_targets[outer_key])
                # Resolve through already-expanded subgraph instances
                src_id_str = ref[0]
                if src_id_str.isdigit():
                    src_id_int = int(src_id_str)
                    if src_id_int in sg_instances:
                        resolved = sg_instance_outputs.get((src_id_int, ref[1]))
                        if resolved:
                            ref = resolved
                sg_input_map[slot_idx] = ref

        inner_nodes = sg_def.get("nodes", [])
        inner_links = sg_def.get("links", [])
        entries, output_map = _convert_nodes(inner_nodes, inner_links, object_info,
                                              node_id_prefix=prefix,
                                              sg_input_map=sg_input_map,
                                              sg_defs=sg_defs,
                                              sg_output_types=sg_def.get("outputs"))
        all_api.update(entries)
        # Store output map for outer nodes that connect from this subgraph
        for out_slot, ref in output_map.items():
            sg_instance_outputs[(sg_node_id, out_slot)] = ref

    # Process outer nodes (non-subgraph)
    outer_nodes = [n for n in workflow["nodes"] if n["id"] not in sg_instances]

    # Build outer linked_by_name, handling subgraph outputs
    def resolve_outer_input(link_id):
        if link_id not in outer_links:
            return None
        src_node, src_slot = outer_links[link_id]
        if src_node in sg_instances:
            # Source is a subgraph instance output
            return sg_instance_outputs.get((src_node, src_slot))
        return [str(src_node), src_slot]

    ui_skip = {"Note", "MarkdownNote", "Reroute", "NoteNode", "PrimitiveStringMultiline",
               "Note (Multiline)"}
    for node in outer_nodes:
        node_type = node.get("type", "")
        if node_type in ui_skip:
            continue
        if node.get("mode", 0) == 4:
            continue

        node_info = object_info.get(node_type)
        if node_info is None:
            continue

        node_id_str = str(node["id"])

        linked_by_name = {}
        for inp in node.get("inputs", []):
            link_id = inp.get("link")
            if link_id is None:
                continue
            ref = resolve_outer_input(link_id)
            if ref is not None:
                linked_by_name[inp["name"]] = ref

        widgets_values = node.get("widgets_values", [])
        wv_is_dict = isinstance(widgets_values, dict)
        if not wv_is_dict:
            widgets_values = list(widgets_values)
        widget_idx = [0]

        def consume(inp_name, wv=widgets_values, idx=widget_idx, _dict=wv_is_dict):
            if _dict:
                return wv.get(inp_name)
            if idx[0] < len(wv):
                val = wv[idx[0]]
                idx[0] += 1
                return val
            return None

        input_def = node_info.get("input", {})
        api_inputs = {}
        for section in [input_def.get("required", {}), input_def.get("optional", {}),
                        input_def.get("hidden", {})]:
            for inp_name, inp_spec in section.items():
                inp_type = (inp_spec[0] if isinstance(inp_spec, (list, tuple)) and inp_spec
                            else inp_spec)
                inp_opts = (inp_spec[1] if isinstance(inp_spec, (list, tuple)) and len(inp_spec) > 1
                            and isinstance(inp_spec[1], dict) else {})
                is_connection_only = _is_connection_only(inp_type)

                if is_connection_only:
                    # Never stored in widgets_values; use linked value if present
                    if inp_name in linked_by_name:
                        api_inputs[inp_name] = linked_by_name[inp_name]
                else:
                    val = consume(inp_name)
                    # control_after_generate injects an extra hidden widget slot after seed
                    if not wv_is_dict and inp_opts.get("control_after_generate"):
                        consume(inp_name)  # skip the injected 'randomize'/'fixed'/etc. slot
                    elif (not wv_is_dict and inp_type == "INT"
                          and widget_idx[0] < len(widgets_values)
                          and isinstance(widgets_values[widget_idx[0]], str)
                          and widgets_values[widget_idx[0]].lower() in _SEED_CONTROL_WORDS):
                        consume(inp_name)  # heuristic: skip undeclared control widget
                    if inp_name in _SKIP_WIDGET_KEYS:
                        pass  # consume the slot but don't add to api_inputs
                    elif inp_name in linked_by_name:
                        api_inputs[inp_name] = linked_by_name[inp_name]
                        # (val from widgets_values is the cached fallback, ignored)
                    elif val is not None:
                        api_inputs[inp_name] = val

                    # Handle format-specific dynamic sub-inputs (e.g. VHS_VideoCombine)
                    fmt_meta = inp_opts.get("formats")
                    if fmt_meta and val in fmt_meta:
                        for extra_def in fmt_meta[val]:
                            extra_name = extra_def[0]
                            extra_val = consume(extra_name)
                            if extra_val is not None:
                                api_inputs[extra_name] = extra_val

                    # Handle COMFY_DYNAMICCOMBO_V3 sub-inputs
                    if inp_type == "COMFY_DYNAMICCOMBO_V3":
                        dyn_options = inp_opts.get("options")
                        if dyn_options and val is not None:
                            for opt in dyn_options:
                                if isinstance(opt, dict) and opt.get("key") == val:
                                    for sub_sec in (opt.get("inputs", {}).get("required", {}),
                                                    opt.get("inputs", {}).get("optional", {})):
                                        for sub_name, sub_spec in sub_sec.items():
                                            sub_val = consume(sub_name)
                                            if sub_val is not None:
                                                api_inputs[f"{inp_name}.{sub_name}"] = sub_val
                                    break

        # Include any dynamic linked inputs not covered by the object_info spec
        for dyn_name, dyn_ref in linked_by_name.items():
            if dyn_name not in api_inputs:
                api_inputs[dyn_name] = dyn_ref

        all_api[node_id_str] = {"class_type": node_type, "inputs": api_inputs}

    # Post-fix: resolve any dangling references to subgraph instance IDs.
    # When subgraph B's inner nodes reference subgraph A (another instance),
    # the raw ID "A" appears in the API prompt but A was expanded into sg_A_*
    # entries. Replace with the resolved inner source from sg_instance_outputs.
    sg_ids_str = {str(sid) for sid in sg_instances}
    for nid, node in all_api.items():
        for inp_name, val in list(node.get("inputs", {}).items()):
            if isinstance(val, list) and len(val) == 2 and isinstance(val[0], str):
                ref_str = val[0]
                if ref_str in sg_ids_str:
                    raw_id = int(ref_str)
                    resolved = sg_instance_outputs.get((raw_id, val[1]))
                    if resolved:
                        node["inputs"][inp_name] = resolved

    return all_api


def upload_image(server_address, image_path, name=None):
    """Upload an image to ComfyUI and return the filename registered on the server.

    Args:
        server_address: e.g. "127.0.0.1:8188"
        image_path: local file path to upload
        name: optional override for the filename stored on the server
    Returns:
        str: the filename as registered on the server (use this in LoadImage nodes)
    """
    import mimetypes
    if name is None:
        name = os.path.basename(image_path)
    url = f"http://{server_address}/upload/image"
    boundary = uuid.uuid4().hex
    with open(image_path, "rb") as f:
        file_data = f.read()
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}\r\n".encode() + (
        f'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
        f"--{boundary}--\r\n"
    ).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("name", name)


def find_nodes_by_type(api_prompt, *class_types):
    """Return {node_id: node_dict} for all nodes matching one of the given class_types."""
    return {k: v for k, v in api_prompt.items() if v.get("class_type") in class_types}


def set_text_prompt(api_prompt, text, node_types=None):
    """Set the text/prompt on all text-encoder nodes in the API prompt.

    Handles: CLIPTextEncode, TextEncodeQwenImageEditPlus, WanTextEncode,
             HunyuanDiTTextEncode, LTXVConditioning, and common text nodes.

    Returns the modified api_prompt.
    """
    if node_types is None:
        node_types = {
            "CLIPTextEncode", "TextEncodeQwenImageEditPlus", "TextEncodeQwenImage",
            "WanTextEncode", "HunyuanVideoTextEncode", "LTXVConditioning",
            "HunyuanDiTTextEncode", "PixArtTextEncode", "SDXLPromptStyler",
            "Text Multiline", "ShowText|pysssss",
        }
    for node_id, node in api_prompt.items():
        if node.get("class_type") in node_types:
            inputs = node.get("inputs", {})
            for field in ("text", "prompt", "positive", "caption"):
                if field in inputs and isinstance(inputs[field], str):
                    inputs[field] = text
                    break
    return api_prompt


def queue_prompt(server_address, prompt, client_id, token=None):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    url = f"http://{server_address}/prompt"
    if token:
        url += f"?token={token}"
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            # Return error dict so caller's `if "error" in res` check handles it
            return json.loads(body)
        except Exception:
            raise RuntimeError(f"HTTP {e.code} from ComfyUI /prompt: {body[:500]}")


def get_history(server_address, prompt_id, token=None):
    url = f"http://{server_address}/history/{prompt_id}"
    if token:
        url += f"?token={token}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def download_file(server_address, filename, subfolder, folder_type, token=None):
    """Download a generated file (image, video, or audio) from the ComfyUI server."""
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url = f"http://{server_address}/view?{urllib.parse.urlencode(data)}"
    if token:
        url += f"&token={token}"
    with urllib.request.urlopen(url) as response:
        return response.read()


def run_workflow(server_address, token_or_none, workflow, output_prefix="output",
                 output_dir=None, object_info=None):
    """Submit a workflow (LiteGraph or API format) and download all outputs.

    Args:
        server_address: e.g. "127.0.0.1:8188"
        token_or_none: auth token string, or None if no auth (portable ComfyUI)
        workflow: dict in LiteGraph format OR API format
        output_prefix: prefix for saved output filenames
        output_dir: directory to save outputs (default: current directory)
        object_info: pre-fetched object_info dict (optional, fetched if None)
    Returns:
        list of saved file paths
    """
    token = token_or_none  # may be None

    # Convert LiteGraph → API format if needed
    api_prompt = litegraph_to_api(workflow, object_info=object_info, server_address=server_address)

    client_id = str(uuid.uuid4())
    ws_url = f"ws://{server_address}/ws?clientId={client_id}"
    if token:
        ws_url += f"&token={token}"
    ws = websocket.WebSocket()
    ws.connect(ws_url)

    res = queue_prompt(server_address, api_prompt, client_id, token=token)
    if "error" in res:
        ws.close()
        raise RuntimeError(f"ComfyUI rejected prompt: {res}")
    prompt_id = res["prompt_id"]

    # Wait for execution to finish
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break
            elif message["type"] == "execution_error":
                ws.close()
                raise RuntimeError(f"ComfyUI execution error: {message['data']}")
    ws.close()

    history = get_history(server_address, prompt_id, token=token)[prompt_id]
    saved_files = []

    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    output_keys = ["images", "gifs", "videos", "audio"]
    for node_id, node_output in history["outputs"].items():
        for key in output_keys:
            if key not in node_output:
                continue
            for item in node_output[key]:
                filename = item.get("filename", item.get("name", ""))
                if not filename:
                    continue
                subfolder = item.get("subfolder", "")
                folder_type = item.get("type", "output")
                file_data = download_file(server_address, filename, subfolder, folder_type, token=token)
                out_path = os.path.join(output_dir, f"{output_prefix}_{filename}")
                with open(out_path, "wb") as f:
                    f.write(file_data)
                saved_files.append(out_path)

    return saved_files


if __name__ == "__main__":
    # Usage: python comfy_api.py <workflow.json> [output_prefix] [server]
    if len(sys.argv) < 2:
        print("Usage: python comfy_api.py <workflow.json> [output_prefix] [server:port]")
        sys.exit(1)

    wf_path = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else "output"
    server = sys.argv[3] if len(sys.argv) > 3 else COMFY_HOST

    with open(wf_path) as f:
        wf = json.load(f)

    files = run_workflow(server, None, wf, output_prefix=prefix)
    print(f"Generated: {', '.join(files)}")
