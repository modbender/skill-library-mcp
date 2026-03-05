#!/usr/bin/env python3
"""Pull Figma file data, extract design tokens, and generate code."""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

import requests

from figma_common import (
    api_get, get_token, rgba_to_hex, rgba_to_rn, setup_logging, stable_id,
    to_camel_case, to_kebab_case, write_json, FIGMA_API,
)

logger = logging.getLogger("figma-sync.pull")


# ---------------------------------------------------------------------------
# Figma tree normalization
# ---------------------------------------------------------------------------

def normalize_node(node: dict, depth: int = 0) -> dict:
    """Convert a Figma API node into our DesignSpec DesignNode."""
    ntype = node.get("type", "UNKNOWN")
    name = node.get("name", "Unnamed")
    fid = node.get("id", "")
    sid = stable_id(name, fid)

    props = {}
    bbox = node.get("absoluteBoundingBox") or node.get("size") or {}
    if bbox:
        props["x"] = bbox.get("x", 0)
        props["y"] = bbox.get("y", 0)
        props["width"] = bbox.get("width", 0)
        props["height"] = bbox.get("height", 0)

    props["visible"] = node.get("visible", True)
    props["opacity"] = node.get("opacity", 1.0)
    props["rotation"] = node.get("rotation", 0)
    props["layoutPositioning"] = node.get("layoutPositioning", "AUTO")
    props["layoutSizingHorizontal"] = node.get("layoutSizingHorizontal", "FIXED")
    props["layoutSizingVertical"] = node.get("layoutSizingVertical", "FIXED")

    if "cornerRadius" in node:
        props["cornerRadius"] = node["cornerRadius"]
    if "rectangleCornerRadii" in node:
        radii = node["rectangleCornerRadii"]
        props["cornerRadii"] = {
            "topLeft": radii[0], "topRight": radii[1],
            "bottomRight": radii[2], "bottomLeft": radii[3],
        }

    if "fills" in node:
        props["fills"] = normalize_paints(node["fills"])
    if "strokes" in node:
        props["strokes"] = normalize_paints(node["strokes"])
    if "strokeWeight" in node:
        props["strokeWeight"] = node["strokeWeight"]
    if "effects" in node:
        props["effects"] = normalize_effects(node["effects"])
    if "constraints" in node:
        props["constraints"] = node["constraints"]
    if "clipsContent" in node:
        props["clipsContent"] = node["clipsContent"]

    # Auto-layout
    if node.get("layoutMode"):
        props["autoLayout"] = {
            "mode": node["layoutMode"],
            "paddingTop": node.get("paddingTop", 0),
            "paddingRight": node.get("paddingRight", 0),
            "paddingBottom": node.get("paddingBottom", 0),
            "paddingLeft": node.get("paddingLeft", 0),
            "itemSpacing": node.get("itemSpacing", 0),
            "counterAxisSpacing": node.get("counterAxisSpacing", 0),
            "primaryAxisAlignItems": node.get("primaryAxisAlignItems", "MIN"),
            "counterAxisAlignItems": node.get("counterAxisAlignItems", "MIN"),
            "primaryAxisSizingMode": node.get("primaryAxisSizingMode", "AUTO"),
            "counterAxisSizingMode": node.get("counterAxisSizingMode", "AUTO"),
        }

    # Text
    if ntype == "TEXT":
        props["textContent"] = node.get("characters", "")
        style = node.get("style", {})
        props["textStyle"] = {
            "fontFamily": style.get("fontFamily", ""),
            "fontWeight": style.get("fontWeight", 400),
            "fontSize": style.get("fontSize", 16),
            "lineHeight": style.get("lineHeightPx", "auto"),
            "letterSpacing": style.get("letterSpacing", 0),
            "textAlignHorizontal": style.get("textAlignHorizontal", "LEFT"),
            "textAlignVertical": style.get("textAlignVertical", "TOP"),
            "textDecoration": style.get("textDecoration", "NONE"),
            "textCase": style.get("textCase", "ORIGINAL"),
        }

    if "componentPropertyDefinitions" in node:
        props["componentPropertyDefinitions"] = node["componentPropertyDefinitions"]

    children = []
    for child in node.get("children", []):
        children.append(normalize_node(child, depth + 1))

    result = {
        "id": sid,
        "name": name,
        "type": ntype,
        "figmaNodeId": fid,
        "properties": props,
    }
    if children:
        result["children"] = children
    return result


