#!/usr/bin/env python3
import os, argparse, json, os, sqlite3, subprocess, sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def run_cmd(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip() or "command failed")
    return r.stdout.strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["run", "show", "queue"])
    p.add_argument("--mode", choices=["passend", "mood-shift", "explore"], default="passend")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--run-id", default="")
    p.add_argument("--device-name", default="")
    args = p.parse_args()

    if args.action == "run":
        cmd = [sys.executable, os.path.join(BASE_DIR, "scripts", "recommend", "recommend-now.py"), "--mode", args.mode, "--top", str(args.top)]
        if args.device_name:
            cmd += ["--device-name", args.device_name]
        print(run_cmd(cmd))
        return

    con = sqlite3.connect(DB)
    try:
        run_id = args.run_id
        if not run_id:
            row = con.execute("SELECT run_id FROM recommend_runs ORDER BY generated_at DESC LIMIT 1").fetchone()
            run_id = row[0] if row else ""
        if not run_id:
            print("no_recommendation_run")
            return

        if args.action == "show":
            rows = con.execute(
                "SELECT rank_no,track_name,artists,score,reason,queued FROM recommend_items WHERE run_id=? ORDER BY rank_no LIMIT ?",
                (run_id, args.top),
            ).fetchall()
            out = [
                {"rank": r[0], "track": r[1], "artists": r[2], "score": round(float(r[3]), 3), "reason": r[4], "queued": int(r[5])}
                for r in rows
            ]
            print(json.dumps(out, ensure_ascii=False))
            return

        if args.action == "queue":
            rows = con.execute(
                "SELECT rank_no,track_name,artists FROM recommend_items WHERE run_id=? ORDER BY rank_no LIMIT ?",
                (run_id, args.top),
            ).fetchall()
            for _, name, artists in rows:
                lead = (artists or "").split(",")[0].strip()
                cmd = [
                    sys.executable,
                    os.path.join(BASE_DIR, "scripts", "playback", "playback_control.py"),
                    "queue_add",
                    "--query",
                    name or "",
                ]
                if lead:
                    cmd += ["--artist", lead]
                if args.device_name:
                    cmd += ["--device-name", args.device_name]
                run_cmd(cmd)
            con.execute("UPDATE recommend_items SET queued=1 WHERE run_id=? AND rank_no<=?", (run_id, args.top))
            con.commit()
            print(json.dumps({"ok": True, "runId": run_id, "queued": min(args.top, len(rows))}))
            return
    finally:
        con.close()


if __name__ == "__main__":
    main()


