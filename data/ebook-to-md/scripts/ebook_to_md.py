# -*- coding: utf-8 -*-
"""
ebook_to_md skill: convert PDF/PNG/JPEG/MOBI/EPUB to Markdown.
Uses Baidu OCR only. Schema auto-inferred from main().
Entry: main() + CLI.
"""

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import argparse
import base64
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

FIG_HEIGHT_PT = 260
API_BASE = "https://aip.baidubce.com"
IMG_SRC_PATTERN = re.compile(r'<img\s+src=["\']?([^"\'>\s]+)["\']?\s*/?>', re.IGNORECASE)

SUPPORTED_INPUT_EXTS = {".pdf", ".png", ".jpeg", ".jpg", ".mobi", ".epub"}
IMAGE_EXTS = {".png", ".jpeg", ".jpg"}


def _detect_input_type(input_path: str) -> str:
    """Return: pdf, image, mobi, epub. For base64/data URI, return image."""
    if not input_path or not isinstance(input_path, str):
        return ""
    s = input_path.strip()
    if s.startswith("data:image") or (len(s) > 50 and re.match(r"^[A-Za-z0-9+/]+=*$", s)):
        return "image"
    p = Path(s)
    ext = p.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext in IMAGE_EXTS:
        return "image"
    if ext == ".mobi":
        return "mobi"
    if ext == ".epub":
        return "epub"
    return ""


def _convert_ebook_to_pdf(ebook_path: str) -> str:
    """Convert mobi/epub to PDF via Calibre ebook-convert. Returns path to temp PDF."""
    path = Path(ebook_path)
    if not path.exists():
        raise FileNotFoundError("文件不存在: {}".format(ebook_path))
    ext = path.suffix.lower()
    if ext not in (".mobi", ".epub"):
        raise ValueError("仅支持 mobi、epub 格式: {}".format(ext))

    try:
        result = subprocess.run(
            ["ebook-convert", str(path), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError("ebook-convert 不可用")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        raise RuntimeError(
            "未检测到 Calibre。请安装: macOS brew install calibre, "
            "Linux apt-get install calibre。错误: {}".format(e)
        )

    fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        result = subprocess.run(
            ["ebook-convert", str(path), tmp_pdf],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError("ebook-convert 转换失败: {}".format(result.stderr or result.stdout))
        return tmp_pdf
    except Exception:
        if os.path.exists(tmp_pdf):
            try:
                os.remove(tmp_pdf)
            except OSError:
                pass
        raise


# ----- Baidu OCR helpers (from ocr skill) -----


def _get_access_token(api_key: str, secret_key: str) -> Optional[str]:
    try:
        url = "{}/oauth/2.0/token".format(API_BASE)
        params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as e:
        logger.error("获取访问令牌失败: {}".format(str(e)))
        return None


def _read_image_file(image_path: str) -> Optional[str]:
    try:
        if image_path.startswith("data:image"):
            parts = image_path.split(",")
            if len(parts) > 1:
                return parts[1]
            return image_path
        base64_pattern = re.compile(r"^[A-Za-z0-9+/]+=*$")
        if len(image_path) > 50 and base64_pattern.match(image_path):
            return image_path
        if not Path(image_path).exists():
            if len(image_path) > 20 and base64_pattern.match(image_path):
                return image_path
            return None
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        logger.error("读取图片失败: {}".format(str(e)))
        return None


def _call_baidu_ocr_api(
    api_key: str, secret_key: str, image_base64: str, language_type: str = "CHN_ENG"
) -> Dict[str, Any]:
    try:
        access_token = _get_access_token(api_key, secret_key)
        if not access_token:
            return {"error_code": -1, "error_msg": "无法获取访问令牌"}
        url = "{}/rest/2.0/ocr/v1/general_basic".format(API_BASE)
        params = {"access_token": access_token}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "image": image_base64,
            "language_type": language_type,
            "detect_direction": "true",
            "paragraph": "true",
        }
        resp = requests.post(url, params=params, headers=headers, data=data)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("OCR API 请求失败: {}".format(str(e)))
        return {"error_code": -1, "error_msg": str(e)}


def _extract_text_from_baidu_result(result: Dict[str, Any]) -> str:
    if "error_code" in result and result.get("error_code", 0) != 0:
        return "OCR识别失败: {}".format(result.get("error_msg", "未知错误"))
    words = result.get("words_result", [])
    if not words:
        return "未识别到文字"
    return "\n".join(item.get("words", "") for item in words)


def _format_image_markdown_paragraphs(content: str) -> str:
    """对图片 OCR 输出添加 Markdown 分段（标题、段落空行）。"""
    if not content or not content.strip():
        return content
    lines = content.split("\n")
    if not lines:
        return content
    out = []
    # 在每段以 " 开头的对话前插入空行（分段）；标题由 OCR 识别，不做首行推测
    for i in range(0, len(lines)):
        line = lines[i]
        if line.strip().startswith("\u201c") and out and out[-1] != "":
            out.append("")
        out.append(line)
    return "\n".join(out).rstrip()


# 文档解析接口：文档解析（PaddleOCR-VL）https://cloud.baidu.com/doc/OCR/s/7mh8u7ruk
# 提交请求 QPS=2，获取结果 QPS=10；建议提交后 5～10 秒轮询。
PADDLE_VL_SUBMIT_URL = "{}/rest/2.0/brain/online/v2/paddle-vl-parser/task".format(API_BASE)
PADDLE_VL_QUERY_URL = "{}/rest/2.0/brain/online/v2/paddle-vl-parser/task/query".format(API_BASE)


def _submit_parser_task(access_token: str, file_path: str, file_name: str) -> str:
    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode("utf-8")
    params = {"access_token": access_token}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"file_data": file_data, "file_name": file_name}
    resp = requests.post(PADDLE_VL_SUBMIT_URL, params=params, headers=headers, data=data)
    if resp.status_code != 200:
        raise RuntimeError("提交任务失败: HTTP {} - {}".format(resp.status_code, resp.text))
    j = resp.json()
    if j.get("error_code", 0) != 0:
        raise RuntimeError(
            "百度 API 错误: error_code={}, error_msg={}".format(j.get("error_code"), j.get("error_msg", ""))
        )
    task_id = (j.get("result") or {}).get("task_id")
    if not task_id:
        raise RuntimeError("响应中无 task_id")
    return task_id


def _query_parser_result(access_token: str, task_id: str) -> dict:
    params = {"access_token": access_token}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"task_id": task_id}
    resp = requests.post(PADDLE_VL_QUERY_URL, params=params, headers=headers, data=data)
    if resp.status_code != 200:
        raise RuntimeError("查询失败: HTTP {}".format(resp.status_code))
    j = resp.json()
    if j.get("error_code", 0) != 0:
        raise RuntimeError("百度 API 错误: {}".format(j.get("error_msg", "")))
    return j.get("result") or {}


