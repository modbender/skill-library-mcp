#!/usr/bin/env python3
"""
comfy_run.py — Universal ComfyUI Workflow Executor

Executes ANY ComfyUI workflow with fully customizable inputs.
Auto-detects text prompts, images, audio, video, resolution, sampler settings.
Monitors execution for errors/warnings via WebSocket.

Usage:
  python comfy_run.py --list                              # List all workflows
  python comfy_run.py -w <name> --inspect                 # Show customizable inputs
  python comfy_run.py -w <name> --prompt "a cat on mars"  # Run with text prompt
  python comfy_run.py -w <name> --prompt "..." --image photo.jpg
  python comfy_run.py -w <name> --prompt "..." --image face.jpg --audio speech.wav
  python comfy_run.py -w <name> --override '{"node_id":{"input":"value"}}'
  python comfy_run.py -w <name> --config inputs.yaml      # Load inputs from YAML/JSON
"""

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import time
import uuid

# Add comfy_api.py to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from comfy_api import (
    COMFY_HOST,
    load_workflow,
    litegraph_to_api,
    get_object_info,
    upload_image,
    find_nodes_by_type,
    set_text_prompt,
    run_workflow,
    queue_prompt,
    get_history,
    download_file,
    WORKFLOW_DIRS,
)

import websocket as ws_module

# ── Configuration ──────────────────────────────────────────────────────────────

# Default paths (can be overridden via config.json in scripts/ or environment variables)
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
WORKFLOW_ROOT = WORKFLOW_DIRS[0] if WORKFLOW_DIRS else os.path.join(SKILL_DIR, "workflows")
CTRL_SCRIPT = os.path.join(SCRIPT_DIR, "comfy_control.sh")
DEFAULT_OUTPUT = os.path.expanduser("~/comfyui_output")

# Node type groups for auto-detection
TEXT_NODE_TYPES = {
    "CLIPTextEncode",
    "TextEncodeQwenImageEditPlus",
    "TextEncodeQwenImage",
    "WanTextEncode",
    "HunyuanVideoTextEncode",
    "LTXVConditioning",
    "HunyuanDiTTextEncode",
    "PixArtTextEncode",
    "SDXLPromptStyler",
    "Text Multiline",
    "ShowText|pysssss",
}

IMAGE_LOADER_TYPES = {"LoadImage", "LoadImageMask"}

AUDIO_LOADER_TYPES = {"LoadAudio", "VHS_LoadAudio"}

VIDEO_LOADER_TYPES = {
    "LoadVideo",
    "VHS_LoadVideo",
    "VHS_LoadVideoPath",
    "LoadVideoUpload",
}

LATENT_SIZE_TYPES = {
    "EmptyLatentImage",
    "EmptySD3LatentImage",
    "EmptyFlux2LatentImage",
    "EmptyHunyuanLatentVideo",
    "EmptyHunyuanVideo15Latent",
    "EmptyWanLatentVideo",
    "EmptyQwenImageLayeredLatentImage",
}

SAMPLER_TYPES = {"KSampler", "KSamplerAdvanced", "SamplerCustomAdvanced"}

OUTPUT_NODE_TYPES = {
    "SaveImage", "VHS_VideoCombine", "SaveAnimatedWEBP", "SaveVideo",
    "SaveAudio", "VHS_SaveAudio",
}

# Types that act as configurable on/off switches or scalar knobs
SWITCH_BOOL_TYPES = {"PrimitiveBoolean"}
SWITCH_SCALAR_TYPES = {"PrimitiveInt", "PrimitiveFloat", "FloatConstant"}
SWITCH_ROUTER_TYPES = {
    "Any Switch (rgthree)", "Context Switch (rgthree)", "easy ifElse",
    "ComfySwitchNode",
}
# Input names that are switch branch slots (not user-facing knobs)
_BRANCH_INPUT_RE = re.compile(r'^(on_true|on_false|any_\d+|input_\d+)$')

# Known negative prompt patterns (Chinese + English)
# We require multiple hits or keyword-only patterns to avoid false positives
# (e.g. "removing all blur" in a positive prompt should not trigger)
_NEG_KEYWORD_PATTERNS = [
    re.compile(r"\blow quality\b", re.IGNORECASE),
    re.compile(r"\bbad anatomy\b", re.IGNORECASE),
    re.compile(r"\bbad hands\b", re.IGNORECASE),
    re.compile(r"\bmissing fingers\b", re.IGNORECASE),
    re.compile(r"\bextra fingers\b", re.IGNORECASE),
    re.compile(r"\bdeformed\b", re.IGNORECASE),
    re.compile(r"\bdisfigured\b", re.IGNORECASE),
    re.compile(r"低分辨率"),
    re.compile(r"低画质"),
    re.compile(r"肢体畸形"),
    re.compile(r"色情"),
    re.compile(r"裸体"),
]


# ── Date-pattern resolution ────────────────────────────────────────────────

_DATE_TOKEN_RE = re.compile(r"%date:([^%]+)%")

# Mapping from ComfyUI date-format tokens to Python strftime codes
_DATE_FMT_MAP = [
    ("yyyy", "%Y"), ("yy", "%y"),
    ("MM", "%m"), ("dd", "%d"),
    ("HH", "%H"), ("hh", "%H"), ("mm", "%M"), ("ss", "%S"),
]


def _resolve_date_patterns(api_prompt):
    """Replace %date:...% frontend-only patterns with real timestamps.

    ComfyUI's frontend resolves these for the UI, but the API server does not.
    On Windows this causes [WinError 267] when a node tries to create a
    directory whose name is literally '%date:yyyy-MM-dd%'.
    """
    from datetime import datetime
    now = datetime.now()

    def _expand(m):
        fmt = m.group(1)
        for token, code in _DATE_FMT_MAP:
            fmt = fmt.replace(token, code)
        return now.strftime(fmt)

    for node_id, node in api_prompt.items():
        inputs = node.get("inputs", {})
        for key, val in inputs.items():
            if isinstance(val, str) and "%date:" in val:
                inputs[key] = _DATE_TOKEN_RE.sub(_expand, val)

    return api_prompt


# ── Extension chain control ────────────────────────────────────────────────

def apply_extend_steps(wf, n_steps):
    """Enable first N steps in a SVI extension chain workflow.

    Detects the extension chain (sequential subgraph instances where each feeds
    into the next) and corresponding VHS_VideoCombine nodes. Sets first N chain
    steps + VHS to mode=0 (active), rest to mode=4 (bypass).
    """
    nodes = wf.get("nodes", [])
    links = wf.get("links", [])

    # Identify subgraph types from definitions
    sg_defs = {}
    for sg in wf.get("definitions", {}).get("subgraphs", []):
        sg_defs[sg.get("id")] = sg
    if not sg_defs:
        return wf

    # Exclude subgraph instances whose definitions have ALL inner nodes bypassed
    # (dead shells that can't produce any output)
    def _has_active_inner(node):
        sd = sg_defs.get(node.get("type", ""))
        if not sd:
            return False
        return any(n.get("mode", 0) != 4 for n in sd.get("nodes", []))

    sg_node_ids = {n["id"] for n in nodes
                   if n.get("type") in sg_defs and _has_active_inner(n)}
    link_by_id = {l[0]: l for l in links if isinstance(l, list)}

    # Build subgraph-to-subgraph directed edges
    fwd = {}   # src_id -> set of dst_ids
    rev = {}   # dst_id -> set of src_ids
    for n in nodes:
        if n["id"] not in sg_node_ids:
            continue
        for inp in n.get("inputs", []):
            lid = inp.get("link")
            if lid and lid in link_by_id:
                src = link_by_id[lid][1]
                if src in sg_node_ids:
                    fwd.setdefault(src, set()).add(n["id"])
                    rev.setdefault(n["id"], set()).add(src)

    # Find chain starts (subgraph nodes with no incoming from another subgraph)
    # Walk forward greedily to find the longest linear chain
    starts = [nid for nid in sg_node_ids if nid not in rev]
    best_chain = []
    for start in starts:
        chain = [start]
        cur = start
        while cur in fwd:
            nexts = fwd[cur]
            # Follow the link to another subgraph node that also chains forward
            found = None
            for nxt in sorted(nexts):
                if nxt not in chain:
                    found = nxt
                    break
            if found is None:
                break
            chain.append(found)
            cur = found
        if len(chain) > len(best_chain):
            best_chain = chain

    if len(best_chain) < 2:
        print(f"  Warning: No extension chain detected (longest chain: {len(best_chain)})")
        return wf

    n_steps = max(1, min(n_steps, len(best_chain)))
    chain_set = set(best_chain)

    # Find VHS_VideoCombine nodes paired with each chain step
    # (VHS that takes images directly from a chain node)
    chain_vhs = {}  # chain_node_id -> vhs_node_id
    for n in nodes:
        if n.get("type") != "VHS_VideoCombine":
            continue
        for inp in n.get("inputs", []):
            if inp.get("name") == "images":
                lid = inp.get("link")
                if lid and lid in link_by_id:
                    src = link_by_id[lid][1]
                    if src in chain_set:
                        chain_vhs[src] = n["id"]

    # Apply modes
    node_by_id = {n["id"]: n for n in nodes}
    for i, nid in enumerate(best_chain):
        mode = 0 if i < n_steps else 4
        node_by_id[nid]["mode"] = mode
        if nid in chain_vhs:
            node_by_id[chain_vhs[nid]]["mode"] = mode

    active = [best_chain[i] for i in range(n_steps)]
    bypassed = [best_chain[i] for i in range(n_steps, len(best_chain))]
    print(f"  Extension chain: {len(best_chain)} steps, {n_steps} enabled")

    return wf


# ── Virtual wire resolution ────────────────────────────────────────────────

_VIRTUAL_WIRE_TYPES = {"easy getNode", "easy setNode"}


def resolve_virtual_wires(workflow):
    """Resolve 'easy getNode'/'easy setNode' virtual wire pairs into real links.

    ComfyUI-Easy-Use's virtual wires connect nodes wirelessly:
    - 'easy setNode' receives data and publishes it under a name
    - 'easy getNode' retrieves published data by name and outputs it

    Rewrites links so downstream nodes connect directly to the original source.
    """
    wf = copy.deepcopy(workflow)
    nodes = wf.get("nodes", [])
    links = wf.get("links", [])

    setter_ids = set()
    getter_ids = set()
    has_any = False
    for n in nodes:
        if n.get("type") in _VIRTUAL_WIRE_TYPES:
            has_any = True
            if n["type"] == "easy setNode":
                setter_ids.add(n["id"])
            else:
                getter_ids.add(n["id"])
    if not has_any:
        return wf

    link_by_id = {lnk[0]: lnk for lnk in links if isinstance(lnk, list)}

    # Build setter map: name -> (source_node_id, source_slot)
    setters = {}
    for node in nodes:
        if node.get("type") != "easy setNode":
            continue
        wv = node.get("widgets_values", [])
        name = (wv[0] if isinstance(wv, list) and wv
                else (list(wv.values())[0] if isinstance(wv, dict) and wv else ""))
        if not name:
            continue
        for inp in node.get("inputs", []):
            link_id = inp.get("link")
            if link_id is not None and link_id in link_by_id:
                lnk = link_by_id[link_id]
                setters[name] = (lnk[1], lnk[2])
                break

    # Map each getter node to its real source
    getter_sources = {}
    for node in nodes:
        if node.get("type") != "easy getNode":
            continue
        wv = node.get("widgets_values", [])
        name = (wv[0] if isinstance(wv, list) and wv
                else (list(wv.values())[0] if isinstance(wv, dict) and wv else ""))
        if name and name in setters:
            getter_sources[node["id"]] = setters[name]

    # Rewrite links: replace getter/setter with direct connections
    new_links = []
    for lnk in links:
        if not isinstance(lnk, list):
            new_links.append(lnk)
            continue
        src_id, dst_id = lnk[1], lnk[3]
        if dst_id in setter_ids or dst_id in getter_ids:
            continue
        if src_id in getter_sources:
            real_src, real_slot = getter_sources[src_id]
            lnk = list(lnk)
            lnk[1], lnk[2] = real_src, real_slot
        if src_id in setter_ids:
            continue
        new_links.append(lnk)

    wf["links"] = new_links
    wf["nodes"] = [n for n in nodes if n["id"] not in setter_ids
                   and n["id"] not in getter_ids]
    return wf


