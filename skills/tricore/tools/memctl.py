import os
import sys
import datetime
import argparse
import glob
import shutil
import re

def get_now():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

def cmd_ensure(args):
    dirs = [
        "memory/state",
        "memory/daily",
        "memory/sessions",
        "memory/kb",
        "memory/archive",
        "tools"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    if not os.path.exists("MEMORY.md"):
        with open("MEMORY.md", "w") as f:
            f.write("# MEMORY (Stable Brief)\n- Identity / operating principles\n- Current top-level focus\n- Pointers (links to KB/state files)\n  - KB decisions: memory/kb/decisions.md\n  - KB playbooks: memory/kb/playbooks.md\n  - Living state: memory/state/WORKING.md\n")
            
    working_path = "memory/state/WORKING.md"
    if not os.path.exists(working_path):
        with open(working_path, "w") as f:
            f.write(f"# WORKING (Living State)\nLastUpdated: {get_now()}\n\n## Active Tasks\n\n## Parking Lot\n- \n\n## Active Constraints\n- \n")
            
    for kb in ["decisions.md", "playbooks.md", "facts.md"]:
        kb_path = f"memory/kb/{kb}"
        if not os.path.exists(kb_path):
            with open(kb_path, "w") as f:
                f.write(f"# {kb.replace('.md', '').capitalize()}\n\n")

def cmd_capture(args):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    path = f"memory/daily/{today}.md"
    with open(path, "a") as f:
        f.write(f"- [{get_now()}] {args.note}\n")

def cmd_work_upsert(args):
    working_path = "memory/state/WORKING.md"
    if not os.path.exists(working_path):
        cmd_ensure(None)
    with open(working_path, "r") as f:
        content = f.read()
    
    content = re.sub(r"LastUpdated: .*", f"LastUpdated: {get_now()}", content)
    
    task_id = args.task_id or ("T" + datetime.datetime.now().strftime("%Y%m%d-%H%M"))
    marker = f"### {task_id}"
    
    if marker not in content:
        new_task = f"### {task_id} | {args.title}\nStatus: active\nGoal: {args.goal}\nDoneWhen: {args.done_when}\nContext: \nNext: \nProgressLog:\n- {get_now()} Created\nArtifacts:\n- \n\n"
        content = content.replace("## Active Tasks\n", f"## Active Tasks\n{new_task}")
        
    with open(working_path, "w") as f:
        f.write(content)

def cmd_work_done(args):
    working_path = "memory/state/WORKING.md"
    if not os.path.exists(working_path):
        print(f"[TriCore] {working_path} not found.")
        return
    with open(working_path, "r") as f:
        content = f.read()
    
    marker = f"### {args.task_id}"
    if marker in content:
        pattern = re.compile(rf"({marker}.*?Status:\s*)active", re.DOTALL)
        content = pattern.sub(r"\1done", content, count=1)
        content = re.sub(r"LastUpdated: .*", f"LastUpdated: {get_now()}", content)
        with open(working_path, "w") as f:
            f.write(content)
        print(f"[TriCore] Task {args.task_id} marked as done.")
    else:
        print(f"[TriCore] Task {args.task_id} not found.")

def cmd_kb_append(args):
    kb_path = f"memory/kb/{args.kb_type}.md"
    with open(kb_path, "a") as f:
        f.write(f"\n## [{get_now()}]\n{args.content}\n")

def cmd_housekeeping_daily(args):
    for f in glob.glob("memory/*-slug.md"):
        shutil.move(f, f"memory/sessions/{os.path.basename(f)}")

def cmd_evolve_weekly_pack(args):
    pass

def cmd_evolve_weekly_apply(args):
    pass

def cmd_migrate_legacy(args):
    if not os.path.exists("MEMORY.md"):
        print("[TriCore] Existing MEMORY.md not found.")
        return
    size = os.path.getsize("MEMORY.md")
    if size < 1500:
        print("[TriCore] MEMORY.md size is normal (minimalist state), no migration needed.")
        return
        
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = f"memory/archive/legacy-MEMORY-{ts}.md"
    shutil.move("MEMORY.md", backup_path)
    cmd_ensure(None)
    print(f"\n[⚠️ Architecture Migration Warning] Found an oversized/bloated legacy MEMORY.md (Size: {size} bytes).")
    print(f"It has been moved to: {backup_path}")
    print(f"A new minimalist MEMORY.md compliant with TriCore constraints has been generated.")
    print(f"\n>>> [Mandatory Agent Action Required] <<<")
    print(f"Please use the 'read' tool to read the contents of {backup_path}, and disassemble/route it using semantic understanding:")
    print(f"  - Long-term facts & conventions -> python3 tools/memctl.py kb_append facts '...'")
    print(f"  - Methodologies/Playbooks -> python3 tools/memctl.py kb_append playbooks '...'")
    print(f"  - Core identity/pointers -> Use the 'edit' tool to concisely write them back into the new MEMORY.md")
    print(f"It is absolutely forbidden to stuff large blocks of long text directly back into MEMORY.md!\n")

def cmd_lint(args):
    text = ""
    if os.path.exists(args.target):
        with open(args.target, "r") as f:
            text = f.read()
    else:
        text = args.target

    errors = []
    
    # Check for forbidden file WRITE commands (not just mere mentions)
    forbidden_files = ["task_plan.md", "findings.md", "progress.md", "reflection.md"]
    for ff in forbidden_files:
        # Match shell redirects like "> findings.md", ">> task_plan.md", or tool arguments like "path": "task_plan.md"
        if re.search(r"(>|>>|touch|vim|nano|cat\s+>)\s*" + re.escape(ff), text) or \
           re.search(r"[\"'](file_)?path[\"']\s*:\s*[\"']" + re.escape(ff) + r"[\"']", text):
            errors.append(f"Forbidden file WRITE detected: {ff} is deprecated in TriCore.")
            
    # Check for writing directly to root date files instead of memory/daily/ or without memctl
    if re.search(r">>.*memory/\d{4}-\d{2}-\d{2}\.md", text):
         errors.append("Forbidden shell append to date file: use 'python3 tools/memctl.py capture' instead.")
         
    # Check for daily-learning dir creation
    if "memory/daily-learning" in text and ("mkdir" in text or "write" in text or ">>" in text):
        errors.append("Forbidden directory: memory/daily-learning/ is deprecated. Use memctl.py kb_append.")

    # Check for direct MEMORY.md modification without memctl logic
    if re.search(r">>.*MEMORY\.md", text):
        errors.append("Forbidden shell append to MEMORY.md: keep it tiny and strict.")

    if errors:
        print("[TriCore LINT ERROR] Target violates TriCore architecture:")
        for e in errors:
            print(f"  - {e}")
        print("\nPlease rewrite your prompt/script to use 'python3 tools/memctl.py (capture|kb_append|work_upsert)'")
        sys.exit(1)
    else:
        print("[TriCore LINT PASS] Target complies with architecture.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")
    
    subparsers.add_parser("ensure")
    
    p_capture = subparsers.add_parser("capture")
    p_capture.add_argument("note")
    
    p_upsert = subparsers.add_parser("work_upsert")
    p_upsert.add_argument("--task_id", default="")
    p_upsert.add_argument("--title", default="New Task")
    p_upsert.add_argument("--goal", default="")
    p_upsert.add_argument("--done_when", default="")
    
    p_done = subparsers.add_parser("work_done")
    p_done.add_argument("task_id")
    
    p_kb = subparsers.add_parser("kb_append")
    p_kb.add_argument("kb_type")
    p_kb.add_argument("content")
    
    subparsers.add_parser("housekeeping_daily")
    subparsers.add_parser("evolve_weekly_pack")
    subparsers.add_parser("evolve_weekly_apply")
    
    subparsers.add_parser("migrate_legacy")
    
    p_lint = subparsers.add_parser("lint")
    p_lint.add_argument("target", help="Text string or file path to check")
    
    args = parser.parse_args()
    
    if args.cmd == "ensure": cmd_ensure(args)
    elif args.cmd == "capture": cmd_capture(args)
    elif args.cmd == "work_upsert": cmd_work_upsert(args)
    elif args.cmd == "work_done": cmd_work_done(args)
    elif args.cmd == "kb_append": cmd_kb_append(args)
    elif args.cmd == "housekeeping_daily": cmd_housekeeping_daily(args)
    elif args.cmd == "evolve_weekly_pack": cmd_evolve_weekly_pack(args)
    elif args.cmd == "evolve_weekly_apply": cmd_evolve_weekly_apply(args)
    elif args.cmd == "migrate_legacy": cmd_migrate_legacy(args)
    elif args.cmd == "lint": cmd_lint(args)