def _download_markdown(markdown_url: str) -> str:
    resp = requests.get(markdown_url)
    resp.raise_for_status()
    return resp.text


def _download_parse_result_json(parse_result_url: str) -> dict:
    resp = requests.get(parse_result_url)
    resp.raise_for_status()
    return json.loads(resp.content.decode("utf-8", errors="replace"))


def _detect_image_mime(raw: bytes) -> str:
    if raw[:2] == b"\xff\xd8":
        return "image/jpeg"
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if raw[:2] == b"BM":
        return "image/bmp"
    if len(raw) > 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _fetch_image_raw(url: str):
    resp = requests.get(url)
    resp.raise_for_status()
    raw = resp.content
    mime = _detect_image_mime(raw)
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
    }
    return raw, ext_map.get(mime, ".jpg")


def _fetch_image_as_base64(url: str) -> str:
    raw, _ = _fetch_image_raw(url)
    return "data:{};base64,{}".format(_detect_image_mime(raw), base64.b64encode(raw).decode("utf-8"))


def _table_to_html(table: dict) -> str:
    cells = table.get("cells") or []
    matrix = table.get("matrix")
    if not cells or not matrix:
        return table.get("markdown", "")
    rows = len(matrix)
    cols = max(len(r) for r in matrix) if matrix else 0
    if rows == 0 or cols == 0:
        return table.get("markdown", "")

    def get_colspan(mat, r, c):
        idx_val = mat[r][c]
        count = 1
        for cc in range(c + 1, len(mat[r])):
            if mat[r][cc] == idx_val:
                count += 1
            else:
                break
        return count

    def get_rowspan(mat, r, c):
        idx_val = mat[r][c]
        count = 1
        for rr in range(r + 1, rows):
            if c < len(mat[rr]) and mat[rr][c] == idx_val:
                count += 1
            else:
                break
        return count

    rowspan_at = {}
    for r in range(rows):
        for c in range(len(matrix[r])):
            if (r, c) in rowspan_at:
                continue
            idx_val = matrix[r][c]
            for rr in range(r + 1, r + get_rowspan(matrix, r, c)):
                for cc in range(c, min(c + get_colspan(matrix, r, c), len(matrix[rr]) if rr < rows else 0)):
                    if rr < rows:
                        rowspan_at[(rr, cc)] = True

    html = ['<table style="text-align:center">']
    for r in range(rows):
        html.append("<tr>")
        c = 0
        while c < len(matrix[r]):
            if (r, c) in rowspan_at:
                c += 1
                continue
            idx_val = matrix[r][c]
            cell = cells[idx_val] if idx_val < len(cells) else {}
            text = (cell.get("text") or "").strip()
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text = text.replace('"', "&quot;").replace("\n", "<br>")
            rspan = get_rowspan(matrix, r, c)
            cspan = get_colspan(matrix, r, c)
            attrs = ['style="text-align:center"']
            if rspan > 1:
                attrs.append('rowspan="{}"'.format(rspan))
            if cspan > 1:
                attrs.append('colspan="{}"'.format(cspan))
            html.append("<td {}>{}</td>".format(" ".join(attrs), text or ""))
            c += cspan
        html.append("</tr>")
    html.append("</table>")
    return "\n".join(html)


