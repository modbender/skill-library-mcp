"""高性能屏幕截图工具 — 基于 mss + Pillow

功能:
  - 全屏截图 / 指定区域截图 / 指定显示器截图
  - 输出格式: PIL Image / PNG 文件 / base64 字符串(JPEG)
  - 自动获取屏幕分辨率信息

依赖: pip install mss pillow  (或 uv add mss pillow)
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import sys
import time
from pathlib import Path
from typing import Optional

import mss
from PIL import Image


class ScreenCapture:
    """使用 mss 进行高性能屏幕截图"""

    def __init__(self, save_dir: str | None = None):
        self._sct = mss.mss()
        self._save_dir: Path | None = None
        if save_dir:
            self._save_dir = Path(save_dir)
            self._save_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 屏幕信息
    # ------------------------------------------------------------------

    @property
    def monitors(self) -> list[dict]:
        """返回所有显示器信息列表。索引 0 是虚拟全屏, 1 开始是物理显示器"""
        return self._sct.monitors

    @property
    def screen_size(self) -> tuple[int, int]:
        """返回主显示器的 (宽, 高)"""
        mon = self._sct.monitors[1]
        return mon["width"], mon["height"]

    @property
    def all_screen_size(self) -> tuple[int, int]:
        """返回虚拟全屏的 (宽, 高) (多显示器合并)"""
        mon = self._sct.monitors[0]
        return mon["width"], mon["height"]

    # ------------------------------------------------------------------
    # 截图核心
    # ------------------------------------------------------------------

    def capture(
        self,
        monitor: int = 1,
        region: Optional[dict] = None,
        delay: float = 0.0,
    ) -> Image.Image:
        """截取屏幕并返回 PIL Image。

        Args:
            monitor: 显示器编号, 1=主显示器, 0=全部合并
            region: 自定义区域 {"left": x, "top": y, "width": w, "height": h}
            delay: 截图前等待秒数
        """
        if delay > 0:
            time.sleep(delay)
        area = region if region else self._sct.monitors[monitor]
        raw = self._sct.grab(area)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

    def capture_to_file(
        self,
        filepath: str | Path = "screenshot.png",
        monitor: int = 1,
        region: Optional[dict] = None,
        delay: float = 0.0,
    ) -> Path:
        """截图并保存为文件, 返回文件路径"""
        img = self.capture(monitor=monitor, region=region, delay=delay)
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(filepath))
        return filepath

    def capture_to_base64(
        self,
        monitor: int = 1,
        region: Optional[dict] = None,
        delay: float = 0.0,
        quality: int = 85,
        fmt: str = "JPEG",
        step: int = 0,
    ) -> str:
        """截图并返回 base64 编码字符串, 适合发送给 API。

        Args:
            monitor: 显示器编号
            region: 自定义区域
            delay: 截图前等待秒数
            quality: JPEG 压缩质量 (1-100)
            fmt: 图片格式, "JPEG" 或 "PNG"
            step: 步骤编号, 用于自动保存文件命名
        """
        img = self.capture(monitor=monitor, region=region, delay=delay)

        if self._save_dir is not None:
            ext = "jpg" if fmt.upper() == "JPEG" else "png"
            save_path = self._save_dir / f"step_{step:03d}.{ext}"
            img.save(str(save_path))

        buf = io.BytesIO()
        save_kwargs = {"format": fmt}
        if fmt.upper() == "JPEG":
            save_kwargs["quality"] = quality
        img.save(buf, **save_kwargs)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def close(self):
        self._sct.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ------------------------------------------------------------------
# CLI 入口
# ------------------------------------------------------------------

_REGION_KEYS = {"left", "top", "width", "height"}


def _parse_region(raw: str) -> dict:
    """解析并验证 --region 参数，只允许包含 left/top/width/height 四个整数键。"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"--region JSON 解析失败: {e}")

    if not isinstance(data, dict):
        raise SystemExit(f"--region 必须是 JSON 对象, 收到: {type(data).__name__}")

    if set(data.keys()) != _REGION_KEYS:
        missing = _REGION_KEYS - set(data.keys())
        extra = set(data.keys()) - _REGION_KEYS
        parts = []
        if missing:
            parts.append(f"缺少: {missing}")
        if extra:
            parts.append(f"多余: {extra}")
        raise SystemExit(f"--region 必须恰好包含 {_REGION_KEYS}。{'; '.join(parts)}")

    for key in _REGION_KEYS:
        if not isinstance(data[key], int):
            raise SystemExit(f"--region 中 '{key}' 必须是整数, 收到: {data[key]!r}")
        if data[key] < 0:
            raise SystemExit(f"--region 中 '{key}' 不能为负数, 收到: {data[key]}")

    if data["width"] == 0 or data["height"] == 0:
        raise SystemExit("--region 中 width 和 height 必须大于 0")

    return data


def main():
    parser = argparse.ArgumentParser(description="Screen capture tool")
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- info ----
    sub.add_parser("info", help="Print monitor information as JSON")

    # ---- capture ----
    cap = sub.add_parser("capture", help="Take a screenshot")
    cap.add_argument("-o", "--output", default="screenshot.png", help="Output file path")
    cap.add_argument("-m", "--monitor", type=int, default=1, help="Monitor index (0=all, 1=primary)")
    cap.add_argument("-d", "--delay", type=float, default=0.0, help="Delay before capture (seconds)")
    cap.add_argument("--region", type=str, default=None,
                     help='Region as JSON: {"left":0,"top":0,"width":800,"height":600}')

    # ---- base64 ----
    b64 = sub.add_parser("base64", help="Capture and output base64 string")
    b64.add_argument("-m", "--monitor", type=int, default=1)
    b64.add_argument("-d", "--delay", type=float, default=0.0)
    b64.add_argument("-q", "--quality", type=int, default=85)
    b64.add_argument("-f", "--format", choices=["JPEG", "PNG"], default="JPEG")

    args = parser.parse_args()

    with ScreenCapture() as sc:
        if args.command == "info":
            info = {
                "monitors": sc.monitors,
                "primary_size": list(sc.screen_size),
                "virtual_size": list(sc.all_screen_size),
            }
            print(json.dumps(info, indent=2))

        elif args.command == "capture":
            region = _parse_region(args.region) if args.region else None
            path = sc.capture_to_file(
                filepath=args.output, monitor=args.monitor,
                region=region, delay=args.delay,
            )
            print(f"Saved: {path} ({path.stat().st_size} bytes)")

        elif args.command == "base64":
            b64_str = sc.capture_to_base64(
                monitor=args.monitor, delay=args.delay,
                quality=args.quality, fmt=args.format,
            )
            print(b64_str)


if __name__ == "__main__":
    main()
