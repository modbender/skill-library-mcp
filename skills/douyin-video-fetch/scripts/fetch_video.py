
import asyncio
import os
import re
import logging
import time
import random
import json
import argparse
from urllib.parse import unquote
from playwright.async_api import async_playwright
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHALLENGE_CHECK_INTERVAL_MS = 2000
CHALLENGE_MAX_WAIT_SECONDS = 45
DETAIL_WAIT_MS = 8000

def _looks_like_waf_challenge(html):
    if not html:
        return True
    text = html.lower()
    markers = [
        "please wait",
        "waf-jschallenge",
        "_wafchallengeid",
        "argus-csp-token",
    ]
    return any(m in text for m in markers)

async def _wait_until_page_ready(page, max_wait_seconds=CHALLENGE_MAX_WAIT_SECONDS):
    deadline = time.monotonic() + max_wait_seconds
    while time.monotonic() < deadline:
        try:
            html = await page.content()
        except Exception as e:
            msg = str(e).lower()
            if "navigating" in msg or "execution context was destroyed" in msg:
                await page.wait_for_timeout(CHALLENGE_CHECK_INTERVAL_MS)
                continue
            return False
        if not _looks_like_waf_challenge(html):
            return True
        await page.wait_for_timeout(CHALLENGE_CHECK_INTERVAL_MS)
    return False

def _first_http_url(urls):
    if not isinstance(urls, list):
        return None
    for url in urls:
        if isinstance(url, str) and url.startswith("http"):
            return url
    return None

def _extract_src_from_aweme_detail(detail_payload):
    if not isinstance(detail_payload, dict):
        return None
    aweme = detail_payload.get("aweme_detail")
    if not isinstance(aweme, dict):
        return None
    video = aweme.get("video")
    if not isinstance(video, dict):
        return None

    # Prefer highest bitrate candidates first.
    bit_rates = video.get("bit_rate")
    if isinstance(bit_rates, list):
        sortable = []
        for item in bit_rates:
            if not isinstance(item, dict):
                continue
            score = item.get("bit_rate", 0)
            play_addr = item.get("play_addr")
            urls = play_addr.get("url_list") if isinstance(play_addr, dict) else []
            src = _first_http_url(urls)
            if src:
                sortable.append((score, src))
        if sortable:
            sortable.sort(key=lambda x: x[0], reverse=True)
            return sortable[0][1]

    # Fallbacks from detail payload.
    for key in ["play_addr_h264", "play_addr", "download_addr", "play_addr_265"]:
        addr = video.get(key)
        if isinstance(addr, dict):
            src = _first_http_url(addr.get("url_list"))
            if src:
                return src
    return None

def _deep_find_aweme_detail(obj):
    """
    Best-effort deep search for a dict that looks like {"aweme_detail": {...}}.
    """
    if isinstance(obj, dict):
        if "aweme_detail" in obj and isinstance(obj.get("aweme_detail"), dict):
            return obj
        for v in obj.values():
            found = _deep_find_aweme_detail(v)
            if found:
                return found
    elif isinstance(obj, list):
        for it in obj:
            found = _deep_find_aweme_detail(it)
            if found:
                return found
    return None

def _extract_src_from_sigi_state(state: dict):
    """
    Extract play URL from Douyin's SIGI_STATE blob (if present in HTML).
    Structure varies; we try common shapes.
    """
    if not isinstance(state, dict):
        return None
    
    # We don't have video_id constraint here easily, so we take the first valid video src we find
    # or iterate through itemModule to find a likely candidate. 
    # Since we are loading a specific video page, there should be one main video.
    
    item_module = state.get("ItemModule") or state.get("itemModule") or {}
    if isinstance(item_module, dict):
        for _k, v in item_module.items():
            if not isinstance(v, dict):
                continue
            video = v.get("video") or {}
            if not isinstance(video, dict):
                continue
            # Try common fields.
            for key in ["playAddr", "play_addr", "downloadAddr", "download_addr"]:
                addr = video.get(key)
                if isinstance(addr, dict):
                    src = _first_http_url(addr.get("urlList") or addr.get("url_list") or [])
                    if src:
                        return src
    return None

