#!/usr/bin/env python3
"""
Poly Haven API 클라이언트 — CC0 무료 에셋 검색/다운로드.

사용법:
  # 카테고리 조회
  python3 polyhaven.py categories hdris
  python3 polyhaven.py categories textures
  python3 polyhaven.py categories models

  # 에셋 검색
  python3 polyhaven.py search --type textures --categories brick
  python3 polyhaven.py search --type models --limit 10

  # 에셋 정보
  python3 polyhaven.py info abandoned_factory_canteen_01

  # 다운로드 URL 조회
  python3 polyhaven.py files ceramic_vase_03

  # 에셋 다운로드
  python3 polyhaven.py download rock_wall_08 --type textures --resolution 1k --output /tmp/textures/
  python3 polyhaven.py download meadow --type hdris --resolution 2k --format hdr --output /tmp/hdri/
  python3 polyhaven.py download food_apple_01 --type models --resolution 1k --format gltf --output /tmp/models/

Poly Haven API 문서: https://api.polyhaven.com
라이선스: CC0 (완전 무료, 상용 포함)
"""

import argparse
import json
import os
import sys

# requests가 없으면 urllib로 폴백
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    HAS_REQUESTS = False


API_BASE = "https://api.polyhaven.com"
USER_AGENT = "misskim-blender-interactive/1.0"


def _get(url, params=None):
    """HTTP GET — requests 또는 urllib 사용"""
    if HAS_REQUESTS:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    else:
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))


def _download_file(url, output_path):
    """파일 다운로드"""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    if HAS_REQUESTS:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, stream=True, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(output_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    return output_path


# ─── API 함수 ───

def get_types():
    """에셋 타입 목록"""
    return _get(f"{API_BASE}/types")


def get_categories(asset_type):
    """카테고리 목록 + 개수"""
    return _get(f"{API_BASE}/categories/{asset_type}")


def search_assets(asset_type=None, categories=None, limit=20):
    """에셋 검색"""
    params = {}
    if asset_type and asset_type != "all":
        params["type"] = asset_type
    if categories:
        params["categories"] = categories

    data = _get(f"{API_BASE}/assets", params)

    # 결과 제한
    if limit and isinstance(data, dict):
        limited = {}
        for i, (key, val) in enumerate(data.items()):
            if i >= limit:
                break
            limited[key] = val
        return {"assets": limited, "total": len(data), "returned": len(limited)}

    return data


def get_info(asset_id):
    """개별 에셋 메타데이터"""
    return _get(f"{API_BASE}/info/{asset_id}")


def get_files(asset_id):
    """에셋 파일 트리 (해상도/포맷별 다운로드 URL)"""
    return _get(f"{API_BASE}/files/{asset_id}")


def download_asset(asset_id, asset_type, resolution="1k",
                   file_format=None, output_dir="/tmp/polyhaven"):
    """에셋 다운로드 — 타입별로 적절한 파일 선택"""
    files_data = get_files(asset_id)

    downloaded = []

    if asset_type == "hdris":
        fmt = file_format or "hdr"
        if "hdri" in files_data and resolution in files_data["hdri"]:
            res_data = files_data["hdri"][resolution]
            if fmt in res_data:
                url = res_data[fmt]["url"]
                path = os.path.join(output_dir, f"{asset_id}_{resolution}.{fmt}")
                _download_file(url, path)
                downloaded.append({"type": "hdri", "path": path, "format": fmt})

    elif asset_type == "textures":
        # PBR 텍스처 — 여러 맵 다운로드
        fmt = file_format or "jpg"
        for map_type, res_dict in files_data.items():
            if map_type in ("Diffuse", "nor_gl", "Rough", "Displacement", "AO",
                           "arm", "nor_dx", "bump", "Metal"):
                if isinstance(res_dict, dict) and resolution in res_dict:
                    fmt_dict = res_dict[resolution]
                    if fmt in fmt_dict:
                        url = fmt_dict[fmt]["url"]
                        path = os.path.join(output_dir, f"{asset_id}_{map_type}_{resolution}.{fmt}")
                        _download_file(url, path)
                        downloaded.append({"type": map_type, "path": path, "format": fmt})

    elif asset_type == "models":
        fmt = file_format or "gltf"
        if fmt in files_data and resolution in files_data[fmt]:
            fmt_data = files_data[fmt][resolution]
            if fmt in fmt_data:
                url = fmt_data[fmt]["url"]
                ext = fmt
                path = os.path.join(output_dir, f"{asset_id}.{ext}")
                _download_file(url, path)
                downloaded.append({"type": "model", "path": path, "format": fmt})

    return {
        "asset_id": asset_id,
        "asset_type": asset_type,
        "resolution": resolution,
        "downloaded": downloaded,
        "count": len(downloaded),
    }


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(description="Poly Haven API Client")
    sub = parser.add_subparsers(dest="action", required=True)

    # categories
    p_cat = sub.add_parser("categories", help="List categories")
    p_cat.add_argument("asset_type", choices=["hdris", "textures", "models", "all"])

    # search
    p_search = sub.add_parser("search", help="Search assets")
    p_search.add_argument("--type", dest="asset_type", default="all")
    p_search.add_argument("--categories", default=None)
    p_search.add_argument("--limit", type=int, default=20)

    # info
    p_info = sub.add_parser("info", help="Asset info")
    p_info.add_argument("asset_id")

    # files
    p_files = sub.add_parser("files", help="Asset files/URLs")
    p_files.add_argument("asset_id")

    # download
    p_dl = sub.add_parser("download", help="Download asset")
    p_dl.add_argument("asset_id")
    p_dl.add_argument("--type", dest="asset_type", required=True,
                      choices=["hdris", "textures", "models"])
    p_dl.add_argument("--resolution", default="1k")
    p_dl.add_argument("--format", dest="file_format", default=None)
    p_dl.add_argument("--output", default="/tmp/polyhaven")

    args = parser.parse_args()

    if args.action == "categories":
        result = get_categories(args.asset_type)
    elif args.action == "search":
        result = search_assets(args.asset_type, args.categories, args.limit)
    elif args.action == "info":
        result = get_info(args.asset_id)
    elif args.action == "files":
        result = get_files(args.asset_id)
    elif args.action == "download":
        result = download_asset(
            args.asset_id, args.asset_type,
            args.resolution, args.file_format, args.output
        )
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
