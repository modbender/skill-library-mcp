#!/usr/bin/env python3
"""
Enhanced helper script for interacting with Octoprint API
Includes status formatting, webcam snapshots, gcode analysis, error monitoring, and Telegram integration
"""
import json
import sys
import os
import re
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_config():
    """Load Octoprint configuration"""
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}", file=sys.stderr)
        print("Please copy config.example.json to config.json and fill in your details", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        return json.load(f)

def make_request(method, endpoint, **kwargs):
    """Make a request to Octoprint API"""
    config = load_config()
    url = f"{config['octoprint_url']}{endpoint}"
    headers = {"X-Api-Key": config["api_key"]}

    if "headers" in kwargs:
        kwargs["headers"].update(headers)
    else:
        kwargs["headers"] = headers

    try:
        response = requests.request(method, url, **kwargs, timeout=10)
        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Octoprint: {e}", file=sys.stderr)
        sys.exit(1)

def format_time(seconds):
    """Format seconds into human-readable time"""
    if seconds is None:
        return "Unknown"

    if seconds < 0:
        return "Calculating..."

    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60

    if td.days > 0:
        return f"{td.days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def progress_bar(percentage, width=30):
    """Create a text progress bar"""
    if percentage is None:
        return "[" + " " * width + "] ???%"

    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage:.1f}%"

def get_status_formatted():
    """Get and display formatted printer status"""
    printer = make_request("GET", "/api/printer")
    job = make_request("GET", "/api/job")
    connection = make_request("GET", "/api/connection")

    # Printer state
    state = printer.get("state", {}).get("text", "Unknown")
    state_flags = printer.get("state", {}).get("flags", {})

    # Color code the state
    if state_flags.get("printing"):
        state_color = Colors.GREEN
    elif state_flags.get("paused"):
        state_color = Colors.YELLOW
    elif state_flags.get("error"):
        state_color = Colors.RED
    else:
        state_color = Colors.BLUE

    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}  OctoPrint Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.END}\n")

    # Connection info
    conn = connection.get("current", {})
    print(f"{Colors.CYAN}Connection:{Colors.END}")
    print(f"  State: {state_color}{state}{Colors.END}")
    print(f"  Port: {conn.get('port', 'Unknown')}")
    print(f"  Baudrate: {conn.get('baudrate', 'Unknown')}")
    print(f"  Profile: {conn.get('printerProfile', 'Unknown')}\n")

    # Temperature info
    temp = printer.get("temperature", {})
    print(f"{Colors.CYAN}Temperature:{Colors.END}")

    for tool_name, tool_data in temp.items():
        if isinstance(tool_data, dict) and 'actual' in tool_data:
            actual = tool_data.get('actual', 0) or 0
            target = tool_data.get('target', 0) or 0

            # Color code temperature based on target
            if target > 0:
                if abs(actual - target) < 3:
                    temp_color = Colors.GREEN
                elif abs(actual - target) < 10:
                    temp_color = Colors.YELLOW
                else:
                    temp_color = Colors.RED
            else:
                temp_color = Colors.BLUE

            tool_display = tool_name.replace('tool', 'Hotend ').replace('bed', 'Bed')
            print(f"  {tool_display}: {temp_color}{actual:.1f}°C{Colors.END} / {target:.1f}°C")

    print()

    # Job info
    job_info = job.get("job", {})
    progress_info = job.get("progress", {})

    if job_info.get("file", {}).get("name"):
        print(f"{Colors.CYAN}Current Job:{Colors.END}")
        print(f"  File: {Colors.BOLD}{job_info['file']['name']}{Colors.END}")

        completion = progress_info.get("completion")
        if completion is not None:
            print(f"  Progress: {progress_bar(completion)}")

        print_time = progress_info.get("printTime")
        print_time_left = progress_info.get("printTimeLeft")

        if print_time is not None:
            print(f"  Elapsed: {format_time(print_time)}")

        if print_time_left is not None:
            print(f"  Remaining: {format_time(print_time_left)}")
            if print_time_left > 0:
                eta = datetime.now() + timedelta(seconds=print_time_left)
                print(f"  ETA: {eta.strftime('%H:%M:%S')}")

        # Filament info
        filament = job_info.get("filament")
        if filament:
            for tool, data in filament.items():
                if isinstance(data, dict):
                    length_m = data.get('length', 0) / 1000
                    volume_cm3 = data.get('volume', 0)
                    print(f"  Filament ({tool}): {length_m:.2f}m / {volume_cm3:.2f}cm³")

        print()
    else:
        print(f"{Colors.CYAN}Current Job:{Colors.END} None\n")

    print(f"{Colors.BOLD}{'=' * 60}{Colors.END}\n")

