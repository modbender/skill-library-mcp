#!/usr/bin/env python3
"""Auto-controller helper: generate slices + subcall prompts + plan.json.
This does not invoke LLMs; it prepares artifacts for OpenClaw root session.

Usage:
  rlm_auto.py --ctx <path> --goal "..." --outdir <dir>
"""
import argparse, json, os, subprocess, sys
from rlm_path import validate_path as _validate_path
from rlm_redact import redact_secrets

def run_plan(ctx, goal):
    cmd = ["python3", os.path.join(os.path.dirname(__file__), "rlm_plan.py"),
           "--ctx", ctx, "--goal", goal]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)

def read_text(path):
    rp = _validate_path(path)
    with open(rp, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ctx', required=True)
    p.add_argument('--goal', required=True)
    p.add_argument('--outdir', required=True)
    p.add_argument('--max-subcalls', type=int, default=32)
    p.add_argument('--slice-max', type=int, default=16000)
    p.add_argument('--redact', dest='redact', action='store_true', default=True,
                   help='Redact secrets from slice text in subcall prompts (default: enabled)')
    p.add_argument('--no-redact', dest='redact', action='store_false',
                   help='Disable secret redaction in subcall prompts')
    args = p.parse_args()

    _validate_path(args.outdir)
    os.makedirs(args.outdir, exist_ok=True)
    plan = run_plan(args.ctx, args.goal)
    slices = plan.get("slices", [])

    # fallback: if no keyword hits, chunk the doc
    if not slices:
        text = read_text(args.ctx)
        step = args.slice_max
        slices = [{"start": i, "end": min(len(text), i+step), "kw": "chunk"}
                  for i in range(0, len(text), step)]

    # trim to max subcalls and max slice length
    slices = slices[:args.max_subcalls]
    trimmed = []
    for sl in slices:
        start, end = sl["start"], sl["end"]
        if end - start > args.slice_max:
            end = start + args.slice_max
        trimmed.append({"start": start, "end": end, "kw": sl.get("kw","")})

    # write prompts for subcalls (slice text separate file)
    text = read_text(args.ctx)
    prompts_dir = os.path.join(args.outdir, "subcalls")
    os.makedirs(prompts_dir, exist_ok=True)
    prompt_files = []
    for i, sl in enumerate(trimmed, 1):
        slice_text = text[sl["start"]:sl["end"]]
        goal_text = args.goal
        if args.redact:
            slice_text = redact_secrets(slice_text)
            goal_text = redact_secrets(goal_text)
        prompt_path = os.path.join(prompts_dir, f"subcall_{i:02d}.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write("Slice:\n")
            f.write(slice_text)
            f.write("\n\nGoal:\n")
            f.write(goal_text)
        prompt_files.append({"file": prompt_path, **sl})

    out = {
        "ctx": args.ctx,
        "goal": args.goal,
        "keywords": plan.get("keywords", []),
        "slices": trimmed,
        "subcall_prompts": prompt_files,
        "policy": {"max_subcalls": args.max_subcalls, "slice_max": args.slice_max}
    }

    out_path = os.path.join(args.outdir, "plan.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
