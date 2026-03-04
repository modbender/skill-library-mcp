# Skill: Nerve Bridge v2 (Bi-Directional)
# Description: Controls Trae and WAITS for execution result via file signal.
# Usage: python3 nerve_bridge.py "<instruction>"
import sys
import subprocess
import time
import os
import json

# Define feedback file path
FEEDBACK_FILE = os.path.expanduser("~/.openclaw/workspace/trae_feedback.json")

def execute_with_feedback(instruction):
    print("⚡️ [Nerve Bridge] Preparing closed-loop instruction...")

    # 1. Clear old signal (Reset the mailbox)
    if os.path.exists(FEEDBACK_FILE):
        try:
            os.remove(FEEDBACK_FILE)
        except:
            pass

    # 2. Append the "Hook" (The Reporter)
    # This Python code will be appended to the instruction sent to Trae.
    # It forces Trae to write a file when done.
    hook_code = (
        "import json, time; "
        "with open('" + FEEDBACK_FILE + "', 'w') as f: "
        "json.dump({'status': 'success', 'timestamp': time.time()}, f)"
    )

    # Construct the full payload
    # We add a clear separator and the hook code
    full_payload = (
        instruction + "\n\n"
        "# --- SYSTEM HOOK ---\n"
        "# REQUIRED: Execute this to report completion:\n"
        + hook_code + "\n"
    )

    # 3. Inject Signal (Send to Clipboard)
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(input=full_payload.encode('utf-8'))

    # 4. Fire Neural Pulse (AppleScript)
    # Using concatenation to avoid Markdown triple-quote issues
    script = (
        'tell application "Trae" to activate\n'
        'delay 0.5\n'
        'tell application "System Events"\n'
        ' key code 49\n'  # Space
        ' delay 0.1\n'
        ' key code 51\n'  # Delete
        ' delay 0.2\n'
        ' keystroke "v" using command down\n'
        ' delay 0.5\n'
        ' key code 36\n'  # Enter
        'end tell'
    )
    subprocess.run(['osascript', '-e', script])

    print("➡️ [Send] Instruction sent. Waiting for Trae signal...")

    # 5. Listen for Echo (The Feedback Loop)
    # Wait up to 300 seconds (5 minutes) for deployment tasks
    timeout = 300
    start_time = time.time()
    while True:
        if os.path.exists(FEEDBACK_FILE):
            # Signal received!
            try:
                with open(FEEDBACK_FILE, 'r') as f:
                    data = json.load(f)
                print(f"✅ [Ack] Feedback received from Trae: {data}")
                return
            except:
                # File might be writing, wait a bit
                time.sleep(1)
        if time.time() - start_time > timeout:
            print("❌ [Timeout] Trae did not report back in time.")
            sys.exit(1)
        time.sleep(2)  # Check every 2 seconds

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No instruction provided.")
    else:
        execute_with_feedback(sys.argv[1])