# ── Inner graph cleanup ───────────────────────────────────────────────────


def _clean_inner_graph(nodes, links):
    """Resolve pass-through nodes (Reroute, mode=4 bypassed) in a graph.

    Used to clean subgraph definition inner graphs before API conversion.
    Also inlines PrimitiveStringMultiline values into target nodes.
    Uses TYPE-MATCHING for bypass: each output connects to the input of
    the same type (not same slot index), matching ComfyUI's actual behavior.
    Handles both list-format and dict-format links.
    Returns (cleaned_nodes, cleaned_links).
    """

    def _link_id(lnk):
        return lnk["id"] if isinstance(lnk, dict) else lnk[0]

    def _link_src(lnk):
        if isinstance(lnk, dict):
            return lnk["origin_id"], lnk["origin_slot"]
        return lnk[1], lnk[2]

    def _link_dst(lnk):
        if isinstance(lnk, dict):
            return lnk["target_id"], lnk["target_slot"]
        return lnk[3], lnk[4]

    def _set_link_src(lnk, src_id, src_slot):
        if isinstance(lnk, dict):
            lnk = dict(lnk)
            lnk["origin_id"] = src_id
            lnk["origin_slot"] = src_slot
        else:
            lnk = list(lnk)
            lnk[1], lnk[2] = src_id, src_slot
        return lnk

    # ── Step 1: Inline PrimitiveStringMultiline values ────────────────
    _PRIMITIVE_TYPES = {"PrimitiveStringMultiline"}
    prim_ids = {n["id"] for n in nodes if n.get("type") in _PRIMITIVE_TYPES}
    if prim_ids:
        prim_values = {}
        for n in nodes:
            if n["id"] in prim_ids:
                wv = n.get("widgets_values", [])
                prim_values[n["id"]] = (wv[0] if isinstance(wv, list) and wv
                                        else (list(wv.values())[0] if isinstance(wv, dict) and wv else ""))

        node_by_id = {n["id"]: n for n in nodes}
        links_to_remove = set()
        for lnk in links:
            src_id, _ = _link_src(lnk)
            if src_id not in prim_ids:
                continue
            lid = _link_id(lnk)
            dst_id, _ = _link_dst(lnk)
            dst_node = node_by_id.get(dst_id)
            if dst_node:
                value = prim_values.get(src_id, "")
                for inp in dst_node.get("inputs", []):
                    if inp.get("link") == lid:
                        inp_name = inp.get("name", "")
                        wv = dst_node.get("widgets_values")
                        if isinstance(wv, dict) and inp_name:
                            wv[inp_name] = value
                        elif isinstance(wv, list):
                            widget_inputs = [i for i in dst_node.get("inputs", [])
                                             if i.get("widget") is not None]
                            widget_name = (inp.get("widget") or {}).get("name", inp_name)
                            for wi_idx, wi in enumerate(widget_inputs):
                                wn = (wi.get("widget") or {}).get("name", wi.get("name"))
                                if wn == widget_name and wi_idx < len(wv):
                                    wv[wi_idx] = value
                                    break
                        inp["link"] = None
                        break
            links_to_remove.add(lid)

        if links_to_remove:
            links = [l for l in links if _link_id(l) not in links_to_remove]
        nodes = [n for n in nodes if n["id"] not in prim_ids]

    # ── Step 2: Resolve bypassed and Reroute nodes ────────────────────
    # Primitive value nodes (PrimitiveBoolean, PrimitiveInt, etc.) are excluded
    # from pass-through resolution even when bypassed: they produce values from
    # their widget settings and should stay in the graph so the pipeline works.
    _primitive_value_types = {"PrimitiveBoolean", "PrimitiveInt", "PrimitiveFloat", "PrimitiveString"}
    passthrough_ids = {n["id"] for n in nodes
                       if (n.get("mode") == 4 or n.get("type") == "Reroute")
                       and n.get("type") not in _primitive_value_types}
    if not passthrough_ids:
        return nodes, links

    link_by_id = {_link_id(lnk): lnk for lnk in links}

    # Build input_feeds using type-based matching for bypassed nodes
    input_feeds = {}  # (node_id, output_slot) -> (src_id, src_slot)
    for node in nodes:
        if node["id"] not in passthrough_ids:
            continue

        # Map input type -> first (src_id, src_slot) from incoming links
        input_sources = {}  # type_str -> (src_id, src_slot)
        for inp in node.get("inputs", []):
            link_id = inp.get("link")
            if link_id is not None and link_id in link_by_id:
                lnk = link_by_id[link_id]
                src_id, src_slot = _link_src(lnk)
                inp_type = inp.get("type", "")
                if inp_type and inp_type not in input_sources:
                    input_sources[inp_type] = (src_id, src_slot)

        # Match each output slot to an input by type
        for out_idx, out in enumerate(node.get("outputs", [])):
            out_type = out.get("type", "")
            if out_type in input_sources:
                input_feeds[(node["id"], out_idx)] = input_sources[out_type]
            elif out_type == "*" and input_sources:
                # Wildcard output: take first available input
                input_feeds[(node["id"], out_idx)] = next(iter(input_sources.values()))
            elif input_sources:
                # Try wildcard inputs
                if "*" in input_sources:
                    input_feeds[(node["id"], out_idx)] = input_sources["*"]

    def resolve(src_id, src_slot, _seen=None):
        if _seen is None:
            _seen = set()
        key = (src_id, src_slot)
        if src_id not in passthrough_ids or key in _seen:
            return src_id, src_slot
        _seen.add(key)
        real = input_feeds.get(key)
        if real is None:
            return src_id, src_slot
        return resolve(real[0], real[1], _seen)

    new_links = []
    for lnk in links:
        src_id, src_slot = _link_src(lnk)
        dst_id, _ = _link_dst(lnk)
        if src_id in passthrough_ids:
            real_src, real_slot = resolve(src_id, src_slot)
            if real_src in passthrough_ids:
                continue
            lnk = _set_link_src(lnk, real_src, real_slot)
        if dst_id in passthrough_ids:
            continue
        new_links.append(lnk)

    nodes = [n for n in nodes if n["id"] not in passthrough_ids]
    # Force-activate bypassed Primitive value nodes so _convert_nodes won't skip them
    for n in nodes:
        if n.get("type") in _primitive_value_types and n.get("mode") == 4:
            n["mode"] = 0
    return nodes, new_links


# ── Bypass pre-processing ──────────────────────────────────────────────────


