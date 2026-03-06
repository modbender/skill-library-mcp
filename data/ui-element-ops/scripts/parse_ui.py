#!/usr/bin/env python3
"""Parse UI screenshot into element types and coordinates using OmniParser.

Usage example:
  python3 parse_ui.py \
    --image ./screen.png \
    --output ./screen.elements.json \
    --overlay ./screen.overlay.png \
    --omniparser-dir /path/to/OmniParser
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import types
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_TYPE_RULES: Dict[str, List[str]] = {
    "button": [
        "login",
        "log in",
        "sign in",
        "submit",
        "confirm",
        "ok",
        "next",
        "done",
        "save",
        "send",
        "cancel",
        "back",
        "continue",
        "buy",
        "pay",
        "install",
        "open",
        "allow",
    ],
    "input": [
        "search",
        "username",
        "password",
        "email",
        "phone",
        "type here",
        "enter",
        "placeholder",
    ],
    "checkbox": ["checkbox", "accept terms", "remember me", "agree"],
    "switch": ["toggle", "switch", "on", "off"],
    "tab": ["home", "feed", "profile", "settings", "notifications"],
    "menu": ["menu", "more", "hamburger", "options"],
    "link": ["http", ".com", ".cn", ".net", ".org", "www."],
    "list_item": ["item", "row", "option", "result"],
}


@dataclass
class ParserConfig:
    image: Path
    output: Path
    overlay: Optional[Path]
    omniparser_dir: Path
    som_model_path: str
    caption_model_name: str
    caption_model_path: str
    box_threshold: float
    iou_threshold: float
    use_paddleocr: bool
    ocr_text_threshold: float
    imgsz: Optional[int]
    type_rules_path: Optional[Path]


def parse_args() -> ParserConfig:
    parser = argparse.ArgumentParser(
        description="Parse UI screenshot into structured elements with OmniParser."
    )
    parser.add_argument("--image", required=True, type=Path, help="Input screenshot path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path. Default: <image>.elements.json",
    )
    parser.add_argument(
        "--overlay",
        type=Path,
        default=None,
        help="Optional output path for OmniParser overlay image.",
    )
    parser.add_argument(
        "--omniparser-dir",
        type=Path,
        default=Path(os.environ.get("OMNIPARSER_DIR", "")),
        help="Local OmniParser repository directory.",
    )
    parser.add_argument(
        "--som-model-path",
        default="weights/icon_detect/model.pt",
        help="Path relative to --omniparser-dir if not absolute.",
    )
    parser.add_argument(
        "--caption-model-name",
        default="florence2",
        choices=["florence2", "blip2", "phi3_v"],
        help="Caption model name used by OmniParser.",
    )
    parser.add_argument(
        "--caption-model-path",
        default="weights/icon_caption_florence",
        help="Path relative to --omniparser-dir if not absolute.",
    )
    parser.add_argument(
        "--box-threshold",
        type=float,
        default=0.05,
        help="Detection confidence threshold.",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.7,
        help="IoU threshold for overlap filtering.",
    )
    parser.add_argument(
        "--use-paddleocr",
        action="store_true",
        help="Use PaddleOCR instead of EasyOCR.",
    )
    parser.add_argument(
        "--ocr-text-threshold",
        type=float,
        default=0.8,
        help="OCR text confidence threshold.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=None,
        help="Optional icon detect image size.",
    )
    parser.add_argument(
        "--type-rules",
        type=Path,
        default=None,
        help="Optional JSON file to override type keyword rules.",
    )
    args = parser.parse_args()

    if not args.image.exists():
        raise FileNotFoundError(f"--image not found: {args.image}")
    if not args.omniparser_dir:
        raise ValueError("Provide --omniparser-dir or set OMNIPARSER_DIR.")
    if not args.omniparser_dir.exists():
        raise FileNotFoundError(f"--omniparser-dir not found: {args.omniparser_dir}")

    output = args.output
    if output is None:
        output = args.image.with_suffix("").with_suffix(".elements.json")

    return ParserConfig(
        image=args.image.resolve(),
        output=output.resolve(),
        overlay=args.overlay.resolve() if args.overlay else None,
        omniparser_dir=args.omniparser_dir.resolve(),
        som_model_path=args.som_model_path,
        caption_model_name=args.caption_model_name,
        caption_model_path=args.caption_model_path,
        box_threshold=args.box_threshold,
        iou_threshold=args.iou_threshold,
        use_paddleocr=args.use_paddleocr,
        ocr_text_threshold=args.ocr_text_threshold,
        imgsz=args.imgsz,
        type_rules_path=args.type_rules.resolve() if args.type_rules else None,
    )


def resolve_model_path(base_dir: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((base_dir / value).resolve())


def ensure_optional_paddleocr_stub() -> None:
    """Provide a lightweight fallback when paddleocr is unavailable.

    OmniParser imports PaddleOCR at module import time even when `use_paddleocr=False`.
    This stub allows the import path to succeed without installing paddleocr.
    """
    try:
        __import__("paddleocr")
        return
    except Exception:
        pass

    stub = types.ModuleType("paddleocr")

    class PaddleOCR:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def ocr(self, *_args: Any, **_kwargs: Any) -> List[Any]:
            return [[]]

    stub.PaddleOCR = PaddleOCR  # type: ignore[attr-defined]
    sys.modules["paddleocr"] = stub


def load_type_rules(path: Optional[Path]) -> Dict[str, List[str]]:
    if path is None:
        return DEFAULT_TYPE_RULES
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("--type-rules must be a JSON object.")
    rules: Dict[str, List[str]] = {}
    for key, value in data.items():
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError(f"Invalid type rule for '{key}', expected list[str].")
        rules[key] = value
    return rules


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def normalize_type(
    raw_type: str,
    clickable: bool,
    content: Optional[str],
    bbox_norm: List[float],
    rules: Dict[str, List[str]],
) -> str:
    text = (content or "").strip().lower()
    x1, y1, x2, y2 = bbox_norm
    width = max(1e-6, x2 - x1)
    height = max(1e-6, y2 - y1)
    aspect_ratio = width / height

    if raw_type == "text":
        if text and contains_any(text, rules.get("link", [])):
            return "link"
        return "text"

    if not clickable:
        if aspect_ratio > 1.8 and text:
            return "text"
        return "image"

    if text:
        if contains_any(text, rules.get("input", [])) and aspect_ratio > 1.6:
            return "input"
        if contains_any(text, rules.get("checkbox", [])):
            return "checkbox"
        if contains_any(text, rules.get("switch", [])):
            return "switch"
        if contains_any(text, rules.get("tab", [])):
            return "tab"
        if contains_any(text, rules.get("menu", [])):
            return "menu"
        if contains_any(text, rules.get("list_item", [])):
            return "list_item"
        if contains_any(text, rules.get("button", [])):
            return "button"

    # Fallbacks for interactable regions from detector.
    if aspect_ratio > 2.2 and text:
        return "input"
    if text:
        return "button"
    return "icon"


def clamp_bbox_norm(bbox_norm: List[float]) -> List[float]:
    x1, y1, x2, y2 = bbox_norm
    x1 = min(max(x1, 0.0), 1.0)
    y1 = min(max(y1, 0.0), 1.0)
    x2 = min(max(x2, 0.0), 1.0)
    y2 = min(max(y2, 0.0), 1.0)
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return [x1, y1, x2, y2]


def norm_to_px(bbox_norm: List[float], width: int, height: int) -> List[int]:
    x1, y1, x2, y2 = bbox_norm
    return [
        max(0, min(width - 1, int(round(x1 * width)))),
        max(0, min(height - 1, int(round(y1 * height)))),
        max(0, min(width - 1, int(round(x2 * width)))),
        max(0, min(height - 1, int(round(y2 * height)))),
    ]


def parse_ui(config: ParserConfig) -> Dict[str, Any]:
    sys.path.insert(0, str(config.omniparser_dir))
    ensure_optional_paddleocr_stub()

    try:
        from PIL import Image
        from util.utils import (  # type: ignore[import-not-found]
            check_ocr_box,
            get_caption_model_processor,
            get_som_labeled_img,
            get_yolo_model,
        )
    except Exception as exc:
        raise RuntimeError(
            "Failed to import OmniParser modules. Make sure dependencies are installed "
            "inside your Python environment."
        ) from exc

    type_rules = load_type_rules(config.type_rules_path)

    image = Image.open(config.image).convert("RGB")
    width, height = image.size

    box_overlay_ratio = max(width, height) / 3200
    draw_bbox_config = {
        "text_scale": 0.8 * box_overlay_ratio,
        "text_thickness": max(int(2 * box_overlay_ratio), 1),
        "text_padding": max(int(3 * box_overlay_ratio), 1),
        "thickness": max(int(3 * box_overlay_ratio), 1),
    }

    som_model_path = resolve_model_path(config.omniparser_dir, config.som_model_path)
    caption_model_path = resolve_model_path(config.omniparser_dir, config.caption_model_path)

    som_model = get_yolo_model(model_path=som_model_path)
    caption_model_processor = get_caption_model_processor(
        model_name=config.caption_model_name,
        model_name_or_path=caption_model_path,
    )

    (ocr_text, ocr_bbox), _ = check_ocr_box(
        image,
        display_img=False,
        output_bb_format="xyxy",
        goal_filtering=None,
        easyocr_args={"paragraph": False, "text_threshold": config.ocr_text_threshold},
        use_paddleocr=config.use_paddleocr,
    )

    som_image_base64, _label_coordinates, parsed_content = get_som_labeled_img(
        image,
        model=som_model,
        BOX_TRESHOLD=config.box_threshold,
        output_coord_in_ratio=True,
        ocr_bbox=ocr_bbox,
        draw_bbox_config=draw_bbox_config,
        caption_model_processor=caption_model_processor,
        ocr_text=ocr_text,
        use_local_semantics=True,
        iou_threshold=config.iou_threshold,
        scale_img=False,
        imgsz=config.imgsz,
        batch_size=128,
    )

    elements: List[Dict[str, Any]] = []
    for idx, item in enumerate(parsed_content):
        raw_bbox = item.get("bbox")
        if raw_bbox is None or len(raw_bbox) != 4:
            continue

        bbox_norm = clamp_bbox_norm([float(v) for v in raw_bbox])
        bbox_px = norm_to_px(bbox_norm, width, height)

        raw_type = str(item.get("type", "unknown"))
        clickable = bool(item.get("interactivity", False))
        content = item.get("content")
        content_str = str(content) if content is not None else None

        norm_type = normalize_type(
            raw_type=raw_type,
            clickable=clickable,
            content=content_str,
            bbox_norm=bbox_norm,
            rules=type_rules,
        )

        cx = int(round((bbox_px[0] + bbox_px[2]) / 2))
        cy = int(round((bbox_px[1] + bbox_px[3]) / 2))

        elements.append(
            {
                "id": f"e_{idx:04d}",
                "type": norm_type,
                "raw_type": raw_type,
                "bbox_px": bbox_px,
                "bbox_norm": [round(v, 6) for v in bbox_norm],
                "center_px": [cx, cy],
                "text": content_str,
                "clickable": clickable,
                "confidence": None,
                "source": item.get("source", "omniparser"),
            }
        )

    result: Dict[str, Any] = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": {
            "name": "omniparser",
            "box_threshold": config.box_threshold,
            "iou_threshold": config.iou_threshold,
            "use_paddleocr": config.use_paddleocr,
            "ocr_text_threshold": config.ocr_text_threshold,
            "caption_model_name": config.caption_model_name,
            "som_model_path": som_model_path,
            "caption_model_path": caption_model_path,
        },
        "image": {
            "path": str(config.image),
            "width": width,
            "height": height,
        },
        "counts": {
            "total": len(elements),
            "clickable": sum(1 for e in elements if e["clickable"]),
            "by_type": _count_by_type(elements),
        },
        "elements": elements,
    }

    if config.overlay:
        config.overlay.parent.mkdir(parents=True, exist_ok=True)
        with config.overlay.open("wb") as f:
            f.write(base64.b64decode(som_image_base64))

    config.output.parent.mkdir(parents=True, exist_ok=True)
    with config.output.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def _count_by_type(elements: List[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for e in elements:
        t = str(e.get("type", "unknown"))
        out[t] = out.get(t, 0) + 1
    return out


def main() -> None:
    config = parse_args()
    result = parse_ui(config)
    print(
        f"Parsed {result['counts']['total']} elements "
        f"from {config.image} -> {config.output}"
    )
    if config.overlay:
        print(f"Overlay image saved to {config.overlay}")


if __name__ == "__main__":
    main()