def _extract_from_html_fallback(html: str):
    """
    Fallbacks when network listeners don't catch aweme/detail:
    1) <script id="SIGI_STATE" type="application/json">...</script>
    2) RENDER_DATA=... (urlencoded json) presence in HTML.
    """
    if not html:
        return None

    # SIGI_STATE JSON
    m = re.search(r'<script[^>]+id="SIGI_STATE"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            state = json.loads(m.group(1))
            src = _extract_src_from_sigi_state(state)
            if src:
                logger.info("Extracted src from SIGI_STATE")
                return src
        except Exception:
            pass

    # RENDER_DATA urlencoded JSON sometimes appears as query-like "RENDER_DATA=..."
    m = re.search(r"RENDER_DATA=([^&]+)&", html)
    if m:
        try:
            decoded = unquote(m.group(1))
            data = json.loads(decoded)
            found = _deep_find_aweme_detail(data)
            src = _extract_src_from_aweme_detail(found) if found else None
            if src:
                logger.info("Extracted src from RENDER_DATA")
                return src
        except Exception:
            pass

    return None

async def download_video(video_url, output_path):
    """
    Open page, get video src, download file.
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN"
        )
        
        page = await context.new_page()
        try:
            logger.info(f"Processing URL: {video_url}")
            aweme_detail_payload = None
            media_candidates = []
            response_tasks = []
            
            # Block non-essential assets to reduce load while keeping scripts/media.
            async def route_handler(route):
                if route.request.resource_type in ["image", "font", "stylesheet"]:
                    await route.abort()
                else:
                    await route.continue_()

            await page.route("**/*", route_handler)

            async def handle_response(response):
                nonlocal aweme_detail_payload
                try:
                    url = response.url
                    if (
                        response.status in [200, 206]
                        and "douyinvod.com" in url
                        and url.startswith("http")
                    ):
                        media_candidates.append(url)

                    if (
                        response.status == 200
                        and "/aweme/v1/web/aweme/detail/" in url
                        and aweme_detail_payload is None
                    ):
                        aweme_detail_payload = await response.json()
                except Exception:
                    return

            def on_response(response):
                task = asyncio.create_task(handle_response(response))
                response_tasks.append(task)

            page.on("response", on_response)

            try:
                await page.goto(video_url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                logger.warning(f"Timeout/Error loading page: {e}")
                return False

            # Fast fail for "video not found" redirects (avoid burning retries / time).
            try:
                u = (page.url or "").lower()
                if "web_video_404_link" in u or "item_non_existent" in u:
                    logger.warning(f"Video appears non-existent (url={page.url})")
                    return False
            except Exception:
                pass

            # Douyin may first return a WAF challenge page; wait until the real page is ready.
            ready = await _wait_until_page_ready(page, max_wait_seconds=CHALLENGE_MAX_WAIT_SECONDS)
            if not ready:
                logger.warning(f"WAF challenge not resolved in time")
                return False

            # Give async response listeners a short window to capture aweme/detail and media URLs.
            await page.wait_for_timeout(DETAIL_WAIT_MS)
            if response_tasks:
                await asyncio.gather(*response_tasks, return_exceptions=True)

            src = None
            if aweme_detail_payload:
                logger.info("Found aweme_detail payload via network interception")
                src = _extract_src_from_aweme_detail(aweme_detail_payload)
            
            if not src and media_candidates:
                logger.info("Using intercepted media candidate")
                src = media_candidates[0]
            
            if not src:
                try:
                    html = await page.content()
                    src = _extract_from_html_fallback(html)
                except Exception:
                    src = None
            
            if not src:
                # Fallback: parse from DOM video tag if present.
                try:
                    logger.info("Attempting DOM extraction")
                    src = await page.evaluate("""() => {
                        const v = document.querySelector('video');
                        if (!v) return null;
                        if (v.src && v.src.startsWith('http')) return v.src;
                        const sources = Array.from(v.querySelectorAll('source'));
                        const mp4 = sources.find(s => s.type === 'video/mp4');
                        return mp4 ? mp4.src : (sources[0] ? sources[0].src : null);
                    }""")
                except Exception as e:
                    logger.warning(f"DOM src evaluate failed: {e}")
                    src = None

            if not src:
                logger.warning(f"No src extraction successful")
                return False
                
            # Only use if http/https
            if not src.startswith("http"):
                logger.warning(f"Invalid src: {src}")
                return False

            # Download
            logger.info(f"Downloading stream from {src}")
            
            # Use headers that mimic browser
            headers = {
                "User-Agent": await page.evaluate("navigator.userAgent"),
                "Referer": "https://www.douyin.com/"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(src, headers=headers, timeout=120) as resp:
                    if resp.status in [200, 206]:
                        with open(output_path, 'wb') as f:
                            while True:
                                chunk = await resp.content.read(1024*1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                        
                        logger.info(f"Successfully downloaded to {output_path}")
                        return True
                    else:
                        logger.warning(f"Failed download: Status {resp.status}")
                        return False

        except Exception as e:
            logger.error(f"Error processing: {e}")
            return False
        finally:
            await page.close()
        
        await browser.close()



def normalize_input_to_url(item: str) -> str:
    item = (item or "").strip()
    if not item:
        return ""
    if item.startswith("http://") or item.startswith("https://"):
        return item
    if item.isdigit() and 8 <= len(item) <= 25:
        return f"https://www.douyin.com/video/{item}"
    return item


def read_inputs(args):
    items = []
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t and not t.startswith("#"):
                    items.append(t)
    items.extend(args.items or [])
    out, seen = [], set()
    for x in items:
        k = x.strip()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out


async def run_batch(items, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for raw in items:
        url = normalize_input_to_url(raw)
        vid_match = re.search(r"/video/(\d{8,25})", url)
        vid = vid_match.group(1) if vid_match else str(int(time.time()*1000))
        output_path = os.path.join(output_dir, f"{vid}.mp4")
        ok = await download_video(url, output_path)
        results.append({"input": raw, "url": url, "video_id": vid, "ok": bool(ok), "output": output_path if ok else ""})
    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch Douyin videos (URL or video_id)")
    parser.add_argument("items", nargs="*", help="Douyin URL(s) or video_id(s)")
    parser.add_argument("--file", help="Input file, one URL/video_id per line")
    parser.add_argument("--output-dir", default="downloads", help="Directory to save mp4 files")
    parser.add_argument("--json", action="store_true", help="Print json result")
    args = parser.parse_args()

    items = read_inputs(args)
    if not items:
        print("No input items")
        return

    results = asyncio.run(run_batch(items, args.output_dir))
    ok = sum(1 for r in results if r["ok"])
    fail = len(results) - ok
    if args.json:
        print(json.dumps({"total": len(results), "ok": ok, "failed": fail, "items": results}, ensure_ascii=False, indent=2))
    else:
        print(f"total={len(results)} ok={ok} failed={fail}")
        for r in results:
            status = "OK" if r["ok"] else "FAIL"
            print(f"[{status}] {r['input']} -> {r['output'] or r['url']}")


if __name__ == "__main__":
    main()