def strip_bypassed_nodes(workflow):
    """Remove mode=4 (bypassed) nodes and inline primitive value nodes from
    a LiteGraph workflow JSON.

    1. Bypassed nodes (mode=4): rewires links so downstream nodes connect
       directly to whatever fed the bypassed node's corresponding input slot.
    2. Primitive value nodes (PrimitiveStringMultiline, etc.): these are
       frontend-only nodes that hold a constant value and feed it to other
       nodes via links.  They aren't real ComfyUI nodes (not in object_info),
       so we inline their widget value into the target node's widgets_values
       and drop the link.

    Works on a copy — the original workflow is never modified.
    """
    wf = copy.deepcopy(workflow)
    nodes = wf.get("nodes", [])
    links = wf.get("links", [])

    # ── Phase 1: Rewire bypassed (mode=4) nodes ──────────────────────────
    # Uses TYPE-MATCHING: when a node is bypassed, each output passes through
    # to the first input of the same type (matching ComfyUI's behavior).
    bypassed_ids = {n["id"] for n in nodes if n.get("mode") == 4}

    if bypassed_ids:
        link_by_id = {lnk[0]: lnk for lnk in links if isinstance(lnk, list)}

        # Build type-based input_feeds: (node_id, output_slot) -> (src_id, src_slot)
        input_feeds = {}
        for node in nodes:
            if node["id"] not in bypassed_ids:
                continue
            # Map input type -> first (src_id, src_slot)
            input_sources = {}  # type_str -> (src_id, src_slot)
            for inp in node.get("inputs", []):
                link_id = inp.get("link")
                if link_id is not None and link_id in link_by_id:
                    lnk = link_by_id[link_id]
                    inp_type = inp.get("type", "")
                    if inp_type and inp_type not in input_sources:
                        input_sources[inp_type] = (lnk[1], lnk[2])
            # Match each output slot to input by type
            for out_idx, out in enumerate(node.get("outputs", [])):
                out_type = out.get("type", "")
                if out_type in input_sources:
                    input_feeds[(node["id"], out_idx)] = input_sources[out_type]
                elif out_type == "*" and input_sources:
                    input_feeds[(node["id"], out_idx)] = next(iter(input_sources.values()))
                elif input_sources and "*" in input_sources:
                    input_feeds[(node["id"], out_idx)] = input_sources["*"]

        def resolve(src_id, src_slot, _seen=None):
            """Follow bypass chains to a real (non-bypassed) source."""
            if _seen is None:
                _seen = set()
            key = (src_id, src_slot)
            if src_id not in bypassed_ids or key in _seen:
                return src_id, src_slot
            _seen.add(key)
            real = input_feeds.get(key)
            if real is None:
                return src_id, src_slot
            return resolve(real[0], real[1], _seen)

        new_links = []
        for lnk in links:
            if not isinstance(lnk, list):
                new_links.append(lnk)
                continue
            src_id, src_slot = lnk[1], lnk[2]
            dst_id = lnk[3]
            if src_id in bypassed_ids:
                real_src, real_slot = resolve(src_id, src_slot)
                if real_src in bypassed_ids:
                    continue
                lnk = list(lnk)
                lnk[1], lnk[2] = real_src, real_slot
            if dst_id in bypassed_ids:
                continue
            new_links.append(lnk)

        links = new_links
        nodes = [n for n in nodes if n["id"] not in bypassed_ids]

    # ── Phase 2: Inline primitive value nodes ────────────────────────────
    # These are frontend-only nodes that provide a constant value via a link.
    # ComfyUI API doesn't know about them, so we must inline their value
    # into the target node's widgets_values and remove the link.
    _PRIMITIVE_TYPES = {"PrimitiveStringMultiline"}
    node_by_id = {n["id"]: n for n in nodes}
    primitive_ids = {n["id"] for n in nodes if n.get("type") in _PRIMITIVE_TYPES}

    if primitive_ids:
        # Extract the constant value from each primitive node
        prim_values = {}  # node_id -> value
        for nid in primitive_ids:
            n = node_by_id[nid]
            wv = n.get("widgets_values", [])
            if isinstance(wv, list) and wv:
                prim_values[nid] = wv[0]
            elif isinstance(wv, dict):
                # dict style: first value
                vals = list(wv.values())
                prim_values[nid] = vals[0] if vals else ""
            else:
                prim_values[nid] = ""

        # Find links sourced from primitive nodes and inline the value
        # link format: [id, src_id, src_slot, dst_id, dst_slot, type]
        links_to_remove = set()
        for lnk in links:
            if not isinstance(lnk, list):
                continue
            src_id = lnk[1]
            if src_id not in primitive_ids:
                continue

            dst_id, dst_slot = lnk[3], lnk[4]
            dst_node = node_by_id.get(dst_id)
            if dst_node is None:
                links_to_remove.add(lnk[0])
                continue

            value = prim_values.get(src_id, "")

            # Find the target input by slot index and set the widget value
            dst_inputs = dst_node.get("inputs", [])
            target_inp = None
            for inp in dst_inputs:
                if inp.get("link") == lnk[0]:
                    target_inp = inp
                    break

            if target_inp is not None:
                inp_name = target_inp.get("name", "")
                # Inject the value into the node's widgets_values
                wv = dst_node.get("widgets_values")
                if isinstance(wv, dict) and inp_name:
                    wv[inp_name] = value
                elif isinstance(wv, list):
                    # For list-style widgets_values, find position by matching
                    # widget name against the ordered widget inputs.
                    # widgets_values slots correspond to the node's widget
                    # names in definition order.  The inputs array may have
                    # extra connection-only entries, so count only widget inputs.
                    widget_name = (target_inp.get("widget") or {}).get("name", inp_name)
                    # Build widget-name → list-index map from this node's
                    # widgets_values by matching input names
                    # Strategy: node inputs with 'widget' key are widget-
                    # capable; they appear in widgets_values in some order.
                    # But simpler: just scan widgets_values for the default
                    # value position.  Node 177 has ['','',''] for
                    # [string_a, string_b, delimiter].  We can iterate inputs
                    # that have a widget key and count their order.
                    widget_inputs_in_order = [
                        inp for inp in dst_inputs
                        if inp.get("widget") is not None
                    ]
                    for wi_idx, wi in enumerate(widget_inputs_in_order):
                        wn = (wi.get("widget") or {}).get("name", wi.get("name"))
                        if wn == widget_name and wi_idx < len(wv):
                            wv[wi_idx] = value
                            break

                # Remove the link so converter treats this as a widget input
                target_inp["link"] = None

            links_to_remove.add(lnk[0])

        if links_to_remove:
            links = [lnk for lnk in links if not isinstance(lnk, list) or lnk[0] not in links_to_remove]

        # Remove primitive nodes
        nodes = [n for n in nodes if n["id"] not in primitive_ids]

    # ── Phase 3: Clean inner subgraph definitions ──────────────────────
    # Resolve Reroute and bypassed nodes inside subgraph definitions,
    # which _convert_nodes can't handle (they're frontend-only pass-throughs).
    sg_list = wf.get("definitions", {}).get("subgraphs", [])
    for sg in sg_list:
        sg["nodes"], sg["links"] = _clean_inner_graph(
            sg.get("nodes", []), sg.get("links", [])
        )

    # ── Phase 4: Clean up ────────────────────────────────────────────────
    wf["links"] = links
    wf["nodes"] = nodes

    valid_link_ids = {lnk[0] for lnk in links if isinstance(lnk, list)}
    for node in wf["nodes"]:
        for inp in node.get("inputs", []):
            if inp.get("link") is not None and inp["link"] not in valid_link_ids:
                inp["link"] = None
        for out in node.get("outputs", []):
            if out.get("links"):
                out["links"] = [lid for lid in out["links"] if lid in valid_link_ids]

    return wf


# ── Helpers ────────────────────────────────────────────────────────────────


def discover_workflows():
    """Find all workflow JSON files under workflows/."""
    workflows = []
    for root, _dirs, files in os.walk(WORKFLOW_ROOT):
        for f in files:
            if f.endswith(".json") and not f.startswith("."):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, WORKFLOW_ROOT)
                category = os.path.dirname(rel) or "Uncategorized"
                workflows.append(
                    {"name": f, "path": full, "rel": rel, "category": category}
                )
    workflows.sort(key=lambda w: (w["category"], w["name"]))
    return workflows


def list_workflows():
    """Print all available workflows grouped by category."""
    wfs = discover_workflows()
    current_cat = None
    for i, w in enumerate(wfs, 1):
        if w["category"] != current_cat:
            current_cat = w["category"]
            print(f"\n  [{current_cat}]")
        print(f"    {i:2d}. {w['name']}")
    print(f"\n  Total: {len(wfs)} workflows")
    return wfs


def find_workflow(name_or_index, wf_list=None):
    """Resolve a workflow by name, partial match, index, or path."""
    # Absolute path
    if os.path.isabs(name_or_index) and os.path.exists(name_or_index):
        return name_or_index

    if wf_list is None:
        wf_list = discover_workflows()

    # Try numeric index
    try:
        idx = int(name_or_index)
        if 1 <= idx <= len(wf_list):
            return wf_list[idx - 1]["path"]
    except ValueError:
        pass

    # Exact name match
    for w in wf_list:
        if w["name"] == name_or_index or w["rel"] == name_or_index:
            return w["path"]

    # Partial / case-insensitive match
    lower = name_or_index.lower()
    matches = [w for w in wf_list if lower in w["name"].lower() or lower in w["rel"].lower()]
    if len(matches) == 1:
        return matches[0]["path"]
    if len(matches) > 1:
        print(f"Ambiguous workflow name '{name_or_index}'. Matches:")
        for m in matches:
            print(f"  - {m['rel']}")
        sys.exit(1)

    # Try load_workflow (searches multiple dirs)
    try:
        load_workflow(name_or_index)
        # If it loads, find the actual path
        for base in [WORKFLOW_ROOT]:
            for root, _d, files in os.walk(base):
                for fn in files:
                    if fn == name_or_index or fn == name_or_index + ".json":
                        return os.path.join(root, fn)
    except FileNotFoundError:
        pass

    print(f"Workflow not found: {name_or_index}")
    sys.exit(1)


def _is_negative_text(text):
    """Heuristic: is this text a negative prompt? Requires 2+ keyword matches."""
    if not isinstance(text, str) or len(text) < 5:
        return False
    hits = sum(1 for pat in _NEG_KEYWORD_PATTERNS if pat.search(text))
    return hits >= 2


def inspect_workflow(api_prompt):
    """Analyze an API prompt and return customizable inputs grouped by type."""
    info = {
        "text_prompts": [],      # (node_id, field_name, current_value, is_negative)
        "image_inputs": [],      # (node_id, class_type, field_name, current_value)
        "audio_inputs": [],      # (node_id, class_type, field_name, current_value)
        "video_inputs": [],      # (node_id, class_type, field_name, current_value)
        "resolution": [],        # (node_id, class_type, width, height)
        "sampler": [],           # (node_id, class_type, params_dict)
        "outputs": [],           # (node_id, class_type, format, filename_prefix, upstream_chain)
        "all_nodes": {},         # node_id -> {class_type, inputs}
    }

    for nid, node in api_prompt.items():
        ct = node.get("class_type", "")
        inputs = node.get("inputs", {})
        info["all_nodes"][nid] = {"class_type": ct, "inputs": dict(inputs)}

        # Text prompts
        if ct in TEXT_NODE_TYPES:
            for field in ("text", "prompt", "positive", "caption"):
                if field in inputs and isinstance(inputs[field], str):
                    is_neg = _is_negative_text(inputs[field])
                    info["text_prompts"].append((nid, field, inputs[field], is_neg))
                    break

        # Image loaders
        if ct in IMAGE_LOADER_TYPES:
            for field in ("image",):
                if field in inputs:
                    info["image_inputs"].append((nid, ct, field, inputs.get(field)))

        # Audio loaders
        if ct in AUDIO_LOADER_TYPES:
            for field in ("audio", "audio_file"):
                if field in inputs:
                    info["audio_inputs"].append((nid, ct, field, inputs.get(field)))

        # Video loaders
        if ct in VIDEO_LOADER_TYPES:
            for field in ("video", "video_path", "video_file"):
                if field in inputs:
                    info["video_inputs"].append((nid, ct, field, inputs.get(field)))

        # Resolution
        if ct in LATENT_SIZE_TYPES:
            w = inputs.get("width")
            h = inputs.get("height")
            if w is not None and h is not None:
                info["resolution"].append((nid, ct, w, h))

        # Sampler settings
        if ct in SAMPLER_TYPES:
            params = {}
            for k in ("seed", "steps", "cfg", "sampler_name", "scheduler", "denoise"):
                if k in inputs and not isinstance(inputs[k], list):
                    params[k] = inputs[k]
            if params:
                info["sampler"].append((nid, ct, params))

        # Output nodes
        if ct in OUTPUT_NODE_TYPES:
            fmt = inputs.get("format", "png")
            prefix = inputs.get("filename_prefix", "")
            # Trace upstream: what feeds into the main visual input
            upstream = _trace_upstream(api_prompt, nid, "images", depth=3)
            info["outputs"].append((nid, ct, fmt, prefix, upstream))

    # ── Detect configurable switches & scalar knobs ──
    info["switches"] = _detect_switches(api_prompt)

    return info


def _compact_controls(controls):
    """Strip node IDs from control strings for display, deduplicate, filter diagnostics.
    'sg146_276(ModelPatchTorchSettings).model' → 'ModelPatchTorchSettings.model'"""
    meaningful = []
    for c in controls:
        if "PreviewAny" in c:
            continue
        m = re.match(r'[^(]*\(([^)]+)\)\.(.+)', c)
        meaningful.append(f"{m.group(1)}.{m.group(2)}" if m else c)
    counts = {}
    for c in meaningful:
        counts[c] = counts.get(c, 0) + 1
    result = []
    for c in dict.fromkeys(meaningful):  # unique, preserve order
        result.append(f"{c} ×{counts[c]}" if counts[c] > 1 else c)
    return result


def _auto_switch_label(controls):
    """Generate brief human-readable label from non-diagnostic control targets.
    Prefers the most meaningful input name (skips generic ones like 'a', 'b')."""
    meaningful = [c for c in controls if "PreviewAny" not in c]
    if not meaningful:
        return "diagnostic"
    inputs = []
    for c in meaningful:
        m = re.match(r'[^(]*\([^)]+\)\.(.+)', c)
        if m and m.group(1) not in inputs:
            inputs.append(m.group(1))
    # Prefer descriptive names over single-letter math vars
    descriptive = [i for i in inputs if len(i) > 1 or i not in 'abcxyz']
    chosen = descriptive if descriptive else inputs
    return ", ".join(chosen[:2]) if chosen else ""


