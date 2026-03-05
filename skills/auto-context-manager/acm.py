#!/usr/bin/env python3
"""CLI wrapper for Auto Context Manager"""
import sys
from auto_context_manager import AutoContextManager

def main():
    if len(sys.argv) < 2:
        print("Usage: python acm.py <command> [args]")
        print("Commands: detect <message>, list, current, switch <project>")
        sys.exit(1)

    acm = AutoContextManager()
    cmd = sys.argv[1]

    if cmd == "detect" and len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])
        project, confidence = acm.detect_project(message)
        print(f"project={project}")
        print(f"confidence={confidence:.2f}")

    elif cmd == "list":
        print(acm.list_projects())

    elif cmd == "current":
        print(acm.get_current_project())

    elif cmd == "switch" and len(sys.argv) > 2:
        print(acm.switch_project(sys.argv[2]))

    else:
        print("Unknown command or missing arguments")

if __name__ == "__main__":
    main()