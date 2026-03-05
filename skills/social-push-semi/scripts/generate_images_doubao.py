#!/usr/bin/env python3
import argparse, base64, json, os, pathlib, sys, time
import requests


def save_image_from_item(item: dict, out_path: pathlib.Path):
    if isinstance(item, dict):
        if item.get("b64_json"):
            out_path.write_bytes(base64.b64decode(item["b64_json"]))
            return True
        if item.get("url"):
            r = requests.get(item["url"], timeout=60)
            r.raise_for_status()
            out_path.write_bytes(r.content)
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--size", default="1920x1920")
    ap.add_argument("--api-key-env", default="DOUBAO_API_KEY")
    args = ap.parse_args()

    key = os.environ.get(args.api_key_env, "").strip()
    if not key:
        print(f"Missing env: {args.api_key_env}", file=sys.stderr)
        sys.exit(2)

    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    endpoint = args.base_url.rstrip("/") + "/images/generations"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    generated = []
    for i in range(1, args.count + 1):
        payload = {
            "model": args.model,
            "prompt": args.prompt + f"\n\n第{i}张：构图和细节与其他图有差异。",
            "size": args.size,
            "n": 1,
        }
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        if resp.status_code >= 300:
            print(f"API error {resp.status_code}: {resp.text[:400]}", file=sys.stderr)
            sys.exit(3)
        data = resp.json()
        items = data.get("data") or []
        if not items:
            print(f"No image data in response: {json.dumps(data)[:400]}", file=sys.stderr)
            sys.exit(4)
        out_path = out / f"img{i}.png"
        ok = save_image_from_item(items[0], out_path)
        if not ok:
            print(f"Unsupported response format: {json.dumps(items[0])[:400]}", file=sys.stderr)
            sys.exit(5)
        generated.append(str(out_path))
        time.sleep(0.4)

    print(json.dumps({"images": generated}, ensure_ascii=False))


if __name__ == "__main__":
    main()