def _detect_switches(api_prompt):
    """Detect configurable boolean switches and scalar knobs in the API prompt.
    Returns list of dicts with node_id, class_type, value_type, value, field,
    controls, label, and (for booleans) related."""
    switches = []
    # Build consumer map: node_id -> [(consumer_nid, consumer_ct, input_name)]
    consumer_map = {}
    for oid, on in api_prompt.items():
        for k, v in on.get("inputs", {}).items():
            if isinstance(v, list) and len(v) == 2:
                src = str(v[0])
                consumer_map.setdefault(src, []).append((oid, on.get("class_type", ""), k))

    for nid, node in api_prompt.items():
        ct = node.get("class_type", "")
        inputs = node.get("inputs", {})

        if ct in SWITCH_BOOL_TYPES:
            val = inputs.get("value")
            controls = _trace_switch_effect(api_prompt, nid, consumer_map, depth=4)
            # Skip orphan booleans that don't control anything
            if not controls:
                continue
            switches.append({
                "node_id": nid, "class_type": ct,
                "value_type": "boolean", "value": val, "field": "value",
                "controls": controls,
            })

        elif ct in SWITCH_SCALAR_TYPES:
            val = inputs.get("value")
            consumers = consumer_map.get(nid, [])
            if not consumers:
                continue
            # Filter out scalars that ONLY feed into switch branch inputs
            # (on_true, on_false, any_01..any_99) — these are internal to switches
            real_consumers = [(cid, cct, cinp) for cid, cct, cinp in consumers
                              if not _BRANCH_INPUT_RE.match(cinp)]
            if not real_consumers:
                continue
            # Skip scalars whose only real consumer is a seed input
            # (already handled by --seed flag)
            if all(cinp in ("seed", "noise_seed") for _, _, cinp in real_consumers):
                continue
            controls = []
            for cid, cct, cinp in real_consumers:
                controls.append(f"{cid}({cct}).{cinp}")
            switches.append({
                "node_id": nid, "class_type": ct,
                "value_type": "int" if ct == "PrimitiveInt" else "float",
                "value": val, "field": "value",
                "controls": controls,
            })

    # Sort: booleans first, then scalars, by node_id
    switches.sort(key=lambda s: (0 if s["value_type"] == "boolean" else 1, s["node_id"]))

    # Auto-label all switches from their downstream targets
    for sw in switches:
        sw["label"] = _auto_switch_label(sw["controls"])

    # Detect related/paired booleans (shared meaningful downstream targets)
    bools_only = [s for s in switches if s["value_type"] == "boolean"]
    target_map = {}
    for sw in bools_only:
        target_map[sw["node_id"]] = frozenset(
            c for c in sw["controls"] if "PreviewAny" not in c
        )
    for sw in bools_only:
        related = []
        my_targets = target_map[sw["node_id"]]
        for other in bools_only:
            if other["node_id"] == sw["node_id"]:
                continue
            if my_targets & target_map[other["node_id"]]:
                related.append(other["node_id"])
        sw["related"] = related

    # Scalars have no pairing
    for sw in switches:
        if "related" not in sw:
            sw["related"] = []

    return switches


def _trace_switch_effect(api_prompt, bool_nid, consumer_map, depth=4):
    """Trace what a boolean switch ultimately controls by following through
    router nodes (Any Switch, ifElse, etc.) to find the meaningful downstream nodes."""
    effects = []
    visited = set()
    queue = [(bool_nid, 0)]
    while queue:
        current, d = queue.pop(0)
        if current in visited or d > depth:
            continue
        visited.add(current)
        for cid, cct, cinp in consumer_map.get(current, []):
            if cct in SWITCH_ROUTER_TYPES:
                # Follow through router to its consumers
                queue.append((cid, d + 1))
            else:
                # Meaningful endpoint — not a router
                effects.append(f"{cid}({cct}).{cinp}")
    return effects


def _trace_upstream(api_prompt, node_id, input_name, depth=3):
    """Trace upstream chain from a node's input. Returns list of (node_id, class_type, input_name)."""
    chain = []
    current_nid = node_id
    current_input = input_name
    for _ in range(depth):
        node = api_prompt.get(str(current_nid), {})
        src = node.get("inputs", {}).get(current_input)
        if not isinstance(src, list) or len(src) != 2:
            break
        src_nid, src_slot = src
        src_node = api_prompt.get(str(src_nid), {})
        src_ct = src_node.get("class_type", "?")
        chain.append((str(src_nid), src_ct))
        # Follow the first linked input of the source node for the next hop
        current_nid = src_nid
        current_input = None
        for k, v in src_node.get("inputs", {}).items():
            if isinstance(v, list) and len(v) == 2:
                current_input = k
                break
        if current_input is None:
            break
    return chain


def _build_node_title_map(wf_path):
    """Build a map of node_id -> title from the original workflow JSON.
    Also returns the raw nodes list for context extraction."""
    try:
        with open(wf_path) as f:
            wf = json.load(f)
    except Exception:
        return {}, []
    nodes = wf.get("nodes", [])
    title_map = {}
    for node in nodes:
        nid = str(node.get("id", ""))
        title = node.get("title") or node.get("properties", {}).get("Node name for S&R")
        if title and title != node.get("type"):
            title_map[nid] = title
    return title_map, nodes


def _find_raw_node(raw_nodes, api_nid):
    """Find the original workflow JSON node matching an API node_id.
    Handles subgraph-prefixed IDs like 'sg197_180' by checking inner nodes."""
    # Direct match
    for node in raw_nodes:
        if str(node.get("id")) == api_nid:
            return node
    # Subgraph prefixed: sg{instance_id}_{inner_id}
    m = re.match(r"sg\d+_(\d+)$", api_nid)
    if m:
        inner_id = m.group(1)
        for node in raw_nodes:
            if str(node.get("id")) == inner_id:
                return node
    return None


def _node_context_summary(raw_node):
    """Build a compact context dict from a raw workflow JSON node."""
    if raw_node is None:
        return None
    ctx = {"id": raw_node.get("id"), "type": raw_node.get("type")}
    if raw_node.get("title"):
        ctx["title"] = raw_node["title"]
    # Include output slot names (helps understand what this node produces)
    out_names = [o.get("name") for o in raw_node.get("outputs", []) if o.get("links")]
    if out_names:
        ctx["output_slots"] = out_names
    # Include connected input names (helps understand dependencies)
    connected = [i.get("name") for i in raw_node.get("inputs", []) if i.get("link") is not None]
    if connected:
        ctx["connected_inputs"] = connected
    return ctx


def _extract_label_from_prefix(prefix):
    """Extract a meaningful label from a filename_prefix like 'video/%date%_SVI'."""
    # Strip date patterns and path prefix
    label = re.sub(r".*%date:[^%]*%", "", prefix).strip("/_ ")
    if not label:
        label = prefix.rsplit("/", 1)[-1] if "/" in prefix else prefix
    return label or "default"


