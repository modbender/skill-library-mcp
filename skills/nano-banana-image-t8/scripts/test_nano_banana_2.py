from __future__ import annotations

import argparse
import base64
import getpass
import os
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import Any

import httpx

TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAIAAABMXPacAAAACXBIWXMAAA7EAAAOxAGVKw4b"
    "AAAAT0lEQVR4nO3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAA4G4IAAAFQh4v8AAAAASUVORK5CYII="
)
_KEY_FILE = Path.home() / ".whaleclaw" / "credentials" / "nano_banana_api_key.txt"
_DEFAULT_OUT_DIR = Path.home() / ".whaleclaw" / "workspace" / "nano_banana_test"


def _build_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _extract_image_bytes(item: dict[str, Any], client: httpx.Client) -> bytes:
    if "b64_json" in item and isinstance(item["b64_json"], str):
        return base64.b64decode(item["b64_json"])

    url_value = item.get("url")
    if isinstance(url_value, str) and url_value:
        resp = client.get(url_value, timeout=60)
        resp.raise_for_status()
        return resp.content

    raise RuntimeError("响应中未包含 b64_json 或 url")


def _save_image(data: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def run_text_to_image(
    client: httpx.Client,
    base_url: str,
    model: str,
    size: str | None,
    aspect_ratio: str,
    prompt: str,
    output_path: Path,
) -> None:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "response_format": "url",
    }
    if size:
        payload["size"] = size
    else:
        payload["aspect_ratio"] = aspect_ratio

    resp = client.post(f"{base_url}/v1/images/generations", json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("data")
    if not isinstance(items, list) or not items:
        raise RuntimeError(f"文生图返回格式异常: {data}")

    image_bytes = _extract_image_bytes(items[0], client)
    _save_image(image_bytes, output_path)


def run_image_to_image(
    client: httpx.Client,
    base_url: str,
    edit_model: str,
    size: str | None,
    aspect_ratio: str,
    input_image_paths: list[Path],
    output_path: Path,
    prompt: str,
) -> None:
    form_data: dict[str, str] = {
        "model": edit_model,
        "prompt": prompt,
        "n": "1",
        "response_format": "url",
    }
    if size:
        form_data["size"] = size
    else:
        form_data["aspect_ratio"] = aspect_ratio

    with ExitStack() as stack:
        if len(input_image_paths) == 1:
            image_path = input_image_paths[0]
            file_obj = stack.enter_context(image_path.open("rb"))
            files: Any = {"image": (image_path.name, file_obj, "image/png")}
        else:
            files = []
            for image_path in input_image_paths:
                file_obj = stack.enter_context(image_path.open("rb"))
                files.append(("image[]", (image_path.name, file_obj, "image/png")))

        resp = client.post(
            f"{base_url}/v1/images/edits",
            data=form_data,
            files=files,
            timeout=300,
        )

    resp.raise_for_status()
    data = resp.json()

    items = data.get("data")
    if not isinstance(items, list) or not items:
        raise RuntimeError(f"图生图返回格式异常: {data}")

    image_bytes = _extract_image_bytes(items[0], client)
    _save_image(image_bytes, output_path)


def ensure_input_image(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(TINY_PNG_BASE64))


def _load_saved_api_key() -> str:
    if not _KEY_FILE.exists():
        return ""
    return _KEY_FILE.read_text(encoding="utf-8").strip()


def _save_api_key(api_key: str) -> None:
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _KEY_FILE.write_text(api_key.strip(), encoding="utf-8")
    os.chmod(_KEY_FILE, 0o600)


def _collect_api_key(provided_api_key: str, interactive: bool) -> str:
    if provided_api_key:
        return provided_api_key
    saved_key = _load_saved_api_key()
    if saved_key:
        if not interactive:
            return saved_key
        print("检测到已保存 API Key。")
        choice = input("输入 1 使用默认 Key，输入 2 替换 Key（默认 1）: ").strip()
        if choice in {"", "1"}:
            return saved_key
        if choice != "2":
            raise SystemExit("无效选择，请输入 1 或 2")

    if not interactive:
        raise SystemExit(
            "缺少 API key（且无已保存 Key）。请用 --api-key 或环境变量 NANO_BANANA_API_KEY 传入。"
        )

    entered = getpass.getpass("请输入 API Key（输入过程不可见）: ").strip()
    if not entered:
        raise SystemExit(
            "缺少 API key，请通过 --api-key / 环境变量 NANO_BANANA_API_KEY / 交互输入提供"
        )
    _save_api_key(entered)
    print(f"API Key 已保存到: {_KEY_FILE}")
    return entered


def _collect_mode(provided_mode: str, interactive: bool) -> str:
    if provided_mode:
        return provided_mode
    if not interactive:
        return "both"
    print("请选择模式：1) 文生图  2) 图生图  3) 两者都测")
    choice = input("输入 1/2/3（默认 3）: ").strip()
    mapping = {"1": "text", "2": "edit", "3": "both", "": "both"}
    mode = mapping.get(choice)
    if not mode:
        raise SystemExit("无效模式，请输入 1/2/3")
    return mode


def _collect_prompt(provided_prompt: str, mode: str, interactive: bool) -> str:
    if provided_prompt:
        return provided_prompt
    if not interactive:
        if mode == "text":
            return "一只站在海边冲浪板上的柴犬，电影感光影，高清细节"
        if mode == "edit":
            return "把这张图改成黄昏时分，暖色调，保持主体构图"
        return "一只站在海边冲浪板上的柴犬，电影感光影，高清细节"
    if mode == "text":
        tip = "请输入文生图提示词: "
    elif mode == "edit":
        tip = "请输入图生图提示词（示例：让图1的女孩站在图2的背景中）: "
    else:
        tip = "请输入提示词（用于文生图；图生图默认自动使用文生图结果）: "
    entered = input(tip).strip()
    if not entered:
        raise SystemExit("提示词不能为空")
    return entered


def _collect_input_images(provided_paths: list[str], interactive: bool) -> list[Path]:
    if provided_paths:
        candidates = provided_paths
    else:
        if not interactive:
            return []
        raw = input("请输入图生图图片路径，可多张，用逗号分隔（顺序即 图1/图2/...）: ").strip()
        if not raw:
            return []
        candidates = [p.strip() for p in raw.split(",") if p.strip()]

    paths = [Path(p).expanduser() for p in candidates]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"以下图片不存在: {missing}")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="测试 Nano-banana-2 文生图与图生图")
    parser.add_argument("--api-key", default=os.getenv("NANO_BANANA_API_KEY", ""))
    parser.add_argument("--check-key", action="store_true")
    parser.add_argument("--base-url", default="https://ai.t8star.cn")
    parser.add_argument("--model", default="nano-banana-2")
    parser.add_argument("--edit-model", default="nano-banana-2")
    parser.add_argument("--mode", choices=["text", "edit", "both"], default="")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--input-image", action="append", default=[])
    parser.add_argument("--size", default="")
    parser.add_argument("--aspect-ratio", default="auto")
    parser.add_argument("--out-dir", default=str(_DEFAULT_OUT_DIR))
    args = parser.parse_args()

    if args.check_key:
        env_key = os.getenv("NANO_BANANA_API_KEY", "").strip()
        saved = _load_saved_api_key()
        provided = bool(args.api_key.strip())
        result = {
            "provided_arg": provided,
            "env_key_exists": bool(env_key),
            "saved_key_exists": bool(saved),
            "saved_key_path": str(_KEY_FILE),
            "preferred_source": (
                "arg" if provided else "env" if env_key else "saved_file" if saved else "none"
            ),
        }
        print(result)
        return 0

    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    api_key = _collect_api_key(args.api_key, interactive)
    mode = _collect_mode(args.mode, interactive)
    prompt = _collect_prompt(args.prompt, mode, interactive)

    out_dir = Path(args.out_dir)
    text_output = out_dir / "text_to_image.png"
    edit_output = out_dir / "image_to_image.png"

    with httpx.Client(headers=_build_headers(api_key), follow_redirects=True) as client:
        try:
            size = args.size.strip() or None
            if mode in {"text", "both"}:
                print("[文生图] 测试中...")
                run_text_to_image(
                    client,
                    args.base_url.rstrip("/"),
                    args.model,
                    size,
                    args.aspect_ratio,
                    prompt,
                    text_output,
                )
                print(f"文生图成功: {text_output}")

            if mode in {"edit", "both"}:
                print("[图生图] 测试中...")
                input_images = _collect_input_images(args.input_image, interactive)
                if mode == "both" and not input_images:
                    input_images = [text_output]
                if not input_images:
                    raise SystemExit("图生图至少需要 1 张输入图片")
                run_image_to_image(
                    client,
                    args.base_url.rstrip("/"),
                    args.edit_model,
                    size,
                    args.aspect_ratio,
                    input_images,
                    edit_output,
                    prompt,
                )
                print(f"图生图成功: {edit_output}")
        except httpx.HTTPStatusError as exc:
            body = exc.response.text
            raise SystemExit(
                f"HTTP {exc.response.status_code} 请求失败: {exc.request.url}\n响应体: {body}"
            ) from exc
        except httpx.HTTPError as exc:
            raise SystemExit(f"请求失败: {exc.__class__.__name__}: {exc}") from exc

    print("任务完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