def normalize_paints(paints: list) -> list:
    result = []
    for p in paints:
        paint = {"type": p.get("type", "SOLID"), "visible": p.get("visible", True)}
        if "color" in p:
            paint["color"] = p["color"]
            paint["opacity"] = p.get("opacity", 1.0)
        if "imageRef" in p:
            paint["imageRef"] = p["imageRef"]
        if "scaleMode" in p:
            paint["scaleMode"] = p["scaleMode"]
        result.append(paint)
    return result


def normalize_effects(effects: list) -> list:
    result = []
    for e in effects:
        eff = {
            "type": e.get("type", "DROP_SHADOW"),
            "visible": e.get("visible", True),
            "radius": e.get("radius", 0),
        }
        if "color" in e:
            eff["color"] = e["color"]
        if "offset" in e:
            eff["offset"] = e["offset"]
        if "spread" in e:
            eff["spread"] = e["spread"]
        result.append(eff)
    return result


# ---------------------------------------------------------------------------
# Style & token extraction
# ---------------------------------------------------------------------------

def extract_styles(file_data: dict) -> dict:
    text_styles, color_styles, effect_styles = [], [], []
    styles = file_data.get("styles", {})
    for style_id, style_meta in sorted(styles.items()):
        stype = style_meta.get("styleType", "")
        entry = {
            "id": stable_id(style_meta.get("name", ""), style_id),
            "name": style_meta.get("name", ""),
            "figmaStyleId": style_id,
        }
        if stype == "TEXT":
            text_styles.append(entry)
        elif stype == "FILL":
            color_styles.append(entry)
        elif stype == "EFFECT":
            effect_styles.append(entry)
    return {"textStyles": text_styles, "colorStyles": color_styles, "effectStyles": effect_styles}


