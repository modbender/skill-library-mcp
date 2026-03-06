#!/usr/bin/env python3
"""Prepare storyboard/asset artifacts from unstructured inputs.

v0.1.6-a scope:
- Parse text/txt/json input
- Extract staged artifacts (outline/episode/subject/scene)
- Build storyboard.draft.v1.json + assets.v1.json
- Output independent stage JSON files
- Emit parse-report.md + confirmation-message.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_VIDEO_MODEL = "doubao-seedance-1-5-pro-251215"
DEFAULT_IMAGE_MODEL = "doubao-seedream-5-0-260128"


class PrepareError(Exception):
    pass


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_input_type(raw: str) -> str:
    txt = raw.strip()
    if not txt:
        return "empty"
    if txt.startswith("{") or txt.startswith("["):
        try:
            json.loads(txt)
            return "json"
        except json.JSONDecodeError:
            return "text"
    return "text"


def to_shot_id(raw_id: str, idx: int) -> str:
    if raw_id:
        m = re.search(r"(\d+)(?:\D+)?(\d+)?", raw_id)
        if m:
            if m.group(2):
                return f"s{int(m.group(1)):02d}-{int(m.group(2)):02d}"
            return f"s{int(m.group(1)):02d}"
    return f"s{idx:02d}"


def parse_outline(raw: str) -> Optional[Dict[str, Any]]:
    """Extract outline from raw text if marked with 【大纲】."""
    m = re.search(r"【\s*大纲\s*】(?P<body>.*?)(?:【\s*单集策划\s*】|【\s*主体列表\s*】|【\s*场景列表\s*】|$)", raw, flags=re.S)
    if not m:
        return None

    body = m.group("body").strip()
    # Try to extract key fields
    title = ""
    summary = ""
    tags = []

    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if re.match(r"^标题[:：]", ln):
            title = re.split(r"[:：]", ln, 1)[1].strip()
        elif re.match(r"^概述[:：]", ln) or re.match(r"^总结[:：]", ln):
            summary = re.split(r"[:：]", ln, 1)[1].strip()
        elif re.match(r"^标签[:：]", ln) or re.match(r"^tag[:：]", ln, flags=re.I):
            tags_part = re.split(r"[:：]", ln, 1)[1].strip()
            tags = [t.strip() for t in tags_part.split(",")]

    return {
        "version": "outline.v1",
        "title": title,
        "summary": summary or body[:500],
        "tags": tags,
        "raw_text": body,
    }


def parse_episode_plan(raw: str) -> Optional[Dict[str, Any]]:
    """Extract episode plan from raw text if marked with 【单集策划】."""
    m = re.search(r"【\s*单集策划\s*】(?P<body>.*?)(?:【\s*主体列表\s*】|【\s*场景列表\s*】|$)", raw, flags=re.S)
    if not m:
        return None

    body = m.group("body").strip()
    # Parse episode structure
    episodes = []
    current: Optional[Dict[str, Any]] = None

    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue

        # Detect episode header like "第1集" or "Ep 1"
        m_ep = re.match(r"^(?:第|Ep)\s*(\d+)\s*[集集](.*)", ln)
        if m_ep:
            if current:
                episodes.append(current)
            ep_num = int(m_ep.group(1))
            ep_title = m_ep.group(2).strip() or f"第{ep_num}集"
            current = {
                "id": f"ep-{ep_num:02d}",
                "number": ep_num,
                "title": ep_title,
                "summary": "",
                "shots": [],
            }
            continue

        if current:
            # Try to parse shots with pattern like "S1-01: description"
            m_shot = re.match(r"^([A-Za-z]\d+-\d+)\s*[:：]\s*(.+)", ln)
            if m_shot:
                shot_id = m_shot.group(1)
                shot_desc = m_shot.group(2).strip()
                current["shots"].append({
                    "id": shot_id,
                    "description": shot_desc,
                })
            else:
                # Accumulate summary
                current["summary"] = (current["summary"] + " " + ln).strip()

    if current:
        episodes.append(current)

    return {
        "version": "episode-plan.v1",
        "episodes": episodes,
        "raw_text": body,
    }


def parse_subject_catalog(raw: str) -> Optional[Dict[str, Any]]:
    """Extract subject catalog from raw text if marked with 【主体列表】."""
    m = re.search(r"【\s*主体列表\s*】(?P<body>.*?)(?:【\s*场景列表\s*】|【\s*角色视觉锚定\s*】|$)", raw, flags=re.S)
    if not m:
        return None

    body = m.group("body").strip()
    subjects = []
    current: Optional[Dict[str, Any]] = None

    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue

        # Detect subject header like "主体: 角色名" or "Subject: Name"
        m_sub = re.match(r"^(?:主体|Subject)[:：]\s*(.+)", ln, flags=re.I)
        if m_sub:
            if current:
                subjects.append(current)
            name = m_sub.group(1).strip()
            current = {
                "id": f"subj-{name}",
                "name": name,
                "type": "character",
                "description": "",
                "traits": [],
            }
            continue

        if current:
            # Trait lines like "- feature"
            if re.match(r"^[-*•]\s+", ln):
                trait = re.sub(r"^[-*•]\s+", "", ln).strip()
                current["traits"].append(trait)
            else:
                current["description"] = (current["description"] + " " + ln).strip()

    if current:
        subjects.append(current)

    return {
        "version": "subject-catalog.v1",
        "subjects": subjects,
        "raw_text": body,
    }


def parse_scene_catalog(raw: str) -> Optional[Dict[str, Any]]:
    """Extract scene catalog from raw text if marked with 【场景列表】."""
    m = re.search(r"【\s*场景列表\s*】(?P<body>.*?)(?:##\s*以下为逐条分镜|【\s*全局世界观|$)", raw, flags=re.S)
    if not m:
        return None

    body = m.group("body").strip()
    scenes = []

    # Parse lines like "Scene 1: Location" or "场景1: 地点"
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue

        m_scene = re.match(r"^(?:Scene|场景)\s*(\d+)\s*[:：]\s*(.+)", ln, flags=re.I)
        if m_scene:
            scene_num = int(m_scene.group(1))
            location = m_scene.group(2).strip()
            scenes.append({
                "id": f"scn-{scene_num:02d}",
                "number": scene_num,
                "location": location,
            })

    return {
        "version": "scene-catalog.v1",
        "scenes": scenes,
        "raw_text": body,
    }


def parse_global_capsules(raw: str) -> Tuple[Dict[str, Any], List[str], str]:
    warnings: List[str] = []

    style_section = ""
    m_style = re.search(
        r"【\s*全局世界观与风格设定\s*】(?P<body>.*?)(?:【\s*角色视觉锚定\s*】|##\s*以下为逐条分镜|$)",
        raw,
        flags=re.S,
    )
    if m_style:
        style_section = m_style.group("body").strip()
    else:
        warnings.append("未检测到【全局世界观与风格设定】段落，使用空风格胶囊。")

    role_section = ""
    m_roles = re.search(
        r"【\s*角色视觉锚定\s*】(?P<body>.*?)(?:##\s*以下为逐条分镜|$)",
        raw,
        flags=re.S,
    )
    if m_roles:
        role_section = m_roles.group("body").strip()

    characters: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    for ln in role_section.splitlines():
        line = ln.strip()
        if not line:
            continue
        m = re.match(r"角色[:：]\s*(.+)", line)
        if m:
            if current:
                current["description"] = "；".join(current.get("_parts", []))
                current.pop("_parts", None)
                characters.append(current)
            name = m.group(1).strip()
            current = {"id": f"char-{name}", "name": name, "_parts": []}
            continue
        if current and re.match(r"^[*\-•]\s+", line):
            current["_parts"].append(re.sub(r"^[*\-•]\s+", "", line))

    if current:
        current["description"] = "；".join(current.get("_parts", []))
        current.pop("_parts", None)
        characters.append(current)

    if role_section and not characters:
        warnings.append("检测到角色段落但未成功解析角色条目。")

    style_rules = [
        re.sub(r"^[*\-•]\s+", "", ln.strip())
        for ln in style_section.splitlines()
        if re.match(r"^[*\-•]\s+", ln.strip())
    ]

    style_capsule = {
        "summary": re.sub(r"\s+", " ", style_section)[:600],
        "visual_rules": style_rules,
        "raw_style_text": style_section,
    }

    return style_capsule, characters, "\n".join(warnings)


def split_shot_blocks(raw: str) -> List[Tuple[str, str]]:
    matches = list(re.finditer(r"【\s*([A-Za-z]\d+-\d+)\s*】", raw))
    blocks: List[Tuple[str, str]] = []

    if matches:
        for i, m in enumerate(matches):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            shot_id = m.group(1)
            body = raw[start:end].strip()
            blocks.append((shot_id, body))
        return blocks

    # fallback: split by headings like "场景1" or markdown separators
    chunks = [c.strip() for c in re.split(r"\n\s*---+\s*\n", raw) if c.strip()]
    if len(chunks) > 1:
        for idx, c in enumerate(chunks, start=1):
            blocks.append((f"S1-{idx:02d}", c))
        return blocks

    return [("S1-01", raw.strip())]


def parse_table_field(block: str, key: str) -> str:
    pattern = rf"\|\s*\*\*?{re.escape(key)}\*\*?\s*\|\s*(.*?)\s*\|"
    m = re.search(pattern, block, flags=re.S)
    return m.group(1).strip() if m else ""


def parse_labeled_fields(block: str) -> Dict[str, str]:
    keys = {
        "scene": ["场景", "场景名称"],
        "visual": ["画面内容"],
        "camera": ["镜头语言", "运镜"],
        "audio": ["音频", "音频氛围"],
        "narration": ["旁白"],
        "constraints": ["硬性约束", "约束"],
        "params": ["生成参数", "模型参数"],
    }

    out: Dict[str, str] = {k: "" for k in keys}

    lines = block.splitlines()
    current: Optional[str] = None

    def maybe_label(line: str) -> Optional[str]:
        for k, aliases in keys.items():
            for alias in aliases:
                if re.match(rf"^\s*{re.escape(alias)}\s*[:：]", line):
                    return k
        return None

    for raw_ln in lines:
        ln = raw_ln.strip()
        if not ln:
            continue

        label_key = maybe_label(ln)
        if label_key:
            current = label_key
            val = re.split(r"[:：]", ln, maxsplit=1)[1].strip() if re.search(r"[:：]", ln) else ""
            if val:
                out[current] = (out[current] + "\n" + val).strip() if out[current] else val
            continue

        if current:
            # stop at obvious new section title
            if ln.startswith("##"):
                current = None
                continue
            out[current] = (out[current] + "\n" + ln).strip() if out[current] else ln

    # scene fallback
    if not out["scene"]:
        m_scene = re.search(r"场景\d+\s*[:：]\s*(.+)", block)
        if m_scene:
            out["scene"] = m_scene.group(1).strip()

    return out


def naturalize_constraints(text: str) -> str:
    if not text:
        return ""
    parts = []
    for ln in text.splitlines():
        s = re.sub(r"^[*\-•]\d\)\.(]+\s*", "", ln.strip())
        if s:
            parts.append(s)
    return "；".join(parts)


def infer_resolution(params: str, default: str = "720p") -> str:
    m = re.search(r"(480p|720p|1080p)", params, flags=re.I)
    return m.group(1).lower() if m else default


def infer_ratio(params: str, default: str = "16:9") -> str:
    m = re.search(r"(16:9|4:3|1:1|3:4|9:16|21:9|adaptive)", params, flags=re.I)
    return m.group(1) if m else default


def infer_duration(params: str, default: int = 5) -> int:
    m = re.search(r"(\d+)\s*(?:s|秒)", params, flags=re.I)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return default


def compile_prompt(
    scene: str,
    visual: str,
    camera: str,
    narration: str,
    constraints: str,
    style_capsule: Dict[str, Any],
    character_capsule: List[Dict[str, Any]],
) -> Dict[str, str]:
    """Compile dual prompts: image_prompt (Seedream) + video_prompt (Seedance)."""
    style_summary = style_capsule.get("summary", "").strip()

    # Image prompt: 画风/景别/视角/机位/内容
    image_chunks: List[str] = []

    if style_summary:
        image_chunks.append(f"画风：{style_summary}")

    # Infer shot_size from visual/camera
    shot_size = "中景"
    shot_size_map = {
        "特写": ["特写", "close-up", "特写镜头"],
        "近景": ["近景", "中近景", "close-up"],
        "中景": ["中景", "medium shot"],
        "全景": ["全景", "wide shot", "全景镜头"],
        "远景": ["远景", "long shot", "远景镜头"],
    }
    combined = (visual or "") + " " + (camera or "")
    for size, keywords in shot_size_map.items():
        if any(k in combined.lower() for k in keywords):
            shot_size = size
            break
    image_chunks.append(f"景别：{shot_size}")

    # Infer view_angle
    view_angle = "平视"
    view_angle_map = {
        "俯视": ["俯视", "top-down", "上帝视角", "鸟瞰"],
        "仰视": ["仰视", "low-angle", "仰拍"],
        "侧视": ["侧视", "侧面"],
        "正面": ["正面", "front"],
    }
    for angle, keywords in view_angle_map.items():
        if any(k in combined.lower() for k in keywords):
            view_angle = angle
            break
    image_chunks.append(f"视角：{view_angle}")

    # Infer camera_position
    camera_position = "固定机位"
    camera_pos_map = {
        "跟随": ["跟", "following", "跟随"],
        "移动": ["移", "移动", "pan", "tracking"],
        "推": ["推", "push-in", "dolly in"],
        "拉": ["拉", "pull-out", "dolly out"],
    }
    for pos, keywords in camera_pos_map.items():
        if any(k in combined.lower() for k in keywords):
            camera_position = pos
            break
    image_chunks.append(f"机位：{camera_position}")

    if character_capsule:
        char_desc = "；".join([f"{c.get('name')}：{c.get('description', '')}" for c in character_capsule])
        image_chunks.append(f"角色：{char_desc}")

    if scene:
        image_chunks.append(f"场景：{scene}")

    if visual:
        image_chunks.append(f"画面内容：{visual}")

    c = naturalize_constraints(constraints)
    if c:
        image_chunks.append(f"关键视觉约束：{c}")

    # screen text hint (model-generated, no post overlay)
    quoted = re.findall(r"[“\"]([^”\"]{1,16})[”\"]", (visual or "") + "\n" + (constraints or ""))
    if quoted:
        t = quoted[0]
        if re.search(r"[\u4e00-\u9fff]", t):
            image_chunks.append(
                f"画内文字：清晰可读的简体中文全息文字""{t}""，字形完整、无乱码、边缘清晰。"
            )

    # Video prompt: dynamic description, movement, audio
    video_chunks: List[str] = []

    if style_summary:
        video_chunks.append(f"全局风格：{style_summary}")

    if scene:
        video_chunks.append(f"场景目标：{scene}")

    if visual:
        video_chunks.append(f"画面内容：{visual}")

    if camera:
        video_chunks.append(f"镜头语言：{camera}")

    c = naturalize_constraints(constraints)
    if c:
        video_chunks.append(f"关键视觉约束：{c}")

    if narration:
        video_chunks.append(f"旁白内容（请完整自然输出）：{narration}")

    return {
        "image_prompt": "\n".join([x for x in image_chunks if x]).strip(),
        "video_prompt": "\n".join([x for x in video_chunks if x]).strip(),
    }


def pick_value(shot: Dict[str, Any], global_cfg: Dict[str, Any], key: str, default: Any = None) -> Any:
    if key in shot:
        return shot.get(key)
    if key in global_cfg:
        return global_cfg.get(key)
    return default


def to_shot_id(raw_id: str, idx: int) -> str:
    if raw_id:
        m = re.search(r"(\d+)(?:\D+)?(\d+)?", raw_id)
        if m:
            if m.group(2):
                return f"s{int(m.group(1)):02d}-{int(m.group(2)):02d}"
            return f"s{int(m.group(1)):02d}"
    return f"s{idx:02d}"


def parse_text_story(
    raw: str,
    project_id: str,
    continuity_mode: str,
    default_ratio: str,
    default_resolution: str,
    default_duration: int,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Parse text and return: (storyboard, assets, report, staged_artifacts)"""
    style_capsule, characters, global_warn = parse_global_capsules(raw)

    # Parse staged artifacts
    outline = parse_outline(raw)
    episode_plan = parse_episode_plan(raw)
    subject_catalog = parse_subject_catalog(raw)
    scene_catalog = parse_scene_catalog(raw)

    # Build staged artifacts dict
    staged_artifacts = {
        "version": "staged-artifacts.v1",
        "project_id": project_id,
        "outline": outline if outline else None,
        "episode_plan": episode_plan if episode_plan else None,
        "subject_catalog": subject_catalog if subject_catalog else None,
        "scene_catalog": scene_catalog if scene_catalog else None,
    }

    blocks = split_shot_blocks(raw)
    shots: List[Dict[str, Any]] = []
    warnings: List[str] = []
    inferred_fields: List[str] = [
        "global.model=doubao-seedance-1-5-pro-251215",
        "global.image_model=doubao-seedream-5-0-260128",
        "global.generate_audio=true",
    ]

    chain_last_frame = False

    seen_ids: set[str] = set()

    for idx, (raw_id, body) in enumerate(blocks, start=1):
        fields = parse_labeled_fields(body)

        params = fields.get("params", "")
        resolution = infer_resolution(params, default_resolution)
        ratio = infer_ratio(params, default_ratio)
        duration = infer_duration(params, default_duration)
        draft = bool(re.search(r"\bdraft\b", params, flags=re.I))
        return_last_frame = bool(re.search(r"return_last_frame\s*=\s*true|return-last-frame|return_last_frame=true", params, flags=re.I))

        use_prev = bool(re.search(r"first_frame\s*=\s*上一条last_frame|上一条\s*last_frame", params, flags=re.I))
        if use_prev:
            chain_last_frame = True

        base_shot_id = to_shot_id(raw_id, idx)
        shot_id = base_shot_id
        if shot_id in seen_ids:
            warnings.append(f"检测到重复镜头编号 {base_shot_id}，已跳过重复块。")
            continue
        seen_ids.add(shot_id)

        prompts = compile_prompt(
            scene=fields.get("scene", ""),
            visual=fields.get("visual", ""),
            camera=fields.get("camera", ""),
            narration=fields.get("narration", ""),
            constraints=fields.get("constraints", ""),
            style_capsule=style_capsule,
            character_capsule=characters,
        )

        shot: Dict[str, Any] = {
            "id": shot_id,
            "title": fields.get("scene", "") or raw_id,
            # v1 backward compatibility: unified prompt
            "prompt": prompts.get("video_prompt", ""),
            # v0.1.6-a new fields: dual prompts
            "image_prompt": prompts.get("image_prompt", ""),
            "video_prompt": prompts.get("video_prompt", ""),
            # explicit fields (from Seko)
            "visual_description": fields.get("visual", ""),
            "composition": fields.get("camera", ""),
            "camera_movement": fields.get("camera", ""),
            "voice_role": "",
            "dialogue": fields.get("narration", ""),
            # technical fields
            "ratio": ratio,
            "duration": duration,
            "resolution": resolution,
            "draft": draft,
            "return_last_frame": return_last_frame,
            "generate_audio": True,
            "meta": {
                "source_raw_id": raw_id,
                "source_fields": fields,
            },
        }
        if use_prev:
            shot["use_prev_last_frame"] = True

        shots.append(shot)

    continuity = {
        "mode": continuity_mode,
        "chain_last_frame": chain_last_frame if continuity_mode != "off" else False,
    }

    storyboard = {
        "version": "storyboard.v1",
        "project_id": project_id,
        "global": {
            "model": DEFAULT_VIDEO_MODEL,
            "image_model": DEFAULT_IMAGE_MODEL,
            "ratio": default_ratio,
            "duration": default_duration,
            "resolution": default_resolution,
            "generate_audio": True,
            "return_last_frame": False,
        },
        "continuity": continuity,
        "prompt_policy": {
            "exclude_control_fields_from_model_prompt": True,
            "inject_global_capsule_each_shot": True,
            "optimization_level": "balanced",
        },
        "shots": shots,
    }

    if global_warn:
        warnings.extend(global_warn.splitlines())

    assets = {
        "assets_version": "assets.v1",
        "project_id": project_id,
        "style_capsule": style_capsule,
        "characters": characters,
    }

    report = {
        "input_type": "text",
        "shots_detected": len(shots),
        "characters_detected": len(characters),
        "warnings": warnings,
        "inferred_fields": inferred_fields,
        "stages_detected": [
            ("outline", outline is not None),
            ("episode_plan", episode_plan is not None),
            ("subject_catalog", subject_catalog is not None),
            ("scene_catalog", scene_catalog is not None),
        ],
    }

    return storyboard, assets, report, staged_artifacts


