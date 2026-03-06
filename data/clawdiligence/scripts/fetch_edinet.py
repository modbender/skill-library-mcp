#!/usr/bin/env python3
"""EDINET から有価証券報告書 PDF を取得する.

Usage:
    python3 fetch_edinet.py --company "会社名" --output ./data
    python3 fetch_edinet.py --corp-number 1234567890123 --output ./data
    python3 fetch_edinet.py --date 2025-06-30 --company "会社名" --output ./data

Output:
    ダウンロードした PDF のパスを stdout に出力する。
    見つからない場合は exit code 1 で終了し、エラーメッセージを stderr に出力。

Environment:
    EDINET_API_KEY  - EDINET API サブスクリプションキー (必須)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

try:
    import httpx
except ImportError:
    print("ERROR: httpx が必要です。`uv pip install httpx` を実行してください。", file=sys.stderr)
    sys.exit(1)

EDINET_BASE = "https://api.edinet-fsa.go.jp/api/v2"


def search_documents(api_key: str, target_date: str) -> list[dict]:
    """指定日の書類一覧を取得."""
    url = f"{EDINET_BASE}/documents.json"
    params = {"date": target_date, "type": 2, "Subscription-Key": api_key}
    resp = httpx.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])


def find_company_docs(
    results: list[dict], company: str | None, corp_number: str | None
) -> list[dict]:
    """企業名 or 法人番号でフィルタ."""
    matched = []
    for doc in results:
        # 有価証券報告書 (ordinanceCode=010, formCode=030XXX) を優先
        filer = doc.get("filerName", "")
        corp = doc.get("JCN", "")  # 法人番号フィールド
        doc_desc = doc.get("docDescription", "")

        name_match = company and company in filer
        number_match = corp_number and corp_number == corp

        if name_match or number_match:
            matched.append(doc)

    # 有報を優先、なければ何でも
    yuho = [d for d in matched if "有価証券報告書" in d.get("docDescription", "")]
    return yuho if yuho else matched


def download_pdf(api_key: str, doc_id: str, output_dir: Path) -> Path | None:
    """EDINET から書類 PDF をダウンロード (ZIP展開)."""
    url = f"{EDINET_BASE}/documents/{doc_id}"
    params = {"type": 2, "Subscription-Key": api_key}  # type=2: PDF
    resp = httpx.get(url, params=params, timeout=60)
    resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")

    if "zip" in content_type or resp.content[:2] == b"PK":
        # ZIP の場合は展開して PDF を探す
        with zipfile.ZipFile(BytesIO(resp.content)) as zf:
            pdf_names = [n for n in zf.namelist() if n.lower().endswith(".pdf")]
            if not pdf_names:
                return None
            # 最初の PDF を取り出す
            pdf_name = pdf_names[0]
            dest = output_dir / f"edinet_{doc_id}.pdf"
            dest.write_bytes(zf.read(pdf_name))
            return dest
    elif "pdf" in content_type:
        dest = output_dir / f"edinet_{doc_id}.pdf"
        dest.write_bytes(resp.content)
        return dest
    else:
        # XBRL 等の場合、そのまま保存
        dest = output_dir / f"edinet_{doc_id}.bin"
        dest.write_bytes(resp.content)
        return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="EDINET 有報 PDF 取得")
    parser.add_argument("--company", help="会社名 (部分一致)")
    parser.add_argument("--corp-number", help="法人番号 (13桁)")
    parser.add_argument("--date", help="検索日 (YYYY-MM-DD)。未指定時は直近90日を探索")
    parser.add_argument("--output", default="./data", help="出力ディレクトリ")
    args = parser.parse_args()

    if not args.company and not args.corp_number:
        print("ERROR: --company または --corp-number を指定してください。", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("EDINET_API_KEY", "")
    if not api_key:
        print("ERROR: 環境変数 EDINET_API_KEY が未設定です。", file=sys.stderr)
        print("EDINET API キーは https://disclosure.edinet-fsa.go.jp/ で取得できます。", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 日付範囲: 指定日 or 直近90日を5日刻みで探索
    if args.date:
        dates_to_check = [args.date]
    else:
        today = date.today()
        dates_to_check = [(today - timedelta(days=d)).isoformat() for d in range(0, 90, 5)]

    print(f"EDINET検索中: {args.company or args.corp_number}", file=sys.stderr)

    for check_date in dates_to_check:
        print(f"  日付: {check_date} を検索...", file=sys.stderr)
        try:
            results = search_documents(api_key, check_date)
        except httpx.HTTPError as e:
            print(f"  API エラー: {e}", file=sys.stderr)
            continue

        matched = find_company_docs(results, args.company, args.corp_number)
        if not matched:
            continue

        # 最新のものをダウンロード
        downloaded: list[str] = []
        for doc in matched[:3]:
            doc_id = doc.get("docID", "")
            desc = doc.get("docDescription", "不明")
            print(f"  発見: {desc} (docID: {doc_id})", file=sys.stderr)

            try:
                path = download_pdf(api_key, doc_id, output_dir)
                if path:
                    downloaded.append(str(path))
                    print(f"  ✓ 保存: {path}", file=sys.stderr)
            except httpx.HTTPError as e:
                print(f"  ダウンロードエラー: {e}", file=sys.stderr)

        if downloaded:
            # 成功: パスを stdout に出力
            for p in downloaded:
                print(p)
            sys.exit(0)

    print("ERROR: 該当する書類が見つかりませんでした。", file=sys.stderr)
    print("手動で PDF をダウンロードしてください:", file=sys.stderr)
    print("  - EDINET: https://disclosure2dl.edinet-fsa.go.jp", file=sys.stderr)
    print("  - 官報: https://kanpou.npb.go.jp", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
