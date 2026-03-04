#!/usr/bin/env python3
"""SNS Auto Poster - Queue-based multi-platform posting."""
import argparse, json, os, sys, uuid
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
QUEUE_FILE = SCRIPT_DIR / "queue.json"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

PLATFORMS = {"x": "platforms.x.XPlatform"}

def load_queue():
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []

def save_queue(q):
    QUEUE_FILE.write_text(json.dumps(q, indent=2, ensure_ascii=False))

def get_platform(name):
    if name not in PLATFORMS:
        print(f"❌ Unknown platform: {name}")
        sys.exit(1)
    mod_path, cls_name = PLATFORMS[name].rsplit(".", 1)
    sys.path.insert(0, str(SCRIPT_DIR))
    import importlib
    mod = importlib.import_module(mod_path)
    return getattr(mod, cls_name)()

def cmd_add(args):
    q = load_queue()
    q.append({
        "id": str(uuid.uuid4())[:8],
        "platform": args.platform,
        "text": args.text,
        "image": args.image,
        "schedule": args.schedule or datetime.now().isoformat(),
        "status": "pending",
        "posted_at": None,
    })
    save_queue(q)
    print(f"✅ Added to queue ({len(q)} total)")

def cmd_run(args):
    q = load_queue()
    now = datetime.now()
    posted = 0
    for item in q:
        if item["status"] != "pending":
            continue
        sched = datetime.fromisoformat(item["schedule"])
        if sched > now:
            continue
        platform = get_platform(item["platform"])
        result = platform.post(item["text"], item.get("image"))
        if result["success"]:
            item["status"] = "posted"
            item["posted_at"] = now.isoformat()
            item["url"] = result.get("url")
            print(f"✅ Posted [{item['platform']}]: {result.get('url', item['id'])}")
            posted += 1
        else:
            item["status"] = "failed"
            item["error"] = result.get("error", "")
            print(f"❌ Failed [{item['platform']}]: {result.get('error', '')[:100]}")
    save_queue(q)
    print(f"Processed: {posted} posted")

def cmd_run_template(args):
    tpl_file = TEMPLATES_DIR / f"{args.template_name}.json"
    if not tpl_file.exists():
        print(f"❌ Template not found: {tpl_file}")
        sys.exit(1)
    tpl = json.loads(tpl_file.read_text())
    text = tpl["text"].format(date=datetime.now().strftime("%Y-%m-%d"), custom_message="")
    platform = get_platform(tpl.get("platform", "x"))
    result = platform.post(text.strip())
    if result["success"]:
        print(f"✅ Template posted: {result.get('url')}")
    else:
        print(f"❌ Failed: {result.get('error', '')[:100]}")

def cmd_list(args):
    q = load_queue()
    if not q:
        print("Queue is empty")
        return
    for item in q:
        status = {"pending": "⏳", "posted": "✅", "failed": "❌"}.get(item["status"], "?")
        print(f"  {status} [{item['platform']}] {item['text'][:50]}... | {item['schedule']} | {item['status']}")

def cmd_clean(args):
    q = [i for i in load_queue() if i["status"] == "pending"]
    save_queue(q)
    print(f"Cleaned. {len(q)} pending remain.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="SNS Auto Poster")
    sub = p.add_subparsers(dest="command")

    a = sub.add_parser("add")
    a.add_argument("--platform", default="x")
    a.add_argument("--text", required=True)
    a.add_argument("--image", default=None)
    a.add_argument("--schedule", default=None)

    sub.add_parser("run")

    rt = sub.add_parser("run-template")
    rt.add_argument("template_name")

    sub.add_parser("list")
    sub.add_parser("clean")

    args = p.parse_args()
    if not args.command:
        p.print_help()
        sys.exit(1)

    {"add": cmd_add, "run": cmd_run, "run-template": cmd_run_template, "list": cmd_list, "clean": cmd_clean}[args.command](args)