def extract_tokens(design_model: dict) -> dict:
    colors, typography, shadows = {}, {}, {}
    spacing, radii = set(), set()

    def walk(node):
        props = node.get("properties", {})
        for fill in props.get("fills", []):
            if fill.get("color") and fill.get("visible", True):
                hex_val = rgba_to_hex(fill["color"])
                colors[to_kebab_case(f"color-{node['name']}")] = hex_val
        ts = props.get("textStyle")
        if ts and ts.get("fontFamily"):
            typography[to_kebab_case(f"type-{node['name']}")] = {
                "fontFamily": ts["fontFamily"], "fontWeight": ts.get("fontWeight", 400),
                "fontSize": ts.get("fontSize", 16), "lineHeight": ts.get("lineHeight", "auto"),
                "letterSpacing": ts.get("letterSpacing", 0),
            }
        al = props.get("autoLayout")
        if al:
            for key in ["paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "itemSpacing"]:
                val = al.get(key, 0)
                if val > 0:
                    spacing.add(val)
        cr = props.get("cornerRadius")
        if cr and cr > 0:
            radii.add(cr)
        for v in (props.get("cornerRadii") or {}).values():
            if v > 0:
                radii.add(v)
        for eff in props.get("effects", []):
            if eff.get("type") in ("DROP_SHADOW", "INNER_SHADOW") and eff.get("visible", True):
                sname = to_kebab_case(f"shadow-{node['name']}")
                shadows[sname] = {
                    "x": (eff.get("offset") or {}).get("x", 0),
                    "y": (eff.get("offset") or {}).get("y", 0),
                    "blur": eff.get("radius", 0),
                    "spread": eff.get("spread", 0),
                    "color": rgba_to_hex(eff["color"]) if "color" in eff else "rgba(0,0,0,0.25)",
                }
        for child in node.get("children", []):
            walk(child)

    for frame in design_model.get("frames", []):
        walk(frame)
    for comp in design_model.get("components", []):
        walk(comp)

    return {
        "colors": dict(sorted(colors.items())),
        "typography": dict(sorted(typography.items())),
        "spacing": {f"spacing-{int(v)}": v for v in sorted(spacing)},
        "radii": {f"radius-{int(v)}": v for v in sorted(radii)},
        "shadows": dict(sorted(shadows.items())),
    }


# ---------------------------------------------------------------------------
# Variant extraction
# ---------------------------------------------------------------------------

def extract_variants(file_data: dict) -> list:
    variants = []
    for cs_id, cs_meta in sorted(file_data.get("componentSets", {}).items()):
        variants.append({
            "id": stable_id(cs_meta.get("name", ""), cs_id),
            "name": cs_meta.get("name", ""),
            "figmaNodeId": cs_id,
            "properties": {},
            "variants": [],
        })
    return variants


# ---------------------------------------------------------------------------
# Code generation helpers
# ---------------------------------------------------------------------------

def _figma_color(color: dict, fill_opacity: float = 1.0) -> str:
    """Convert Figma color dict to rgba string."""
    r = round(color.get("r", 0) * 255)
    g = round(color.get("g", 0) * 255)
    b = round(color.get("b", 0) * 255)
    a = color.get("a", 1.0) * fill_opacity
    if a >= 1.0:
        return f"#{r:02x}{g:02x}{b:02x}"
    return f"rgba({r}, {g}, {b}, {a:.2f})"


def _style_key(name: str, used: set) -> str:
    """Make a unique camelCase style key."""
    camel = to_camel_case(name)
    if not camel:
        camel = "Item"
    key = camel[0].lower() + camel[1:]
    # Sanitize: only allow valid JS identifier chars
    key = re.sub(r"[^a-zA-Z0-9]", "", key)
    if not key or key[0].isdigit():
        key = "s" + key
    base = key
    i = 2
    while key in used:
        key = f"{base}{i}"
        i += 1
    used.add(key)
    return key


def _get_bg_color(props: dict) -> str | None:
    """Get background color from fills."""
    for fill in props.get("fills", []):
        if not fill.get("visible", True):
            continue
        if fill.get("type") == "SOLID" and fill.get("color"):
            return _figma_color(fill["color"], fill.get("opacity", 1.0))
        if fill.get("type") in ("GRADIENT_LINEAR", "GRADIENT_RADIAL") and fill.get("color"):
            return _figma_color(fill["color"], fill.get("opacity", 1.0))
    return None


def _has_image_fill(props: dict) -> str | None:
    """Return imageRef if node has an image fill."""
    for fill in props.get("fills", []):
        if fill.get("type") == "IMAGE" and fill.get("visible", True) and fill.get("imageRef"):
            return fill["imageRef"]
    return None


def _get_scale_mode(props: dict) -> str:
    for fill in props.get("fills", []):
        if fill.get("type") == "IMAGE":
            mode = fill.get("scaleMode", "FILL")
            return "contain" if mode == "FIT" else "cover"
    return "cover"


def _get_stroke_styles(props: dict) -> dict:
    styles = {}
    sw = props.get("strokeWeight", 0)
    if sw and sw > 0:
        for s in props.get("strokes", []):
            if s.get("visible", True) and s.get("color"):
                styles["borderWidth"] = sw
                styles["borderColor"] = f'"{_figma_color(s["color"], s.get("opacity", 1.0))}"'
                break
    return styles


def _get_shadow_styles(props: dict) -> dict:
    styles = {}
    for eff in props.get("effects", []):
        if eff.get("type") == "DROP_SHADOW" and eff.get("visible", True):
            c = eff.get("color", {})
            ox = (eff.get("offset") or {}).get("x", 0)
            oy = (eff.get("offset") or {}).get("y", 0)
            r = eff.get("radius", 0)
            a = c.get("a", 0.25)
            styles["shadowColor"] = f'"rgba({round(c.get("r",0)*255)}, {round(c.get("g",0)*255)}, {round(c.get("b",0)*255)}, 1)"'
            styles["shadowOffset"] = f'{{ width: {ox}, height: {oy} }}'
            styles["shadowOpacity"] = round(a, 2)
            styles["shadowRadius"] = round(r / 2, 1)
            styles["elevation"] = max(1, round(r / 2))
            break
    return styles


def _border_radius_styles(props: dict) -> dict:
    styles = {}
    radii = props.get("cornerRadii")
    cr = props.get("cornerRadius")
    if radii:
        if radii["topLeft"] == radii["topRight"] == radii["bottomRight"] == radii["bottomLeft"]:
            if radii["topLeft"] > 0:
                styles["borderRadius"] = radii["topLeft"]
        else:
            for k, rn_k in [("topLeft", "borderTopLeftRadius"), ("topRight", "borderTopRightRadius"),
                             ("bottomRight", "borderBottomRightRadius"), ("bottomLeft", "borderBottomLeftRadius")]:
                if radii[k] > 0:
                    styles[rn_k] = radii[k]
    elif cr and cr > 0:
        styles["borderRadius"] = cr
    return styles


# ---------------------------------------------------------------------------
# Recursive RN component generation
# ---------------------------------------------------------------------------

class RNGenerator:
    """Generates a React Native component from a normalized Figma node tree."""

    def __init__(self, file_key: str):
        self.file_key = file_key
        self.style_defs: dict[str, dict] = {}  # style_key -> style dict
        self.style_keys = set()
        self.image_nodes: dict[str, dict] = {}  # imageRef -> {node_id, style_key, scale_mode}
        self.needs_image = False
        self.needs_scroll = False
        self.needs_text = False

    def generate(self, root_node: dict) -> str:
        comp_name = to_camel_case(root_node["name"])
        if not comp_name:
            comp_name = "Screen"

        # Generate JSX tree
        jsx = self._render_node(root_node, parent_has_autolayout=False, parent_bbox=None, is_root=True, depth=2)

        # Build imports
        rn_imports = ["View", "StyleSheet"]
        if self.needs_text:
            rn_imports.insert(1, "Text")
        if self.needs_image:
            rn_imports.insert(1, "Image")
        if self.needs_scroll:
            rn_imports.append("ScrollView")
        rn_imports_str = ", ".join(rn_imports)

        # Build styles
        style_lines = []
        for key, sdict in self.style_defs.items():
            entries = []
            for sk, sv in sdict.items():
                if isinstance(sv, str) and not sv.startswith('"') and not sv.startswith("'") and not sv.startswith("{"):
                    entries.append(f'    {sk}: "{sv}"')
                elif isinstance(sv, str) and (sv.startswith("{") or sv.startswith('"')):
                    entries.append(f"    {sk}: {sv}")
                elif isinstance(sv, bool):
                    entries.append(f"    {sk}: {'true' if sv else 'false'}")
                elif isinstance(sv, float):
                    # Clean float
                    if sv == int(sv):
                        entries.append(f"    {sk}: {int(sv)}")
                    else:
                        entries.append(f"    {sk}: {sv}")
                else:
                    entries.append(f"    {sk}: {sv}")
            style_lines.append(f"  {key}: {{\n" + ",\n".join(entries) + ",\n  }")

        styles_str = ",\n".join(style_lines)

        # Determine if content is tall enough to need ScrollView
        root_props = root_node.get("properties", {})
        root_h = root_props.get("height", 0)
        wrap_scroll = root_h > 900
        self.needs_scroll = wrap_scroll

        # Rebuild imports if scroll needed
        if wrap_scroll and "ScrollView" not in rn_imports:
            rn_imports.append("ScrollView")
            rn_imports_str = ", ".join(rn_imports)

        indent = "    "
        if wrap_scroll:
            body = f'{indent}<ScrollView style={{styles.root}} contentContainerStyle={{{{ flexGrow: 1 }}}}>\n{jsx}\n{indent}</ScrollView>'
        else:
            body = jsx

        return f'''import React from "react";
import {{ {rn_imports_str} }} from "react-native";

export const {comp_name}: React.FC = () => {{
  return (
{body}
  );
}};

const styles = StyleSheet.create({{
{styles_str}
}});

export default {comp_name};
'''

    def _render_node(self, node: dict, parent_has_autolayout: bool, parent_bbox: dict | None,
                     is_root: bool, depth: int) -> str:
        ntype = node.get("type", "UNKNOWN")
        props = node.get("properties", {})

        # Skip invisible nodes
        if not props.get("visible", True):
            return ""

        # Skip complex vector types
        if ntype in ("VECTOR", "BOOLEAN_OPERATION"):
            # TODO: Support VECTOR/BOOLEAN_OPERATION nodes (SVG paths)
            return ""

        if ntype == "TEXT":
            return self._render_text(node, parent_has_autolayout, parent_bbox, depth)

        # FRAME, GROUP, RECTANGLE, ELLIPSE, INSTANCE, COMPONENT, LINE, etc → View
        if ntype == "LINE":
            return self._render_line(node, parent_has_autolayout, parent_bbox, depth)

        # Check for image fill
        image_ref = _has_image_fill(props)
        if image_ref:
            return self._render_image(node, image_ref, parent_has_autolayout, parent_bbox, depth)

        # Regular container (View)
        return self._render_view(node, parent_has_autolayout, parent_bbox, is_root, depth)

    def _build_layout_style(self, node: dict, parent_has_autolayout: bool, parent_bbox: dict | None,
                            is_root: bool = False) -> dict:
        """Build the style dict for a node's layout properties."""
        props = node.get("properties", {})
        ntype = node.get("type", "UNKNOWN")
        style = {}

        has_al = "autoLayout" in props
        al = props.get("autoLayout")

        # --- Sizing ---
        sizing_h = props.get("layoutSizingHorizontal", "FIXED")
        sizing_v = props.get("layoutSizingVertical", "FIXED")
        w = props.get("width", 0)
        h = props.get("height", 0)

        if parent_has_autolayout:
            if sizing_h == "FILL":
                style["flex"] = 1
            elif sizing_h == "FIXED" and w:
                style["width"] = round(w)
            # HUG = no explicit width
            if sizing_v == "FILL" and "flex" not in style:
                style["flex"] = 1
            elif sizing_v == "FIXED" and h:
                style["height"] = round(h)
        else:
            if is_root:
                if w:
                    style["width"] = round(w)
                if h:
                    style["height"] = round(h)
            else:
                # Absolute positioning relative to parent
                style["position"] = '"absolute"'
                if parent_bbox and props.get("x") is not None:
                    style["left"] = round(props["x"] - parent_bbox.get("x", 0))
                    style["top"] = round(props["y"] - parent_bbox.get("y", 0))
                if w:
                    style["width"] = round(w)
                if h:
                    style["height"] = round(h)

        # Override: layoutPositioning ABSOLUTE inside auto-layout parent
        if parent_has_autolayout and props.get("layoutPositioning") == "ABSOLUTE":
            style["position"] = '"absolute"'
            if parent_bbox and props.get("x") is not None:
                style["left"] = round(props["x"] - parent_bbox.get("x", 0))
                style["top"] = round(props["y"] - parent_bbox.get("y", 0))
            if w:
                style["width"] = round(w)
            if h:
                style["height"] = round(h)

        # --- Auto-layout (flexbox) ---
        if has_al and al:
            mode = al.get("mode", "VERTICAL")
            if mode == "HORIZONTAL":
                style["flexDirection"] = '"row"'
            else:
                style["flexDirection"] = '"column"'

            justify_map = {"MIN": '"flex-start"', "CENTER": '"center"', "MAX": '"flex-end"',
                           "SPACE_BETWEEN": '"space-between"'}
            align_map = {"MIN": '"flex-start"', "CENTER": '"center"', "MAX": '"flex-end"'}

            j = justify_map.get(al.get("primaryAxisAlignItems", "MIN"))
            if j and j != '"flex-start"':
                style["justifyContent"] = j
            a = align_map.get(al.get("counterAxisAlignItems", "MIN"))
            if a and a != '"flex-start"':
                style["alignItems"] = a

            gap = al.get("itemSpacing", 0)
            if gap > 0:
                style["gap"] = gap

            pt, pr, pb, pl = al.get("paddingTop", 0), al.get("paddingRight", 0), al.get("paddingBottom", 0), al.get("paddingLeft", 0)
            if pt == pr == pb == pl and pt > 0:
                style["padding"] = pt
            else:
                if pt > 0: style["paddingTop"] = pt
                if pr > 0: style["paddingRight"] = pr
                if pb > 0: style["paddingBottom"] = pb
                if pl > 0: style["paddingLeft"] = pl

        return style

    def _build_visual_style(self, props: dict, ntype: str) -> dict:
        """Build visual styles (colors, borders, shadows, opacity)."""
        style = {}

        bg = _get_bg_color(props)
        if bg:
            style["backgroundColor"] = f'"{bg}"'

        style.update({k: (f'"{v}"' if isinstance(v, str) and not v.startswith('"') else v)
                      for k, v in _border_radius_styles(props).items()})

        if ntype == "ELLIPSE":
            w = props.get("width", 0)
            if w:
                style["borderRadius"] = round(w / 2)

        style.update(_get_stroke_styles(props))
        style.update(_get_shadow_styles(props))

        opacity = props.get("opacity", 1.0)
        if opacity < 1.0:
            style["opacity"] = round(opacity, 2)

        if props.get("clipsContent"):
            style["overflow"] = '"hidden"'

        return style

    def _render_view(self, node: dict, parent_has_autolayout: bool, parent_bbox: dict | None,
                     is_root: bool, depth: int) -> str:
        props = node.get("properties", {})
        ntype = node.get("type", "UNKNOWN")
        has_al = "autoLayout" in props

        # Build style
        layout_style = self._build_layout_style(node, parent_has_autolayout, parent_bbox, is_root)
        visual_style = self._build_visual_style(props, ntype)
        combined = {**layout_style, **visual_style}

        style_key = _style_key(node["name"], self.style_keys)
        if is_root:
            style_key = "root"
            self.style_keys.add("root")
        self.style_defs[style_key] = combined

        # Render children
        children_jsx = []
        child_bbox = {"x": props.get("x", 0), "y": props.get("y", 0)}
        for child in node.get("children", []):
            child_jsx = self._render_node(child, parent_has_autolayout=has_al,
                                          parent_bbox=child_bbox, is_root=False, depth=depth + 1)
            if child_jsx:
                children_jsx.append(child_jsx)

        pad = "  " * depth
        if children_jsx:
            inner = "\n".join(children_jsx)
            return f'{pad}<View style={{styles.{style_key}}}>\n{inner}\n{pad}</View>'
        else:
            return f'{pad}<View style={{styles.{style_key}}} />'

    def _render_text(self, node: dict, parent_has_autolayout: bool, parent_bbox: dict | None, depth: int) -> str:
        self.needs_text = True
        props = node.get("properties", {})
        ts = props.get("textStyle", {})
        text = props.get("textContent", "")

        style = {}

        # Layout
        sizing_h = props.get("layoutSizingHorizontal", "FIXED")
        sizing_v = props.get("layoutSizingVertical", "FIXED")
        w = props.get("width", 0)

        if parent_has_autolayout:
            if sizing_h == "FILL":
                style["flex"] = 1
            elif sizing_h == "FIXED" and w:
                style["width"] = round(w)
        else:
            style["position"] = '"absolute"'
            if parent_bbox and props.get("x") is not None:
                style["left"] = round(props["x"] - parent_bbox.get("x", 0))
                style["top"] = round(props["y"] - parent_bbox.get("y", 0))
            if w:
                style["width"] = round(w)

        if parent_has_autolayout and props.get("layoutPositioning") == "ABSOLUTE":
            style["position"] = '"absolute"'
            if parent_bbox and props.get("x") is not None:
                style["left"] = round(props["x"] - parent_bbox.get("x", 0))
                style["top"] = round(props["y"] - parent_bbox.get("y", 0))

        # Text styles
        if ts.get("fontSize"):
            style["fontSize"] = ts["fontSize"]
        fw = ts.get("fontWeight", 400)
        if fw and fw != 400:
            fw_map = {100: '"100"', 200: '"200"', 300: '"300"', 500: '"500"',
                      600: '"600"', 700: '"bold"', 800: '"800"', 900: '"900"'}
            style["fontWeight"] = fw_map.get(fw, f'"{fw}"')
        if ts.get("fontFamily"):
            style["fontFamily"] = f'"{ts["fontFamily"]}"'

        align_map = {"LEFT": '"left"', "CENTER": '"center"', "RIGHT": '"right"', "JUSTIFIED": '"justify"'}
        ta = align_map.get(ts.get("textAlignHorizontal", "LEFT"))
        if ta and ta != '"left"':
            style["textAlign"] = ta

        lh = ts.get("lineHeight")
        if lh and lh != "auto" and isinstance(lh, (int, float)) and lh > 0:
            style["lineHeight"] = round(lh, 1)

        ls = ts.get("letterSpacing", 0)
        if ls and ls != 0:
            style["letterSpacing"] = round(ls, 2)

        # Text color from fills
        for fill in props.get("fills", []):
            if fill.get("visible", True) and fill.get("color"):
                style["color"] = f'"{_figma_color(fill["color"], fill.get("opacity", 1.0))}"'
                break

        opacity = props.get("opacity", 1.0)
        if opacity < 1.0:
            style["opacity"] = round(opacity, 2)

        td = ts.get("textDecoration", "NONE")
        if td == "UNDERLINE":
            style["textDecorationLine"] = '"underline"'
        elif td == "STRIKETHROUGH":
            style["textDecorationLine"] = '"line-through"'

        tc = ts.get("textCase", "ORIGINAL")
        if tc == "UPPER":
            style["textTransform"] = '"uppercase"'
        elif tc == "LOWER":
            style["textTransform"] = '"lowercase"'
        elif tc == "TITLE":
            style["textTransform"] = '"capitalize"'

        style_key = _style_key(node["name"], self.style_keys)
        self.style_defs[style_key] = style

        # Escape text for JSX
        escaped = text.replace("{", "&#123;").replace("}", "&#125;").replace("<", "&lt;").replace(">", "&gt;")
        # For multi-line, keep as-is (React Native Text handles newlines)
        pad = "  " * depth
        if "\n" in escaped:
            return f'{pad}<Text style={{styles.{style_key}}}>{{\n{pad}  `{text}`\n{pad}}}</Text>'
        return f'{pad}<Text style={{styles.{style_key}}}>{escaped}</Text>'

    def _render_line(self, node: dict, parent_has_autolayout: bool, parent_bbox: dict | None, depth: int) -> str:
        props = node.get("properties", {})
        style = {}
        w = props.get("width", 0)
        if parent_has_autolayout:
            style["alignSelf"] = '"stretch"'
        else:
            style["position"] = '"absolute"'
            if parent_bbox and props.get("x") is not None:
                style["left"] = round(props["x"] - parent_bbox.get("x", 0))
                style["top"] = round(props["y"] - parent_bbox.get("y", 0))
            if w:
                style["width"] = round(w)
        style["height"] = 1
        bg = _get_bg_color(props)
        if bg:
            style["backgroundColor"] = f'"{bg}"'
        else:
            # Use stroke color for lines
            for s in props.get("strokes", []):
                if s.get("visible", True) and s.get("color"):
                    style["backgroundColor"] = f'"{_figma_color(s["color"], s.get("opacity", 1.0))}"'
                    break

        style_key = _style_key(node["name"], self.style_keys)
        self.style_defs[style_key] = style
        pad = "  " * depth
        return f'{pad}<View style={{styles.{style_key}}} />'

    def _render_image(self, node: dict, image_ref: str, parent_has_autolayout: bool,
                      parent_bbox: dict | None, depth: int) -> str:
        self.needs_image = True
        props = node.get("properties", {})
        style = {}
        w = props.get("width", 0)
        h = props.get("height", 0)

        if parent_has_autolayout:
            sizing_h = props.get("layoutSizingHorizontal", "FIXED")
            if sizing_h == "FILL":
                style["flex"] = 1
            elif w:
                style["width"] = round(w)
            if h:
                style["height"] = round(h)
        else:
            style["position"] = '"absolute"'
            if parent_bbox and props.get("x") is not None:
                style["left"] = round(props["x"] - parent_bbox.get("x", 0))
                style["top"] = round(props["y"] - parent_bbox.get("y", 0))
            if w:
                style["width"] = round(w)
            if h:
                style["height"] = round(h)

        style.update({k: (f'"{v}"' if isinstance(v, str) and not v.startswith('"') else v)
                      for k, v in _border_radius_styles(props).items()})

        style_key = _style_key(node["name"], self.style_keys)
        self.style_defs[style_key] = style

        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", node["name"]).strip("_").lower()
        scale_mode = _get_scale_mode(props)
        self.image_nodes[image_ref] = {
            "node_id": node["figmaNodeId"],
            "style_key": style_key,
            "safe_name": safe_name,
            "scale_mode": scale_mode,
        }

        pad = "  " * depth
        return f'{pad}<Image source={{require("../assets/{safe_name}.png")}} style={{styles.{style_key}}} resizeMode="{scale_mode}" />'

    def collect_image_refs(self) -> dict:
        """Return {imageRef: {node_id, safe_name}} for downloading."""
        return self.image_nodes


# ---------------------------------------------------------------------------
# Image downloading
# ---------------------------------------------------------------------------

def download_images(file_key: str, image_nodes: dict, output_dir: Path):
    """Download image fills from Figma and save to assets/."""
    if not image_nodes:
        return

    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Collect node IDs that have image fills
    node_ids = [info["node_id"] for info in image_nodes.values()]
    if not node_ids:
        return

    ids_str = ",".join(node_ids)
    logger.info("Exporting %d images from Figma...", len(node_ids))

    try:
        resp = api_get(f"/v1/images/{file_key}", file_key=file_key,
                       params={"ids": ids_str, "format": "png", "scale": "2"},
                       use_cache=False)
        images = resp.get("images", {})

        hdrs = {"X-Figma-Token": get_token()}
        for ref, info in image_nodes.items():
            url = images.get(info["node_id"])
            if url:
                try:
                    img_resp = requests.get(url, timeout=30)
                    img_resp.raise_for_status()
                    out_path = assets_dir / f"{info['safe_name']}.png"
                    out_path.write_bytes(img_resp.content)
                    logger.info("Saved image: %s", out_path)
                except Exception as e:
                    logger.warning("Failed to download image %s: %s", info["safe_name"], e)
    except Exception as e:
        logger.warning("Failed to export images: %s", e)


# ---------------------------------------------------------------------------
# Code generation (top-level)
# ---------------------------------------------------------------------------

def generate_code_plan(design_model: dict, platform: str) -> dict:
    plan = {"platform": platform, "components": []}
    for comp in design_model.get("components", []):
        comp_name = to_camel_case(comp["name"])
        plan["components"].append({
            "componentName": comp_name,
            "figmaNodeId": comp["figmaNodeId"],
            "filePath": f"components/{comp_name}.tsx",
            "stableId": comp["id"],
        })
    for frame in design_model.get("frames", []):
        comp_name = to_camel_case(frame["name"])
        if platform == "rn-expo":
            plan["components"].append({
                "componentName": comp_name,
                "figmaNodeId": frame["figmaNodeId"],
                "filePath": f"screens/{comp_name}Screen.tsx",
                "stableId": frame["id"],
            })
        else:
            plan["components"].append({
                "componentName": comp_name,
                "figmaNodeId": frame["figmaNodeId"],
                "filePath": f"pages/{comp_name}Page.tsx",
                "stableId": frame["id"],
            })
    return plan


def generate_rn_component(node: dict, tokens: dict, file_key: str = "") -> tuple[str, dict]:
    """Generate a React Native Expo TypeScript component. Returns (code, image_refs)."""
    gen = RNGenerator(file_key)
    code = gen.generate(node)
    return code, gen.collect_image_refs()


def generate_web_component(node: dict, tokens: dict) -> str:
    """Generate a React + Tailwind component (basic, unchanged)."""
    comp_name = to_camel_case(node["name"])
    return f'''import React from "react";

export const {comp_name}: React.FC = () => {{
  return <div>{{/* TODO: web component */}}</div>;
}};

export default {comp_name};
'''


# ---------------------------------------------------------------------------
# Asset extraction
# ---------------------------------------------------------------------------

def extract_assets(file_data: dict) -> list:
    assets = []
    for comp_id, comp_meta in sorted(file_data.get("components", {}).items()):
        assets.append({
            "id": stable_id(comp_meta.get("name", ""), comp_id),
            "name": comp_meta.get("name", ""),
            "figmaNodeId": comp_id,
            "exportSettings": [{"format": "PNG", "scale": 2}],
        })
    return assets


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def pull(file_key: str, node_ids: list = None, platform: str = "rn-expo", output_dir: str = "./out"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Fetch file data
    if node_ids:
        ids_str = ",".join(node_ids)
        logger.info("Fetching nodes %s from file %s", ids_str, file_key)
        data = api_get(f"/v1/files/{file_key}/nodes", file_key=file_key, params={"ids": ids_str})
        nodes_data = data.get("nodes", {})
        children = []
        for nid, ninfo in sorted(nodes_data.items()):
            doc = ninfo.get("document")
            if doc:
                children.append(doc)
        file_data = data
        document = {"children": children, "type": "DOCUMENT", "name": "Partial", "id": "0:0"}
    else:
        logger.info("Fetching full file %s", file_key)
        data = api_get(f"/v1/files/{file_key}", file_key=file_key)
        file_data = data
        document = data.get("document", {})

    file_name = data.get("name", file_key)
    last_modified = data.get("lastModified", "")

    # Normalize tree
    frames = []
    components = []
    if node_ids:
        # When fetching specific nodes, each document IS the frame itself
        for page in document.get("children", []):
            if not isinstance(page, dict):
                continue
            normalized = normalize_node(page)
            ctype = page.get("type", "")
            if ctype in ("COMPONENT", "COMPONENT_SET"):
                components.append(normalized)
            else:
                frames.append(normalized)
    else:
        for page in document.get("children", []):
            for child in page.get("children", []) if page.get("children") else []:
                if not isinstance(child, dict):
                    continue
                normalized = normalize_node(child)
                ctype = child.get("type", "")
                if ctype in ("COMPONENT", "COMPONENT_SET"):
                    components.append(normalized)
                else:
                    frames.append(normalized)

    # Extract styles
    styles = extract_styles(file_data)
    variants = extract_variants(file_data)
    assets = extract_assets(file_data)

    design_model = {
        "version": "1.0.0",
        "fileKey": file_key,
        "fileName": file_name,
        "lastModified": last_modified,
        "frames": frames,
        "components": components,
        "variants": variants,
        "textStyles": styles["textStyles"],
        "colorStyles": styles["colorStyles"],
        "effectStyles": styles["effectStyles"],
        "assets": assets,
    }

    tokens = extract_tokens(design_model)
    design_model["tokens"] = tokens

    write_json(out / "designModel.json", design_model)
    write_json(out / "tokens.json", tokens)

    code_plan = generate_code_plan(design_model, platform)
    write_json(out / "codePlan.json", code_plan)

    # Generate component files
    all_image_refs = {}
    for entry in code_plan["components"]:
        node = None
        for n in components + frames:
            if n["figmaNodeId"] == entry["figmaNodeId"]:
                node = n
                break
        if node:
            if platform == "rn-expo":
                code, img_refs = generate_rn_component(node, tokens, file_key)
                all_image_refs.update(img_refs)
            else:
                code = generate_web_component(node, tokens)
            file_path = out / entry["filePath"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(code)
            logger.info("Generated %s", file_path)

    # Download images
    if all_image_refs:
        download_images(file_key, all_image_refs, out)

    logger.info("Pull complete. Output in %s", out)
    return design_model


def main():
    parser = argparse.ArgumentParser(description="Pull Figma file and generate code")
    parser.add_argument("--file-key", required=True, help="Figma file key")
    parser.add_argument("--node-ids", help="Comma-separated node IDs (optional)")
    parser.add_argument("--platform", choices=["rn-expo", "web-react"], default="rn-expo")
    parser.add_argument("--output-dir", default="./out")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)
    node_ids = args.node_ids.split(",") if args.node_ids else None
    pull(args.file_key, node_ids, args.platform, args.output_dir)


if __name__ == "__main__":
    main()
