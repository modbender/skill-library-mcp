#!/usr/bin/env python3
"""IP Camera ONVIF PTZ Control & Discovery.

Usage: ptz.py [--cam <name>] <command> [args...]

Run 'ptz.py --help' for full command list.
Auto-activates the skill venv if present.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# ── Auto-activate venv if not already active ─────────────────────────────────
SKILL_DIR = Path(__file__).resolve().parent.parent
VENV_DIR = SKILL_DIR / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"

if VENV_PYTHON.exists() and not sys.prefix.startswith(str(VENV_DIR)):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

# ── Config Loading ───────────────────────────────────────────────────────────

DEFAULT_CONFIG = Path.home() / ".config" / "ipcam" / "config.json"

COMMON_ONVIF_PORTS = [2020, 80, 8000, 8080, 8899]


def load_config(cam_name=None):
    """Load camera config from file or environment variables."""
    config_path = Path(os.environ.get("IPCAM_CONFIG", str(DEFAULT_CONFIG)))
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    # Multi-camera format: { "default": "cam1", "cameras": { ... } }
    if "cameras" in config:
        if not cam_name:
            cam_name = config.get("default", "")
            if not cam_name:
                cam_name = next(iter(config["cameras"]), "")
        if cam_name not in config["cameras"]:
            available = ", ".join(config["cameras"].keys())
            print(
                f"Error: Camera '{cam_name}' not found. Available: {available}",
                file=sys.stderr,
            )
            sys.exit(1)
        cam_cfg = config["cameras"][cam_name]
    else:
        # Legacy flat format (backward compatible)
        cam_name = cam_name or "default"
        cam_cfg = config

    return {
        "name": cam_name,
        "ip": os.environ.get("CAM_IP", cam_cfg.get("ip", "")),
        "username": os.environ.get("CAM_USER", cam_cfg.get("username", "admin")),
        "password": os.environ.get("CAM_PASS", cam_cfg.get("password", "")),
        "onvif_port": int(
            os.environ.get("CAM_ONVIF_PORT", cam_cfg.get("onvif_port", 2020))
        ),
    }


def list_cameras():
    """List all configured cameras."""
    config_path = Path(os.environ.get("IPCAM_CONFIG", str(DEFAULT_CONFIG)))
    if not config_path.exists():
        print(f"No config file found: {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(config_path) as f:
        config = json.load(f)
    if "cameras" in config:
        default = config.get("default", "none")
        print(f"Configured cameras (default: {default}):")
        for name, cam in config["cameras"].items():
            marker = " *" if name == default else ""
            print(
                f"  {name}: {cam.get('ip', '?')}:{cam.get('onvif_port', 2020)}{marker}"
            )
    else:
        print("Single camera (legacy config):")
        print(
            f"  default: {config.get('ip', '?')}:{config.get('onvif_port', 2020)}"
        )


# ── ONVIF Camera Connection ─────────────────────────────────────────────────


def connect_camera(cfg):
    """Connect to camera via ONVIF and return (camera, ptz_service, media_service, profile)."""
    try:
        from onvif import ONVIFCamera
    except ImportError:
        print("Error: python-onvif-zeep not installed.", file=sys.stderr)
        print("Run: pip3 install onvif-zeep", file=sys.stderr)
        sys.exit(1)

    if not cfg["ip"]:
        print("Error: Camera IP not configured.", file=sys.stderr)
        print(f"Set CAM_IP or configure {DEFAULT_CONFIG}", file=sys.stderr)
        sys.exit(1)

    ip = cfg["ip"]
    port = cfg["onvif_port"]
    print(f"Connecting to {ip}:{port}...", file=sys.stderr)

    try:
        cam = ONVIFCamera(ip, port, cfg["username"], cfg["password"])
    except Exception as e:
        print(f"✗ ONVIF connection failed: {e}", file=sys.stderr)
        other_ports = [p for p in COMMON_ONVIF_PORTS if p != port]
        print(
            f"  Tried port {port}. Common ONVIF ports: {', '.join(map(str, other_ports))}",
            file=sys.stderr,
        )
        print(
            "  Tip: Check that ONVIF is enabled in your camera's web interface.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        media_service = cam.create_media_service()
        ptz_service = cam.create_ptz_service()
    except Exception as e:
        print(f"✗ Failed to create ONVIF services: {e}", file=sys.stderr)
        print(
            "  The camera may not support PTZ or the credentials may be wrong.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        profiles = media_service.GetProfiles()
    except Exception as e:
        print(f"✗ Failed to get media profiles: {e}", file=sys.stderr)
        sys.exit(1)

    if not profiles:
        print("Error: No media profiles found on camera.", file=sys.stderr)
        sys.exit(1)
    profile = profiles[0]

    return cam, ptz_service, media_service, profile


# ── ONVIF WS-Discovery (raw socket) ─────────────────────────────────────────

WS_DISCOVERY_MULTICAST = ("239.255.255.250", 3702)
WS_DISCOVERY_PROBE_TEMPLATE = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"'
    ' xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing"'
    ' xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery"'
    ' xmlns:dn="http://www.onvif.org/ver10/network/wsdl">'
    "<soap:Header>"
    "<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>"
    "<wsa:MessageID>urn:uuid:{msg_id}</wsa:MessageID>"
    "<wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>"
    "</soap:Header>"
    "<soap:Body>"
    "<wsd:Probe>"
    "<wsd:Types>dn:NetworkVideoTransmitter</wsd:Types>"
    "</wsd:Probe>"
    "</soap:Body>"
    "</soap:Envelope>"
)


def _ws_discovery_probe(timeout=3, probes=3):
    """Send WS-Discovery Probes via raw UDP multicast; return list of (addr, xml_bytes).

    Sends multiple probes on the same socket to catch slow responders.
    Each probe uses a fresh MessageID. Responses are deduplicated by source IP.
    """
    import socket
    import time
    import uuid

    seen_ips = set()
    all_responses = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(1.0)  # short recv timeout for polling

    try:
        for i in range(probes):
            msg_id = str(uuid.uuid4())
            probe = WS_DISCOVERY_PROBE_TEMPLATE.format(msg_id=msg_id)
            sock.sendto(probe.encode("utf-8"), WS_DISCOVERY_MULTICAST)

            # Collect responses until timeout
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    data, addr = sock.recvfrom(65535)
                    if addr[0] not in seen_ips:
                        seen_ips.add(addr[0])
                        all_responses.append((addr, data))
                except socket.timeout:
                    continue
    finally:
        sock.close()

    return all_responses


def _parse_discovery_response(xml_bytes):
    """Parse a WS-Discovery ProbeMatch response into camera info dict."""
    from xml.etree import ElementTree as ET
    from urllib.parse import urlparse, unquote

    text = xml_bytes.decode("utf-8", errors="replace")
    root = ET.fromstring(text)

    # Namespace-agnostic search for XAddrs and Scopes
    xaddrs_el = root.find(
        ".//{http://schemas.xmlsoap.org/ws/2005/04/discovery}XAddrs"
    )
    scopes_el = root.find(
        ".//{http://schemas.xmlsoap.org/ws/2005/04/discovery}Scopes"
    )

    xaddrs = (
        xaddrs_el.text.strip().split() if xaddrs_el is not None and xaddrs_el.text else []
    )
    scopes = (
        scopes_el.text.strip().split() if scopes_el is not None and scopes_el.text else []
    )

    # Extract name and hardware model from scopes
    name = ""
    hardware = ""
    for s in scopes:
        if "/name/" in s:
            name = unquote(s.rsplit("/name/", 1)[-1])
        elif "/hardware/" in s:
            hardware = unquote(s.rsplit("/hardware/", 1)[-1])

    # Extract ONVIF endpoint from first XAddr
    onvif_ip = ""
    onvif_port = 80
    if xaddrs:
        parsed = urlparse(xaddrs[0])
        onvif_ip = parsed.hostname or ""
        onvif_port = parsed.port or 80

    return {
        "ip": onvif_ip,
        "port": onvif_port,
        "manufacturer": name,
        "model": hardware,
        "xaddrs": " ".join(xaddrs),
    }


def cmd_discover(add_mode=False, cam_name=None, cam_user=None, cam_pass=None):
    """Discover ONVIF cameras on the local network using WS-Discovery."""
    print("Scanning for ONVIF cameras (this may take a few seconds)...")

    responses = _ws_discovery_probe(timeout=3, probes=3)

    cameras = []
    for addr, xml_bytes in responses:
        try:
            info = _parse_discovery_response(xml_bytes)
            if info["ip"]:
                cameras.append(info)
        except Exception as e:
            print(f"  Warning: Failed to parse response from {addr[0]}: {e}", file=sys.stderr)

    if not cameras:
        print("No ONVIF cameras found on the network.")
        print("  Tip: Ensure cameras are on the same subnet and ONVIF is enabled.")
        return

    print(f"\nDiscovered {len(cameras)} ONVIF camera(s):\n")
    for i, cam in enumerate(cameras, 1):
        label = cam["manufacturer"] or "Unknown"
        if cam["model"]:
            label += f" {cam['model']}"
        print(f"  [{i}] {cam['ip']}:{cam['port']}  ({label})")

    if not add_mode:
        print(
            "\nTo add a camera to config, run: ptz.py discover --add"
        )
        return

    # ── Add mode: write discovered cameras to config ─────────────────────
    config_path = Path(os.environ.get("IPCAM_CONFIG", str(DEFAULT_CONFIG)))
    config = {"cameras": {}}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        if "cameras" not in config:
            # Migrate legacy flat config
            config = {"cameras": {}, "default": ""}

    for i, cam in enumerate(cameras, 1):
        label = cam["manufacturer"] or "Unknown"
        if cam["model"]:
            label += f" {cam['model']}"
        print(f"\n--- Camera [{i}] {cam['ip']}:{cam['port']} ({label}) ---")

        # Check if IP already in config
        existing = [
            n
            for n, c in config.get("cameras", {}).items()
            if c.get("ip") == cam["ip"]
        ]
        if existing:
            print(f"  Already in config as: {', '.join(existing)}. Skipping.")
            continue

        if cam_name and len(cameras) == 1:
            name = cam_name
        else:
            # Generate suggestion
            suggestion = (
                cam["model"].lower().replace(" ", "-")
                if cam["model"]
                else f"cam{i}"
            )
            if sys.stdin.isatty() and not cam_name:
                name = input(f"  Camera name [{suggestion}]: ").strip() or suggestion
            else:
                name = cam_name or suggestion

        if cam_user is not None:
            username = cam_user
        elif sys.stdin.isatty():
            username = input("  Username [admin]: ").strip() or "admin"
        else:
            username = "admin"

        if cam_pass is not None:
            password = cam_pass
        elif sys.stdin.isatty():
            import getpass

            password = getpass.getpass("  Password: ")
        else:
            password = ""
            print("  Warning: No password provided (use --pass to set).")

        config["cameras"][name] = {
            "ip": cam["ip"],
            "username": username,
            "password": password,
            "rtsp_port": 554,
            "onvif_port": cam["port"],
        }
        print(f"  ✓ Added '{name}' ({cam['ip']}:{cam['port']})")

        # Set as default if first camera
        if not config.get("default"):
            config["default"] = name
            print(f"  ✓ Set as default camera")

    # Write config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n✓ Config saved: {config_path}")


# ── PTZ Commands ─────────────────────────────────────────────────────────────

DIRECTION_MAP = {
    "left": {"pan": -1, "tilt": 0, "zoom": 0},
    "right": {"pan": 1, "tilt": 0, "zoom": 0},
    "up": {"pan": 0, "tilt": 1, "zoom": 0},
    "down": {"pan": 0, "tilt": -1, "zoom": 0},
    "zoomin": {"pan": 0, "tilt": 0, "zoom": 1},
    "zoomout": {"pan": 0, "tilt": 0, "zoom": -1},
    "upleft": {"pan": -1, "tilt": 1, "zoom": 0},
    "upright": {"pan": 1, "tilt": 1, "zoom": 0},
    "downleft": {"pan": -1, "tilt": -1, "zoom": 0},
    "downright": {"pan": 1, "tilt": -1, "zoom": 0},
}


def cmd_status(ptz_service, profile):
    """Show current PTZ position."""
    status = ptz_service.GetStatus({"ProfileToken": profile.token})
    pos = status.Position
    print("PTZ Status:")
    if pos and pos.PanTilt:
        print(f"  Pan:  {pos.PanTilt.x:.4f}")
        print(f"  Tilt: {pos.PanTilt.y:.4f}")
    if pos and pos.Zoom:
        print(f"  Zoom: {pos.Zoom.x:.4f}")
    if status.MoveStatus:
        ms = status.MoveStatus
        pan_tilt_status = getattr(ms, "PanTilt", None)
        zoom_status = getattr(ms, "Zoom", None)
        if pan_tilt_status:
            print(f"  PanTilt Moving: {pan_tilt_status}")
        if zoom_status:
            print(f"  Zoom Moving: {zoom_status}")


def cmd_move(ptz_service, profile, direction, speed=0.5, duration=0.5):
    """Continuous move in a direction, then stop after duration."""
    import time

    d = DIRECTION_MAP.get(direction.lower())
    if not d:
        print(f"Error: Unknown direction '{direction}'", file=sys.stderr)
        print(f"Valid: {', '.join(DIRECTION_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    request = ptz_service.create_type("ContinuousMove")
    request.ProfileToken = profile.token
    request.Velocity = {
        "PanTilt": {"x": d["pan"] * speed, "y": d["tilt"] * speed},
        "Zoom": {"x": d["zoom"] * speed},
    }

    print(f"Moving {direction} (speed={speed}, duration={duration}s)...")
    ptz_service.ContinuousMove(request)
    time.sleep(duration)
    ptz_service.Stop({"ProfileToken": profile.token})
    print("✓ Move complete")


def cmd_goto(ptz_service, profile, pan, tilt, zoom=0.5):
    """Absolute move to pan/tilt/zoom coordinates."""
    request = ptz_service.create_type("AbsoluteMove")
    request.ProfileToken = profile.token
    request.Position = {
        "PanTilt": {"x": pan, "y": tilt},
        "Zoom": {"x": zoom},
    }
    request.Speed = {
        "PanTilt": {"x": 1.0, "y": 1.0},
        "Zoom": {"x": 1.0},
    }

    print(f"Moving to pan={pan}, tilt={tilt}, zoom={zoom}...")
    ptz_service.AbsoluteMove(request)
    print("✓ Move initiated")


def cmd_stop(ptz_service, profile):
    """Stop all PTZ movement."""
    ptz_service.Stop({"ProfileToken": profile.token})
    print("✓ PTZ stopped")


def cmd_home(ptz_service, profile):
    """Go to home position."""
    try:
        ptz_service.GotoHomePosition({"ProfileToken": profile.token})
        print("✓ Moving to home position")
    except Exception:
        print("Home position not set, moving to center (0, 0)...")
        cmd_goto(ptz_service, profile, 0.0, 0.0, 0.5)


def cmd_preset_list(ptz_service, profile):
    """List all saved presets."""
    presets = ptz_service.GetPresets({"ProfileToken": profile.token})
    if not presets:
        print("No presets found.")
        return
    print(f"Presets ({len(presets)}):")
    for p in presets:
        name = getattr(p, "Name", "unnamed")
        token = p.token
        pos_info = ""
        if hasattr(p, "PTZPosition") and p.PTZPosition:
            pp = p.PTZPosition
            if pp.PanTilt:
                pos_info = f" pan={pp.PanTilt.x:.2f} tilt={pp.PanTilt.y:.2f}"
            if pp.Zoom:
                pos_info += f" zoom={pp.Zoom.x:.2f}"
        print(f"  [{token}] {name}{pos_info}")


def cmd_preset_goto(ptz_service, profile, token):
    """Go to a preset position."""
    request = {
        "ProfileToken": profile.token,
        "PresetToken": str(token),
    }
    ptz_service.GotoPreset(request)
    print(f"✓ Moving to preset {token}")


def cmd_preset_set(ptz_service, profile, token, name=None):
    """Save current position as a preset."""
    request = {
        "ProfileToken": profile.token,
        "PresetToken": str(token),
    }
    if name:
        request["PresetName"] = name
    result = ptz_service.SetPreset(request)
    print(f"✓ Preset saved: token={result}")


def cmd_preset_remove(ptz_service, profile, token):
    """Remove a preset."""
    request = {
        "ProfileToken": profile.token,
        "PresetToken": str(token),
    }
    ptz_service.RemovePreset(request)
    print(f"✓ Preset {token} removed")


# ── Stream URI ───────────────────────────────────────────────────────────────


def cmd_stream_uri(media_service, cfg, save=False):
    """Query ONVIF for actual RTSP stream URIs and optionally save paths to config."""
    from urllib.parse import urlparse

    profiles = media_service.GetProfiles()
    if not profiles:
        print("No media profiles found.", file=sys.stderr)
        sys.exit(1)

    print(f"RTSP streams for [{cfg['name']}] ({cfg['ip']}):\n")

    uris = []
    for p in profiles:
        try:
            result = media_service.GetStreamUri(
                {
                    "StreamSetup": {
                        "Stream": "RTP-Unicast",
                        "Transport": {"Protocol": "RTSP"},
                    },
                    "ProfileToken": p.token,
                }
            )
            uri = result.Uri
            parsed = urlparse(uri)
            path = parsed.path.lstrip("/")

            # Try to get resolution from video encoder config
            resolution = ""
            vec = getattr(p, "VideoEncoderConfiguration", None)
            if vec and hasattr(vec, "Resolution") and vec.Resolution:
                resolution = f" ({vec.Resolution.Width}x{vec.Resolution.Height})"

            uris.append(
                {
                    "profile_name": p.Name,
                    "token": p.token,
                    "uri": uri,
                    "path": path,
                    "resolution": resolution,
                }
            )
            print(f"  {p.Name} (token={p.token}){resolution}")
            print(f"    URI:  {uri}")
            print(f"    Path: {path}")
            print()
        except Exception as e:
            print(f"  {p.Name}: Error - {e}", file=sys.stderr)

    if not uris:
        return

    # Save paths to config if requested
    if save and len(uris) >= 1:
        config_path = Path(os.environ.get("IPCAM_CONFIG", str(DEFAULT_CONFIG)))
        if not config_path.exists():
            print(f"Config file not found: {config_path}", file=sys.stderr)
            return

        with open(config_path) as f:
            config = json.load(f)

        cam_name = cfg["name"]
        if "cameras" in config and cam_name in config["cameras"]:
            cam_cfg = config["cameras"][cam_name]
            # First profile = main, second = sub (common convention)
            cam_cfg["rtsp_main_path"] = uris[0]["path"]
            if len(uris) >= 2:
                cam_cfg["rtsp_sub_path"] = uris[1]["path"]

            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            print(f"✓ Saved to config [{cam_name}]:")
            print(f"    rtsp_main_path = {uris[0]['path']}")
            if len(uris) >= 2:
                print(f"    rtsp_sub_path  = {uris[1]['path']}")
        else:
            print(
                f"Camera '{cam_name}' not in multi-camera config, skipping save.",
                file=sys.stderr,
            )
    elif not save:
        print("Tip: Use --save to write paths to config:")
        print(f"  ptz.py --cam {cfg['name']} stream-uri --save")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="IP Camera ONVIF PTZ Control & Discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ptz.py status
  ptz.py --cam cam2 status
  ptz.py move left
  ptz.py move up 0.8
  ptz.py goto 0.5 -0.3 0.2
  ptz.py home
  ptz.py stop
  ptz.py preset list
  ptz.py preset goto 1
  ptz.py preset set 1 "door"
  ptz.py preset remove 1
  ptz.py stream-uri
  ptz.py --cam cam2 stream-uri --save
  ptz.py list-cameras
  ptz.py discover
  ptz.py discover --add
  ptz.py discover --add --name garage --user admin --pass secret

Works with ONVIF Profile S/T cameras. Tested with TP-Link Tapo/Vigi.
        """,
    )

    parser.add_argument(
        "--cam", default=None, help="Camera name from config (default: from config)"
    )
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    # Discovery-specific options (parsed manually to avoid argparse conflicts)
    # --add, --name, --user, --pass are handled in discover command

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    # Pre-parse commands that need special arg handling (bypass argparse)
    if "discover" in sys.argv:
        _handle_discover()
        return
    if "stream-uri" in sys.argv or "streamuri" in sys.argv:
        _handle_stream_uri()
        return

    args = parser.parse_args()

    # Handle list-cameras without connecting
    if args.command.lower() in ("list-cameras", "list"):
        list_cameras()
        return

    cfg = load_config(args.cam)
    cam, ptz_service, media_service, profile = connect_camera(cfg)

    cmd = args.command.lower()
    cmd_args = args.args

    if cmd == "status":
        cmd_status(ptz_service, profile)

    elif cmd == "move":
        if not cmd_args:
            print(
                "Usage: ptz.py move <direction> [speed] [duration]", file=sys.stderr
            )
            print(f"Directions: {', '.join(DIRECTION_MAP.keys())}", file=sys.stderr)
            sys.exit(1)
        direction = cmd_args[0]
        speed = float(cmd_args[1]) if len(cmd_args) > 1 else 0.5
        duration = float(cmd_args[2]) if len(cmd_args) > 2 else 0.5
        cmd_move(ptz_service, profile, direction, speed, duration)

    elif cmd == "goto":
        if len(cmd_args) < 2:
            print("Usage: ptz.py goto <pan> <tilt> [zoom]", file=sys.stderr)
            sys.exit(1)
        pan = float(cmd_args[0])
        tilt = float(cmd_args[1])
        zoom = float(cmd_args[2]) if len(cmd_args) > 2 else 0.5
        cmd_goto(ptz_service, profile, pan, tilt, zoom)

    elif cmd == "stop":
        cmd_stop(ptz_service, profile)

    elif cmd == "home":
        cmd_home(ptz_service, profile)

    elif cmd == "preset":
        if not cmd_args:
            print(
                "Usage: ptz.py preset <list|goto|set|remove> [args]", file=sys.stderr
            )
            sys.exit(1)
        sub = cmd_args[0].lower()
        if sub == "list":
            cmd_preset_list(ptz_service, profile)
        elif sub == "goto":
            if len(cmd_args) < 2:
                print("Usage: ptz.py preset goto <token>", file=sys.stderr)
                sys.exit(1)
            cmd_preset_goto(ptz_service, profile, cmd_args[1])
        elif sub == "set":
            if len(cmd_args) < 2:
                print("Usage: ptz.py preset set <token> [name]", file=sys.stderr)
                sys.exit(1)
            name = cmd_args[2] if len(cmd_args) > 2 else None
            cmd_preset_set(ptz_service, profile, cmd_args[1], name)
        elif sub == "remove":
            if len(cmd_args) < 2:
                print("Usage: ptz.py preset remove <token>", file=sys.stderr)
                sys.exit(1)
            cmd_preset_remove(ptz_service, profile, cmd_args[1])
        else:
            print(f"Unknown preset subcommand: {sub}", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


def _handle_stream_uri():
    """Parse stream-uri arguments and query ONVIF for RTSP URIs."""
    save = "--save" in sys.argv
    cam_name = None
    for i, arg in enumerate(sys.argv):
        if arg == "--cam" and i + 1 < len(sys.argv):
            cam_name = sys.argv[i + 1]
    cfg = load_config(cam_name)
    _, _, media_service, _ = connect_camera(cfg)
    cmd_stream_uri(media_service, cfg, save=save)


def _handle_discover():
    """Parse discover-specific arguments and run discovery."""
    add_mode = "--add" in sys.argv
    cam_name = None
    cam_user = None
    cam_pass = None

    args = sys.argv[:]
    for i, arg in enumerate(args):
        if arg == "--name" and i + 1 < len(args):
            cam_name = args[i + 1]
        elif arg == "--user" and i + 1 < len(args):
            cam_user = args[i + 1]
        elif arg == "--pass" and i + 1 < len(args):
            cam_pass = args[i + 1]

    cmd_discover(
        add_mode=add_mode,
        cam_name=cam_name,
        cam_user=cam_user,
        cam_pass=cam_pass,
    )


if __name__ == "__main__":
    main()
