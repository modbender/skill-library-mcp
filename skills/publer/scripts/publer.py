#!/usr/bin/env python3
"""Publer API client — upload media, schedule/publish posts, check job status."""

import argparse, json, os, sys, time, requests

BASE = "https://app.publer.com/api/v1"

def headers():
    key = os.environ.get("PUBLER_API_KEY")
    ws = os.environ.get("PUBLER_WORKSPACE_ID")
    if not key:
        sys.exit("PUBLER_API_KEY not set")
    if not ws:
        sys.exit("PUBLER_WORKSPACE_ID not set")
    return {
        "Authorization": f"Bearer-API {key}",
        "Publer-Workspace-Id": ws,
    }

def accounts(args):
    """List connected accounts."""
    r = requests.get(f"{BASE}/accounts", headers=headers())
    r.raise_for_status()
    for a in r.json():
        print(json.dumps({"id": a.get("id"), "name": a.get("name"), "network": a.get("network"), "type": a.get("type")}, indent=2))

def upload(args):
    """Upload local files, return media IDs."""
    h = headers()
    # Remove Content-Type so requests sets multipart boundary
    results = []
    for fp in args.files:
        filename = os.path.basename(fp)
        # Determine MIME type
        ext = filename.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "gif": "image/gif", "mp4": "video/mp4", "mov": "video/quicktime"}.get(ext, "application/octet-stream")
        with open(fp, "rb") as f:
            r = requests.post(f"{BASE}/media", headers=h, 
                              files={"file": (filename, f, mime)},
                              data={"direct_upload": "false", "in_library": "false"})
        r.raise_for_status()
        data = r.json()
        results.append({"id": data.get("id"), "path": data.get("path"), "name": os.path.basename(fp)})
        print(json.dumps(results[-1]))
    return results

def poll_job(job_id, h, timeout=120):
    """Poll job until completed or failed."""
    for _ in range(timeout // 3):
        r = requests.get(f"{BASE}/job_status/{job_id}", headers=h)
        r.raise_for_status()
        data = r.json()
        status = data.get("status")
        if status == "completed":
            return data
        if status in ("failed", "error"):
            sys.exit(f"Job failed: {json.dumps(data)}")
        time.sleep(3)
    sys.exit("Job timed out")

def post(args):
    """Create a TikTok carousel or video post.
    
    Usage:
      publer.py post --account-id ID --type photo --title "Title" --text "Caption" --media-ids id1,id2,id3 [--schedule ISO8601] [--auto-music] [--privacy PUBLIC_TO_EVERYONE]
    """
    h = headers()
    h["Content-Type"] = "application/json"

    media_ids = args.media_ids.split(",")
    
    if args.type == "photo":
        # Carousel
        media_arr = [{"id": mid.strip()} for mid in media_ids]
        network = {
            "type": "photo",
            "title": args.title or "",
            "text": args.text or "",
            "media": media_arr,
            "details": {
                "privacy": args.privacy,
                "comment": True,
                "auto_add_music": args.auto_music,
                "promotional": False,
                "paid": False,
            }
        }
    else:
        # Video
        media_arr = [{"id": media_ids[0].strip()}]
        network = {
            "type": "video",
            "text": args.text or "",
            "media": media_arr,
            "details": {
                "privacy": args.privacy,
                "comment": True,
                "duet": True,
                "stitch": True,
                "promotional": False,
                "paid": False,
            }
        }

    account = {"id": args.account_id}
    if args.schedule:
        account["scheduled_at"] = args.schedule
        endpoint = f"{BASE}/posts/schedule"
    else:
        endpoint = f"{BASE}/posts/schedule/publish"

    payload = {
        "bulk": {
            "state": "scheduled",
            "posts": [{
                "accounts": [account],
                "networks": {"tiktok": network}
            }]
        }
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return

    r = requests.post(endpoint, headers=h, json=payload)
    r.raise_for_status()
    data = r.json()
    job_id = data.get("job_id")
    print(f"Job submitted: {job_id}")
    
    if not args.no_poll and job_id:
        result = poll_job(job_id, {k: v for k, v in h.items() if k != "Content-Type"})
        print(f"Job completed: {json.dumps(result, indent=2)}")

def job_status(args):
    """Check a job status."""
    h = headers()
    r = requests.get(f"{BASE}/job_status/{args.job_id}", headers=h)
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))

def main():
    p = argparse.ArgumentParser(description="Publer API client")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("accounts", help="List connected accounts")

    up = sub.add_parser("upload", help="Upload media files")
    up.add_argument("files", nargs="+", help="File paths to upload")

    pp = sub.add_parser("post", help="Create a TikTok post")
    pp.add_argument("--account-id", required=True)
    pp.add_argument("--type", choices=["photo", "video"], default="photo")
    pp.add_argument("--title", help="Carousel title (max 90 chars)")
    pp.add_argument("--text", help="Description/caption")
    pp.add_argument("--media-ids", required=True, help="Comma-separated media IDs")
    pp.add_argument("--schedule", help="ISO 8601 timestamp for scheduling")
    pp.add_argument("--privacy", default="PUBLIC_TO_EVERYONE")
    pp.add_argument("--auto-music", action="store_true", default=True)
    pp.add_argument("--no-poll", action="store_true")
    pp.add_argument("--dry-run", action="store_true", help="Print payload without sending")

    js = sub.add_parser("job-status", help="Check job status")
    js.add_argument("job_id")

    args = p.parse_args()
    {"accounts": accounts, "upload": upload, "post": post, "job-status": job_status}[args.cmd](args)

if __name__ == "__main__":
    main()
