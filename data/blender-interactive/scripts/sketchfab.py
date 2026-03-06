#!/usr/bin/env python3
"""
Sketchfab 3D 모델 검색/다운로드 클라이언트.
Blender MCP의 Sketchfab 통합에서 개념을 흡수하여 자체 구현.

무료 다운로드 가능한 3D 모델 검색 → glTF 다운로드 → Blender 임포트 파이프라인.

사용법:
    python3 sketchfab.py search "dragon" --downloadable --max 10
    python3 sketchfab.py info <model_uid>
    python3 sketchfab.py download <model_uid> --output /tmp/models/
"""

import argparse
import json
import os
import sys
import time
import zipfile
from urllib import request, parse, error

API_BASE = "https://api.sketchfab.com/v3"
USER_AGENT = "misskim-blender-interactive/1.0"


def _request(url, headers=None):
    """HTTP GET 요청"""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    req = request.Request(url, headers=hdrs)
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def search_models(query, downloadable=True, max_results=10, sort_by="relevance",
                  categories=None, animated=None, license_type=None):
    """Sketchfab 모델 검색.

    Args:
        query: 검색어
        downloadable: 다운로드 가능한 모델만 (기본 True)
        max_results: 최대 결과 수 (1-24)
        sort_by: 정렬 (relevance, likeCount, viewCount, publishedAt)
        categories: 카테고리 필터 (characters, nature, architecture 등)
        animated: 애니메이션 모델만 필터
        license_type: 라이선스 (by, by-sa, by-nd, by-nc, cc0 등)
    """
    params = {
        "type": "models",
        "q": query,
        "count": min(max_results, 24),
        "sort_by": f"-{sort_by}",
    }
    if downloadable:
        params["downloadable"] = "true"
    if categories:
        params["categories"] = categories
    if animated is not None:
        params["animated"] = str(animated).lower()
    if license_type:
        params["license"] = license_type

    url = f"{API_BASE}/search?{parse.urlencode(params)}"
    data = _request(url)

    if "error" in data:
        return data

    results = []
    for item in data.get("results", []):
        model = {
            "uid": item.get("uid"),
            "name": item.get("name"),
            "description": (item.get("description") or "")[:200],
            "url": item.get("viewerUrl"),
            "vertex_count": item.get("vertexCount", 0),
            "face_count": item.get("faceCount", 0),
            "animated": item.get("isAnimated", False),
            "license": item.get("license", {}).get("slug", "unknown"),
            "user": item.get("user", {}).get("displayName", "unknown"),
            "likes": item.get("likeCount", 0),
            "views": item.get("viewCount", 0),
            "thumbnail": "",
        }
        # 썸네일 추출
        thumbs = item.get("thumbnails", {}).get("images", [])
        for t in thumbs:
            if t.get("width", 0) >= 200:
                model["thumbnail"] = t.get("url", "")
                break
        results.append(model)

    return {
        "query": query,
        "total": data.get("totalCount", 0),
        "count": len(results),
        "results": results,
    }


def get_model_info(uid):
    """모델 상세 정보 조회"""
    url = f"{API_BASE}/models/{uid}"
    data = _request(url)

    if "error" in data:
        return data

    return {
        "uid": data.get("uid"),
        "name": data.get("name"),
        "description": (data.get("description") or "")[:500],
        "url": data.get("viewerUrl"),
        "vertex_count": data.get("vertexCount", 0),
        "face_count": data.get("faceCount", 0),
        "animated": data.get("isAnimated", False),
        "license": data.get("license", {}).get("slug", "unknown"),
        "user": data.get("user", {}).get("displayName", "unknown"),
        "likes": data.get("likeCount", 0),
        "views": data.get("viewCount", 0),
        "download_count": data.get("downloadCount", 0),
        "categories": [c.get("name") for c in data.get("categories", [])],
        "tags": [t.get("name") for t in data.get("tags", [])],
    }


