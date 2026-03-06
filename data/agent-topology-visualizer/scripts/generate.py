#!/usr/bin/env python3
"""Agent Topology Generator — Creates interactive SVG architecture diagrams from JSON topology definitions.

Usage:
    python3 generate.py topology.json -o output.html [--format html|svg|paths]

Zero external dependencies. Python 3.8+.
"""

import json
import math
import argparse
import sys
import os
import random
import html as html_mod
import re


def sanitize_css(css_text: str) -> str:
    """Strip XSS vectors from user-provided CSS.
    
    Removes </style> tags, <script> tags, javascript: URIs,
    expression() calls, and @import rules that could escape
    the style block or execute code.
    """
    if not css_text:
        return ""
    # Remove anything that closes the style tag
    css_text = re.sub(r'<\s*/\s*style\s*>', '', css_text, flags=re.IGNORECASE)
    # Remove script tags
    css_text = re.sub(r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', '', css_text, flags=re.IGNORECASE | re.DOTALL)
    css_text = re.sub(r'<\s*script[^>]*>', '', css_text, flags=re.IGNORECASE)
    # Remove HTML tags entirely
    css_text = re.sub(r'<[^>]+>', '', css_text)
    # Remove javascript: URIs
    css_text = re.sub(r'javascript\s*:', '', css_text, flags=re.IGNORECASE)
    # Remove expression() (IE CSS XSS vector)
    css_text = re.sub(r'expression\s*\(', '/**/(', css_text, flags=re.IGNORECASE)
    # Remove @import (can load external resources)
    css_text = re.sub(r'@import\b', '/* @import blocked */', css_text, flags=re.IGNORECASE)
    return css_text


# ─── DEFAULTS ───

DEFAULT_VIEWBOX = [1220, 1000]
DEFAULT_ACCENT = "#5d9b93"
DEFAULT_BG = "#0a0e14"
DEFAULT_TEXT = "#c8d6e0"
DEFAULT_FONT = "Inter, system-ui, sans-serif"

RADIUS_DEFAULTS = {
    "orchestrator": 58, "agent": 32, "system": 44,
    "pipeline": 25, "ops": 25, "human": 38
}

ZONE_POSITIONS = {
    "center":       (0.50, 0.48),
    "top-left":     (0.18, 0.15),
    "top-right":    (0.82, 0.15),
    "left":         (0.12, 0.48),
    "right":        (0.88, 0.48),
    "bottom-left":  (0.18, 0.82),
    "bottom-right": (0.82, 0.82),
    "bottom":       (0.50, 0.85),
    "top":          (0.50, 0.12),
}

CONN_STYLES = {
    "hub":     {"cls": "conn-hub",     "opacity": 0.35, "width": 2.0, "dash": "", "curve": 0.15},
    "core":    {"cls": "conn-core",    "opacity": 0.25, "width": 1.5, "dash": "", "curve": 0.18},
    "cross":   {"cls": "conn-cross",   "opacity": 0.18, "width": 1.2, "dash": "", "curve": 0.22},
    "cluster": {"cls": "conn-cluster", "opacity": 0.30, "width": 1.5, "dash": "", "curve": 0.12},
    "sys":     {"cls": "conn-sys",     "opacity": 0.15, "width": 1.0, "dash": "4,4", "curve": 0.20},
}


# ─── GEOMETRY ───

def edge_point(cx, cy, r, tx, ty):
    """Point on circle perimeter facing target."""
    dx, dy = tx - cx, ty - cy
    dist = math.sqrt(dx*dx + dy*dy)
    if dist == 0:
        return cx, cy
    return cx + r * dx / dist, cy + r * dy / dist


def curve_control_points(x1, y1, x2, y2, curvature, vb_cx, vb_cy):
    """Cubic bezier control points that arc outward from viewbox center."""
    mx, my = (x1+x2)/2, (y1+y2)/2
    dx, dy = x2-x1, y2-y1
    dist = math.sqrt(dx*dx + dy*dy)
    if dist == 0:
        return x1, y1, x2, y2
    nx = -dy / dist * curvature * dist
    ny = dx / dist * curvature * dist
    # Pick direction pushing outward from center
    d1 = math.sqrt((mx+nx - vb_cx)**2 + (my+ny - vb_cy)**2)
    d2 = math.sqrt((mx-nx - vb_cx)**2 + (my-ny - vb_cy)**2)
    if d2 > d1:
        nx, ny = -nx, -ny
    c1x = x1 + dx*0.3 + nx*0.8
    c1y = y1 + dy*0.3 + ny*0.8
    c2x = x1 + dx*0.7 + nx*0.8
    c2y = y1 + dy*0.7 + ny*0.8
    return c1x, c1y, c2x, c2y


# ─── AUTO-LAYOUT ───

def auto_layout(nodes, vb_w, vb_h):
    """Assign positions to nodes missing explicit coordinates."""
    zones = {}
    for n in nodes:
        if n.get("position"):
            continue
        zone = n.get("zone", "center")
        zones.setdefault(zone, []).append(n)

    for zone, group in zones.items():
        base = ZONE_POSITIONS.get(zone, (0.5, 0.5))
        cx, cy = base[0] * vb_w, base[1] * vb_h
        count = len(group)
        if count == 1:
            group[0]["position"] = [cx, cy]
        else:
            for i, n in enumerate(group):
                angle = 2 * math.pi * i / count - math.pi/2
                spread = min(vb_w, vb_h) * 0.08 * min(count, 6)
                n["position"] = [
                    cx + spread * math.cos(angle),
                    cy + spread * math.sin(angle)
                ]


# ─── PARSING ───

def load_topology(path):
    """Load and validate topology JSON."""
    with open(path) as f:
        topo = json.load(f)

    # Defaults
    topo.setdefault("title", "Agent Topology")
    topo.setdefault("theme", "dark")
    topo.setdefault("viewBox", DEFAULT_VIEWBOX)
    topo.setdefault("colors", {})
    topo.setdefault("font", DEFAULT_FONT)
    topo.setdefault("nodes", [])
    topo.setdefault("connections", [])
    topo.setdefault("pipelines", {})
    topo.setdefault("background", {})

    # Handle pipelines as list (single unnamed pipeline)
    if isinstance(topo["pipelines"], list):
        topo["pipelines"] = {"default": topo["pipelines"]}

    # Validate node IDs
    node_ids = set()
    for n in topo["nodes"]:
        if "id" not in n or "name" not in n:
            print(f"Warning: Node missing id or name: {n}", file=sys.stderr)
            continue
        n.setdefault("type", "agent")
        n.setdefault("radius", RADIUS_DEFAULTS.get(n["type"], 32))
        n.setdefault("emoji", "")
        n.setdefault("subtitle", "")
        node_ids.add(n["id"])

    # Validate connections
    for c in topo["connections"]:
        c.setdefault("type", "core")
        if c["from"] not in node_ids:
            print(f"Warning: Connection source '{c['from']}' not found in nodes", file=sys.stderr)
        if c["to"] not in node_ids:
            print(f"Warning: Connection target '{c['to']}' not found in nodes", file=sys.stderr)

    return topo


# ─── SVG GENERATION ───

def generate_paths(topo, node_map):
    """Generate SVG path elements for connections."""
    vb = topo["viewBox"]
    vb_cx, vb_cy = vb[0] * 0.48, vb[1] * 0.45
    lines = []

    for i, conn in enumerate(topo["connections"]):
        src_id, tgt_id = conn["from"], conn["to"]
        if src_id not in node_map or tgt_id not in node_map:
            continue
        src, tgt = node_map[src_id], node_map[tgt_id]
        sx, sy = src["position"]
        tx, ty = tgt["position"]
        sr, tr = src["radius"], tgt["radius"]

        ex1, ey1 = edge_point(sx, sy, sr, tx, ty)
        ex2, ey2 = edge_point(tx, ty, tr, sx, sy)

        style = CONN_STYLES.get(conn["type"], CONN_STYLES["core"])
        c1x, c1y, c2x, c2y = curve_control_points(ex1, ey1, ex2, ey2, style["curve"], vb_cx, vb_cy)

        cls = style["cls"]
        d = f"M {ex1:.0f},{ey1:.0f} C {c1x:.0f},{c1y:.0f} {c2x:.0f},{c2y:.0f} {ex2:.0f},{ey2:.0f}"
        lines.append(f'<path class="{cls}" data-conn="{i}" data-src="{src_id}" data-tgt="{tgt_id}" d="{d}"/>')

    return lines


def generate_node_svg(node):
    """Generate SVG elements for a single node."""
    nid = node["id"]
    ntype = node["type"]
    x, y = node["position"]
    r = node["radius"]
    emoji = html_mod.escape(node.get("emoji", ""))
    name = html_mod.escape(node["name"])
    subtitle = html_mod.escape(node.get("subtitle", ""))

    if ntype == "orchestrator":
        return f'''<g data-nid="{nid}" data-name="{name}" data-desc="{subtitle}" class="orch-group" style="cursor:pointer">
    <circle class="pulse-ring" cx="{x}" cy="{y}" r="{r}"/>
    <circle class="pulse-ring pr2" cx="{x}" cy="{y}" r="{r}"/>
    <circle class="pulse-ring pr3" cx="{x}" cy="{y}" r="{r}"/>
    <circle class="orch-outer" cx="{x}" cy="{y}" r="{r}"/>
    <circle class="orch-inner" cx="{x}" cy="{y}" r="{int(r*0.72)}"/>
    <text class="lbl-emoji" x="{x}" y="{y-13}" font-size="22">{emoji}</text>
    <text class="lbl-orch-name" x="{x}" y="{y+10}">{name}</text>
    <text class="lbl-orch-sub" x="{x}" y="{y+25}">{subtitle}</text>
</g>'''
    elif ntype == "system":
        return f'''<g class="sys-node" data-nid="{nid}" data-name="{name}" data-desc="{subtitle}" transform="translate({x:.0f},{y:.0f})">
    <circle class="sys-circle" r="{r}"/>
    <text class="lbl-emoji" font-size="17" y="-10">{emoji}</text>
    <text class="lbl-main" y="8">{name}</text>
    <text class="lbl-sub" y="20">{subtitle}</text>
</g>'''
    elif ntype == "agent":
        return f'''<g class="agent-node" data-nid="{nid}" data-name="{name}" data-desc="{subtitle}" transform="translate({x:.0f},{y:.0f})">
    <circle class="agent-circle" r="{r}"/>
    <text class="lbl-emoji" font-size="13" y="-7">{emoji}</text>
    <text class="lbl-main" font-size="10" y="7">{name}</text>
    <text class="lbl-sub" y="19">{subtitle}</text>
</g>'''
    elif ntype == "human":
        return f'''<g class="human-node" data-nid="{nid}" data-name="{name}" data-desc="{subtitle}" transform="translate({x:.0f},{y:.0f})">
    <circle class="human-circle" r="{r}"/>
    <text class="lbl-emoji" font-size="17" y="-10">{emoji}</text>
    <text class="lbl-main" y="8">{name}</text>
    <text class="lbl-sub" y="20">{subtitle}</text>
</g>'''
    else:  # pipeline, ops
        circle_cls = "pipe-circle" if ntype == "pipeline" else "ops-circle"
        return f'''<g class="small-node" data-nid="{nid}" data-name="{name}" data-desc="{subtitle}" transform="translate({x:.0f},{y:.0f})">
    <circle class="{circle_cls}" r="{r}"/>
    <text class="lbl-emoji" font-size="11" y="-6">{emoji}</text>
    <text class="lbl-sm" y="7">{name}</text>
    <text class="lbl-sm-sub" y="17">{subtitle}</text>
</g>'''


def generate_svg(topo, node_map):
    """Generate complete SVG content."""
    vb = topo["viewBox"]
    paths = generate_paths(topo, node_map)

    # Render nodes in order: systems, small nodes, agents, humans, orchestrators (on top)
    type_order = ["system", "pipeline", "ops", "agent", "human", "orchestrator"]
    ordered_nodes = []
    for t in type_order:
        for n in topo["nodes"]:
            if n["type"] == t:
                ordered_nodes.append(n)

    node_svgs = [generate_node_svg(n) for n in ordered_nodes]

    # Glow gradient for orchestrator
    accent = topo["colors"].get("accent", DEFAULT_ACCENT)
    glow = f'''<defs>
    <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="{accent}" stop-opacity="0.06"/>
        <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
</defs>'''

    # Find orchestrator center for glow ellipse
    orch_nodes = [n for n in topo["nodes"] if n["type"] == "orchestrator"]
    glow_ellipse = ""
    if orch_nodes:
        ox, oy = orch_nodes[0]["position"]
        glow_ellipse = f'<ellipse cx="{ox:.0f}" cy="{oy:.0f}" rx="{vb[0]*0.4:.0f}" ry="{vb[1]*0.45:.0f}" fill="url(#centerGlow)"/>'

    svg = f'''<svg class="arch-svg" viewBox="0 0 {vb[0]} {vb[1]}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html_mod.escape(topo['title'])}">
{glow}
{glow_ellipse}
<!-- Connections -->
{chr(10).join(paths)}
<!-- Nodes -->
{chr(10).join(node_svgs)}
</svg>'''
    return svg


# ─── CSS ───

def generate_css(topo):
    """Generate themed CSS."""
    theme = topo.get("theme", "dark")
    c = topo.get("colors", {})
    accent = c.get("accent", DEFAULT_ACCENT)
    bg = c.get("background", DEFAULT_BG if theme == "dark" else "#f5f5f5")
    text = c.get("text", DEFAULT_TEXT if theme == "dark" else "#1a1a2e")
    stroke = c.get("nodeStroke", f"rgba(93,155,147,0.4)" if theme == "dark" else "rgba(93,155,147,0.6)")
    font = topo.get("font", DEFAULT_FONT)

    # Compute derived colors
    if theme == "dark":
        bg2 = "#0d1117"
        muted = "rgba(200,214,224,0.5)"
        dim_text = "rgba(200,214,224,0.35)"
        conn_color = accent
        node_fill_sys = "rgba(93,155,147,0.08)"
        node_fill_agent = "rgba(93,155,147,0.12)"
        node_fill_pipe = "rgba(93,155,147,0.14)"
        node_fill_ops = "rgba(93,155,147,0.06)"
        node_fill_human = "rgba(93,155,147,0.10)"
        orch_outer = "rgba(93,155,147,0.25)"
        orch_inner = "rgba(93,155,147,0.12)"
        legend_bg = "rgba(10,14,20,0.7)"
    else:
        bg2 = "#eaeaea"
        muted = "rgba(40,60,70,0.5)"
        dim_text = "rgba(40,60,70,0.35)"
        conn_color = "#3d7b73"
        node_fill_sys = "rgba(93,155,147,0.12)"
        node_fill_agent = "rgba(93,155,147,0.16)"
        node_fill_pipe = "rgba(93,155,147,0.18)"
        node_fill_ops = "rgba(93,155,147,0.10)"
        node_fill_human = "rgba(93,155,147,0.14)"
        orch_outer = "rgba(93,155,147,0.35)"
        orch_inner = "rgba(93,155,147,0.18)"
        legend_bg = "rgba(245,245,245,0.8)"

    return f'''* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: {bg}; color: {text}; font-family: {font}; min-height: 100vh; }}
.topo-container {{ max-width: 1400px; margin: 0 auto; padding: 2rem 1rem; }}
.topo-title {{ text-align: center; font-size: 1.6rem; font-weight: 600; color: {accent}; margin-bottom: 1.5rem; letter-spacing: 0.02em; }}
.arch-svg {{ width: 100%; height: auto; display: block; }}
.arch-svg path {{ fill: none; stroke: {conn_color}; stroke-linecap: round; transition: opacity 0.3s, stroke-width 0.3s; }}
.conn-hub {{ stroke-opacity: 0.35; stroke-width: 2; }}
.conn-core {{ stroke-opacity: 0.25; stroke-width: 1.5; }}
.conn-cross {{ stroke-opacity: 0.18; stroke-width: 1.2; }}
.conn-cluster {{ stroke-opacity: 0.30; stroke-width: 1.5; }}
.conn-sys {{ stroke-opacity: 0.15; stroke-width: 1; stroke-dasharray: 4,4; }}

/* Node styles */
.sys-circle {{ fill: {node_fill_sys}; stroke: {stroke}; stroke-width: 1.5; }}
.agent-circle {{ fill: {node_fill_agent}; stroke: {accent}; stroke-width: 1.5; }}
.pipe-circle {{ fill: {node_fill_pipe}; stroke: {accent}; stroke-opacity: 0.7; stroke-width: 1.2; }}
.ops-circle {{ fill: {node_fill_ops}; stroke: {stroke}; stroke-width: 1; }}
.human-circle {{ fill: {node_fill_human}; stroke: {accent}; stroke-width: 1.5; }}
.orch-outer {{ fill: {orch_outer}; stroke: {accent}; stroke-width: 2.5; }}
.orch-inner {{ fill: {orch_inner}; stroke: {accent}; stroke-opacity: 0.5; stroke-width: 1; }}

/* Labels */
.lbl-emoji {{ text-anchor: middle; dominant-baseline: central; pointer-events: none; }}
.lbl-main {{ text-anchor: middle; font-size: 11px; fill: {text}; font-weight: 500; pointer-events: none; }}
.lbl-sub {{ text-anchor: middle; font-size: 8px; fill: {dim_text}; pointer-events: none; }}
.lbl-sm {{ text-anchor: middle; font-size: 9px; fill: {muted}; font-weight: 500; pointer-events: none; }}
.lbl-sm-sub {{ text-anchor: middle; font-size: 7px; fill: {dim_text}; pointer-events: none; }}
.lbl-orch-name {{ text-anchor: middle; font-size: 16px; fill: {accent}; font-weight: 700; letter-spacing: 0.04em; pointer-events: none; }}
.lbl-orch-sub {{ text-anchor: middle; font-size: 8px; fill: {muted}; letter-spacing: 0.15em; text-transform: uppercase; pointer-events: none; }}

/* Pulse animation for orchestrator */
.pulse-ring {{ fill: none; stroke: {accent}; stroke-width: 1.5; opacity: 0; animation: pulse 4s ease-out infinite; }}
.pr2 {{ animation-delay: 1.3s; }}
.pr3 {{ animation-delay: 2.6s; }}
@keyframes pulse {{
    0% {{ r: inherit; opacity: 0.5; stroke-width: 2; }}
    100% {{ r: calc(inherit + 40px); opacity: 0; stroke-width: 0.5; }}
}}

/* Node cursor */
[data-nid] {{ cursor: pointer; }}

/* Hover highlight system */
.arch-svg.has-hover path {{ opacity: 0.08; transition: opacity 0.3s; }}
.arch-svg.has-hover path.hl {{ opacity: 1; stroke-opacity: 0.7; stroke-width: 2.5; }}
.arch-svg.has-hover g {{ opacity: 0.2; transition: opacity 0.3s; }}
.arch-svg.has-hover g.hl {{ opacity: 1; }}
.arch-svg.has-hover .orch-group {{ opacity: 0.4; }}
.arch-svg.has-hover .orch-group.hl {{ opacity: 1; }}
.arch-svg.has-hover .pulse-ring {{ opacity: 0 !important; }}

/* Tooltip */
.arch-tip {{ position: fixed; background: {"rgba(13,17,23,0.95)" if theme == "dark" else "rgba(255,255,255,0.95)"}; color: {text}; padding: 6px 12px; border-radius: 6px; font-size: 13px; pointer-events: none; opacity: 0; transition: opacity 0.15s; z-index: 100; border: 1px solid {stroke}; white-space: nowrap; }}
.arch-tip.show {{ opacity: 1; }}

/* Legend */
.arch-legend {{ display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; margin-top: 1.5rem; padding: 0.8rem 1.2rem; background: {legend_bg}; border-radius: 8px; }}
.arch-legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 12px; color: {muted}; }}
.leg-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
.leg-dot.orch {{ background: {orch_outer}; border: 2px solid {accent}; }}
.leg-dot.agent {{ background: {node_fill_agent}; border: 1.5px solid {accent}; }}
.leg-dot.pipeline {{ background: {node_fill_pipe}; border: 1.5px solid {accent}; }}
.leg-dot.ops {{ background: {node_fill_ops}; border: 1px solid {stroke}; }}
.leg-dot.system {{ background: {node_fill_sys}; border: 1.5px solid {stroke}; }}
.leg-dot.human {{ background: {node_fill_human}; border: 1.5px solid {accent}; }}
.leg-line {{ width: 24px; height: 2px; background: {accent}; opacity: 0.4; border-radius: 1px; }}

/* Star canvas */
#starCanvas {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; }}

/* Custom CSS */
{sanitize_css(topo.get("css", ""))}'''


# ─── JAVASCRIPT ───

def generate_js(topo):
    """Generate interactive hover/highlight JS."""
    pipeline_nodes = set()
    for chain in topo.get("pipelines", {}).values():
        pipeline_nodes.update(chain)

    return f'''(function () {{
    var tip = document.getElementById('archTip');
    var svg = document.querySelector('.arch-svg');
    if (!svg) return;
    var allNodes = svg.querySelectorAll('[data-nid]');
    var allPaths = svg.querySelectorAll('path[data-conn]');
    var hideTimer, hoverTimer;

    var pipelineNodes = {json.dumps(list(pipeline_nodes))};
    var pipelineSet = {{}};
    pipelineNodes.forEach(function(n) {{ pipelineSet[n] = true; }});

    // Build adjacency
    var adj = {{}};
    allPaths.forEach(function(p) {{
        var src = p.getAttribute('data-src');
        var tgt = p.getAttribute('data-tgt');
        var cls = p.getAttribute('class') || '';
        if (!adj[src]) adj[src] = [];
        if (!adj[tgt]) adj[tgt] = [];
        adj[src].push({{node: tgt, path: p, cls: cls}});
        adj[tgt].push({{node: src, path: p, cls: cls}});
    }});

    function showTip(e, n, d) {{
        clearTimeout(hideTimer);
        tip.innerHTML = '<strong>' + n + '</strong>' + (d ? ' &mdash; ' + d : '');
        tip.classList.add('show');
        moveTip(e);
    }}
    function moveTip(e) {{
        var x = e.clientX + 14, y = e.clientY - tip.offsetHeight - 8;
        if (x + tip.offsetWidth > window.innerWidth - 8) x = e.clientX - tip.offsetWidth - 14;
        if (y < 8) y = e.clientY + 14;
        tip.style.left = x + 'px'; tip.style.top = y + 'px';
    }}
    function hideTip() {{ hideTimer = setTimeout(function(){{ tip.classList.remove('show'); }}, 120); }}

    function highlightNode(nid) {{
        svg.classList.add('has-hover');
        var visited = {{}};
        var queue = [nid];
        visited[nid] = true;

        while (queue.length) {{
            var cur = queue.shift();
            var nodeEl = svg.querySelector('[data-nid="' + cur + '"]');
            if (nodeEl) nodeEl.classList.add('hl');

            var edges = adj[cur] || [];
            for (var i = 0; i < edges.length; i++) {{
                var e = edges[i];
                var isCluster = e.cls.indexOf('conn-cluster') >= 0;
                if (cur === nid) {{
                    e.path.classList.add('hl');
                    if (!visited[e.node]) {{
                        visited[e.node] = true;
                        if (isCluster || (pipelineSet[nid] && pipelineSet[e.node])) {{
                            queue.push(e.node);
                        }}
                    }}
                }} else if (isCluster && !visited[e.node]) {{
                    e.path.classList.add('hl');
                    visited[e.node] = true;
                    queue.push(e.node);
                }}
            }}
        }}
    }}

    function clearHighlight() {{
        svg.classList.remove('has-hover');
        allNodes.forEach(function(n) {{ n.classList.remove('hl'); }});
        allPaths.forEach(function(p) {{ p.classList.remove('hl'); }});
    }}

    allNodes.forEach(function(node) {{
        var n = node.getAttribute('data-name') || '';
        var d = node.getAttribute('data-desc') || '';
        var nid = node.getAttribute('data-nid') || '';

        node.addEventListener('mouseenter', function(e) {{
            clearTimeout(hoverTimer);
            showTip(e, n, d);
            highlightNode(nid);
        }});
        node.addEventListener('mousemove', moveTip);
        node.addEventListener('mouseleave', function() {{
            hideTip();
            hoverTimer = setTimeout(clearHighlight, 150);
        }});
        node.addEventListener('click', function(e) {{
            showTip(e, n, d);
            highlightNode(nid);
            clearTimeout(hideTimer);
            clearTimeout(hoverTimer);
            hideTimer = setTimeout(function(){{ tip.classList.remove('show'); }}, 3000);
            hoverTimer = setTimeout(clearHighlight, 3000);
        }});
    }});

    allPaths.forEach(function(p) {{
        p.style.cursor = 'pointer';
        p.addEventListener('mouseenter', function(e) {{
            clearTimeout(hoverTimer);
            var src = p.getAttribute('data-src');
            var tgt = p.getAttribute('data-tgt');
            svg.classList.add('has-hover');
            p.classList.add('hl');
            var srcNode = svg.querySelector('[data-nid="' + src + '"]');
            var tgtNode = svg.querySelector('[data-nid="' + tgt + '"]');
            if (srcNode) srcNode.classList.add('hl');
            if (tgtNode) tgtNode.classList.add('hl');
            var sn = srcNode ? srcNode.getAttribute('data-name') || src : src;
            var tn = tgtNode ? tgtNode.getAttribute('data-name') || tgt : tgt;
            showTip(e, sn + ' \\u2192 ' + tn, '');
        }});
        p.addEventListener('mousemove', moveTip);
        p.addEventListener('mouseleave', function() {{
            hideTip();
            hoverTimer = setTimeout(clearHighlight, 150);
        }});
    }});

}})();'''


def generate_star_js(topo):
    """Generate star field background canvas JS."""
    bg_opts = topo.get("background", {})
    if bg_opts.get("stars") == False:
        return ""
    count = bg_opts.get("starCount", 150)
    color = bg_opts.get("starColor", "rgba(200,214,224,0.3)")
    return f'''(function(){{
    var c=document.getElementById('starCanvas');
    if(!c)return;
    var ctx=c.getContext('2d');
    function resize(){{c.width=window.innerWidth;c.height=window.innerHeight;draw();}}
    function draw(){{
        ctx.clearRect(0,0,c.width,c.height);
        for(var i=0;i<{count};i++){{
            var x=Math.random()*c.width;
            var y=Math.random()*c.height;
            var r=Math.random()*1.2+0.3;
            ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);
            ctx.fillStyle='{color}';ctx.fill();
        }}
    }}
    window.addEventListener('resize',resize);resize();
}})();'''


# ─── HTML ASSEMBLY ───

def generate_html(topo, node_map):
    """Assemble complete self-contained HTML page."""
    title = html_mod.escape(topo["title"])
    css = generate_css(topo)
    svg = generate_svg(topo, node_map)
    js = generate_js(topo)
    star_js = generate_star_js(topo)

    # Legend items based on node types present
    types_present = set(n["type"] for n in topo["nodes"])
    legend_items = []
    type_labels = {
        "orchestrator": ("orch", "Orchestrator"),
        "agent": ("agent", "Agents"),
        "pipeline": ("pipeline", "Pipeline"),
        "ops": ("ops", "Operations"),
        "system": ("system", "Systems"),
        "human": ("human", "Human"),
    }
    for t in ["orchestrator", "agent", "pipeline", "ops", "system", "human"]:
        if t in types_present:
            cls, label = type_labels[t]
            legend_items.append(f'<div class="arch-legend-item"><div class="leg-dot {cls}"></div><span>{label}</span></div>')
    if topo["connections"]:
        legend_items.append('<div class="arch-legend-item"><div class="leg-line"></div><span>Data Flow</span></div>')

    bg_opts = topo.get("background", {})
    star_canvas = '<canvas id="starCanvas"></canvas>' if bg_opts.get("stars", True) else ""

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    {star_canvas}
    <div class="topo-container">
        <h1 class="topo-title">{title}</h1>
        {svg}
        <div class="arch-legend">
            {chr(10).join(f"            {item}" for item in legend_items)}
        </div>
    </div>
    <div class="arch-tip" id="archTip"></div>
    <script>{star_js}</script>
    <script>{js}</script>
</body>
</html>'''


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(description="Generate interactive agent topology diagrams")
    parser.add_argument("topology", help="Path to topology JSON file")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument("--format", choices=["html", "svg", "paths"], default="html", help="Output format")
    args = parser.parse_args()

    topo = load_topology(args.topology)

    # Auto-layout nodes without positions
    auto_layout(topo["nodes"], topo["viewBox"][0], topo["viewBox"][1])

    # Build node map
    node_map = {n["id"]: n for n in topo["nodes"]}

    # Generate output
    if args.format == "paths":
        output = "\n".join(generate_paths(topo, node_map))
    elif args.format == "svg":
        output = generate_svg(topo, node_map)
    else:
        output = generate_html(topo, node_map)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"✅ Generated {args.format} → {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
