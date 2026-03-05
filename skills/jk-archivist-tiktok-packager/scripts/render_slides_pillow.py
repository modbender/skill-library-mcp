"""Thin wrapper to keep script path stable while using src/python implementation."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.python.render_slides_pillow import main


if __name__ == "__main__":
    main()