def download_model(uid, output_dir="/tmp/sketchfab/", api_token=None):
    """모델 다운로드 (glTF 형식).

    주의: 다운로드에는 Sketchfab API 토큰이 필요.
    무료 계정으로 토큰 발급 가능: sketchfab.com/settings/password

    Args:
        uid: 모델 UID
        output_dir: 저장 경로
        api_token: Sketchfab API 토큰 (환경변수 SKETCHFAB_TOKEN도 가능)
    """
    token = api_token or os.environ.get("SKETCHFAB_TOKEN")
    if not token:
        return {
            "error": "Sketchfab API 토큰 필요. "
                     "https://sketchfab.com/settings/password 에서 발급 후 "
                     "SKETCHFAB_TOKEN 환경변수로 설정하거나 --token 옵션 사용."
        }

    # 다운로드 URL 요청
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"Token {token}",
    }
    url = f"{API_BASE}/models/{uid}/download"
    data = _request(url, headers=headers)

    if "error" in data:
        return data

    download_url = data.get("gltf", {}).get("url")
    if not download_url:
        download_url = data.get("glb", {}).get("url")
    if not download_url:
        # source 포맷 시도
        download_url = data.get("source", {}).get("url")
    if not download_url:
        return {"error": "다운로드 URL을 찾을 수 없음"}

    # 파일 다운로드
    os.makedirs(output_dir, exist_ok=True)
    zip_path = os.path.join(output_dir, f"{uid}.zip")

    try:
        req = request.Request(download_url, headers={"User-Agent": USER_AGENT})
        with request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    except Exception as e:
        return {"error": f"다운로드 실패: {e}"}

    # 압축 해제
    extract_dir = os.path.join(output_dir, uid)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)
        os.remove(zip_path)
    except Exception as e:
        return {"error": f"압축 해제 실패: {e}"}

    # glTF/GLB 파일 찾기
    model_files = []
    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            if f.endswith((".gltf", ".glb")):
                model_files.append(os.path.join(root, f))

    return {
        "status": "success",
        "uid": uid,
        "output_dir": extract_dir,
        "model_files": model_files,
        "file_count": len(os.listdir(extract_dir)),
    }


def main():
    parser = argparse.ArgumentParser(description="Sketchfab 3D 모델 검색/다운로드")
    subparsers = parser.add_subparsers(dest="command")

    # search
    sp_search = subparsers.add_parser("search", help="모델 검색")
    sp_search.add_argument("query", help="검색어")
    sp_search.add_argument("--downloadable", action="store_true", default=True, help="다운로드 가능만")
    sp_search.add_argument("--max", type=int, default=10, help="최대 결과")
    sp_search.add_argument("--sort", default="relevance", help="정렬 (relevance/likeCount/viewCount)")
    sp_search.add_argument("--category", help="카테고리 필터")
    sp_search.add_argument("--animated", action="store_true", default=None, help="애니메이션만")
    sp_search.add_argument("--license", help="라이선스 (cc0, by, by-sa 등)")
    sp_search.add_argument("--raw", action="store_true", help="읽기 쉬운 텍스트")

    # info
    sp_info = subparsers.add_parser("info", help="모델 상세 정보")
    sp_info.add_argument("uid", help="모델 UID")

    # download
    sp_dl = subparsers.add_parser("download", help="모델 다운로드")
    sp_dl.add_argument("uid", help="모델 UID")
    sp_dl.add_argument("--output", default="/tmp/sketchfab/", help="저장 경로")
    sp_dl.add_argument("--token", help="Sketchfab API 토큰")

    args = parser.parse_args()

    if args.command == "search":
        result = search_models(
            args.query,
            downloadable=args.downloadable,
            max_results=args.max,
            sort_by=args.sort,
            categories=args.category,
            animated=args.animated,
            license_type=args.license,
        )
        if args.raw and "results" in result:
            print(f"Sketchfab 검색: '{args.query}' ({result['total']}건 중 {result['count']}건)")
            print("=" * 60)
            for i, m in enumerate(result["results"], 1):
                print(f"\n{i}. {m['name']}")
                print(f"   UID: {m['uid']}")
                print(f"   작성자: {m['user']} | 좋아요: {m['likes']} | 조회: {m['views']}")
                print(f"   버텍스: {m['vertex_count']:,} | 면: {m['face_count']:,} | 애니메이션: {m['animated']}")
                print(f"   라이선스: {m['license']}")
                if m['description']:
                    print(f"   설명: {m['description'][:100]}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "info":
        result = get_model_info(args.uid)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "download":
        result = download_model(args.uid, args.output, args.token)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