def get_status():
    """Get raw printer status as JSON"""
    printer = make_request("GET", "/api/printer")
    job = make_request("GET", "/api/job")
    connection = make_request("GET", "/api/connection")

    print(json.dumps({
        "printer": printer,
        "job": job,
        "connection": connection
    }, indent=2))

def check_errors():
    """Monitor for errors and anomalies"""
    printer = make_request("GET", "/api/printer")
    job = make_request("GET", "/api/job")

    errors = []
    warnings = []

    # Check state
    state_flags = printer.get("state", {}).get("flags", {})
    if state_flags.get("error"):
        errors.append("Printer is in error state")

    if state_flags.get("closedOrError"):
        errors.append("Printer connection closed or error")

    # Check temperatures
    temp = printer.get("temperature", {})
    for tool_name, tool_data in temp.items():
        if isinstance(tool_data, dict) and 'actual' in tool_data:
            actual = tool_data.get('actual', 0) or 0
            target = tool_data.get('target', 0) or 0

            # Check if temperature is way off from target while printing
            if state_flags.get("printing") and target > 0:
                diff = abs(actual - target)
                if diff > 15:
                    errors.append(f"{tool_name} temperature off by {diff:.1f}°C (actual: {actual:.1f}°C, target: {target:.1f}°C)")
                elif diff > 5:
                    warnings.append(f"{tool_name} temperature {diff:.1f}°C from target")

            # Check for overheating
            if actual > 280:  # Most hotends shouldn't exceed this
                errors.append(f"{tool_name} overheating: {actual:.1f}°C")

    # Check if print is stalled
    if state_flags.get("printing"):
        progress = job.get("progress", {}).get("completion")
        print_time = job.get("progress", {}).get("printTime")

        # If printing but no progress or time
        if progress == 0 and print_time and print_time > 300:  # 5 minutes
            warnings.append("Print may be stalled (no progress after 5 minutes)")

    # Output results
    result = {
        "status": "error" if errors else "warning" if warnings else "ok",
        "errors": errors,
        "warnings": warnings,
        "timestamp": datetime.now().isoformat()
    }

    print(json.dumps(result, indent=2))
    return len(errors) == 0

def analyze_gcode(filepath):
    """Analyze a gcode file for metadata"""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    analysis = {
        "filename": os.path.basename(filepath),
        "size_bytes": os.path.getsize(filepath),
        "layers": 0,
        "estimated_time": None,
        "filament_length": None,
        "filament_weight": None,
        "bed_temp": None,
        "hotend_temp": None,
        "first_layer_height": None,
        "layer_height": None,
        "bounding_box": {"min": [None, None, None], "max": [None, None, None]}
    }

    layer_count = 0
    z_positions = set()

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()

            # Layer detection
            if ';LAYER:' in line or 'LAYER_CHANGE' in line:
                layer_count += 1

            # Detect Z movement for layer counting (alternative method)
            if line.startswith('G0') or line.startswith('G1'):
                z_match = re.search(r'Z([\d.]+)', line)
                if z_match:
                    z_positions.add(float(z_match.group(1)))

            # Temperature settings
            if line.startswith('M140') or line.startswith('M190'):  # Bed temp
                temp_match = re.search(r'S([\d.]+)', line)
                if temp_match and analysis["bed_temp"] is None:
                    analysis["bed_temp"] = float(temp_match.group(1))

            if line.startswith('M104') or line.startswith('M109'):  # Hotend temp
                temp_match = re.search(r'S([\d.]+)', line)
                if temp_match and analysis["hotend_temp"] is None:
                    analysis["hotend_temp"] = float(temp_match.group(1))

            # Slicer comments (Cura/PrusaSlicer format)
            if ';TIME:' in line:
                time_match = re.search(r';TIME:([\d]+)', line)
                if time_match:
                    analysis["estimated_time"] = int(time_match.group(1))

            if ';Filament used:' in line:
                filament_match = re.search(r'([\d.]+)m', line)
                if filament_match:
                    analysis["filament_length"] = float(filament_match.group(1))

            if 'filament used [mm]' in line.lower():
                filament_match = re.search(r'=\s*([\d.]+)', line)
                if filament_match:
                    analysis["filament_length"] = float(filament_match.group(1)) / 1000

            if ';MINX:' in line or '; min_x' in line.lower():
                match = re.search(r'([\d.-]+)', line.split(':')[1])
                if match:
                    analysis["bounding_box"]["min"][0] = float(match.group(1))

    # Use Z positions if layer count not found in comments
    if layer_count == 0 and z_positions:
        analysis["layers"] = len(z_positions)
    else:
        analysis["layers"] = layer_count

    print(json.dumps(analysis, indent=2))

