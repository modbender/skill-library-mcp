#!/usr/bin/env python3
"""desktopctl: minimal desktop GUI control helper (Linux X11).

This wraps common X11 automation utilities (xdotool + scrot) so a higher-level
agent can run a simple loop: screenshot -> decide -> click/type -> repeat.
"""

import argparse
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DEFAULT_DISPLAY = os.environ.get("DISPLAY") or ":0"
DEFAULT_XAUTHORITY = os.environ.get("XAUTHORITY") or str(Path.home() / ".Xauthority")


@dataclass
class Ctx:
    display: str
    xauthority: str


def run(ctx: Ctx, cmd, check=True, capture=False):
    env = os.environ.copy()
    env["DISPLAY"] = ctx.display
    env["XAUTHORITY"] = ctx.xauthority
    if capture:
        return subprocess.run(cmd, env=env, check=check, text=True, capture_output=True)
    return subprocess.run(cmd, env=env, check=check)


def require_bins(*bins):
    missing = [b for b in bins if shutil.which(b) is None]
    if missing:
        raise SystemExit(
            "Missing required command(s): "
            + ", ".join(missing)
            + "\nInstall (Debian/Ubuntu): sudo apt-get install -y "
            + " ".join(missing)
        )


def cmd_screenshot(ctx: Ctx, args):
    require_bins("scrot")
    out = (
        Path(args.out)
        if args.out
        else Path(args.out_dir) / f"desktop-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.png"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    run(ctx, ["scrot", str(out)])
    print(out)


def cmd_click(ctx: Ctx, args):
    require_bins("xdotool")
    run(ctx, ["xdotool", "mousemove", str(args.x), str(args.y)])
    run(ctx, ["xdotool", "click", str(args.button)])


def cmd_type(ctx: Ctx, args):
    require_bins("xdotool")
    run(ctx, ["xdotool", "type", "--delay", str(args.delay), args.text])


def cmd_key(ctx: Ctx, args):
    require_bins("xdotool")
    run(ctx, ["xdotool", "key", args.keys])


def cmd_where(ctx: Ctx, _args):
    require_bins("xdotool")
    r = run(ctx, ["xdotool", "getmouselocation", "--shell"], capture=True)
    print(r.stdout.strip())


def cmd_windows(ctx: Ctx, _args):
    require_bins("xdotool")
    r = run(ctx, ["xdotool", "search", "--onlyvisible", "--name", ".*"], capture=True, check=False)
    ids = [x for x in r.stdout.split() if x.strip()]
    for wid in ids:
        name = run(ctx, ["xdotool", "getwindowname", wid], capture=True, check=False).stdout.strip()
        print(f"{wid}\t{name}")


def cmd_activate(ctx: Ctx, args):
    require_bins("xdotool")
    r = run(ctx, ["xdotool", "search", "--onlyvisible", "--name", args.name], capture=True, check=False)
    ids = [x for x in r.stdout.split() if x.strip()]
    if not ids:
        raise SystemExit(f"No window found matching: {args.name}")
    wid = ids[-1]
    run(ctx, ["xdotool", "windowactivate", wid])
    print(wid)


def cmd_open(ctx: Ctx, args):
    opener = shutil.which("xdg-open") or shutil.which("gio")
    if opener and Path(opener).name == "gio":
        run(ctx, [opener, "open", args.url], check=False)
        return
    if opener:
        run(ctx, [opener, args.url], check=False)
        return
    # Fallback
    if shutil.which("chromium-browser"):
        run(ctx, ["chromium-browser", args.url], check=False)
        return
    raise SystemExit("No URL opener found (tried xdg-open/gio/chromium-browser)")


def main():
    p = argparse.ArgumentParser(description="Desktop GUI control helper (Linux X11)")
    p.add_argument("--display", default=DEFAULT_DISPLAY, help=f"X display (default: {DEFAULT_DISPLAY})")
    p.add_argument(
        "--xauthority",
        default=DEFAULT_XAUTHORITY,
        help=f"Path to XAUTHORITY cookie file (default: {DEFAULT_XAUTHORITY})",
    )

    sp = p.add_subparsers(dest="cmd", required=True)

    a = sp.add_parser("screenshot", help="Take a screenshot")
    a.add_argument("--out", help="Output file path")
    a.add_argument(
        "--out-dir",
        default=str(Path.cwd() / "tmp"),
        help="Directory for auto-named screenshots (used when --out is not set)",
    )
    a.set_defaults(func=cmd_screenshot)

    a = sp.add_parser("click", help="Move mouse and click")
    a.add_argument("x", type=int)
    a.add_argument("y", type=int)
    a.add_argument("--button", type=int, default=1)
    a.set_defaults(func=cmd_click)

    a = sp.add_parser("type", help="Type text")
    a.add_argument("text")
    a.add_argument("--delay", type=int, default=12)
    a.set_defaults(func=cmd_type)

    a = sp.add_parser("key", help="Send a key chord")
    a.add_argument("keys", help="e.g. ctrl+l or Return")
    a.set_defaults(func=cmd_key)

    a = sp.add_parser("where", help="Print current mouse location")
    a.set_defaults(func=cmd_where)

    a = sp.add_parser("windows", help="List visible windows")
    a.set_defaults(func=cmd_windows)

    a = sp.add_parser("activate", help="Activate (focus) a window by regex name")
    a.add_argument("name")
    a.set_defaults(func=cmd_activate)

    a = sp.add_parser("open", help="Open a URL")
    a.add_argument("url")
    a.set_defaults(func=cmd_open)

    args = p.parse_args()
    ctx = Ctx(display=args.display, xauthority=args.xauthority)
    args.func(ctx, args)


if __name__ == "__main__":
    main()