def _replace_tables_with_html(md_content: str, parse_data: dict) -> str:
    tables = []
    for p in sorted(parse_data.get("pages", []), key=lambda x: x.get("page_num", 0)):
        tables.extend(p.get("tables") or [])
    if not tables:
        return md_content
    table_pattern = re.compile(r"(\|[^\n]+\|\s*\n)+", re.MULTILINE)
    idx = [0]

    def repl(m):
        if idx[0] >= len(tables):
            return m.group(0)
        html = _table_to_html(tables[idx[0]])
        idx[0] += 1
        return html + "\n"

    return table_pattern.sub(repl, md_content)


def _build_markdown_from_pages(pages: List[dict]) -> str:
    parts = []
    for p in sorted(pages, key=lambda x: x.get("page_num", 0)):
        text = p.get("text", "")
        if text and text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts)


def _normalize_figure_to_markdown(md_content: str) -> str:
    figure_pattern = re.compile(
        r"<figure>\s*(?:!\[\]\(([^)]+)\)|<\s*img[^>]+>)\s*<figcaption>([^<]*)</figcaption>.*?</figure>",
        re.IGNORECASE | re.DOTALL,
    )

    def _repl(m):
        path = m.group(1)
        if path is None:
            # Matched <img> branch (no capturing group); extract src from match
            src_m = re.search(r'src=["\']([^"\']+)["\']', m.group(0))
            path = src_m.group(1) if src_m else "."
        cap = (m.group(2) or "").strip()
        if path and not path.startswith("./") and not path.startswith("data:"):
            path = "./" + path
        # 图注显示在图片下方，而非仅放在 alt 中（alt 通常不显示）
        if cap:
            return "![]({})\n\n*{}*".format(path, cap)
        return "![]({})".format(path)

    return figure_pattern.sub(_repl, md_content)


# 图中标签行：紧跟在 ![](...) 后的短行（如构造图标注），合并为「（图中文字：xxx）」
FIG_LABEL_MAX_LEN = 28
FIG_IMG_LINE = re.compile(r"^\s*!\[\]\([^\)]*\)\s*$")


def _collapse_figure_labels(md_content: str) -> str:
    """将图片后的多行短标签合并为单行「（图中文字：a、b、c）」或移除。"""
    lines = md_content.split("\n")
    out: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if FIG_IMG_LINE.match(line):
            out.append(line)
            i += 1
            labels: List[str] = []
            while i < len(lines):
                cur = lines[i]
                s = cur.strip()
                if not s:
                    i += 1
                    continue
                if FIG_IMG_LINE.match(cur) or cur.strip().startswith(("#", "-", "*", "<")):
                    break
                if "。" in s or "！" in s or "？" in s:
                    break
                if len(s) > FIG_LABEL_MAX_LEN:
                    break
                # 同一行可能有多项（如「触角\t\t头部」），按空白拆开
                for part in re.split(r"[\s]+", s):
                    if part:
                        labels.append(part)
                i += 1
            if labels:
                out.append("（图中文字：{}）".format("、".join(labels)))
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _inline_images_as_base64(md_content: str) -> str:
    def repl(m):
        url = m.group(1).strip()
        try:
            return "![]({})".format(_fetch_image_as_base64(url))
        except Exception as e:
            return m.group(0) + "  <!-- 下载失败: {} -->".format(e)

    return IMG_SRC_PATTERN.sub(repl, md_content)


