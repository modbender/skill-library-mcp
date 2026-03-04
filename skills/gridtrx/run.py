"""
Grid — Double-click this file to start.
Opens your browser automatically.

Prerequisites: pip install flask
"""
import sys
import os

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        import flask  # noqa: F401
    except ImportError:
        print("Flask is not installed. Install it first:")
        print(f"  {sys.executable} -m pip install flask")
        sys.exit(1)

    from app import main as run_app
    run_app()

if __name__ == '__main__':
    main()
