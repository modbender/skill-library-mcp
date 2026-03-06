import argparse
import json
import re
import urllib.request
from urllib.error import URLError, HTTPError


def _fetch_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def _extract_store_json(html: str) -> dict:
    marker = "store: "
    start = html.find(marker)
    if start == -1:
        return {}

    i = html.find("{", start + len(marker))
    if i == -1:
        return {}

    depth = 0
    in_str = False
    esc = False

    for j in range(i, len(html)):
        ch = html[j]

        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                raw = html[i : j + 1]
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {}

    return {}


def _vtt_to_text(vtt: str) -> str:
    lines = vtt.splitlines()
    out = []

    ts_pattern = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}$")

    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s == "WEBVTT":
            continue
        if ts_pattern.match(s):
            continue
        if s.isdigit():
            continue
        out.append(s)

    # remove immediate duplicates
    deduped = []
    prev = None
    for line in out:
        if line != prev:
            deduped.append(line)
        prev = line

    return "\n".join(deduped).strip()


def _parse_from_store(store: dict) -> dict:
    viewer = store.get("viewer", {}) if isinstance(store, dict) else {}
    item = viewer.get("item", {}) if isinstance(viewer, dict) else {}

    attrs = item.get("attributes", {}) if isinstance(item, dict) else {}
    links = item.get("links", {}) if isinstance(item, dict) else {}

    title = (
        attrs.get("name_without_extension")
        or attrs.get("name")
        or "Title not found"
    )

    smart_actions = (
        viewer.get("smart_actions", {})
        .get("attributes", {})
        .get("smart_action_data", "")
    )

    chapters = (
        viewer.get("item_ai_metadata", {})
        .get("data", {})
        .get("attributes", {})
        .get("chapters", [])
    )

    share_url = links.get("share_url")
    hls_url = links.get("hls_url")
    captions_url = links.get("captions_url")

    # Some pages expose mp4 in attrs; otherwise keep empty.
    mp4_url = attrs.get("source_mp4") or attrs.get("source_url") or ""

    return {
        "video_title": title,
        "share_url": share_url,
        "mp4_url": mp4_url,
        "hls_url": hls_url,
        "captions_url": captions_url,
        "smart_actions": smart_actions,
        "chapters": chapters,
    }


def run(*args, **kwargs):
    zight_url = kwargs.get("zight_url") or (args[0] if args else None)

    if not zight_url:
        print(json.dumps({"error": "No Zight URL provided."}, indent=2))
        return

    # Accept common Zight share URL formats, including:
    # - https://a.cl.ly/XXXXX
    # - https://share.zight.com/XXXXX
    if not re.match(r"^https?://", zight_url, re.I):
        zight_url = "https://" + zight_url

    try:
        html = _fetch_text(zight_url)
    except (HTTPError, URLError, TimeoutError, ValueError) as e:
        print(json.dumps({"error": f"Failed to fetch Zight URL: {e}"}, indent=2))
        return

    store = _extract_store_json(html)
    if not store:
        print(json.dumps({"error": "Could not parse Zight page data (store JSON not found)."}, indent=2))
        return

    output = _parse_from_store(store)

    transcript = ""
    captions_url = output.get("captions_url")
    if captions_url:
        try:
            vtt = _fetch_text(captions_url)
            transcript = _vtt_to_text(vtt)
        except Exception as e:
            transcript = f"Failed to fetch/parse captions: {e}"

    output["transcript"] = transcript

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts information from a Zight share URL.")
    parser.add_argument("--zight-url", required=True, help="The Zight share URL")
    args = parser.parse_args()
    run(zight_url=args.zight_url)
