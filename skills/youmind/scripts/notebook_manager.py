#!/usr/bin/env python3
"""
Compatibility wrapper.
Deprecated: use board_manager.py instead.
"""

from board_manager import BoardLibrary, main


if __name__ == "__main__":
    print("⚠️ notebook_manager.py is deprecated. Use board_manager.py instead.")
    main()