def get_snapshot(output_path=None):
    """Capture webcam snapshot"""
    config = load_config()

    # Get webcam URL from config or use default
    webcam_url = config.get("webcam_url", f"{config['octoprint_url']}/webcam/?action=snapshot")

    try:
        response = requests.get(webcam_url, timeout=10)
        response.raise_for_status()

        # Determine output path
        if output_path is None:
            output_path = f"/tmp/octoprint_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"Snapshot saved to: {output_path}")
        return output_path

    except requests.exceptions.RequestException as e:
        print(f"Error capturing snapshot: {e}", file=sys.stderr)
        sys.exit(1)

def send_telegram_message(message):
    """Send a text message via Telegram"""
    config = load_config()

    if "telegram_bot_token" not in config or "telegram_chat_id" not in config:
        print("Error: Telegram not configured. Add telegram_bot_token and telegram_chat_id to config.json", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{config['telegram_bot_token']}/sendMessage"

    try:
        response = requests.post(url, json={
            "chat_id": config["telegram_chat_id"],
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
        response.raise_for_status()
        print("Telegram message sent successfully")

    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}", file=sys.stderr)
        sys.exit(1)

def send_telegram_photo(image_path, caption=None):
    """Send a photo via Telegram"""
    config = load_config()

    if "telegram_bot_token" not in config or "telegram_chat_id" not in config:
        print("Error: Telegram not configured. Add telegram_bot_token and telegram_chat_id to config.json", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{config['telegram_bot_token']}/sendPhoto"

    try:
        with open(image_path, 'rb') as f:
            files = {'photo': f}
            data = {
                "chat_id": config["telegram_chat_id"]
            }
            if caption:
                data["caption"] = caption

            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()

        print("Telegram photo sent successfully")

    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram photo: {e}", file=sys.stderr)
        sys.exit(1)

def telegram_status():
    """Send formatted status to Telegram"""
    printer = make_request("GET", "/api/printer")
    job = make_request("GET", "/api/job")

    state = printer.get("state", {}).get("text", "Unknown")
    job_info = job.get("job", {})
    progress_info = job.get("progress", {})

    # Build message
    message = f"*🖨️ Printer Status*\n\n"
    message += f"*State:* {state}\n"

    # Temperature
    temp = printer.get("temperature", {})
    temp_lines = []
    for tool_name, tool_data in temp.items():
        if isinstance(tool_data, dict) and 'actual' in tool_data:
            actual = tool_data.get('actual', 0) or 0
            target = tool_data.get('target', 0) or 0
            tool_display = tool_name.replace('tool', 'Hotend ').replace('bed', 'Bed')
            temp_lines.append(f"{tool_display}: {actual:.1f}°C / {target:.1f}°C")

    if temp_lines:
        message += f"*Temperature:*\n" + "\n".join(f"  • {line}" for line in temp_lines) + "\n"

    # Job info
    if job_info.get("file", {}).get("name"):
        message += f"\n*Current Job:*\n"
        message += f"  • File: {job_info['file']['name']}\n"

        completion = progress_info.get("completion")
        if completion is not None:
            message += f"  • Progress: {completion:.1f}%\n"

        print_time_left = progress_info.get("printTimeLeft")
        if print_time_left is not None:
            message += f"  • Remaining: {format_time(print_time_left)}\n"

    send_telegram_message(message)

def telegram_snapshot():
    """Capture and send snapshot to Telegram with status"""
    # Get snapshot
    snapshot_path = get_snapshot()

    # Get job info for caption
    job = make_request("GET", "/api/job")
    progress_info = job.get("progress", {})
    job_info = job.get("job", {})

    caption = "📸 OctoPrint Snapshot"
    if job_info.get("file", {}).get("name"):
        caption += f"\n🗂️ {job_info['file']['name']}"
        completion = progress_info.get("completion")
        if completion is not None:
            caption += f"\n📊 {completion:.1f}% complete"

    send_telegram_photo(snapshot_path, caption)

    # Clean up temp file
    if snapshot_path.startswith("/tmp/"):
        os.remove(snapshot_path)

def list_files():
    """List available files"""
    data = make_request("GET", "/api/files?recursive=true")
    files = []

    def extract_files(items, path=""):
        for item in items:
            if item["type"] == "folder":
                extract_files(item.get("children", []), f"{path}{item['name']}/")
            else:
                files.append({
                    "name": item["name"],
                    "path": f"{path}{item['name']}",
                    "size": item.get("size", 0),
                    "date": item.get("date", 0)
                })

    extract_files(data.get("files", []))
    print(json.dumps(files, indent=2))

def start_print(filepath):
    """Start printing a file"""
    # Select the file
    make_request("POST", f"/api/files/local/{filepath}", json={"command": "select"})
    # Start the print
    make_request("POST", "/api/job", json={"command": "start"})
    print(f"Started printing {filepath}")

def control_print(command):
    """Control print job (pause, resume, cancel)"""
    valid_commands = ["pause", "resume", "cancel"]
    if command not in valid_commands:
        print(f"Error: Invalid command. Must be one of {valid_commands}", file=sys.stderr)
        sys.exit(1)

    make_request("POST", "/api/job", json={"command": command})
    print(f"Print {command}ed")

def set_temperature(tool, temp):
    """Set tool or bed temperature"""
    if tool == "bed":
        make_request("POST", "/api/printer/bed", json={"command": "target", "target": int(temp)})
    else:
        make_request("POST", "/api/printer/tool", json={"command": "target", "targets": {tool: int(temp)}})
    print(f"Set {tool} temperature to {temp}°C")

def upload_file(filepath, filename=None):
    """Upload a gcode file to Octoprint"""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    if filename is None:
        filename = os.path.basename(filepath)

    config = load_config()
    url = f"{config['octoprint_url']}/api/files/local"
    headers = {"X-Api-Key": config["api_key"]}

    with open(filepath, 'rb') as f:
        files = {'file': (filename, f, 'application/octet-stream')}
        response = requests.post(url, headers=headers, files=files, timeout=30)
        response.raise_for_status()

    print(f"Uploaded {filename} successfully")
    return filename

def main():
    if len(sys.argv) < 2:
        print("Usage: octoprint.py <command> [args...]", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  status              - Get raw status JSON", file=sys.stderr)
        print("  status-pretty       - Get formatted status display", file=sys.stderr)
        print("  check-errors        - Monitor for errors", file=sys.stderr)
        print("  list-files          - List available gcode files", file=sys.stderr)
        print("  analyze <file>      - Analyze gcode file", file=sys.stderr)
        print("  snapshot [path]     - Capture webcam snapshot", file=sys.stderr)
        print("  print <file>        - Start printing", file=sys.stderr)
        print("  control <cmd>       - Control print (pause/resume/cancel)", file=sys.stderr)
        print("  temp <tool> <temp>  - Set temperature", file=sys.stderr)
        print("  upload <file>       - Upload gcode file", file=sys.stderr)
        print("  telegram-status     - Send status to Telegram", file=sys.stderr)
        print("  telegram-snapshot   - Send snapshot to Telegram", file=sys.stderr)
        print("  telegram-msg <msg>  - Send message to Telegram", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        get_status()
    elif command == "status-pretty":
        get_status_formatted()
    elif command == "check-errors":
        success = check_errors()
        sys.exit(0 if success else 1)
    elif command == "list-files":
        list_files()
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("Error: Missing filename", file=sys.stderr)
            sys.exit(1)
        analyze_gcode(sys.argv[2])
    elif command == "snapshot":
        output = sys.argv[2] if len(sys.argv) > 2 else None
        get_snapshot(output)
    elif command == "print":
        if len(sys.argv) < 3:
            print("Error: Missing filename", file=sys.stderr)
            sys.exit(1)
        start_print(sys.argv[2])
    elif command == "control":
        if len(sys.argv) < 3:
            print("Error: Missing control command", file=sys.stderr)
            sys.exit(1)
        control_print(sys.argv[2])
    elif command == "temp":
        if len(sys.argv) < 4:
            print("Error: Missing tool and temperature", file=sys.stderr)
            sys.exit(1)
        set_temperature(sys.argv[2], sys.argv[3])
    elif command == "upload":
        if len(sys.argv) < 3:
            print("Error: Missing filepath", file=sys.stderr)
            sys.exit(1)
        filename = sys.argv[3] if len(sys.argv) > 3 else None
        upload_file(sys.argv[2], filename)
    elif command == "telegram-status":
        telegram_status()
    elif command == "telegram-snapshot":
        telegram_snapshot()
    elif command == "telegram-msg":
        if len(sys.argv) < 3:
            print("Error: Missing message", file=sys.stderr)
            sys.exit(1)
        send_telegram_message(" ".join(sys.argv[2:]))
    else:
        print(f"Error: Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
