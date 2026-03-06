import sys
import json
import subprocess

# Simple CLI wrapper to integrate the existing Python agent into an OpenClaw skill
# Usage: python poetry_hub_entrypoint.py [register|run|state|feed|reset]

def main():
    if len(sys.argv) < 2:
        print("Usage: poetry_hub_entrypoint.py [register|run|state|feed|reset]")
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "register":
        # Run the existing agent's register path
        subprocess.run([sys.executable, "poetry_hub_agent.py", "register"], check=True)
    elif cmd == "run":
        subprocess.run([sys.executable, "poetry_hub_agent.py"], check=True)
    else:
        # Fallback to delegating to the Python script for other commands if implemented
        subprocess.run([sys.executable, "poetry_hub_agent.py", cmd], check=True)

if __name__ == "__main__":
    main()
