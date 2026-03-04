#!/usr/bin/env python3
"""Operate desktop UI using parsed element JSON from parse_ui.py.

Headless note:
  - Works without GUI: list, find, wait, calibrate (when using existing elements JSON).
  - Requires GUI session: click, click-xy, type, key, hotkey, screenshot, screen-info.

Examples:
  python3 operate_ui.py list --elements ./1.elements.json
  python3 operate_ui.py find --elements ./1.elements.json --type button --text-contains login
  python3 operate_ui.py find --elements ./1.elements.json --text-regex "sign\\s*in" --click
  python3 operate_ui.py wait --elements ./1.elements.json --state appear --type button --text-contains continue
  python3 operate_ui.py click --elements ./1.elements.json --id e_0007
  python3 operate_ui.py click-xy --x 800 --y 520
  python3 operate_ui.py click-xy --x 420 --y 300 --coord-space parsed --coord-profile ./coord_profile.json
  python3 operate_ui.py type --text "hello world"
  python3 operate_ui.py key --key enter
  python3 operate_ui.py hotkey --keys command c
  python3 operate_ui.py screenshot
  python3 operate_ui.py calibrate --parsed-size 1515 2880 --actual-size 982 1864 --output ./coord_profile.json
  python3 operate_ui.py calibrate --parsed-anchor 300 200 --actual-anchor 620 430 --parsed-anchor-2 1200 2400 --actual-anchor-2 1010 1690 --output ./coord_profile.json
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass
class CoordProfile:
    x_scale: float = 1.0
    y_scale: float = 1.0
    x_offset: float = 0.0
    y_offset: float = 0.0
    display_origin_x: float = 0.0
    display_origin_y: float = 0.0
    name: str = "default"
    created_at: str = ""

    @staticmethod
    def identity() -> "CoordProfile":
        return CoordProfile(created_at=utc_now())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"elements json not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_elements(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    elements = data.get("elements", [])
    if not isinstance(elements, list):
        raise ValueError("Invalid JSON: 'elements' must be a list.")
    return elements


def find_element(elements: List[Dict[str, Any]], element_id: str) -> Dict[str, Any]:
    for elem in elements:
        if str(elem.get("id")) == element_id:
            return elem
    raise ValueError(f"Element id not found: {element_id}")


def parse_bool_str(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    s = str(value).strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return True
    if s in {"false", "0", "no", "n"}:
        return False
    return None


def element_text(elem: Dict[str, Any]) -> str:
    for key in ("text", "content"):
        if key in elem and elem[key] is not None:
            return str(elem[key])
    return ""


def element_bbox_px(elem: Dict[str, Any]) -> Optional[Tuple[int, int, int, int]]:
    bbox = elem.get("bbox_px")
    if isinstance(bbox, list) and len(bbox) == 4:
        x1, y1, x2, y2 = [int(v) for v in bbox]
        return x1, y1, x2, y2
    return None


def element_center(elem: Dict[str, Any]) -> Tuple[int, int]:
    center = elem.get("center_px")
    if isinstance(center, list) and len(center) == 2:
        return int(center[0]), int(center[1])

    bbox = element_bbox_px(elem)
    if bbox:
        x1, y1, x2, y2 = bbox
        return int(round((x1 + x2) / 2)), int(round((y1 + y2) / 2))

    raise ValueError(f"Element has no valid center/bbox: {elem.get('id')}")


def element_area(elem: Dict[str, Any]) -> int:
    bbox = element_bbox_px(elem)
    if not bbox:
        return 0
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)


def require_pyautogui():
    try:
        import pyautogui  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "pyautogui is required for UI operation. Install it with:\n"
            "  pip install pyautogui"
        ) from exc
    return pyautogui


def apply_delay(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


def default_screenshot_path() -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    rand = secrets.token_hex(4)
    return Path(tempfile.gettempdir()) / f"ui-shot-{ts}-{rand}.png"


def default_coord_profile_path() -> Path:
    return Path.cwd() / "coord_profile.json"


def expand_csv(values: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = []
    if not values:
        return out
    for v in values:
        if v is None:
            continue
        for piece in str(v).split(","):
            p = piece.strip()
            if p:
                out.append(p)
    return out


def load_coord_profile(path: Optional[Path]) -> CoordProfile:
    if path is None:
        return CoordProfile.identity()
    if not path.exists():
        raise FileNotFoundError(f"coord profile not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    display_origin = data.get("display_origin", [0, 0])
    if not (isinstance(display_origin, list) and len(display_origin) == 2):
        display_origin = [data.get("display_origin_x", 0), data.get("display_origin_y", 0)]

    return CoordProfile(
        x_scale=float(data.get("x_scale", 1.0)),
        y_scale=float(data.get("y_scale", 1.0)),
        x_offset=float(data.get("x_offset", 0.0)),
        y_offset=float(data.get("y_offset", 0.0)),
        display_origin_x=float(display_origin[0]),
        display_origin_y=float(display_origin[1]),
        name=str(data.get("name", "default")),
        created_at=str(data.get("created_at", "")),
    )


def transform_parsed_point(x: float, y: float, profile: CoordProfile) -> Tuple[int, int]:
    tx = x * profile.x_scale + profile.x_offset + profile.display_origin_x
    ty = y * profile.y_scale + profile.y_offset + profile.display_origin_y
    return int(round(tx)), int(round(ty))


def describe_profile(profile: CoordProfile) -> str:
    return (
        f"name={profile.name} "
        f"scale=({profile.x_scale:.6f},{profile.y_scale:.6f}) "
        f"offset=({profile.x_offset:.3f},{profile.y_offset:.3f}) "
        f"display_origin=({profile.display_origin_x:.3f},{profile.display_origin_y:.3f})"
    )


def click_at(x: int, y: int, args: argparse.Namespace, source: str = "") -> None:
    apply_delay(args.delay)
    if args.dry_run:
        prefix = f"{source} " if source else ""
        print(f"[dry-run] {prefix}click at ({x}, {y})")
        return

    pyautogui = require_pyautogui()
    pyautogui.FAILSAFE = not args.disable_failsafe
    pyautogui.moveTo(x=x, y=y, duration=args.duration)
    pyautogui.click(
        x=x,
        y=y,
        clicks=args.clicks,
        interval=args.click_interval,
        button=args.button,
    )
    prefix = f"{source} " if source else ""
    print(f"{prefix}clicked at ({x}, {y})")


def matches_element(elem: Dict[str, Any], args: argparse.Namespace) -> bool:
    type_filters = {x.lower() for x in expand_csv(getattr(args, "types", None))}
    raw_type_filters = {x.lower() for x in expand_csv(getattr(args, "raw_types", None))}
    text_contains = [x.lower() for x in expand_csv(getattr(args, "text_contains", None))]

    elem_type = str(elem.get("type", "")).lower()
    raw_type = str(elem.get("raw_type", "")).lower()
    elem_text_value = element_text(elem)
    elem_text_lower = elem_text_value.lower()
    elem_id = str(elem.get("id", ""))

    if type_filters and elem_type not in type_filters:
        return False
    if raw_type_filters and raw_type not in raw_type_filters:
        return False

    clickable_filter = getattr(args, "clickable", "any")
    elem_clickable = bool(elem.get("clickable", False))
    if clickable_filter == "true" and not elem_clickable:
        return False
    if clickable_filter == "false" and elem_clickable:
        return False

    for token in text_contains:
        if token not in elem_text_lower:
            return False

    id_regex = getattr(args, "id_regex", None)
    if id_regex and re.search(id_regex, elem_id, flags=re.IGNORECASE) is None:
        return False

    text_regex = getattr(args, "text_regex", None)
    if text_regex and re.search(text_regex, elem_text_value, flags=re.IGNORECASE) is None:
        return False

    return True


def filter_elements(elements: List[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    matches = [elem for elem in elements if matches_element(elem, args)]
    sort_by = getattr(args, "sort", "yx")
    if sort_by == "id":
        matches.sort(key=lambda e: str(e.get("id", "")))
    elif sort_by == "area":
        matches.sort(key=lambda e: element_area(e), reverse=True)
    else:
        matches.sort(
            key=lambda e: (
                int(element_center(e)[1]) if "center_px" in e or "bbox_px" in e else 0,
                int(element_center(e)[0]) if "center_px" in e or "bbox_px" in e else 0,
                str(e.get("id", "")),
            )
        )
    return matches


def format_element_line(elem: Dict[str, Any]) -> str:
    elem_id = elem.get("id", "")
    elem_type = elem.get("type", "")
    raw_type = elem.get("raw_type", "")
    clickable = bool(elem.get("clickable", False))
    center = elem.get("center_px")
    text = element_text(elem).replace("\n", " ").strip()
    if len(text) > 80:
        text = text[:77] + "..."
    return (
        f"id={elem_id} type={elem_type} raw_type={raw_type} "
        f"clickable={clickable} center={center} text={text!r}"
    )


def resolve_click_point_from_element(
    elem: Dict[str, Any],
    coord_profile_path: Optional[Path],
    offset_x: int = 0,
    offset_y: int = 0,
) -> Tuple[int, int, CoordProfile]:
    px, py = element_center(elem)
    px += offset_x
    py += offset_y
    profile = load_coord_profile(coord_profile_path)
    tx, ty = transform_parsed_point(px, py, profile)
    return tx, ty, profile


def run_refresh_command(cmd: str, timeout: float, ignore_errors: bool) -> None:
    result = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if result.returncode == 0:
        return

    msg = (
        f"refresh command failed (exit={result.returncode}): {cmd}\n"
        f"stdout:\n{result.stdout[-600:]}\n"
        f"stderr:\n{result.stderr[-600:]}"
    )
    if ignore_errors:
        print(f"warning: {msg}")
    else:
        raise RuntimeError(msg)


def cmd_list(args: argparse.Namespace) -> None:
    data = load_json(args.elements)
    elements = get_elements(data)
    limit = args.limit if args.limit > 0 else len(elements)

    print(f"total={len(elements)}")
    for elem in elements[:limit]:
        print(format_element_line(elem))


def cmd_find(args: argparse.Namespace) -> None:
    data = load_json(args.elements)
    elements = get_elements(data)
    matches = filter_elements(elements, args)

    if args.as_json:
        output = {
            "count": len(matches),
            "matches": matches[: args.limit if args.limit > 0 else len(matches)],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"matched={len(matches)}")
        limit = args.limit if args.limit > 0 else len(matches)
        for elem in matches[:limit]:
            print(format_element_line(elem))

    if args.click:
        if not matches:
            raise ValueError("No element matched the find criteria, cannot click.")
        idx = args.index
        if idx < 0 or idx >= len(matches):
            raise ValueError(f"--index out of range. got={idx}, available={len(matches)}")
        elem = matches[idx]
        x, y, profile = resolve_click_point_from_element(
            elem,
            args.coord_profile,
            offset_x=args.offset_x,
            offset_y=args.offset_y,
        )
        print(f"using profile: {describe_profile(profile)}")
        click_at(x, y, args, source=f"find id={elem.get('id')}")


def cmd_click(args: argparse.Namespace) -> None:
    data = load_json(args.elements)
    elements = get_elements(data)
    elem = find_element(elements, args.id)
    x, y, profile = resolve_click_point_from_element(
        elem,
        args.coord_profile,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
    )
    print(f"using profile: {describe_profile(profile)}")
    click_at(x, y, args, source=f"id={args.id}")


def cmd_click_xy(args: argparse.Namespace) -> None:
    if args.coord_space == "parsed":
        profile = load_coord_profile(args.coord_profile)
        x, y = transform_parsed_point(args.x, args.y, profile)
        print(f"using profile: {describe_profile(profile)}")
    else:
        x, y = int(args.x), int(args.y)
    click_at(x, y, args)


def cmd_type(args: argparse.Namespace) -> None:
    apply_delay(args.delay)
    if args.dry_run:
        print(f"[dry-run] type text={args.text!r}")
        return

    pyautogui = require_pyautogui()
    pyautogui.FAILSAFE = not args.disable_failsafe
    pyautogui.write(args.text, interval=args.interval)
    print("typed text")


def cmd_key(args: argparse.Namespace) -> None:
    apply_delay(args.delay)
    if args.dry_run:
        print(f"[dry-run] press key={args.key}")
        return

    pyautogui = require_pyautogui()
    pyautogui.FAILSAFE = not args.disable_failsafe
    pyautogui.press(args.key)
    print(f"pressed key={args.key}")


def cmd_hotkey(args: argparse.Namespace) -> None:
    apply_delay(args.delay)
    if args.dry_run:
        print(f"[dry-run] hotkey keys={args.keys}")
        return

    pyautogui = require_pyautogui()
    pyautogui.FAILSAFE = not args.disable_failsafe
    pyautogui.hotkey(*args.keys)
    print(f"pressed hotkey keys={args.keys}")


def cmd_screenshot(args: argparse.Namespace) -> None:
    output = Path(args.output) if args.output else default_screenshot_path()
    output.parent.mkdir(parents=True, exist_ok=True)
    apply_delay(args.delay)

    if args.dry_run:
        if args.region:
            print(f"[dry-run] screenshot region={tuple(args.region)} -> {output}")
        else:
            print(f"[dry-run] screenshot full screen -> {output}")
        return

    pyautogui = require_pyautogui()
    pyautogui.FAILSAFE = not args.disable_failsafe
    if args.region:
        x, y, w, h = args.region
        image = pyautogui.screenshot(region=(x, y, w, h))
    else:
        image = pyautogui.screenshot()
    image.save(str(output))
    print(f"saved screenshot: {output}")


def cmd_wait(args: argparse.Namespace) -> None:
    deadline = time.time() + args.timeout
    attempts = 0

    if args.state == "disappear" and args.click:
        raise ValueError("--click is only valid when --state appear.")

    while True:
        attempts += 1

        if args.refresh_cmd:
            run_refresh_command(args.refresh_cmd, args.refresh_timeout, args.ignore_refresh_errors)

        matches: List[Dict[str, Any]] = []
        read_error: Optional[Exception] = None
        try:
            data = load_json(args.elements)
            elements = get_elements(data)
            matches = filter_elements(elements, args)
        except Exception as exc:  # noqa: BLE001
            read_error = exc
            if args.strict_read_errors:
                raise

        matched_count = len(matches)
        ok = matched_count > 0 if args.state == "appear" else matched_count == 0

        if args.verbose:
            elapsed = args.timeout - max(0.0, deadline - time.time())
            err_txt = f" read_error={read_error}" if read_error else ""
            print(
                f"attempt={attempts} elapsed={elapsed:.1f}s state={args.state} "
                f"matches={matched_count}{err_txt}"
            )

        if ok:
            print(
                f"wait success after {attempts} attempts: "
                f"state={args.state}, matches={matched_count}"
            )
            if args.state == "appear" and args.click:
                idx = args.index
                if idx < 0 or idx >= len(matches):
                    raise ValueError(
                        f"--index out of range for click. got={idx}, available={len(matches)}"
                    )
                elem = matches[idx]
                x, y, profile = resolve_click_point_from_element(
                    elem,
                    args.coord_profile,
                    offset_x=args.offset_x,
                    offset_y=args.offset_y,
                )
                print(f"using profile: {describe_profile(profile)}")
                click_at(x, y, args, source=f"wait id={elem.get('id')}")
            return

        if time.time() >= deadline:
            raise SystemExit(
                f"wait timeout after {args.timeout:.1f}s: state={args.state}, matches={matched_count}"
            )

        time.sleep(args.interval)


def cmd_screen_info(_args: argparse.Namespace) -> None:
    pyautogui = require_pyautogui()
    width, height = pyautogui.size()
    print(f"primary_screen_size=({width}, {height})")

    try:
        from screeninfo import get_monitors  # type: ignore
    except Exception:
        print("monitor_details=unavailable (install screeninfo for monitor list)")
        return

    monitors = get_monitors()
    if not monitors:
        print("monitor_details=none")
        return

    for i, m in enumerate(monitors):
        print(
            f"monitor[{i}]: x={m.x} y={m.y} width={m.width} "
            f"height={m.height} name={getattr(m, 'name', '')}"
        )


def validate_pair(name: str, value: Optional[Sequence[float]]) -> Tuple[float, float]:
    if value is None or len(value) != 2:
        raise ValueError(f"{name} requires exactly 2 numeric values")
    return float(value[0]), float(value[1])


def cmd_calibrate(args: argparse.Namespace) -> None:
    parsed_anchor = tuple(args.parsed_anchor) if args.parsed_anchor else None
    actual_anchor = tuple(args.actual_anchor) if args.actual_anchor else None
    parsed_anchor_2 = tuple(args.parsed_anchor_2) if args.parsed_anchor_2 else None
    actual_anchor_2 = tuple(args.actual_anchor_2) if args.actual_anchor_2 else None

    if bool(parsed_anchor_2) != bool(actual_anchor_2):
        raise ValueError("--parsed-anchor-2 and --actual-anchor-2 must be provided together")

    if parsed_anchor_2 and actual_anchor_2:
        if not parsed_anchor or not actual_anchor:
            raise ValueError(
                "Two-point calibration requires both --parsed-anchor and --actual-anchor"
            )

        px1, py1 = parsed_anchor
        ax1, ay1 = actual_anchor
        px2, py2 = parsed_anchor_2
        ax2, ay2 = actual_anchor_2

        if px2 == px1 or py2 == py1:
            raise ValueError("Anchor points must not share same x or y in parsed coordinates")

        x_scale = (ax2 - ax1) / (px2 - px1)
        y_scale = (ay2 - ay1) / (py2 - py1)

        x_offset = ax1 - px1 * x_scale
        y_offset = ay1 - py1 * y_scale
        mode = "two-point"
    else:
        if bool(args.parsed_size) != bool(args.actual_size):
            raise ValueError("--parsed-size and --actual-size must be provided together")
        if not args.parsed_size or not args.actual_size:
            raise ValueError(
                "Provide either two-point anchors or size-based calibration via "
                "--parsed-size/--actual-size"
            )

        parsed_w, parsed_h = validate_pair("--parsed-size", args.parsed_size)
        actual_w, actual_h = validate_pair("--actual-size", args.actual_size)
        if parsed_w <= 0 or parsed_h <= 0:
            raise ValueError("--parsed-size values must be > 0")
        if actual_w <= 0 or actual_h <= 0:
            raise ValueError("--actual-size values must be > 0")

        x_scale = actual_w / parsed_w
        y_scale = actual_h / parsed_h

        if parsed_anchor and actual_anchor:
            px1, py1 = parsed_anchor
            ax1, ay1 = actual_anchor
            x_offset = ax1 - px1 * x_scale
            y_offset = ay1 - py1 * y_scale
        else:
            x_offset = 0.0
            y_offset = 0.0
        mode = "size"

    win_off_x, win_off_y = validate_pair("--window-offset", args.window_offset)
    disp_x, disp_y = validate_pair("--display-origin", args.display_origin)
    x_offset += win_off_x
    y_offset += win_off_y

    profile = CoordProfile(
        x_scale=x_scale,
        y_scale=y_scale,
        x_offset=x_offset,
        y_offset=y_offset,
        display_origin_x=disp_x,
        display_origin_y=disp_y,
        name=args.name,
        created_at=utc_now(),
    )

    payload = asdict(profile)
    payload["display_origin"] = [profile.display_origin_x, profile.display_origin_y]
    payload["calibration_mode"] = mode

    output = args.output
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"saved coord profile: {output}")
    print(describe_profile(profile))


def add_matcher_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--elements", type=Path, required=True, help="Path to elements JSON.")
    parser.add_argument(
        "--type",
        dest="types",
        action="append",
        default=[],
        help="Normalized type filter (repeatable or comma-separated).",
    )
    parser.add_argument(
        "--raw-type",
        dest="raw_types",
        action="append",
        default=[],
        help="Raw detector type filter (repeatable or comma-separated).",
    )
    parser.add_argument(
        "--text-contains",
        action="append",
        default=[],
        help="Case-insensitive text substring filter (AND semantics).",
    )
    parser.add_argument(
        "--text-regex",
        default=None,
        help="Case-insensitive regex against element text.",
    )
    parser.add_argument(
        "--id-regex",
        default=None,
        help="Case-insensitive regex against element id.",
    )
    parser.add_argument(
        "--clickable",
        choices=["any", "true", "false"],
        default="any",
        help="Filter by clickable flag.",
    )
    parser.add_argument(
        "--sort",
        choices=["yx", "id", "area"],
        default="yx",
        help="Sort order for matched results.",
    )


def add_click_runtime_args(
    parser: argparse.ArgumentParser, click_interval_option: str = "--interval"
) -> None:
    parser.add_argument("--duration", type=float, default=0.0, help="Mouse move duration.")
    parser.add_argument("--clicks", type=int, default=1, help="Number of clicks.")
    parser.add_argument(
        click_interval_option,
        dest="click_interval",
        type=float,
        default=0.0,
        help="Interval between clicks.",
    )
    parser.add_argument(
        "--button",
        choices=["left", "middle", "right"],
        default="left",
        help="Mouse button.",
    )
    parser.add_argument("--delay", type=float, default=0.2, help="Pre-action delay seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Print action without execution.")
    parser.add_argument(
        "--disable-failsafe",
        action="store_true",
        help="Disable pyautogui failsafe.",
    )


def add_coord_profile_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--coord-profile",
        type=Path,
        default=None,
        help="Path to coordinate profile JSON for parsed->screen transform.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Operate UI from parsed element JSON. "
            "Headless-safe: list/find/wait/calibrate. "
            "GUI-required: click/click-xy/type/key/hotkey/screenshot/screen-info."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_p = sub.add_parser("list", help="List parsed elements.")
    list_p.add_argument("--elements", type=Path, required=True, help="Path to elements JSON.")
    list_p.add_argument("--limit", type=int, default=50, help="Number of lines to print.")
    list_p.set_defaults(func=cmd_list)

    find_p = sub.add_parser("find", help="Find elements by type/text/regex filters.")
    add_matcher_args(find_p)
    find_p.add_argument("--limit", type=int, default=20, help="Number of rows to print.")
    find_p.add_argument("--as-json", action="store_true", help="Print matches as JSON.")
    find_p.add_argument("--click", action="store_true", help="Click the selected match.")
    find_p.add_argument("--index", type=int, default=0, help="Match index used with --click.")
    find_p.add_argument("--offset-x", type=int, default=0, help="Parsed-space x offset.")
    find_p.add_argument("--offset-y", type=int, default=0, help="Parsed-space y offset.")
    add_coord_profile_args(find_p)
    add_click_runtime_args(find_p)
    find_p.set_defaults(func=cmd_find)

    wait_p = sub.add_parser("wait", help="Wait until element match appears or disappears.")
    add_matcher_args(wait_p)
    wait_p.add_argument(
        "--state",
        choices=["appear", "disappear"],
        default="appear",
        help="Success condition.",
    )
    wait_p.add_argument("--timeout", type=float, default=20.0, help="Timeout seconds.")
    wait_p.add_argument("--interval", type=float, default=1.0, help="Polling interval seconds.")
    wait_p.add_argument(
        "--refresh-cmd",
        default=None,
        help="Optional shell command run before each poll (e.g. re-parse screenshot).",
    )
    wait_p.add_argument(
        "--refresh-timeout",
        type=float,
        default=120.0,
        help="Timeout for refresh command.",
    )
    wait_p.add_argument(
        "--ignore-refresh-errors",
        action="store_true",
        help="Continue polling if refresh command exits non-zero.",
    )
    wait_p.add_argument(
        "--strict-read-errors",
        action="store_true",
        help="Fail immediately when elements JSON cannot be read during polling.",
    )
    wait_p.add_argument("--verbose", action="store_true", help="Print per-attempt status.")
    wait_p.add_argument("--click", action="store_true", help="Click matched element on success.")
    wait_p.add_argument("--index", type=int, default=0, help="Match index used with --click.")
    wait_p.add_argument("--offset-x", type=int, default=0, help="Parsed-space x offset.")
    wait_p.add_argument("--offset-y", type=int, default=0, help="Parsed-space y offset.")
    add_coord_profile_args(wait_p)
    add_click_runtime_args(wait_p, click_interval_option="--click-interval")
    wait_p.set_defaults(func=cmd_wait)

    click_p = sub.add_parser("click", help="Click by element id.")
    click_p.add_argument("--elements", type=Path, required=True, help="Path to elements JSON.")
    click_p.add_argument("--id", required=True, help="Element id, e.g. e_0007.")
    click_p.add_argument("--offset-x", type=int, default=0, help="Parsed-space x offset.")
    click_p.add_argument("--offset-y", type=int, default=0, help="Parsed-space y offset.")
    add_coord_profile_args(click_p)
    add_click_runtime_args(click_p)
    click_p.set_defaults(func=cmd_click)

    click_xy_p = sub.add_parser("click-xy", help="Click by coordinates.")
    click_xy_p.add_argument("--x", type=float, required=True)
    click_xy_p.add_argument("--y", type=float, required=True)
    click_xy_p.add_argument(
        "--coord-space",
        choices=["screen", "parsed"],
        default="screen",
        help="Coordinate space for x/y. parsed requires --coord-profile.",
    )
    add_coord_profile_args(click_xy_p)
    add_click_runtime_args(click_xy_p)
    click_xy_p.set_defaults(func=cmd_click_xy)

    type_p = sub.add_parser("type", help="Type text.")
    type_p.add_argument("--text", required=True, help="Text to type.")
    type_p.add_argument("--interval", type=float, default=0.02, help="Keystroke interval.")
    type_p.add_argument("--delay", type=float, default=0.2, help="Pre-action delay seconds.")
    type_p.add_argument("--dry-run", action="store_true", help="Print action without typing.")
    type_p.add_argument(
        "--disable-failsafe",
        action="store_true",
        help="Disable pyautogui failsafe.",
    )
    type_p.set_defaults(func=cmd_type)

    key_p = sub.add_parser("key", help="Press one key.")
    key_p.add_argument("--key", required=True, help="Key name, e.g. enter, tab, esc.")
    key_p.add_argument("--delay", type=float, default=0.2, help="Pre-action delay seconds.")
    key_p.add_argument("--dry-run", action="store_true", help="Print action without key press.")
    key_p.add_argument(
        "--disable-failsafe",
        action="store_true",
        help="Disable pyautogui failsafe.",
    )
    key_p.set_defaults(func=cmd_key)

    hotkey_p = sub.add_parser("hotkey", help="Press multi-key combo.")
    hotkey_p.add_argument(
        "--keys",
        nargs="+",
        required=True,
        help="Key list, e.g. --keys command c",
    )
    hotkey_p.add_argument("--delay", type=float, default=0.2, help="Pre-action delay seconds.")
    hotkey_p.add_argument("--dry-run", action="store_true", help="Print action without hotkey.")
    hotkey_p.add_argument(
        "--disable-failsafe",
        action="store_true",
        help="Disable pyautogui failsafe.",
    )
    hotkey_p.set_defaults(func=cmd_hotkey)

    shot_p = sub.add_parser("screenshot", help="Take screenshot.")
    shot_p.add_argument(
        "--output",
        default=None,
        help="Output image path. Default: user's temp directory.",
    )
    shot_p.add_argument(
        "--region",
        nargs=4,
        type=int,
        metavar=("X", "Y", "W", "H"),
        help="Optional region in pixels.",
    )
    shot_p.add_argument("--delay", type=float, default=0.2, help="Pre-action delay seconds.")
    shot_p.add_argument("--dry-run", action="store_true", help="Print action without screenshot.")
    shot_p.add_argument(
        "--disable-failsafe",
        action="store_true",
        help="Disable pyautogui failsafe.",
    )
    shot_p.set_defaults(func=cmd_screenshot)

    info_p = sub.add_parser("screen-info", help="Show primary screen and monitor info.")
    info_p.set_defaults(func=cmd_screen_info)

    cal_p = sub.add_parser("calibrate", help="Create coordinate transform profile.")
    cal_p.add_argument(
        "--output",
        type=Path,
        default=default_coord_profile_path(),
        help="Output profile path. Default: ./coord_profile.json",
    )
    cal_p.add_argument("--name", default="default", help="Profile name.")
    cal_p.add_argument(
        "--parsed-size",
        nargs=2,
        type=float,
        default=None,
        metavar=("W", "H"),
        help="Parsed screenshot size, e.g. 1515 2880.",
    )
    cal_p.add_argument(
        "--actual-size",
        nargs=2,
        type=float,
        default=None,
        metavar=("W", "H"),
        help="Actual screen/render size corresponding to parsed image.",
    )
    cal_p.add_argument(
        "--parsed-anchor",
        nargs=2,
        type=float,
        default=None,
        metavar=("X", "Y"),
        help="Parsed coordinate anchor point.",
    )
    cal_p.add_argument(
        "--actual-anchor",
        nargs=2,
        type=float,
        default=None,
        metavar=("X", "Y"),
        help="Actual screen coordinate for anchor point.",
    )
    cal_p.add_argument(
        "--parsed-anchor-2",
        nargs=2,
        type=float,
        default=None,
        metavar=("X", "Y"),
        help="Second parsed anchor for two-point calibration.",
    )
    cal_p.add_argument(
        "--actual-anchor-2",
        nargs=2,
        type=float,
        default=None,
        metavar=("X", "Y"),
        help="Second actual anchor for two-point calibration.",
    )
    cal_p.add_argument(
        "--window-offset",
        nargs=2,
        type=float,
        default=(0.0, 0.0),
        metavar=("DX", "DY"),
        help="Extra offset after scaling (window origin offset).",
    )
    cal_p.add_argument(
        "--display-origin",
        nargs=2,
        type=float,
        default=(0.0, 0.0),
        metavar=("X", "Y"),
        help="Display origin for multi-monitor coordinate systems.",
    )
    cal_p.add_argument("--dry-run", action="store_true", help="Print profile JSON only.")
    cal_p.set_defaults(func=cmd_calibrate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
