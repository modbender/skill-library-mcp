#!/usr/bin/env python3
"""FinClaw setup: create venv, install dependencies, initialize database."""

import subprocess
import sys
import os

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(SKILL_DIR, "venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python3")
VENV_PIP = os.path.join(VENV_DIR, "bin", "pip")
REQ_FILE = os.path.join(SKILL_DIR, "requirements.txt")


def create_venv():
    if os.path.exists(VENV_PYTHON):
        print(f"Venv already exists at {VENV_DIR}")
        return
    print(f"Creating venv at {VENV_DIR}...")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    print("Venv created.")


def install_deps():
    print("Installing dependencies...")
    subprocess.check_call([VENV_PIP, "install", "--upgrade", "pip"],
                          stdout=subprocess.DEVNULL)
    subprocess.check_call([VENV_PIP, "install", "-r", REQ_FILE])
    print("Dependencies installed.")


def init_db():
    print("Initializing database...")
    subprocess.check_call([VENV_PYTHON, os.path.join(SKILL_DIR, "scripts", "init_db.py")])


def main():
    print("=== FinClaw Setup ===\n")
    create_venv()
    install_deps()
    init_db()
    print("\n=== Setup complete! ===")
    print(f"Python: {VENV_PYTHON}")
    print(f"Database: {os.path.join(SKILL_DIR, 'data', 'finance.db')}")


if __name__ == "__main__":
    main()
