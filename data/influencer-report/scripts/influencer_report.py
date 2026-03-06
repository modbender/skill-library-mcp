#!/usr/bin/env python3
"""
Influencer Vetting Report Generator

Uses Memories.ai V1 API to scrape creator profiles and V2 API for deep video analysis.

Environment variables required:
  MEMORIES_V1_API_KEY - Memories.ai V1 API key (scraper, list, search)
  MEMORIES_API_KEY    - Memories.ai V2 API key (MAI transcript, metadata)
"""

import argparse
import json
import os
import sys
import time
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

V1_BASE = "https://api.memories.ai/serve/api/v1"
V2_BASE = "https://mavi-backend.memories.ai/serve/api/v2"

PLATFORM_MAI_ENDPOINTS = {
    "youtube": "/youtube/video/mai/transcript",
    "tiktok": "/tiktok/video/mai/transcript",
    "instagram": "/instagram/video/mai/transcript",
    "twitter": "/twitter/video/mai/transcript",
}

PLATFORM_METADATA_ENDPOINTS = {
    "youtube": "/youtube/video/metadata",
    "tiktok": "/tiktok/video/metadata",
    "instagram": "/instagram/video/metadata",
    "twitter": "/twitter/video/metadata",
}

POLL_INTERVAL = 15
POLL_TIMEOUT = 300
SCRAPER_POLL_TIMEOUT = 600  # scraping can take longer


