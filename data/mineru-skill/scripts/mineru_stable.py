#!/usr/bin/env python3
"""
MinerU Document Parser - 稳健串行版 (适合网络不稳定)

支持 PDF / Word / PPT / 图片 → Markdown，一次只处理一个文件，最大化成功率
"""

import argparse
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

API_BASE = "https://mineru.net/api/v4"

SUPPORTED_EXTS = {
    ".pdf", ".docx", ".pptx",
    ".jpg", ".jpeg", ".png",
}


def collect_files(path: Path) -> list[Path]:
    files = []
    for f in sorted(path.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS:
            files.append(f)
    return files


def get_token(args):
    return args.token or os.environ.get("MINERU_TOKEN")


def headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


def process_single_file(token, file_path, output_dir, model, language, enable_formula, enable_table):
    """处理单个文件，带重试"""
    filename = Path(file_path).name
    stem = Path(file_path).stem

    # 检查是否已存在
    if (output_dir / stem).exists():
        print(f"  ⏭️  已存在: {stem}")
        return True

    print(f"  📤 {stem}...", end=" ", flush=True)

    # 获取上传链接
    for attempt in range(5):
        try:
            payload = {
                "files": [{"name": filename, "data_id": stem}],
                "model_version": model,
                "enable_formula": enable_formula,
                "enable_table": enable_table,
            }
            if language != "auto":
                payload["language"] = language
            resp = requests.post(
                f"{API_BASE}/file-urls/batch",
                headers=headers(token),
                json=payload,
                timeout=60,
            )
            result = resp.json()
            
            if result.get("code") != 0:
                raise Exception(result.get("msg"))
            
            batch_id = result["data"]["batch_id"]
            upload_url = result["data"]["file_urls"][0]
            
            # 上传
            with open(file_path, "rb") as f:
                upload_resp = requests.put(upload_url, data=f, timeout=300)
            
            if upload_resp.status_code != 200:
                raise Exception(f"上传状态码: {upload_resp.status_code}")
            
            print("⏳ 解析中...", end=" ", flush=True)
            
            # 等待解析
            for _ in range(120):  # 最多等 10 分钟
                status_resp = requests.get(
                    f"{API_BASE}/extract-results/batch/{batch_id}",
                    headers=headers(token),
                    timeout=30,
                )
                results = status_resp.json()["data"]["extract_result"]
                
                if results:
                    state = results[0].get("state")
                    if state == "done":
                        # 下载
                        zip_url = results[0]["full_zip_url"]
                        zip_path = output_dir / f"{stem}.zip"
                        
                        dl_resp = requests.get(zip_url, timeout=300)
                        zip_path.write_bytes(dl_resp.content)
                        
                        extract_dir = output_dir / stem
                        with zipfile.ZipFile(zip_path) as zf:
                            zf.extractall(extract_dir)
                        
                        zip_path.unlink()
                        
                        # 重命名
                        md = extract_dir / "full.md"
                        if md.exists():
                            md.rename(extract_dir / f"{stem}.md")
                        
                        print("✅")
                        return True
                    
                    elif state == "failed":
                        raise Exception(results[0].get("err_msg", "解析失败"))
                
                time.sleep(5)
            
            raise Exception("等待超时")
            
        except Exception as e:
            if attempt < 4:
                print(f"🔄 重试{attempt+1}...", end=" ", flush=True)
                time.sleep(3)
            else:
                print(f"❌ {e}")
                return False
    
    return False


def main():
    parser = argparse.ArgumentParser(description="MinerU Document Parser (稳健串行版)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", help="Input directory (PDF/Word/PPT/images)")
    group.add_argument("--file", help="Single file path")
    parser.add_argument("--output", required=True)
    parser.add_argument("--token")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--model", default="vlm",
                        choices=["pipeline", "vlm", "MinerU-HTML"],
                        help="Model version (default: vlm)")
    parser.add_argument("--language", default="auto",
                        choices=["auto", "en", "ch"],
                        help="Document language (default: auto)")
    parser.add_argument("--no-formula", action="store_true",
                        help="Disable formula recognition")
    parser.add_argument("--no-table", action="store_true",
                        help="Disable table extraction")

    args = parser.parse_args()

    token = get_token(args)
    if not token:
        print("❌ 请设置 MINERU_TOKEN — https://mineru.net/user-center/api-token")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 收集文件
    if args.file:
        input_files = [Path(args.file)]
    else:
        input_files = collect_files(Path(args.dir))

    if not input_files:
        print("❌ 未找到支持的文件 (PDF/docx/pptx/jpg/png)")
        sys.exit(1)

    # 过滤已处理的
    if args.resume:
        original = len(input_files)
        input_files = [f for f in input_files if not (output_dir / f.stem).exists()]
        skipped = original - len(input_files)
        if skipped:
            print(f"⏭️  跳过已处理: {skipped} 个\n")

    if not input_files:
        print("✅ 所有文件已完成!")
        return

    print(f"📚 待处理: {len(input_files)} 个文件 (模型: {args.model})\n")

    enable_formula = not args.no_formula
    enable_table = not args.no_table

    success = 0
    failed = 0
    failed_files = []

    start = time.time()

    for i, f in enumerate(input_files):
        print(f"[{i+1}/{len(input_files)}]", end=" ")
        if process_single_file(token, f, output_dir, args.model, args.language, enable_formula, enable_table):
            success += 1
        else:
            failed += 1
            failed_files.append(f.name)
    
    elapsed = time.time() - start
    print(f"\n{'='*50}")
    print(f"✅ 成功: {success}")
    print(f"❌ 失败: {failed}")
    print(f"⏱️  耗时: {elapsed/60:.1f} 分钟")
    
    if failed_files:
        print(f"\n失败文件: {failed_files}")


if __name__ == "__main__":
    main()