def print_inspect(info, workflow_name, wf_path=None, as_json=False):
    """Print or return inspection results with rich context for agent consumption."""
    title_map, raw_nodes = _build_node_title_map(wf_path) if wf_path else ({}, [])

    if as_json:
        return _inspect_as_json(info, workflow_name, wf_path, title_map, raw_nodes)

    print(f"\n{'='*70}")
    print(f"  Workflow: {workflow_name}")
    print(f"  Path:     {wf_path or 'unknown'}")
    print(f"  Total API nodes: {len(info['all_nodes'])}")
    print(f"{'='*70}")

    # ── Text prompts ──
    if info["text_prompts"]:
        print(f"\n  TEXT PROMPTS ({len(info['text_prompts'])} nodes):")
        print(f"  {'─'*66}")
        for idx, (nid, field, val, is_neg) in enumerate(info["text_prompts"]):
            label = "NEGATIVE" if is_neg else "POSITIVE"
            title = title_map.get(nid, "")
            title_str = f' "{title}"' if title else ""
            print(f"    [{label}] node={nid}{title_str}  field={field}")
            preview = val[:120].replace("\n", " ") + ("..." if len(val) > 120 else "")
            print(f"      current: {preview}")
            # Show downstream: what this text node feeds into
            downstream = _trace_downstream_from_text(info["all_nodes"], nid)
            if downstream:
                print(f"      feeds → {downstream}")
        print(f"\n  Set with: --prompt 'your text here'")
        print(f"            --negative 'negative text' (optional)")

    # ── Image inputs ──
    if info["image_inputs"]:
        print(f"\n  IMAGE INPUTS ({len(info['image_inputs'])} loaders):")
        print(f"  {'─'*66}")
        for idx, (nid, ct, field, val) in enumerate(info["image_inputs"]):
            title = title_map.get(nid, "")
            title_str = f' "{title}"' if title else ""
            role = _infer_input_role(raw_nodes, nid, idx, len(info["image_inputs"]), "image")
            print(f"    [{idx+1}] node={nid} type={ct}{title_str}")
            print(f"        current: {val}")
            print(f"        role: {role}")
            raw = _find_raw_node(raw_nodes, nid)
            if raw:
                ctx = _node_context_summary(raw)
                if ctx:
                    print(f"        json_context: {json.dumps(ctx, ensure_ascii=False)}")
        print(f"\n  Set with: --image /path/to/image.jpg [/path/to/image2.jpg ...]")
        print(f"  Order: images are assigned to loaders in the order listed above")

    # ── Audio inputs ──
    if info["audio_inputs"]:
        print(f"\n  AUDIO INPUTS ({len(info['audio_inputs'])} loaders):")
        print(f"  {'─'*66}")
        for idx, (nid, ct, field, val) in enumerate(info["audio_inputs"]):
            title = title_map.get(nid, "")
            title_str = f' "{title}"' if title else ""
            print(f"    [{idx+1}] node={nid} type={ct}{title_str}")
            print(f"        current: {val}")
        print(f"\n  Set with: --audio /path/to/audio.wav")

    # ── Video inputs ──
    if info["video_inputs"]:
        print(f"\n  VIDEO INPUTS ({len(info['video_inputs'])} loaders):")
        print(f"  {'─'*66}")
        for idx, (nid, ct, field, val) in enumerate(info["video_inputs"]):
            title = title_map.get(nid, "")
            title_str = f' "{title}"' if title else ""
            print(f"    [{idx+1}] node={nid} type={ct}{title_str}")
            print(f"        current: {val}")
        print(f"\n  Set with: --video /path/to/video.mp4")

    # ── Resolution ──
    if info["resolution"]:
        print(f"\n  RESOLUTION ({len(info['resolution'])} latent nodes):")
        print(f"  {'─'*66}")
        for nid, ct, w, h in info["resolution"]:
            print(f"    node={nid} type={ct} width={w} height={h}")
        print(f"\n  Set with: --width 1024 --height 1024")

    # ── Sampler ──
    if info["sampler"]:
        print(f"\n  SAMPLER SETTINGS ({len(info['sampler'])} samplers):")
        print(f"  {'─'*66}")
        for nid, ct, params in info["sampler"]:
            print(f"    node={nid} type={ct}")
            for k, v in params.items():
                print(f"      {k}: {v}")
        print(f"\n  Set with: --steps 20 --cfg 4.0 --seed 42")

    # ── Outputs ──
    if info["outputs"]:
        print(f"\n  OUTPUTS ({len(info['outputs'])} save nodes):")
        print(f"  {'─'*66}")
        for idx, (nid, ct, fmt, prefix, upstream) in enumerate(info["outputs"]):
            label = _extract_label_from_prefix(prefix)
            print(f"    [{idx+1}] node={nid} type={ct}")
            print(f"        format: {fmt}")
            print(f"        label: {label}")
            print(f"        filename_prefix: {prefix}")
            if upstream:
                chain_str = " ← ".join(f"{uid}({uct})" for uid, uct in upstream)
                print(f"        pipeline: {chain_str}")
    else:
        print(f"\n  OUTPUTS: No save/output nodes detected")

    # ── Configurable switches ──
    if info["switches"]:
        bools = [s for s in info["switches"] if s["value_type"] == "boolean"]
        scalars = [s for s in info["switches"] if s["value_type"] != "boolean"]

        # Build index map for display cross-references
        _bool_idx = {sw["node_id"]: i + 1 for i, sw in enumerate(bools)}

        if bools:
            print(f"\n  CONFIGURABLE SWITCHES ({len(bools)} toggles):")
            print(f"  {'─'*66}")
            for idx, sw in enumerate(bools):
                nid = sw["node_id"]
                state = "ON" if sw["value"] else "OFF"
                label = sw.get("label", "")
                label_str = f"  [{label}]" if label and label != "diagnostic" else ""
                print(f"    [{idx+1}] {nid} = {state}{label_str}")
                compact = _compact_controls(sw["controls"])
                if compact:
                    print(f"        affects: {', '.join(compact[:4])}")
                elif sw.get("label") == "diagnostic":
                    print(f"        affects: diagnostic preview only")
                related = sw.get("related", [])
                if related:
                    ref = ", ".join(f"[{_bool_idx[r]}]" for r in related if r in _bool_idx)
                    print(f"        ⚠ related: {ref} — shared targets, consider changing together")

            # Detect same-state conflicts only for DIRECT pairs
            # (booleans with identical meaningful target sets, not just partial overlap)
            _seen_pairs = set()
            _conflicts = []
            for sw in bools:
                my_targets = frozenset(c for c in sw["controls"] if "PreviewAny" not in c)
                for rnid in sw.get("related", []):
                    pair_key = tuple(sorted([sw["node_id"], rnid]))
                    if pair_key in _seen_pairs:
                        continue
                    _seen_pairs.add(pair_key)
                    partner = next((b for b in bools if b["node_id"] == rnid), None)
                    if not partner:
                        continue
                    partner_targets = frozenset(c for c in partner["controls"] if "PreviewAny" not in c)
                    # Only warn if targets are identical (true complementary pair)
                    if my_targets == partner_targets and sw["value"] == partner["value"]:
                        i1, i2 = _bool_idx[sw["node_id"]], _bool_idx[rnid]
                        state = "ON" if sw["value"] else "OFF"
                        _conflicts.append((i1, i2, state))
            if _conflicts:
                print(f"\n  ⚠ SAME-STATE WARNING:")
                for i1, i2, state in _conflicts:
                    print(f"    Toggles [{i1}] and [{i2}] are both {state} — normally one ON, one OFF")

            print(f"\n  Toggle: --override '{{\"node_id\": {{\"value\": true}}}}' or false")
            example_nid = bools[0]["node_id"]
            print(f"  Example: --override '{{\"{example_nid}\": {{\"value\": false}}}}'")
            has_related = any(sw.get("related") for sw in bools)
            if has_related:
                print(f"  ⚠ Related toggles share downstream targets. When flipping one, flip its pair too.")
            print(f"  ℹ Defaults are author-recommended. Only change on user request.")

        if scalars:
            print(f"\n  CONFIGURABLE VALUES ({len(scalars)} knobs):")
            print(f"  {'─'*66}")
            for idx, sw in enumerate(scalars):
                nid = sw["node_id"]
                val = sw["value"]
                vt = sw["value_type"]
                label = sw.get("label", "")
                label_str = f"  [{label}]" if label else ""
                print(f"    [{idx+1}] {nid} = {val} ({vt}){label_str}")
                compact = _compact_controls(sw["controls"])
                if compact:
                    print(f"        affects: {', '.join(compact[:4])}")
            print(f"\n  Set: --override '{{\"node_id\": {{\"value\": 42}}}}'")

    # ── Node type summary ──
    types = {}
    for nid, nd in info["all_nodes"].items():
        ct = nd["class_type"]
        types[ct] = types.get(ct, 0) + 1
    print(f"\n  ALL NODE TYPES:")
    print(f"  {'─'*66}")
    for ct, count in sorted(types.items()):
        print(f"    {ct} ×{count}")

    print(f"\n  ADVANCED: --override '{{\"node_id\": {{\"input_name\": value}}}}' for any input")
    if wf_path:
        print(f"  WORKFLOW JSON: {wf_path}")
        print(f"  To understand a node's role, read the workflow JSON and search for its id.")
    print()


def _trace_downstream_from_text(all_nodes, text_nid):
    """Find what the text node feeds into (e.g., KSampler positive/negative)."""
    consumers = []
    for nid, nd in all_nodes.items():
        for k, v in nd["inputs"].items():
            if isinstance(v, list) and len(v) == 2 and str(v[0]) == str(text_nid):
                consumers.append(f"{nid}({nd['class_type']}).{k}")
    return ", ".join(consumers[:3]) if consumers else ""


def _infer_input_role(raw_nodes, api_nid, idx, total, media_type):
    """Infer the role of an input node from its title, position, and downstream connections."""
    raw = _find_raw_node(raw_nodes, api_nid)
    if raw and raw.get("title"):
        return raw["title"]
    if total == 1:
        return f"Primary {media_type} input"
    ordinals = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]
    ord_str = ordinals[idx] if idx < len(ordinals) else f"{idx+1}th"
    return f"{ord_str} {media_type} input"


def _inspect_as_json(info, workflow_name, wf_path, title_map, raw_nodes):
    """Output inspection results as machine-readable JSON."""
    result = {
        "workflow": workflow_name,
        "path": wf_path,
        "total_nodes": len(info["all_nodes"]),
        "inputs": {
            "text_prompts": [],
            "image_inputs": [],
            "audio_inputs": [],
            "video_inputs": [],
            "resolution": [],
            "sampler": [],
        },
        "outputs": [],
    }

    for nid, field, val, is_neg in info["text_prompts"]:
        title = title_map.get(nid, None)
        downstream = _trace_downstream_from_text(info["all_nodes"], nid)
        result["inputs"]["text_prompts"].append({
            "node_id": nid, "field": field, "is_negative": is_neg,
            "current_value": val[:200], "title": title,
            "feeds_into": downstream, "set_with": "--prompt" if not is_neg else "--negative",
        })

    for idx, (nid, ct, field, val) in enumerate(info["image_inputs"]):
        title = title_map.get(nid, None)
        role = _infer_input_role(raw_nodes, nid, idx, len(info["image_inputs"]), "image")
        raw = _find_raw_node(raw_nodes, nid)
        ctx = _node_context_summary(raw) if raw else None
        result["inputs"]["image_inputs"].append({
            "node_id": nid, "class_type": ct, "field": field, "current_value": val,
            "position": idx + 1, "title": title, "role": role,
            "json_context": ctx, "set_with": f"--image (position {idx+1})",
        })

    for idx, (nid, ct, field, val) in enumerate(info["audio_inputs"]):
        title = title_map.get(nid, None)
        result["inputs"]["audio_inputs"].append({
            "node_id": nid, "class_type": ct, "field": field, "current_value": val,
            "position": idx + 1, "title": title, "set_with": f"--audio (position {idx+1})",
        })

    for idx, (nid, ct, field, val) in enumerate(info["video_inputs"]):
        title = title_map.get(nid, None)
        result["inputs"]["video_inputs"].append({
            "node_id": nid, "class_type": ct, "field": field, "current_value": val,
            "position": idx + 1, "title": title, "set_with": f"--video (position {idx+1})",
        })

    for nid, ct, w, h in info["resolution"]:
        result["inputs"]["resolution"].append({
            "node_id": nid, "class_type": ct, "width": w, "height": h,
            "set_with": "--width W --height H",
        })

    for nid, ct, params in info["sampler"]:
        result["inputs"]["sampler"].append({
            "node_id": nid, "class_type": ct, "params": params,
            "set_with": "--steps N --cfg F --seed N",
        })

    for idx, (nid, ct, fmt, prefix, upstream) in enumerate(info["outputs"]):
        label = _extract_label_from_prefix(prefix)
        result["outputs"].append({
            "node_id": nid, "class_type": ct, "format": fmt,
            "label": label, "filename_prefix": prefix, "position": idx + 1,
            "upstream_pipeline": [{"node_id": uid, "class_type": uct} for uid, uct in upstream],
        })

    if info["switches"]:
        result["switches"] = []
        for sw in info["switches"]:
            entry = {
                "node_id": sw["node_id"], "class_type": sw["class_type"],
                "value_type": sw["value_type"], "value": sw["value"],
                "field": sw["field"],
                "label": sw.get("label", ""),
                "affects": _compact_controls(sw["controls"]),
                "controls_raw": sw["controls"],
                "set_with": f'--override \'{{"' + sw["node_id"] + '": {{"value": ...}}}}\'',
            }
            if sw.get("related"):
                entry["related"] = sw["related"]
            result["switches"].append(entry)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def validate_inputs(args, info, wf_name):
    """Pre-flight validation: catch common agent mistakes BEFORE submitting to ComfyUI.
    Returns list of (level, message) tuples: 'error' = fatal, 'warning' = proceed with caution."""
    issues = []

    # --- Required inputs ---
    has_image_loaders = len(info["image_inputs"]) > 0
    has_text_nodes = any(not neg for _, _, _, neg in info["text_prompts"])
    has_audio_loaders = len(info["audio_inputs"]) > 0
    has_video_loaders = len(info["video_inputs"]) > 0

    # Workflow needs images but agent didn't provide any
    if has_image_loaders and not args.image:
        issues.append(("error",
            f"Workflow requires {len(info['image_inputs'])} image input(s) but none provided.\n"
            f"  Fix: add --image /path/to/image.jpg\n"
            f"  Hint: run --inspect to see what each image slot expects."))

    # Workflow expects text prompt but agent didn't provide one
    if has_text_nodes and not args.prompt and not args.config:
        issues.append(("warning",
            f"Workflow has positive text node(s) but no --prompt provided.\n"
            f"  The default prompt from the workflow JSON will be used.\n"
            f"  Fix: add --prompt 'your prompt text' if you want custom text."))

    # --- Image count mismatch ---
    if args.image:
        n_provided = len(args.image)
        n_expected = len(info["image_inputs"])
        if n_provided < n_expected:
            issues.append(("error",
                f"Workflow expects {n_expected} image(s) but only {n_provided} provided.\n"
                f"  Loaders: {', '.join(f'{nid} ({ct})' for nid, ct, _, _ in info['image_inputs'])}\n"
                f"  Fix: provide exactly {n_expected} --image argument(s)."))
        elif n_provided > n_expected:
            issues.append(("warning",
                f"Provided {n_provided} images but workflow only has {n_expected} loader(s).\n"
                f"  Extra images will be ignored."))

    # --- File existence ---
    for path_list, media_type in [(args.image, "image"), (args.audio, "audio"), (args.video, "video")]:
        if not path_list:
            continue
        for fpath in path_list:
            if not os.path.exists(fpath):
                issues.append(("error",
                    f"{media_type.title()} file not found: {fpath}\n"
                    f"  Fix: check the path. Use absolute paths from WSL (e.g., /tmp/image.png).\n"
                    f"  Common mistake: using Windows paths (D:\\...) instead of WSL paths."))
            elif os.path.getsize(fpath) == 0:
                issues.append(("error",
                    f"{media_type.title()} file is empty (0 bytes): {fpath}"))

    # --- Override JSON validation ---
    if args.override:
        try:
            overrides = json.loads(args.override)
            if not isinstance(overrides, dict):
                issues.append(("error",
                    f"--override must be a JSON object, got {type(overrides).__name__}.\n"
                    f"  Fix: use format '{{\"node_id\": {{\"input_name\": value}}}}'"))
            else:
                for nid_str, updates in overrides.items():
                    if not isinstance(updates, dict):
                        issues.append(("error",
                            f"Override for node '{nid_str}' must be a dict, got {type(updates).__name__}.\n"
                            f"  Fix: '{{\"node_id\": {{\"input_name\": value}}}}'"))
        except json.JSONDecodeError as e:
            issues.append(("error",
                f"--override is not valid JSON: {e}\n"
                f"  Fix: check quotes and braces. Must be valid JSON.\n"
                f"  Example: --override '{{\"sg146_429\": {{\"value\": 17}}}}'"))

    # --- Resolution bounds ---
    if args.width or args.height:
        is_video = has_video_loaders or any(
            ct in ("VHS_VideoCombine",) for _, ct, _, _, _ in info["outputs"]
        ) or "video" in wf_name.lower() or "wan" in wf_name.lower()
        w = args.width or 640
        h = args.height or 640
        if is_video and (w > 1280 or h > 1280):
            issues.append(("warning",
                f"Resolution {w}×{h} is very large for a video workflow.\n"
                f"  This will likely cause GPU out-of-memory (OOM) errors.\n"
                f"  Recommended: ≤1280 on longest edge for video workflows."))
        elif w > 2160 or h > 2160:
            issues.append(("warning",
                f"Resolution {w}×{h} is very large.\n"
                f"  May cause GPU OOM. Recommended: ≤2160 on longest edge."))

    # --- Switch conflict detection ---
    if info.get("switches"):
        bools = [s for s in info["switches"] if s["value_type"] == "boolean"]
        # Check if overrides would create same-state conflicts
        if args.override:
            try:
                ov = json.loads(args.override)
                for sw in bools:
                    if sw["node_id"] in ov and "value" in ov[sw["node_id"]]:
                        new_val = ov[sw["node_id"]]["value"]
                        my_targets = frozenset(c for c in sw["controls"] if "PreviewAny" not in c)
                        for partner in bools:
                            if partner["node_id"] == sw["node_id"]:
                                continue
                            partner_targets = frozenset(c for c in partner["controls"] if "PreviewAny" not in c)
                            if my_targets != partner_targets:
                                continue
                            # True complementary pair — check conflict
                            partner_val = ov.get(partner["node_id"], {}).get("value", partner["value"])
                            if new_val == partner_val:
                                issues.append(("warning",
                                    f"Switches {sw['node_id']} and {partner['node_id']} are "
                                    f"complementary pair but both set to {new_val}.\n"
                                    f"  Normally one should be ON and the other OFF.\n"
                                    f"  This may cause both pipelines to run (doubled VRAM/time) or undefined output."))
            except (json.JSONDecodeError, TypeError):
                pass  # Override JSON errors already caught above

    return issues