def env_required(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: Environment variable {name} is required", file=sys.stderr)
        sys.exit(1)
    return val


def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "tiktok.com" in url_lower:
        return "tiktok"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "instagram.com" in url_lower:
        return "instagram"
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return "twitter"
    return ""


# ---------------------------------------------------------------------------
# V1 API: Scrape, List, Search
# ---------------------------------------------------------------------------

def v1_scrape(profile_url: str, count: int, v1_key: str, callback_url: str = "") -> Optional[str]:
    """Scrape a creator's recent videos via V1 scraper. Returns task_id."""
    url = f"{V1_BASE}/scraper"
    headers = {"Authorization": v1_key, "Content-Type": "application/json"}
    payload = {
        "username": profile_url,
        "unique_id": "default",
        "scraper_cnt": count,
    }
    if callback_url:
        payload["callback_url"] = callback_url

    print(f"[V1] Scraping profile: {profile_url} (count={count})...")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "0000":
            task_id = data["data"]["taskId"]
            print(f"[V1] Scraper task ID: {task_id}")
            return task_id
        else:
            print(f"WARNING: V1 scraper error: {data}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"WARNING: V1 scraper failed: {e}", file=sys.stderr)
        return None


def v1_list_videos(v1_key: str) -> list[dict]:
    """List all videos in the V1 library."""
    url = f"{V1_BASE}/list_videos"
    headers = {"Authorization": v1_key, "Content-Type": "application/json"}

    print("[V1] Listing videos in library...")
    try:
        resp = requests.post(url, headers=headers, json={}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        videos = data.get("data", [])
        if isinstance(videos, dict):
            videos = videos.get("videos", [])
        print(f"[V1] Found {len(videos)} videos in library")
        return videos
    except Exception as e:
        print(f"WARNING: V1 list_videos failed: {e}", file=sys.stderr)
        return []


def v1_search(query: str, v1_key: str, top_k: int = 5) -> list[dict]:
    """Search videos in library via V1."""
    url = f"{V1_BASE}/search"
    headers = {"Authorization": v1_key, "Content-Type": "application/json"}
    payload = {
        "search_param": query,
        "search_type": "BY_VIDEO",
        "top_k": top_k,
    }

    print(f"[V1] Searching: '{query}'...")
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("data", [])
        if isinstance(results, dict):
            results = results.get("results", [])
        print(f"[V1] Search returned {len(results)} results")
        return results
    except Exception as e:
        print(f"WARNING: V1 search failed: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# V2 API: MAI Transcript, Metadata
# ---------------------------------------------------------------------------

def v2_mai_transcript(video_url: str, platform: str, v2_key: str) -> Optional[str]:
    """Submit video for MAI transcript (visual + audio). Returns task_id."""
    endpoint = PLATFORM_MAI_ENDPOINTS.get(platform)
    if not endpoint:
        print(f"WARNING: No MAI endpoint for '{platform}'", file=sys.stderr)
        return None

    url = f"{V2_BASE}{endpoint}"
    headers = {"Authorization": v2_key, "Content-Type": "application/json"}

    print(f"[V2] Submitting MAI transcript: {video_url[:80]}...")
    try:
        resp = requests.post(url, headers=headers, json={"video_url": video_url}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "0000":
            task_id = data["data"]["task_id"]
            print(f"[V2] MAI task ID: {task_id}")
            return task_id
        else:
            print(f"WARNING: V2 MAI error: {data}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"WARNING: V2 MAI failed: {e}", file=sys.stderr)
        return None


def v2_metadata(video_url: str, platform: str, v2_key: str) -> Optional[dict]:
    """Get video metadata (engagement stats) via V2."""
    endpoint = PLATFORM_METADATA_ENDPOINTS.get(platform)
    if not endpoint:
        return None

    url = f"{V2_BASE}{endpoint}"
    headers = {"Authorization": v2_key, "Content-Type": "application/json"}

    print(f"[V2] Fetching metadata: {video_url[:80]}...")
    try:
        resp = requests.post(url, headers=headers,
                             json={"video_url": video_url, "channel": "rapid"}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "0000":
            return data.get("data", {})
        return None
    except Exception as e:
        print(f"WARNING: V2 metadata failed: {e}", file=sys.stderr)
        return None


def poll_result(task_id: str) -> Optional[dict]:
    """Poll webhook results endpoint for task completion."""
    webhook_url = f"https://demo.memories-ai.org/webhooks/memories/result/{task_id}"

    print(f"[Poll] Waiting for task {task_id}...")
    for attempt in range(int(POLL_TIMEOUT / POLL_INTERVAL)):
        time.sleep(POLL_INTERVAL)
        try:
            resp = requests.get(webhook_url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "completed" or data.get("data"):
                    print(f"[Poll] Task {task_id} completed")
                    return data
        except Exception:
            pass
        print(f"[Poll] Attempt {attempt + 1}...")

    print(f"WARNING: Timed out waiting for task {task_id}", file=sys.stderr)
    return None


def parse_mai_result(result: dict) -> dict:
    """Parse MAI transcript result into structured analysis."""
    analysis = {"video_transcript": "", "audio_transcript": "", "scenes": []}
    if not result:
        return analysis

    data = result.get("data", result)

    vt = data.get("videoTranscript", {}).get("data", {}).get("data", [])
    if vt:
        analysis["scenes"] = vt
        analysis["video_transcript"] = " | ".join(
            item.get("description", "") for item in vt[:10]
        )

    at = data.get("audioTranscript", {}).get("data", {}).get("data", [])
    if at:
        analysis["audio_transcript"] = " ".join(item.get("text", "") for item in at)

    return analysis


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_video(analysis: dict, metadata: Optional[dict] = None) -> dict:
    scores = {
        "camera_facing": False,
        "audio_quality": False,
        "lighting": False,
        "content_relevance": False,
        "brand_safety": True,
    }
    notes = {k: "" for k in scores}

    vt = analysis.get("video_transcript", "").lower()
    at = analysis.get("audio_transcript", "").lower()
    scenes = analysis.get("scenes", [])

    # Camera-facing
    face_kw = ["person", "face", "woman", "man", "speaking", "talking", "looking at camera", "selfie"]
    if any(kw in vt for kw in face_kw):
        scores["camera_facing"] = True
        notes["camera_facing"] = "Creator visible in frame"
    else:
        notes["camera_facing"] = "Creator not clearly visible"

    # Audio
    if len(at) > 50:
        scores["audio_quality"] = True
        notes["audio_quality"] = "Clear speech detected"
    else:
        notes["audio_quality"] = "Limited or no speech detected"

    # Lighting
    if any(kw in vt for kw in ["dark", "dim", "poor lighting", "grainy"]):
        notes["lighting"] = "Poor lighting detected"
    else:
        scores["lighting"] = True
        notes["lighting"] = "Acceptable lighting"

    # Content relevance
    if len(at) > 100 or len(scenes) >= 3:
        scores["content_relevance"] = True
        notes["content_relevance"] = "Substantial content"
    else:
        notes["content_relevance"] = "Limited content"

    # Brand safety
    unsafe = ["violence", "drugs", "explicit", "hate", "offensive", "nsfw", "weapon", "gun"]
    for kw in unsafe:
        if kw in vt or kw in at:
            scores["brand_safety"] = False
            notes["brand_safety"] = f"Flagged: '{kw}' detected"
            break
    if scores["brand_safety"]:
        notes["brand_safety"] = "No safety concerns detected"

    weights = {"camera_facing": 20, "audio_quality": 15, "lighting": 15,
               "content_relevance": 25, "brand_safety": 25}
    total = sum(weights[k] for k, v in scores.items() if v)

    return {"scores": scores, "notes": notes, "total": total, "metadata": metadata}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate influencer vetting report")
    parser.add_argument("--handle", required=True, help="Influencer handle (e.g. charlidamelio)")
    parser.add_argument("--profile-url", default=None,
                        help="Creator profile URL (e.g. https://www.tiktok.com/@handle)")
    parser.add_argument("--platform", default=None,
                        choices=["instagram", "tiktok", "youtube", "twitter"])
    parser.add_argument("--videos", nargs="*",
                        help="Direct video URLs (skips V1 scraper)")
    parser.add_argument("--scrape-count", type=int, default=5,
                        help="Number of recent videos to scrape (default: 5)")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--skip-analysis", action="store_true", help="Dry run")
    args = parser.parse_args()

    v1_key = env_required("MEMORIES_V1_API_KEY")
    v2_key = env_required("MEMORIES_API_KEY")

    video_urls = []
    platform = args.platform

    if args.videos:
        # Direct video URLs provided
        video_urls = args.videos
        if not platform and video_urls:
            platform = detect_platform(video_urls[0])
    elif args.profile_url:
        # Step 1: Scrape via V1
        if not platform:
            platform = detect_platform(args.profile_url)
        task_id = v1_scrape(args.profile_url, args.scrape_count, v1_key)
        if task_id:
            print(f"[Info] Scraper running, waiting for ingestion...")
            time.sleep(30)  # give scraper time to ingest

        # Step 2: List videos
        all_videos = v1_list_videos(v1_key)

        # Step 3: Search for relevant content
        search_results = v1_search("creator talking to camera", v1_key, top_k=args.scrape_count)

        # Extract video URLs from library
        for v in all_videos[:args.scrape_count]:
            url = v.get("video_url") or v.get("url") or v.get("videoUrl", "")
            if url:
                video_urls.append(url)

        # Also check search results
        for r in search_results:
            url = r.get("video_url") or r.get("url") or r.get("videoUrl", "")
            if url and url not in video_urls:
                video_urls.append(url)
    else:
        print("ERROR: Provide --profile-url or --videos", file=sys.stderr)
        sys.exit(1)

    if not platform:
        platform = "tiktok"  # fallback

    if not video_urls:
        print("ERROR: No video URLs found", file=sys.stderr)
        sys.exit(1)

    video_urls = video_urls[:args.scrape_count]
    print(f"\n[Info] Analyzing {len(video_urls)} videos on {platform}\n")

    # Step 4 & 5: V2 analysis (MAI transcript + metadata)
    analyses = []
    for vurl in video_urls:
        vid_platform = detect_platform(vurl) or platform

        if args.skip_analysis:
            analyses.append({"video": {"url": vurl, "title": vurl.split("/")[-1][:60], "platform": vid_platform},
                             "analysis": {}, "score": score_video({})})
            continue

        # MAI transcript
        task_id = v2_mai_transcript(vurl, vid_platform, v2_key)
        if task_id:
            result = poll_result(task_id)
            analysis = parse_mai_result(result)
        else:
            analysis = {}

        # Metadata
        metadata = v2_metadata(vurl, vid_platform, v2_key)

        score = score_video(analysis, metadata)
        analyses.append({
            "video": {"url": vurl, "title": vurl.split("/")[-1][:60], "platform": vid_platform},
            "analysis": analysis,
            "score": score,
            "metadata": metadata,
        })

    # Generate report
    from generate_report import generate_report
    report = generate_report(handle=args.handle, platform=platform, analyses=analyses)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\n[Done] Report saved to {args.output}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()
