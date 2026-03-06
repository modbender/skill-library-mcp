#!/usr/bin/env python3
"""
flomo-sync.py — 将 flomo 所有 memo 同步为本地 Markdown 文件。

用法:
    python flomo-sync.py --token <access_token> --dir /abs/path/to/output
    python flomo-sync.py --token <access_token> --after 2024-01-01
    python flomo-sync.py --dir /abs/path/to/output  # 从 .flomo.config 读取 token

获取 access_token:
    **获取 token**：在浏览器打开 [https://v.flomoapp.com](https://v.flomoapp.com) 
    登录后，按 `F12` → Network → 点击任意请求 → Headers → 复制 `Authorization` 的值（形如 `Bearer 1023456|...`）。
"""

import argparse
import hashlib
import re
import sys
import time
import uuid
from collections.abc import Generator
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import requests
from markdownify import markdownify

# ──────────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://flomoapp.com/api/v1"
SIGN_SECRET = "dbbc3dd73364b4084c3a69346e0ce2b2"
LIMIT = 200

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".ogg"}

# ──────────────────────────────────────────────────────────────────────────────
# 配置文件与锁文件
# ──────────────────────────────────────────────────────────────────────────────

CONFIG_FILE = Path(".flomo.config")
LOCK_FILE = Path(".flomo.lock")

_LOCK_DT_FMT = "%Y-%m-%d %H:%M:%S"


def _parse_kv_file(path: Path) -> dict:
    """解析 key=value 格式文件，忽略注释行（# 开头）和空行。
    value 会自动去除首尾空格及单双引号，兼容从命令行复制粘贴的写法。
    """
    result: dict = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                v = v.strip().strip("\"'")
                result[k.strip()] = v
    except OSError:
        pass
    return result


def load_config(config_path: Path = CONFIG_FILE) -> dict:
    """读取 .flomo.config（key=value 格式），若不存在则返回空 dict。"""
    if not config_path.exists():
        return {}
    return _parse_kv_file(config_path)


def load_lock(lock_path: Path = LOCK_FILE) -> int:
    """
    读取 .flomo.lock 中的 last_updated_at 值（YYYY-MM-DD HH:MM:SS），
    转换为 Unix 时间戳整数；文件不存在或解析失败时返回 0。
    """
    if not lock_path.exists():
        return 0
    try:
        data = _parse_kv_file(lock_path)
        raw = data.get("last_updated_at", "")
        if raw:
            return int(datetime.strptime(raw, _LOCK_DT_FMT).timestamp())
    except (ValueError, OSError):
        pass
    return 0