def get_queue_info(server):
    """Get current ComfyUI queue state: running + pending counts and prompt_ids."""
    import urllib.request
    url = f"http://{server}/queue"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        running = data.get("queue_running", [])
        pending = data.get("queue_pending", [])
        return {
            "running_count": len(running),
            "pending_count": len(pending),
            "running": [{"prompt_id": r[1], "index": r[0]} for r in running] if running else [],
            "pending": [{"prompt_id": p[1], "index": p[0]} for p in pending] if pending else [],
        }
    except Exception as e:
        return {"error": str(e)}


def apply_inputs(api_prompt, args, info):
    """Apply user-specified inputs to the API prompt. Returns modified prompt."""
    api = copy.deepcopy(api_prompt)
    server = args.server or COMFY_HOST

    # --- Text prompt ---
    if args.prompt:
        positive_nodes = [
            (nid, field)
            for nid, field, _val, is_neg in info["text_prompts"]
            if not is_neg
        ]
        for nid, field in positive_nodes:
            api[nid]["inputs"][field] = args.prompt

    # --- Negative prompt ---
    if args.negative:
        negative_nodes = [
            (nid, field)
            for nid, field, _val, is_neg in info["text_prompts"]
            if is_neg
        ]
        for nid, field in negative_nodes:
            api[nid]["inputs"][field] = args.negative

    # --- Image inputs ---
    if args.image:
        image_nodes = info["image_inputs"]
        for i, img_path in enumerate(args.image):
            if i >= len(image_nodes):
                print(f"  Warning: More images ({len(args.image)}) than image loader"
                      f" nodes ({len(image_nodes)}). Extra images ignored.")
                break
            nid, ct, field, _old = image_nodes[i]
            server_name = upload_image(server, img_path)
            api[nid]["inputs"][field] = server_name
            print(f"  Uploaded {os.path.basename(img_path)} → node {nid} ({ct})")

    # --- Audio inputs ---
    if args.audio:
        audio_nodes = info["audio_inputs"]
        for i, audio_path in enumerate(args.audio):
            if i >= len(audio_nodes):
                print(f"  Warning: More audio files than audio loader nodes. Extra ignored.")
                break
            nid, ct, field, _old = audio_nodes[i]
            # upload_image works for audio too (same /upload/image endpoint)
            server_name = upload_image(server, audio_path)
            api[nid]["inputs"][field] = server_name
            print(f"  Uploaded {os.path.basename(audio_path)} → node {nid} ({ct})")

    # --- Video inputs ---
    if args.video:
        video_nodes = info["video_inputs"]
        for i, vid_path in enumerate(args.video):
            if i >= len(video_nodes):
                print(f"  Warning: More video files than video loader nodes. Extra ignored.")
                break
            nid, ct, field, _old = video_nodes[i]
            server_name = upload_image(server, vid_path)
            api[nid]["inputs"][field] = server_name
            print(f"  Uploaded {os.path.basename(vid_path)} → node {nid} ({ct})")

    # --- Resolution ---
    if args.width or args.height:
        for nid, ct, old_w, old_h in info["resolution"]:
            if args.width:
                api[nid]["inputs"]["width"] = args.width
            if args.height:
                api[nid]["inputs"]["height"] = args.height

    # --- Sampler settings ---
    if args.steps is not None or args.cfg is not None or args.seed is not None:
        for nid, ct, _params in info["sampler"]:
            if args.steps is not None:
                if "steps" in api[nid]["inputs"]:
                    api[nid]["inputs"]["steps"] = args.steps
            if args.cfg is not None:
                if "cfg" in api[nid]["inputs"]:
                    api[nid]["inputs"]["cfg"] = args.cfg
            if args.seed is not None:
                if "seed" in api[nid]["inputs"]:
                    api[nid]["inputs"]["seed"] = args.seed

    # --- Free-form overrides ---
    if args.override:
        overrides = json.loads(args.override)
        for nid_str, updates in overrides.items():
            if nid_str in api:
                for inp_name, inp_val in updates.items():
                    api[nid_str]["inputs"][inp_name] = inp_val
                    print(f"  Override: node {nid_str}.{inp_name} = {inp_val}")
            else:
                print(f"  Warning: node {nid_str} not found in API prompt, skipping override")

    # --- Config file overrides ---
    if args.config:
        cfg = _load_config_file(args.config)
        if "prompt" in cfg and not args.prompt:
            for nid, field, _val, is_neg in info["text_prompts"]:
                if not is_neg:
                    api[nid]["inputs"][field] = cfg["prompt"]
        if "negative" in cfg and not args.negative:
            for nid, field, _val, is_neg in info["text_prompts"]:
                if is_neg:
                    api[nid]["inputs"][field] = cfg["negative"]
        if "overrides" in cfg:
            for nid_str, updates in cfg["overrides"].items():
                if nid_str in api:
                    for inp_name, inp_val in updates.items():
                        api[nid_str]["inputs"][inp_name] = inp_val

    return api


