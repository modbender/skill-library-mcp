#!/usr/bin/env python3
"""Test OpenCLAW script example."""

from datetime import datetime
import os

def main():
    print("=" * 40)
    print("  Test OpenCLAW Skill!")
    print("=" * 40)
    print()
    print("This is a simple script that demonstrates")
    print("how scripts work in OpenCLAW skills.")
    print()
    print(f"Current time: {datetime.now()}")
    print(f"Current directory: {os.getcwd()}")
    print()
    print("=" * 40)

if __name__ == "__main__":
    main()