def _inline_images_as_local(md_content: str, output_path: Path) -> str:
    out_dir = output_path.parent
    images_dir = output_path.stem + "_images"
    images_path = out_dir / images_dir
    images_path.mkdir(parents=True, exist_ok=True)
    rel_prefix = "./" + images_dir + "/"
    idx = [0]

    def repl(m):
        url = m.group(1).strip()
        try:
            raw, ext = _fetch_image_raw(url)
            fname = "{}{}".format(idx[0], ext)
            idx[0] += 1
            (images_path / fname).write_bytes(raw)
            return "![]({})".format(rel_prefix + fname)
        except Exception as e:
            return m.group(0) + "  <!-- 下载失败: {} -->".format(e)

    return IMG_SRC_PATTERN.sub(repl, md_content)


@dataclass
class _BaiduComplexConfig:
    api_key: str
    secret_key: str
    output_path: Optional[str] = None
    inline_images: bool = True


def _execute_baidu_complex(config: _BaiduComplexConfig, file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        return "错误: 文件不存在: {}".format(file_path)
    output_path_obj = Path(config.output_path) if config.output_path else path.with_suffix(".md")
    access_token = _get_access_token(config.api_key, config.secret_key)
    if not access_token:
        return "错误: 无法获取访问令牌，请检查 API 密钥"
    try:
        task_id = _submit_parser_task(access_token, str(path), path.name)
    except Exception as e:
        return "错误: {}".format(str(e))
    max_wait = 120
    poll_interval = 5
    elapsed = 0
    status = None
    result = {}
    while elapsed < max_wait:
        try:
            result = _query_parser_result(access_token, task_id)
        except Exception as e:
            return "错误: {}".format(str(e))
        status = result.get("status")
        if status == "success":
            break
        if status == "failed":
            return "错误: 文档解析失败: {}".format(result.get("task_error", "未知错误"))
        time.sleep(poll_interval)
        elapsed += poll_interval
    if status != "success":
        return "错误: 超时，任务未在 {} 秒内完成".format(max_wait)
    markdown_url = result.get("markdown_url")
    parse_result_url = result.get("parse_result_url")
    parse_data = None
    if parse_result_url:
        try:
            parse_data = _download_parse_result_json(parse_result_url)
        except Exception as e:
            logger.warning("下载 parse_result_url 失败: {}".format(e))
    md_content = None
    if markdown_url:
        try:
            md_content = _download_markdown(markdown_url)
        except Exception as e:
            logger.warning("下载 markdown 失败: {}".format(e))
    if md_content is None or not md_content.strip():
        if parse_data:
            md_content = _build_markdown_from_pages(parse_data.get("pages", []))
        else:
            return "错误: 无法获取解析结果"
    if parse_data:
        md_content = _replace_tables_with_html(md_content, parse_data)
    if "img src=" in md_content or 'img src="' in md_content:
        if config.inline_images:
            md_content = _inline_images_as_base64(md_content)
        else:
            md_content = _inline_images_as_local(md_content, output_path_obj)
    if "<figure>" in md_content or "<figcaption>" in md_content:
        md_content = _normalize_figure_to_markdown(md_content)
    md_content = _collapse_figure_labels(md_content)
    return md_content


# ----- Main router -----


class _EbookToMdImpl:
    """Unified ebook/image to Markdown."""

    def execute(self, **kwargs) -> Dict[str, Any]:
        params = kwargs.get("parameters", kwargs) if isinstance(kwargs.get("parameters"), dict) else kwargs
        input_path = params.get("input_path") or kwargs.get("input_path")
        output_path = params.get("output_path") or kwargs.get("output_path")
        ocr_backend = (params.get("ocr_backend") or kwargs.get("ocr_backend") or "baidu").lower()
        inline_images = params.get("inline_images", kwargs.get("inline_images", True))

        if not input_path:
            return {"success": False, "error": "input_path 不能为空"}

        input_type = _detect_input_type(input_path)
        if not input_type:
            return {"success": False, "error": "不支持的格式，请使用 pdf/png/jpeg/mobi/epub"}

        is_path = not (
            input_path.startswith("data:")
            or (len(input_path) > 50 and re.match(r"^[A-Za-z0-9+/]+=*$", input_path))
        )
        if is_path and not Path(input_path).exists():
            return {"success": False, "error": "文件不存在: {}".format(input_path)}

        if input_type in ("mobi", "epub"):
            try:
                pdf_path = _convert_ebook_to_pdf(input_path)
                input_path = pdf_path
                input_type = "pdf"
                _temp_ebook_pdf = pdf_path
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            _temp_ebook_pdf = None

        if ocr_backend != "baidu":
            return {"success": False, "error": "仅支持百度 OCR"}

        api_key = os.getenv("BAIDU_OCR_API_KEY")
        secret_key = os.getenv("BAIDU_OCR_SECRET_KEY")
        baidu_config = _BaiduComplexConfig(
            api_key=api_key,
            secret_key=secret_key,
            output_path=output_path,
            inline_images=inline_images,
        )
        _temp_image_file = None
        try:
            if input_type == "image":
                if is_path:
                    file_path = input_path
                else:
                    image_base64 = _read_image_file(input_path)
                    if not image_base64:
                        return {"success": False, "error": "无法读取图片"}
                    try:
                        raw = base64.b64decode(image_base64)
                    except Exception:
                        return {"success": False, "error": "无法解码图片数据"}
                    fd, _temp_image_file = tempfile.mkstemp(suffix=".png")
                    os.close(fd)
                    Path(_temp_image_file).write_bytes(raw)
                    file_path = _temp_image_file
                md_content = _execute_baidu_complex(baidu_config, file_path)
                if md_content.startswith("错误:"):
                    return {"success": False, "error": md_content}
                markdown = md_content.strip()
                if not markdown:
                    return {"success": False, "error": "未识别到文字"}

            elif input_type == "pdf":
                md_content = _execute_baidu_complex(baidu_config, input_path)
                if md_content.startswith("错误:"):
                    return {"success": False, "error": md_content}
                markdown = md_content.strip()
                if not markdown:
                    return {"success": False, "error": "未识别到文字"}
            else:
                return {"success": False, "error": "不支持的输入类型"}

            final_content = markdown
            written_path = None
            if output_path:
                out = Path(output_path)
                if out.suffix.lower() != ".md":
                    out = out.with_suffix(".md")
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(final_content, encoding="utf-8")
                written_path = str(out.resolve())

            response = {
                "success": True,
                "markdown": markdown,
                "content": final_content,
                "message": "转换成功",
            }
            if written_path:
                response["output_path"] = written_path
            return response

        finally:
            if _temp_ebook_pdf and os.path.exists(_temp_ebook_pdf):
                try:
                    os.remove(_temp_ebook_pdf)
                except OSError:
                    pass
            if _temp_image_file and os.path.exists(_temp_image_file):
                try:
                    os.remove(_temp_image_file)
                except OSError:
                    pass


def main(
    *,
    input_path: str = "",
    output_path: str = None,
    ocr_backend: str = "baidu",
    inline_images: bool = True,
    **kwargs,
) -> str:
    """Execute ebook_to_md and return str."""
    params = kwargs.get("parameters", kwargs) if isinstance(kwargs.get("parameters"), dict) else kwargs
    input_path = params.get("input_path") or input_path
    output_path = params.get("output_path") or output_path
    ocr_backend = (params.get("ocr_backend") or ocr_backend or "baidu").lower()
    inline_images = params.get("inline_images", inline_images)

    if not input_path:
        return "错误: input_path 不能为空"
    try:
        impl = _EbookToMdImpl()
        result = impl.execute(
            input_path=input_path,
            output_path=output_path,
            ocr_backend=ocr_backend,
            inline_images=inline_images,
        )
        if result.get("success"):
            msg = "转换成功"
            if result.get("output_path"):
                msg += "，已写入: {}".format(result["output_path"])
            content = result.get("content", result.get("markdown", ""))
            if content:
                preview = content[:500].strip() + ("..." if len(content) > 500 else "")
                msg += "\n\n预览:\n{}".format(preview)
            return msg
        return "错误: {}".format(result.get("error", result.get("message", "转换失败")))
    except ImportError:
        return "错误: 请安装依赖: pip install pymupdf requests"
    except Exception as e:
        logger.exception("ebook_to_md 失败: %s", e)
        return "错误: {}".format(str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF/图片/MOBI/EPUB 转 Markdown（百度 OCR）")
    parser.add_argument("--input_path", required=True, help="文档路径或 base64 图片")
    parser.add_argument("--output_path", help="输出 .md 路径")
    parser.add_argument("--ocr_backend", default="baidu", help="仅支持 baidu")
    parser.add_argument(
        "--no_inline_images",
        action="store_false",
        dest="inline_images",
        help="不将图片 base64 内联（默认内联）",
    )
    args = parser.parse_args()
    kw = {
        "input_path": args.input_path,
        "output_path": args.output_path,
        "ocr_backend": args.ocr_backend,
        "inline_images": args.inline_images,
    }
    print(main(**kw))
    sys.exit(0)