def _load_config_file(path):
    """Load a YAML or JSON config file."""
    with open(path) as f:
        content = f.read()

    # Try JSON first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try YAML
    try:
        import yaml
        return yaml.safe_load(content)
    except ImportError:
        print("Warning: PyYAML not installed. Config file must be JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)


def ensure_comfyui(server):
    """Make sure ComfyUI is running."""
    import urllib.request
    try:
        urllib.request.urlopen(f"http://{server}/", timeout=3)
        return True
    except Exception:
        pass

    print("ComfyUI not running. Starting via comfy_control.sh ensure ...")
    try:
        result = subprocess.run(
            ["bash", CTRL_SCRIPT, "ensure"],
            capture_output=True, text=True, timeout=200,
        )
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(f"Failed to start ComfyUI:\n{result.stderr}")
            return False
    except FileNotFoundError:
        print(f"Control script not found: {CTRL_SCRIPT}")
        print(f"Please start ComfyUI manually and retry.")
        return False
    except subprocess.TimeoutExpired:
        print("ComfyUI startup timed out (200s)")
        return False


def execute_workflow(server, api_prompt, output_prefix, output_dir, check_ps=False):
    """
    Execute a workflow via WebSocket, monitor progress & errors.
    Returns list of saved output file paths.
    """
    client_id = str(uuid.uuid4())
    ws_url = f"ws://{server}/ws?clientId={client_id}"
    ws = ws_module.WebSocket()
    ws.settimeout(600)  # 10 min max for long video generations
    ws.connect(ws_url)

    # Submit
    res = queue_prompt(server, api_prompt, client_id)
    if "error" in res:
        ws.close()
        print(f"\n  ERROR: ComfyUI rejected the prompt:")
        _print_prompt_error(res)
        return []

    prompt_id = res["prompt_id"]
    print(f"  Queued: {prompt_id}")

    # Collect warnings/errors during execution
    warnings = []
    errors = []
    progress_nodes = set()

    # Monitor execution
    try:
        while True:
            out = ws.recv()
            if isinstance(out, str):
                msg = json.loads(out)
                msg_type = msg.get("type", "")
                data = msg.get("data", {})

                if msg_type == "executing":
                    node_id = data.get("node")
                    if node_id is None and data.get("prompt_id") == prompt_id:
                        print(f"\r  Execution complete.{' '*30}")
                        break
                    elif node_id:
                        node_type = api_prompt.get(str(node_id), {}).get("class_type", "?")
                        progress_nodes.add(node_id)
                        print(f"\r  Executing node {node_id} ({node_type})...{' '*10}", end="", flush=True)

                elif msg_type == "progress":
                    val = data.get("value", 0)
                    mx = data.get("max", 0)
                    pct = int(val / mx * 100) if mx > 0 else 0
                    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                    print(f"\r  Progress: [{bar}] {pct}% ({val}/{mx}){' '*5}", end="", flush=True)

                elif msg_type == "execution_error":
                    errors.append(data)
                    print(f"\n  EXECUTION ERROR: {json.dumps(data, indent=2)[:300]}")
                    break

                elif msg_type == "execution_cached":
                    cached = data.get("nodes", [])
                    if cached:
                        print(f"\r  Cached: {len(cached)} nodes{' '*30}", end="", flush=True)

                elif msg_type == "status":
                    queue_remaining = data.get("status", {}).get("exec_info", {}).get("queue_remaining", 0)
                    if queue_remaining > 1:
                        print(f"\r  Queue position: {queue_remaining}{' '*20}", end="", flush=True)

            elif isinstance(out, bytes):
                # Binary preview data, skip
                pass

    except ws_module.WebSocketTimeoutException:
        errors.append({"message": "WebSocket timeout — generation may still be running on server"})
        print(f"\n  TIMEOUT: WebSocket timed out after 600s")
    finally:
        ws.close()

    # Check PowerShell output for ComfyUI console errors
    ps_warnings = []
    if check_ps:
        ps_warnings = _check_powershell_output()

    # Print diagnostics
    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")
    if ps_warnings:
        print(f"\n  POWERSHELL WARNINGS ({len(ps_warnings)}):")
        for w in ps_warnings:
            print(f"    - {w}")
    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    - {json.dumps(e)[:200]}")
        return []

    # Retrieve outputs
    print(f"  Downloading outputs...")
    import urllib.request
    try:
        history = get_history(server, prompt_id)[prompt_id]
    except Exception as e:
        print(f"  Error fetching history: {e}")
        return []

    # Check for execution status in history
    status = history.get("status", {})
    if status.get("status_str") == "error":
        msgs = status.get("messages", [])
        print(f"\n  EXECUTION FAILED:")
        for m in msgs:
            if isinstance(m, list) and len(m) >= 2:
                print(f"    [{m[0]}] {json.dumps(m[1])[:200]}")
        return []

    saved_files = []
    os.makedirs(output_dir, exist_ok=True)

    output_keys = ["images", "gifs", "videos", "video", "audio", "animated_webp", "files"]
    for node_id, node_output in history.get("outputs", {}).items():
        for key in output_keys:
            if key not in node_output:
                continue
            for item in node_output[key]:
                filename = item.get("filename", item.get("name", ""))
                if not filename:
                    continue
                subfolder = item.get("subfolder", "")
                folder_type = item.get("type", "output")
                try:
                    file_data = download_file(
                        server, filename, subfolder, folder_type
                    )
                    out_path = os.path.join(output_dir, f"{output_prefix}_{filename}")
                    with open(out_path, "wb") as f:
                        f.write(file_data)
                    saved_files.append(out_path)
                    size_mb = len(file_data) / (1024 * 1024)
                    print(f"  Saved: {out_path} ({size_mb:.1f} MB)")
                except Exception as e:
                    print(f"  Error downloading {filename}: {e}")

    if not saved_files:
        # Debug: show what's actually in the history outputs
        all_node_keys = {}
        for node_id, node_output in history.get("outputs", {}).items():
            if node_output:
                all_node_keys[node_id] = list(node_output.keys())
        if all_node_keys:
            print(f"  Debug: history has outputs in nodes: {all_node_keys}")
        else:
            print(f"  Debug: history has no output data (all nodes may have been cached with no new output)")

    return saved_files


def _print_prompt_error(res):
    """Pretty-print a ComfyUI prompt rejection error."""
    err = res.get("error", {})
    print(f"    Type: {err.get('type', '?')}")
    print(f"    Message: {err.get('message', '?')}")
    details = res.get("node_errors", {})
    for nid, nerr in details.items():
        print(f"    Node {nid} ({nerr.get('class_type', '?')}):")
        for e in nerr.get("errors", []):
            print(f"      - [{e.get('type', '?')}] {e.get('message', e)}")
            if e.get("details"):
                print(f"        details: {e['details']}")
            extra = e.get("extra_info", {})
            if extra:
                print(f"        extra: {json.dumps(extra)[:300]}")


def _check_powershell_output():
    """
    Check ComfyUI's Windows-side process for recent errors/warnings.
    Uses PowerShell to query the running process and recent event logs.
    Returns a list of warning/error strings.
    """
    warnings = []
    ps_exe = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

    if not os.path.exists(ps_exe):
        return ["PowerShell not accessible from WSL"]

    # Check if ComfyUI process is alive and get its status
    ps_cmd = r"""
$procs = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like '*ComfyUI*' -or $_.CommandLine -like '*ComfyUI*' -or $_.Path -like '*ComfyUI*'
}
if (-not $procs) {
    $procs = Get-Process -Name python -ErrorAction SilentlyContinue
}
foreach ($p in $procs) {
    $ws = [math]::Round($p.WorkingSet64 / 1MB, 0)
    $cpu = [math]::Round($p.CPU, 1)
    Write-Output "PROC:$($p.Id)|WS=${ws}MB|CPU=${cpu}s|Responding=$($p.Responding)"
    if (-not $p.Responding) {
        Write-Output "WARNING:Process $($p.Id) is NOT responding"
    }
    if ($ws -lt 1000 -and $cpu -gt 300) {
        Write-Output "WARNING:Process $($p.Id) has unusually low memory (${ws}MB) for a long-running process"
    }
}
if (-not $procs) {
    Write-Output "WARNING:No ComfyUI python process found"
}

# Check for recent Windows Application event log errors (last 5 min)
$since = (Get-Date).AddMinutes(-5)
$events = Get-WinEvent -FilterHashtable @{LogName='Application'; Level=1,2; StartTime=$since} -MaxEvents 5 -ErrorAction SilentlyContinue
foreach ($ev in $events) {
    if ($ev.Message -like '*python*' -or $ev.Message -like '*ComfyUI*' -or $ev.Message -like '*CUDA*' -or $ev.Message -like '*GPU*') {
        Write-Output "EVENT_WARNING:$($ev.TimeCreated) - $($ev.Message.Substring(0, [math]::Min(200, $ev.Message.Length)))"
    }
}

# Check GPU status
$gpu = & nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu,utilization.gpu --format=csv,noheader,nounits 2>$null
if ($gpu) {
    Write-Output "GPU:$gpu"
    $parts = $gpu -split ','
    if ($parts.Count -ge 4) {
        $temp = [int]$parts[3].Trim()
        $memUsed = [int]$parts[1].Trim()
        $memTotal = [int]$parts[2].Trim()
        if ($temp -gt 85) {
            Write-Output "WARNING:GPU temperature is ${temp}C (>85C)"
        }
        if ($memUsed / $memTotal -gt 0.95) {
            Write-Output "WARNING:GPU memory nearly full (${memUsed}/${memTotal} MB)"
        }
    }
} else {
    Write-Output "WARNING:nvidia-smi not available or GPU error"
}
"""
    try:
        result = subprocess.run(
            [ps_exe, "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=15,
        )
        output = result.stdout.strip()
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("WARNING:") or line.startswith("EVENT_WARNING:"):
                warnings.append(line)
            elif line.startswith("PROC:"):
                print(f"  PS> {line}")
            elif line.startswith("GPU:"):
                print(f"  PS> {line}")

        if result.stderr.strip():
            # Filter out benign PowerShell noise
            for line in result.stderr.strip().split("\n"):
                line = line.strip()
                if line and "ProgressPreference" not in line:
                    warnings.append(f"PS_STDERR: {line[:200]}")

    except subprocess.TimeoutExpired:
        warnings.append("PowerShell check timed out (15s)")
    except Exception as e:
        warnings.append(f"PowerShell check failed: {e}")

    return warnings


# ── Main ───────────────────────────────────────────────────────────────────


def build_parser():
    p = argparse.ArgumentParser(
        description="Universal ComfyUI Workflow Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list
  %(prog)s -w image_qwen_Image_2512 --inspect
  %(prog)s -w image_qwen_Image_2512 --prompt "a cat wearing a top hat"
  %(prog)s -w image_qwen_image_edit_2511 --prompt "change bg to beach" --image photo.jpg
  %(prog)s -w "WAN 2.2 Smooth Workflow v3.0 (audio)" --image face.jpg --audio speech.wav
  %(prog)s -w video_hunyuan_video_1.5_720p_i2v --prompt "person walks" --image start.jpg
  %(prog)s -w 5 --prompt "test" --steps 10 --seed 42
  %(prog)s -w qwen_2512 --prompt "test" --override '{"180":{"text":"custom prompt"}}'
  %(prog)s -w qwen_2512 --config my_inputs.yaml
        """,
    )

    p.add_argument("--list", action="store_true", help="List all available workflows")
    p.add_argument("-w", "--workflow", help="Workflow name, index, partial match, or path")
    p.add_argument("--inspect", action="store_true", help="Show customizable inputs (don't run)")
    p.add_argument("--inspect-json", action="store_true",
                   help="Inspect workflow and output machine-readable JSON")
    p.add_argument("--dry-run", action="store_true", help="Convert to API format and print (don't run)")
    p.add_argument("--queue", action="store_true",
                   help="Submit to ComfyUI queue and return immediately (print prompt_id)")
    p.add_argument("--status", nargs="*", metavar="PROMPT_ID",
                   help="Check job status. No args = show queue. With prompt_ids = check specific jobs.")
    p.add_argument("--no-validate", action="store_true",
                   help="Skip input validation (not recommended)")

    # Input customization
    inp = p.add_argument_group("Input customization")
    inp.add_argument("--prompt", "-p", help="Text prompt (sets all positive text nodes)")
    inp.add_argument("--negative", "-n", help="Negative prompt (sets all negative text nodes)")
    inp.add_argument("--image", "-i", nargs="+", help="Input image(s) for LoadImage nodes")
    inp.add_argument("--audio", "-a", nargs="+", help="Input audio file(s) for LoadAudio nodes")
    inp.add_argument("--video", "-v", nargs="+", help="Input video file(s) for LoadVideo nodes")

    # Generation settings
    gen = p.add_argument_group("Generation settings")
    gen.add_argument("--width", "-W", type=int, help="Output width")
    gen.add_argument("--height", "-H", type=int, help="Output height")
    gen.add_argument("--steps", type=int, help="Sampling steps")
    gen.add_argument("--cfg", type=float, help="CFG scale")
    gen.add_argument("--seed", type=int, help="Random seed (for reproducibility)")
    gen.add_argument("--extend-steps", type=int, metavar="N",
                     help="Number of SVI extension steps to enable (SVI-28 workflow)")

    # Advanced
    adv = p.add_argument_group("Advanced")
    adv.add_argument("--override", help="JSON: {node_id: {input_name: value}} for arbitrary overrides")
    adv.add_argument("--config", help="YAML/JSON config file with inputs")
    adv.add_argument("--server", default=None, help=f"ComfyUI server (default: {COMFY_HOST})")
    adv.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT, help="Output directory")
    adv.add_argument("--output-prefix", default=None, help="Output filename prefix")
    adv.add_argument("--no-ensure", action="store_true", help="Skip auto-starting ComfyUI")
    adv.add_argument("--check-ps", action="store_true",
                     help="Check PowerShell/GPU status for errors/warnings")

    return p


def _collect_finished_outputs(server, prompt_ids, output_dir, output_prefix=None):
    """Check history for finished jobs and download their outputs.
    Returns dict: {prompt_id: {"status": str, "files": list, "error": str|None}}"""
    results = {}
    for pid in prompt_ids:
        try:
            hist = get_history(server, pid)
        except Exception as e:
            results[pid] = {"status": "unknown", "files": [], "error": str(e)}
            continue

        if pid not in hist:
            results[pid] = {"status": "pending", "files": [], "error": None}
            continue

        entry = hist[pid]
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            msgs = status.get("messages", [])
            err_text = "; ".join(
                f"[{m[0]}] {json.dumps(m[1])[:150]}"
                for m in msgs if isinstance(m, list) and len(m) >= 2
            )
            results[pid] = {"status": "error", "files": [], "error": err_text}
            continue

        # Completed — download outputs
        saved = []
        os.makedirs(output_dir, exist_ok=True)
        prefix = output_prefix or f"job_{pid[:8]}"
        output_keys = ["images", "gifs", "videos", "video", "audio", "animated_webp", "files"]
        for node_id, node_output in entry.get("outputs", {}).items():
            for key in output_keys:
                if key not in node_output:
                    continue
                for item in node_output[key]:
                    filename = item.get("filename", item.get("name", ""))
                    if not filename:
                        continue
                    subfolder = item.get("subfolder", "")
                    folder_type = item.get("type", "output")
                    out_path = os.path.join(output_dir, f"{prefix}_{filename}")
                    if os.path.exists(out_path):
                        saved.append(out_path)
                        continue  # Already downloaded
                    try:
                        file_data = download_file(server, filename, subfolder, folder_type)
                        with open(out_path, "wb") as f:
                            f.write(file_data)
                        saved.append(out_path)
                    except Exception as e:
                        print(f"  Error downloading {filename} for {pid[:8]}: {e}")

        if saved:
            results[pid] = {"status": "completed", "files": saved, "error": None}
        else:
            results[pid] = {"status": "completed", "files": [], "error": "No output files found in history"}

    return results


def main():
    parser = build_parser()
    args = parser.parse_args()
    server = args.server or COMFY_HOST

    # ── List mode ──
    if args.list:
        list_workflows()
        return

    # ── Status mode: check queue and/or specific jobs ──
    if args.status is not None:
        if not args.no_ensure:
            if not ensure_comfyui(server):
                sys.exit(1)

        # Show queue state
        q = get_queue_info(server)
        if "error" in q:
            print(f"  Error checking queue: {q['error']}")
            sys.exit(1)

        print(f"\n  ComfyUI Queue Status:")
        print(f"    Running: {q['running_count']}")
        print(f"    Pending: {q['pending_count']}")
        if q["running"]:
            for r in q["running"]:
                print(f"      [running] {r['prompt_id']}")
        if q["pending"]:
            for p in q["pending"]:
                print(f"      [pending] {p['prompt_id']}")

        # If specific prompt_ids given, check + download their outputs
        if args.status:
            output_dir = args.output_dir
            print(f"\n  Checking {len(args.status)} job(s)...")
            results = _collect_finished_outputs(server, args.status, output_dir)
            n_done = 0
            n_err = 0
            n_pending = 0
            for pid, res in results.items():
                status_str = res["status"]
                if status_str == "completed" and res["files"]:
                    n_done += 1
                    print(f"    ✓ {pid[:12]} — completed, {len(res['files'])} output(s):")
                    for fp in res["files"]:
                        print(f"        {fp}")
                elif status_str == "completed":
                    n_done += 1
                    print(f"    ✓ {pid[:12]} — completed (outputs already downloaded or none)")
                elif status_str == "error":
                    n_err += 1
                    print(f"    ✗ {pid[:12]} — error: {res['error']}")
                elif status_str == "pending":
                    n_pending += 1
                    print(f"    … {pid[:12]} — still running/pending")
                else:
                    n_pending += 1
                    print(f"    ? {pid[:12]} — {status_str}: {res.get('error', '')}")

            print(f"\n  Summary: {n_done} done, {n_pending} pending, {n_err} errors")
            if n_pending > 0:
                print(f"  Tip: re-run --status with the same prompt_ids to check again later.")
        elif q["running_count"] == 0 and q["pending_count"] == 0:
            print(f"\n  Queue is empty — all jobs finished.")
        print()
        return

    # ── Require workflow for all other modes ──
    if not args.workflow:
        parser.print_help()
        return

    # ── Resolve workflow ──
    wf_list = discover_workflows()
    wf_path = find_workflow(args.workflow, wf_list)
    wf_name = os.path.basename(wf_path)
    is_queue_mode = getattr(args, 'queue', False)
    # In JSON mode or queue mode, progress messages → stderr to keep stdout clean
    _log = (lambda *a, **kw: print(*a, file=sys.stderr, **kw)) if getattr(args, 'inspect_json', False) else print
    _log(f"Workflow: {wf_name}")
    _log(f"Path: {wf_path}")

    # ── Ensure ComfyUI is running ──
    if not args.no_ensure and not args.dry_run and not args.inspect_json:
        if not ensure_comfyui(server):
            sys.exit(1)

    # ── Load and convert workflow ──
    _log("Loading workflow...")
    wf_raw = load_workflow(wf_path)
    if args.extend_steps is not None:
        wf_raw = apply_extend_steps(wf_raw, args.extend_steps)
    wf_raw = resolve_virtual_wires(wf_raw)
    wf_raw = strip_bypassed_nodes(wf_raw)

    _log("Fetching object_info from ComfyUI...")
    try:
        obj_info = get_object_info(server)
    except Exception as e:
        if args.dry_run or args.inspect or args.inspect_json:
            _log(f"  Warning: Cannot reach ComfyUI ({e}). Using limited inspection.")
            obj_info = None
        else:
            print(f"  Error: Cannot reach ComfyUI at {server}: {e}")
            sys.exit(1)

    if obj_info:
        _log("Converting LiteGraph → API format...")
        api_prompt = litegraph_to_api(wf_raw, object_info=obj_info)
    else:
        # Fallback: check if already API format
        if "nodes" not in wf_raw:
            api_prompt = wf_raw
        else:
            print("Cannot convert LiteGraph format without ComfyUI object_info.")
            sys.exit(1)

    # Resolve %date:...% patterns (frontend-only, not handled by API server)
    api_prompt = _resolve_date_patterns(api_prompt)

    # ── Inspect ──
    info = inspect_workflow(api_prompt)

    if args.inspect or args.inspect_json:
        print_inspect(info, wf_name, wf_path=wf_path, as_json=args.inspect_json)
        return

    if args.dry_run:
        api_prompt = apply_inputs(api_prompt, args, info)
        print(json.dumps(api_prompt, indent=2, ensure_ascii=False))
        return

    # ── Pre-flight validation ──
    if not getattr(args, 'no_validate', False):
        issues = validate_inputs(args, info, wf_name)
        errors = [msg for level, msg in issues if level == "error"]
        warnings = [msg for level, msg in issues if level == "warning"]
        if warnings:
            print(f"\n  ⚠ VALIDATION WARNINGS ({len(warnings)}):")
            for i, w in enumerate(warnings, 1):
                print(f"    {i}. {w}")
        if errors:
            print(f"\n  ✗ VALIDATION ERRORS ({len(errors)}):")
            for i, e in enumerate(errors, 1):
                print(f"    {i}. {e}")
            print(f"\n  Aborting. Fix the errors above and retry.")
            print(f"  To skip validation (not recommended): add --no-validate")
            sys.exit(1)
        if warnings:
            print()  # Visual separator after warnings

    # ── Apply user inputs ──
    print("Applying inputs...")
    api_prompt = apply_inputs(api_prompt, args, info)

    # ── Determine output prefix ──
    if args.output_prefix:
        prefix = args.output_prefix
    else:
        base = os.path.splitext(wf_name)[0]
        # Clean up for filesystem
        prefix = re.sub(r'[^\w\-.]', '_', base)[:40]
        prefix = f"{prefix}_{int(time.time()) % 100000}"

    # ── Queue-only mode: submit and return immediately ──
    if is_queue_mode:
        client_id = str(uuid.uuid4())
        res = queue_prompt(server, api_prompt, client_id)
        if "error" in res:
            print(f"\n  ERROR: ComfyUI rejected the prompt:")
            _print_prompt_error(res)
            sys.exit(1)
        prompt_id = res["prompt_id"]
        q = get_queue_info(server)
        queue_depth = q.get("running_count", 0) + q.get("pending_count", 0)
        print(f"\n  QUEUED: {prompt_id}")
        print(f"  Workflow: {wf_name}")
        print(f"  Queue depth: {queue_depth} job(s)")
        print(f"  Output dir: {args.output_dir}")
        print(f"  Output prefix: {prefix}")
        print(f"\n  To check status:  $VENV $SCRIPT --status {prompt_id} -o {args.output_dir}")
        print(f"  To check queue:   $VENV $SCRIPT --status")
        # Machine-readable line for agent to parse
        print(f"\n  PROMPT_ID={prompt_id}")
        return 0

    # ── Execute (blocking: wait for completion via WebSocket) ──
    print(f"\nExecuting workflow: {wf_name}")
    print(f"Output dir: {args.output_dir}")
    print(f"Output prefix: {prefix}")
    print(f"Server: {server}")
    print(f"{'─'*60}")

    # Pre-execution PowerShell check
    if args.check_ps:
        print("\nPre-execution system check:")
        pre_warnings = _check_powershell_output()
        if pre_warnings:
            print(f"  Pre-run warnings: {len(pre_warnings)}")
            for w in pre_warnings:
                print(f"    - {w}")
            print()

    files = execute_workflow(
        server, api_prompt, prefix, args.output_dir, check_ps=args.check_ps
    )

    # Post-execution PowerShell check
    if args.check_ps:
        print("\nPost-execution system check:")
        post_warnings = _check_powershell_output()
        if post_warnings:
            print(f"  Post-run warnings: {len(post_warnings)}")
            for w in post_warnings:
                print(f"    - {w}")

    # ── Summary ──
    print(f"\n{'='*60}")
    if files:
        print(f"  SUCCESS: {len(files)} output(s) saved:")
        for f in files:
            print(f"    {f}")
    else:
        print("  NO OUTPUTS generated. Check errors above.")
    print(f"{'='*60}\n")

    return 0 if files else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