def save_lock(last_updated_at: int, lock_path: Path = LOCK_FILE) -> None:
    """将时间戳转为 YYYY-MM-DD HH:MM:SS 格式后以 key=value 格式写入 .flomo.lock。"""
    dt_str = datetime.fromtimestamp(last_updated_at).strftime(_LOCK_DT_FMT)
    lock_path.write_text(f"last_updated_at={dt_str}\n", encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Sign 算法（逆向自前端 JS）
# ──────────────────────────────────────────────────────────────────────────────

def _sign(params: dict) -> str:
    """
    对参数字典生成签名。
    规则:
      1. 按 key 字典序排列
      2. 跳过值为 None、空字符串、False 的参数（保留数字 0）
      3. 列表类型：每项追加 key[]=value，并对 value 排序
      4. 追加 secret 后取 MD5
    """
    sorted_keys = sorted(params.keys())
    parts = []
    for k in sorted_keys:
        v = params[k]
        if v is None:
            continue
        if v == "" or v is False:
            continue
        if isinstance(v, (list, tuple)):
            for item in sorted(str(x) for x in v):
                parts.append(f"{k}[]={item}")
        else:
            parts.append(f"{k}={v}")
    qs = "&".join(parts)
    return hashlib.md5((qs + SIGN_SECRET).encode()).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# API 封装
# ──────────────────────────────────────────────────────────────────────────────

def _build_params(extra: dict) -> dict:
    """组装公共参数（timestamp / api_key / app_version / platform / webp）。"""
    params = dict(extra)
    params["timestamp"] = int(time.time())
    params["api_key"] = "flomo_web"
    params["app_version"] = "4.0"
    params["platform"] = "web"
    params["webp"] = "1"
    params["sign"] = _sign(params)
    return params


def _headers(token: str) -> dict:
    return {
        "accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "origin": "https://v.flomoapp.com",
        "referer": "https://v.flomoapp.com/",
        "device-id": str(uuid.UUID("503b6439-1884-443d-b04e-0828bf9f138f")),
        "device-model": "Chrome",
        "platform": "Web",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    }


def fetch_memos_page(
    token: str,
    latest_updated_at: int,
    latest_slug: str,
) -> list[dict]:
    """拉取一页 memo（最多 LIMIT 条）。"""
    extra: dict = {
        "limit": str(LIMIT),
        "latest_updated_at": str(latest_updated_at) if latest_updated_at else "",
        "latest_slug": latest_slug or "",
        "tz": "8:0",
    }
    params = _build_params(extra)
    url = f"{BASE_URL}/memo/updated/"
    resp = requests.get(url, params=params, headers=_headers(token), timeout=30)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code") != 0:
        raise RuntimeError(f"API 错误: code={body.get('code')} msg={body.get('message')}")
    return body["data"]


def iter_memo_pages(
    token: str,
    after_ts: int = 0,
) -> Generator[list[dict], None, None]:
    """
    分页拉取 memo 的生成器，每次 yield 一页数据（list[dict]）。
    after_ts — 起始 updated_at 时间戳（含），0 表示从最早开始。
               直接作为 API 游标，真正跳过更早的页面，不产生多余请求。
    """
    latest_updated_at = after_ts
    latest_slug = ""
    page = 1

    while True:
        print(
            f"  第 {page} 页（游标 updated_at={latest_updated_at} slug={latest_slug!r}）…",
            end=" ",
            flush=True,
        )
        items = fetch_memos_page(token, latest_updated_at, latest_slug)
        if not items:
            print("0 条，结束。", flush=True)
            break

        print(f"拉取 {len(items)} 条", flush=True)
        yield items

        if len(items) < LIMIT:
            break

        last = items[-1]
        last_updated_at = last["updated_at"]
        if isinstance(last_updated_at, str):
            dt = datetime.strptime(last_updated_at, "%Y-%m-%d %H:%M:%S")
            latest_updated_at = int(dt.timestamp())
        else:
            latest_updated_at = int(last_updated_at)

        latest_slug = last["slug"]
        page += 1
        time.sleep(0.3)  # 礼貌性限速


# ──────────────────────────────────────────────────────────────────────────────
# 附件下载
# ──────────────────────────────────────────────────────────────────────────────

def _ext_from_url(url: str) -> str:
    """从 URL 路径中提取不带查询参数的文件扩展名（小写）。"""
    path = urlparse(url).path
    return Path(path).suffix.lower()


def download_attachment(
    url: str,
    name: str,
    slug: str,
    created_at: str,
    images_dir: Path,
) -> str | None:
    """
    下载单个附件到 images_dir/YYYY/MM/DD/{slug}_{name}。
    返回相对于 output_dir 的路径字符串，失败返回 None。
    """
    ext = _ext_from_url(url) or Path(name).suffix.lower()
    if ext not in IMAGE_EXTS and ext not in AUDIO_EXTS:
        return None

    # 按创建时间分组目录 YYYY/MM/DD
    try:
        dt = datetime.strptime(created_at[:10], "%Y-%m-%d")
        date_path = Path(f"{dt.year:04d}") / f"{dt.month:02d}" / f"{dt.day:02d}"
    except (ValueError, TypeError):
        date_path = Path("unknown")

    dest_dir = images_dir / date_path
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 文件名：slug 前缀避免同日冲突
    safe_name = name.replace("/", "_").replace("\\", "_")
    # 若 name 本身无扩展名，则补充从 URL 提取到的扩展名
    if not Path(safe_name).suffix and ext:
        safe_name = safe_name + ext
    filename = f"{slug}_{safe_name}"
    dest_path = dest_dir / filename

    if dest_path.exists():
        return str(Path("images") / date_path / filename)

    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
        return str(Path("images") / date_path / filename)
    except Exception as e:
        print(f"    ⚠ 下载失败 {name}: {e}", flush=True)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# HTML → Markdown 转换
# ──────────────────────────────────────────────────────────────────────────────

def html_to_md(html: str) -> str:
    """将 flomo memo 的 HTML 内容转换为 Markdown。"""
    if not html:
        return ""
    md = markdownify(
        html,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )
    lines = md.splitlines()
    cleaned: list[str] = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 1:
                cleaned.append("")
        else:
            blank_count = 0
            cleaned.append(line)
    return "\n".join(cleaned).strip()


# ──────────────────────────────────────────────────────────────────────────────
# 文件输出
# ──────────────────────────────────────────────────────────────────────────────

def memo_to_md_text(memo: dict, images_dir: Path | None = None) -> str:
    """
    生成单条 memo 的 Markdown 文本（含 front matter）。
    若提供 images_dir，则下载图片/音频附件到本地并以 Markdown 语法嵌入；
    否则以远程链接形式写入。
    """
    tags = memo.get("tags") or []
    tags_str = "[" + ", ".join(tags) + "]" if tags else "[]"

    files = memo.get("files") or []
    files_section = ""
    if files:
        slug = memo.get("slug") or f"memo_{id(memo)}"
        created_at = str(memo.get("created_at") or "")
        file_lines = []
        for f in files:
            name = f.get("name") or Path(urlparse(f.get("url", "")).path).name or "file"
            url = f.get("url", "")
            if not url:
                file_lines.append(f"- {name}")
                continue

            local_path = None
            if images_dir is not None:
                local_path = download_attachment(url, name, slug, created_at, images_dir)

            ext = _ext_from_url(url) or Path(name).suffix.lower()
            display_url = local_path.replace("\\", "/") if local_path else url
            if ext in IMAGE_EXTS:
                file_lines.append(f"![{name}]({display_url})")
            else:
                file_lines.append(f"[{name}]({display_url})")

        files_section = "\n\n**附件:**\n" + "\n".join(file_lines)

    body = html_to_md(memo.get("content", ""))

    return (
        f"---\n"
        f"slug: {memo.get('slug', '')}\n"
        f"created_at: {memo.get('created_at', '')}\n"
        f"updated_at: {memo.get('updated_at', '')}\n"
        f"tags: {tags_str}\n"
        f"source: {memo.get('source', '')}\n"
        f"---\n\n"
        f"{body}"
        f"{files_section}\n"
    )


def _memo_filename(memo: dict) -> str:
    """
    根据 memo 生成可读文件名，格式：
        {created_at日期}_{标签叶}_{内容前6字}_{slug}.md
    各部分均为可选，若无内容则省略，最终以 _ 连接。
    """
    slug = memo.get("slug") or f"memo_{id(memo)}"
    parts: list[str] = []

    # 1. 日期
    created_at = str(memo.get("created_at") or "")
    if len(created_at) >= 10:
        parts.append(created_at[:10])

    # 2. 取第一个标签斜杠后最后一段
    tags = memo.get("tags") or []
    if tags:
        leaf = tags[0].split("/")[-1]
        # 去掉文件系统不允许的字符
        leaf = re.sub(r'[\\/:*?"<>|]', "", leaf).strip()
        if leaf:
            parts.append(leaf)

    # 3. 内容前 6 个有效字符（汉字 + 字母数字，不含符号）
    content_md = html_to_md(memo.get("content") or "")
    # 去掉 #标签词 模式（flomo 正文中嵌入的标签）
    content_clean = re.sub(r"#\S+", "", content_md)
    # 只保留汉字和字母数字
    chars = re.findall(r"[\u4e00-\u9fff\w]", content_clean)
    preview = "".join(chars[:6])
    if preview:
        parts.append(preview)

    # 4. slug
    parts.append(slug)

    return "_".join(parts) + ".md"


def write_memo(memo: dict, output_dir: Path, images_dir: Path | None) -> str:
    """
    将单条 memo 写入独立 .md 文件，返回操作状态：
    - "created"  新文件
    - "updated"  内容或文件名有变化
    - "skipped"  文件已存在且内容完全相同
    """
    new_filename = _memo_filename(memo)
    new_path = output_dir / new_filename
    slug = memo.get("slug") or ""
    new_content = memo_to_md_text(memo, images_dir)

    status = "created"
    if slug:
        for old in output_dir.glob(f"*_{slug}.md"):
            if old.name != new_filename:
                old.unlink()
                status = "updated"
            else:
                if old.read_text(encoding="utf-8") == new_content:
                    return "skipped"
                status = "updated"

    new_path.write_text(new_content, encoding="utf-8")
    return status



# ──────────────────────────────────────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────────────────────────────────────

def _parse_date_to_ts(s: str) -> int:
    """将 YYYY-MM-DD 字符串解析为当天 00:00:00 的 Unix 时间戳。"""
    try:
        return int(datetime.strptime(s, "%Y-%m-%d").timestamp())
    except ValueError:
        raise argparse.ArgumentTypeError(f"日期格式错误，需为 YYYY-MM-DD，收到: {s!r}")


class ItemProgress:
    """无第三方依赖的页内条目进度显示（TTY 进度条 + 非 TTY 文本降级）。"""

    def __init__(self, total: int, prefix: str = "    页内处理", width: int = 24):
        self.total = max(0, int(total))
        self.prefix = prefix
        self.width = max(10, int(width))
        self._is_tty = sys.stdout.isatty()
        self._last_line_len = 0
        self._last_reported = 0
        # 非交互终端按 10% 粒度输出，避免 CI/重定向日志过于冗长。
        self._report_step = max(1, self.total // 10) if self.total else 1

    def _tty_line(self, current: int) -> str:
        if self.total <= 0:
            return f"{self.prefix} 0/0"
        current = min(max(0, current), self.total)
        filled = int(self.width * current / self.total)
        bar = "#" * filled + "-" * (self.width - filled)
        return f"{self.prefix} [{bar}] {current}/{self.total}"

    def update(self, current: int, force: bool = False) -> None:
        if self.total <= 0:
            return
        current = min(max(0, current), self.total)
        if self._is_tty:
            line = self._tty_line(current)
            pad = " " * max(0, self._last_line_len - len(line))
            print(f"\r{line}{pad}", end="", flush=True)
            self._last_line_len = len(line)
            return

        should_print = (
            force
            or current == self.total
            or current - self._last_reported >= self._report_step
        )
        if should_print:
            pct = int((current * 100) / self.total)
            print(f"{self.prefix} {current}/{self.total} ({pct}%)", flush=True)
            self._last_reported = current

    def finish(self) -> None:
        if self.total <= 0:
            return
        self.update(self.total, force=True)
        if self._is_tty:
            print("", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="同步 flomo 所有 memo 为本地 Markdown 文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--token",
        default=None,
        metavar="ACCESS_TOKEN",
        help=(
            "flomo access_token（可省略，从 .flomo.config 读取）。\n"
            "**获取 token**：在浏览器打开 [https://v.flomoapp.com](https://v.flomoapp.com) 登录后，按 `F12` → Network → 点击任意请求 → Headers → 复制 `Authorization` 的值（形如 `Bearer 1023456|...`）。"
        ),
    )
    parser.add_argument(
        "--dir",
        "--output",
        dest="output_dir",
        default=None,
        metavar="ABS_DIR",
        help=(
            "输出目录绝对路径（推荐使用 --dir；"
            "未传时默认使用当前执行目录）"
        ),
    )
    parser.add_argument(
        "--after",
        metavar="YYYY-MM-DD",
        type=_parse_date_to_ts,
        default=None,
        help=(
            "仅拉取该日期（含）之后更新的 memo（基于 updated_at）。\n"
            "未指定时自动从 .flomo.lock 读取上次拉取时间并减去 1 天。\n"
            "日期时间戳直接作为 API 游标，跳过更早的页面，真正减少网络请求。"
        ),
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="不下载附件到本地，改为保留远程 URL 链接（默认行为为自动下载）",
    )

    args = parser.parse_args()

    # ── token 解析：命令行 > .flomo.json ──
    token: str = args.token or ""
    if not token:
        cfg = load_config()
        token = cfg.get("token", "")
    if not token:
        print(
            "❌ 未找到 access_token。\n"
            "   请通过 --token 参数传入，或在 .flomo.config 中配置 token=...",
            file=sys.stderr,
        )
        sys.exit(1)

    # 兼容 "Bearer <token>" 格式，自动提取实际 token
    if token.lower().startswith("bearer "):
        token = token[len("bearer "):].strip()

    # ── after 时间戳解析：命令行 > .flomo.lock - 1天 > 全量 ──
    after_ts: int
    if args.after is not None:
        after_ts = args.after
        after_source = "命令行 --after"
    else:
        lock_ts = load_lock()
        if lock_ts:
            after_ts = int((datetime.fromtimestamp(lock_ts) - timedelta(days=1)).timestamp())
            after_source = f".flomo.lock（上次 {datetime.fromtimestamp(lock_ts).strftime('%Y-%m-%d %H:%M:%S')} - 1 天）"
        else:
            after_ts = 0
            after_source = "无（全量拉取）"

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser()
        if not output_dir.is_absolute():
            print(
                "❌ --dir 必须是绝对路径，例如: --dir /Users/you/flomo-output",
                file=sys.stderr,
            )
            sys.exit(1)
        output_dir = output_dir.resolve()
    else:
        output_dir = Path.cwd().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    images_dir: Path | None = None
    if not args.no_download:
        images_dir = output_dir / "images"

    print("=" * 50)
    print("flomo → Markdown 同步工具")
    print("=" * 50)

    if after_ts:
        after_str = datetime.fromtimestamp(after_ts).strftime("%Y-%m-%d")
        print(f"\nafter={after_str}（来源: {after_source}）")
    else:
        print(f"\n拉取范围: 全部（来源: {after_source}）")

    print(f"输出目录: {output_dir}")
    print()
    start_time = time.time()
    total = 0
    n_created = 0
    n_updated = 0
    n_skipped = 0
    max_updated_at: int = 0

    def _track_max(items: list[dict]) -> None:
        """更新本次拉取到的最大 updated_at 时间戳。"""
        nonlocal max_updated_at
        for m in items:
            raw = m.get("updated_at") or ""
            try:
                if isinstance(raw, str):
                    ts = int(datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").timestamp())
                else:
                    ts = int(raw)
                if ts > max_updated_at:
                    max_updated_at = ts
            except (ValueError, TypeError):
                pass

    try:
        for items in iter_memo_pages(token, after_ts=after_ts):
            progress = ItemProgress(total=len(items), prefix="    页内处理")
            for idx, memo in enumerate(items, start=1):
                s = write_memo(memo, output_dir, images_dir)
                if s == "created":
                    n_created += 1
                elif s == "updated":
                    n_updated += 1
                else:
                    n_skipped += 1
                progress.update(idx)
            progress.finish()
            _track_max(items)
            total += len(items)
            print(f"    → 已处理，累计 {total} 条", flush=True)

    except RuntimeError as e:
        print(f"\n❌ 拉取失败: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"\n❌ HTTP 错误: {e}", file=sys.stderr)
        sys.exit(1)

    # ── 写入 lock 文件 ──
    if max_updated_at:
        save_lock(max_updated_at)
        lock_str = datetime.fromtimestamp(max_updated_at).strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n已更新 .flomo.lock（last_updated_at={lock_str}）")

    elapsed = time.time() - start_time
    print(f"\n✅ 完成！新增 {n_created} 条，更新 {n_updated} 条，跳过 {n_skipped} 条（耗时 {elapsed:.1f}s）")


if __name__ == "__main__":
    main()