def load_staged_artifacts(path: Optional[Path]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Load v0.1.5-b staged-artifacts.json if exists."""
    if not path or not path.exists():
        return None, None

    try:
        obj = load_json(path)
    except json.JSONDecodeError:
        raise PrepareError(f"Staged artifacts 文件格式错误：{path}")

    # Expected structure:
    # {
    #   "version": "staged-artifacts.v1",
    #   "outline": {...},
    #   "episode_plan": {...},
    #   "subject_catalog": {...},
    #   "scene_catalog": {...},
    #   "storyboard": {"version":"storyboard.v1", ...},
    #   "assets": {...}
    # }

    if not isinstance(obj, dict):
        raise PrepareError(f"Staged artifacts 格式错误：应为对象")

    version = obj.get("version")
    if version != "staged-artifacts.v1":
        raise PrepareError(f"Staged artifacts 版本不支持：{version}")

    sb = obj.get("storyboard")
    assets = obj.get("assets")

    if not isinstance(sb, dict):
        raise PrepareError("Staged artifacts 中缺少 storyboard")

    if not isinstance(assets, dict):
        raise PrepareError("Staged artifacts 中缺少 assets")

    return sb, assets


def merge_staged_into_primary(
    primary: Dict[str, Any],
    primary_assets: Dict[str, Any],
    staged_sb: Optional[Dict[str, Any]],
    staged_assets: Optional[Dict[str, Any]],
    global_cfg_override: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Merge staged artifacts into primary storyboard/assets if provided."""
    merged_assets = dict(primary_assets or {})

    if not staged_sb:
        if staged_assets:
            merged_assets = {**merged_assets, **staged_assets}
        return primary, merged_assets

    # Merge global settings
    if global_cfg_override:
        primary["global"] = {**primary.get("global", {}), **global_cfg_override}

    # Override shots with staged shot data if any
    staged_shots = staged_sb.get("shots", []) if isinstance(staged_sb.get("shots"), list) else []
    if staged_shots:
        # Create lookup map
        staged_map = {s.get("id"): s for s in staged_shots}
        for i, shot in enumerate(primary.get("shots", [])):
            sid = shot.get("id")
            if sid in staged_map:
                # Preserve explicitly set fields
                override = staged_map[sid]
                for k, v in override.items():
                    if k != "id" and v is not None:
                        shot[k] = v
            if i >= len(staged_shots):
                # Append any extra shots from staged that aren't in primary
                primary["shots"].append(override)

    # Merge assets
    if staged_assets:
        if staged_assets.get("style_capsule"):
            existing = merged_assets.get("style_capsule", {}) if isinstance(merged_assets, dict) else {}
            merged_assets["style_capsule"] = {**existing, **staged_assets.get("style_capsule")}

        if staged_assets.get("characters"):
            merged_assets["characters"] = staged_assets.get("characters")

        # Keep other staged asset keys too
        for k, v in staged_assets.items():
            if k not in merged_assets:
                merged_assets[k] = v

    # Ensure project_id consistency
    if staged_sb.get("project_id"):
        primary["project_id"] = staged_sb.get("project_id")

    if isinstance(merged_assets, dict):
        merged_assets["project_id"] = primary.get("project_id", merged_assets.get("project_id", ""))

    return primary, merged_assets


def parse_any_input(
    raw: str,
    project_id: str,
    continuity_mode: str,
    default_ratio: str,
    default_resolution: str,
    default_duration: int,
    staged_path: Optional[Path] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    input_type = detect_input_type(raw)

    if input_type == "empty" and not staged_path:
        raise PrepareError("输入为空，无法生成 storyboard。")

    if input_type == "json":
        obj = json.loads(raw)
        if isinstance(obj, dict):
            # Case A: already storyboard.v1
            if obj.get("version") == "storyboard.v1":
                storyboard = obj
                assets = {
                    "assets_version": "assets.v1",
                    "project_id": storyboard.get("project_id", project_id),
                    "style_capsule": {"summary": "", "visual_rules": [], "raw_style_text": ""},
                    "characters": [],
                }
                report = {
                    "input_type": "json",
                    "shots_detected": len(storyboard.get("shots", [])) if isinstance(storyboard.get("shots"), list) else 0,
                    "characters_detected": 0,
                    "warnings": ["输入已是 storyboard.v1，按原样输出 draft。"],
                    "inferred_fields": [],
                    "stages_detected": [],
                }
                staged_artifacts = {
                    "version": "staged-artifacts.v1",
                    "project_id": storyboard.get("project_id", project_id),
                    "outline": None,
                    "episode_plan": None,
                    "subject_catalog": None,
                    "scene_catalog": None,
                }
                return storyboard, assets, report, staged_artifacts

            # Case B: sub-agent packaged output
            # {
            #   "storyboard": {"version":"storyboard.v1", ...},
            #   "assets": {"assets_version":"assets.v1", ...},
            #   "parse_report": {...}
            # }
            sb = obj.get("storyboard")
            if isinstance(sb, dict) and sb.get("version") == "storyboard.v1":
                storyboard = sb
                assets = obj.get("assets") if isinstance(obj.get("assets"), dict) else {
                    "assets_version": "assets.v1",
                    "project_id": sb.get("project_id", project_id),
                    "style_capsule": {"summary": "", "visual_rules": [], "raw_style_text": ""},
                    "characters": [],
                }
                report = obj.get("parse_report") if isinstance(obj.get("parse_report"), dict) else {
                    "input_type": "json-subagent",
                    "shots_detected": len(storyboard.get("shots", [])) if isinstance(storyboard.get("shots"), list) else 0,
                    "characters_detected": len(assets.get("characters", [])) if isinstance(assets.get("characters"), list) else 0,
                    "warnings": ["检测到 sub-agent 结构化输出，已直接采用。"],
                    "inferred_fields": [],
                    "stages_detected": [],
                }
                staged_artifacts = {
                    "version": "staged-artifacts.v1",
                    "project_id": storyboard.get("project_id", project_id),
                    "outline": obj.get("outline") if isinstance(obj.get("outline"), dict) else None,
                    "episode_plan": obj.get("episode_plan") if isinstance(obj.get("episode_plan"), dict) else None,
                    "subject_catalog": obj.get("subject_catalog") if isinstance(obj.get("subject_catalog"), dict) else None,
                    "scene_catalog": obj.get("scene_catalog") if isinstance(obj.get("scene_catalog"), dict) else None,
                }
                return storyboard, assets, report, staged_artifacts

    # Load staged artifacts if path provided
    if staged_path:
        staged_sb, staged_assets = load_staged_artifacts(staged_path)
    else:
        staged_sb, staged_assets = None, None

    # Case C: staged-only input (no raw text/json)
    if input_type == "empty" and staged_sb:
        storyboard = staged_sb
        assets = staged_assets if isinstance(staged_assets, dict) else {
            "assets_version": "assets.v1",
            "project_id": storyboard.get("project_id", project_id),
            "style_capsule": {"summary": "", "visual_rules": [], "raw_style_text": ""},
            "characters": [],
        }
        report = {
            "input_type": "staged-only",
            "shots_detected": len(storyboard.get("shots", [])) if isinstance(storyboard.get("shots"), list) else 0,
            "characters_detected": len(assets.get("characters", [])) if isinstance(assets.get("characters"), list) else 0,
            "warnings": [f"仅使用 staged artifacts: {staged_path}"],
            "inferred_fields": [],
            "stages_detected": [],
        }
        final_staged = {
            "version": "staged-artifacts.v1",
            "project_id": storyboard.get("project_id", project_id),
            "outline": None,
            "episode_plan": None,
            "subject_catalog": None,
            "scene_catalog": None,
            "storyboard": storyboard,
            "assets": assets,
        }
        return storyboard, assets, report, final_staged

    # Fallback to text parser
    primary_storyboard, primary_assets, report, primary_staged = parse_text_story(
        raw=raw,
        project_id=project_id,
        continuity_mode=continuity_mode,
        default_ratio=default_ratio,
        default_resolution=default_resolution,
        default_duration=default_duration,
    )

    # Merge staged into primary
    storyboard, assets = merge_staged_into_primary(
        primary=primary_storyboard,
        primary_assets=primary_assets,
        staged_sb=staged_sb,
        staged_assets=staged_assets,
        global_cfg_override={
            "model": DEFAULT_VIDEO_MODEL,
            "image_model": DEFAULT_IMAGE_MODEL,
        },
    )

    # Merge stage artifacts from staged input if provided
    final_staged = primary_staged
    if staged_sb:
        final_staged = {
            **primary_staged,
            **staged_sb,
        }

    report["input_type"] = f"{'text' if not staged_path else 'json+staged'}"
    if staged_sb or staged_assets:
        report["warnings"].append(f"已加载并合并 staged artifacts：{staged_path}")

    return storyboard, assets, report, final_staged


def render_parse_report(report: Dict[str, Any]) -> str:
    warnings = report.get("warnings", []) or []
    inferred = report.get("inferred_fields", []) or []
    stages_detected = report.get("stages_detected", []) or []

    lines = [
        "# Parse Report",
        "",
        f"- input_type: `{report.get('input_type', 'unknown')}`",
        f"- shots_detected: `{report.get('shots_detected', 0)}`",
        f"- characters_detected: `{report.get('characters_detected', 0)}`",
        "",
        "## Stages Detected",
    ]

    if stages_detected:
        for stage_name, detected in stages_detected:
            status = "✓" if detected else "✗"
            lines.append(f"- {status} `{stage_name}`")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## Inferred Fields")
    if inferred:
        lines.extend([f"- {x}" for x in inferred])
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## Warnings")
    if warnings:
        lines.extend([f"- {x}" for x in warnings])
    else:
        lines.append("- (none)")

    return "\n".join(lines) + "\n"


def render_confirmation_message(storyboard: Dict[str, Any], plan_dir: Path) -> str:
    shots = storyboard.get("shots", []) if isinstance(storyboard.get("shots"), list) else []
    continuity = storyboard.get("continuity", {}) if isinstance(storyboard.get("continuity"), dict) else {}

    lines = [
        "# Confirmation Request",
        "",
        "已生成可执行草稿，请确认：",
        f"- project_id: `{storyboard.get('project_id', '')}`",
        f"- shots: `{len(shots)}`",
        f"- continuity.mode: `{continuity.get('mode', 'style-anchor')}`",
        f"- continuity.chain_last_frame: `{continuity.get('chain_last_frame', False)}`",
        "",
        "## Shot Summary",
    ]

    for i, s in enumerate(shots, start=1):
        lines.append(f"- {i}. `{s.get('id', f's{i:02d}')}` | `{s.get('title', '')}`")

    lines.extend([
        "",
        "## Next Step",
        f"1. 如需修改，请编辑：`{plan_dir / 'storyboard.draft.v1.json'}`",
        f"2. 确认后可复制为：`{plan_dir / 'storyboard.confirmed.v1.json'}`",
        "3. 执行 run：",
        "```bash",
        f"python3 scripts/orchestrate_story.py run --storyboard {plan_dir / 'storyboard.confirmed.v1.json'}",
        "```",
    ])

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare storyboard/assets from unstructured input")
    parser.add_argument("--input-text", help="Raw text input")
    parser.add_argument("--input-file", help="Path to txt/json file")
    parser.add_argument("--staged-artifacts", help="Path to v0.1.5-b staged-artifacts.json")
    parser.add_argument("--output-dir", default="./outputs", help="Output directory")
    parser.add_argument("--project-id", help="Optional project id")
    parser.add_argument("--continuity-mode", choices=["style-anchor", "chain-last-frame", "hybrid", "off"], default="style-anchor")
    parser.add_argument("--default-ratio", default="16:9")
    parser.add_argument("--default-resolution", default="720p")
    parser.add_argument("--default-duration", type=int, default=5)

    args = parser.parse_args()

    if not args.input_text and not args.input_file and not args.staged_artifacts:
        raise PrepareError("请提供 --input-text、--input-file 或 --staged-artifacts。")

    if args.input_text and args.input_file:
        raise PrepareError("--input-text 与 --input-file 只能二选一。")

    raw = ""
    if args.input_text or args.input_file:
        if args.input_text:
            raw = args.input_text or ""
        else:
            raw = load_text(Path(args.input_file).expanduser())

    # staged-only mode is allowed
    if not raw and not args.staged_artifacts:
        raise PrepareError("输入为空，无法生成 storyboard。")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    project_id = args.project_id or f"story-{ts}"
    plan_dir = Path(args.output_dir).expanduser() / f"plan-{ts}"
    plan_dir.mkdir(parents=True, exist_ok=True)

    storyboard, assets, report, staged_artifacts = parse_any_input(
        raw=raw,
        project_id=project_id,
        continuity_mode=args.continuity_mode,
        default_ratio=args.default_ratio,
        default_resolution=args.default_resolution,
        default_duration=args.default_duration,
        staged_path=Path(args.staged_artifacts).expanduser() if args.staged_artifacts else None,
    )

    # ensure project_id consistency
    storyboard["project_id"] = storyboard.get("project_id") or project_id
    assets["project_id"] = storyboard["project_id"]
    staged_artifacts["project_id"] = storyboard["project_id"]

    draft_path = plan_dir / "storyboard.draft.v1.json"
    assets_path = plan_dir / "assets.v1.json"
    report_path = plan_dir / "parse-report.md"
    confirm_path = plan_dir / "confirmation-message.md"
    staged_path = plan_dir / "staged-artifacts.v1.json"

    # Write main files
    draft_path.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8")
    assets_path.write_text(json.dumps(assets, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(render_parse_report(report), encoding="utf-8")
    confirm_path.write_text(render_confirmation_message(storyboard, plan_dir), encoding="utf-8")

    # Write staged artifacts file
    staged_path.write_text(json.dumps(staged_artifacts, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write individual stage JSON files if they exist
    output_files = {
        "storyboard_draft": str(draft_path),
        "assets": str(assets_path),
        "parse_report": str(report_path),
        "confirmation_message": str(confirm_path),
        "staged_artifacts": str(staged_path),
    }

    if staged_artifacts.get("outline"):
        outline_path = plan_dir / "outline.v1.json"
        outline_path.write_text(json.dumps(staged_artifacts["outline"], ensure_ascii=False, indent=2), encoding="utf-8")
        output_files["outline"] = str(outline_path)

    if staged_artifacts.get("episode_plan"):
        episode_path = plan_dir / "episode-plan.v1.json"
        episode_path.write_text(json.dumps(staged_artifacts["episode_plan"], ensure_ascii=False, indent=2), encoding="utf-8")
        output_files["episode_plan"] = str(episode_path)

    if staged_artifacts.get("subject_catalog"):
        subject_path = plan_dir / "subject-catalog.v1.json"
        subject_path.write_text(json.dumps(staged_artifacts["subject_catalog"], ensure_ascii=False, indent=2), encoding="utf-8")
        output_files["subject_catalog"] = str(subject_path)

    if staged_artifacts.get("scene_catalog"):
        scene_path = plan_dir / "scene-catalog.v1.json"
        scene_path.write_text(json.dumps(staged_artifacts["scene_catalog"], ensure_ascii=False, indent=2), encoding="utf-8")
        output_files["scene_catalog"] = str(scene_path)

    print(json.dumps(
        {
            "ok": True,
            "plan_dir": str(plan_dir),
            **output_files,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    try:
        main()
    except PrepareError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
