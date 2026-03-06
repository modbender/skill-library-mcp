#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCalendar Sync - Module entry point
Allows execution via: python -m icalendar_sync

@author: Black_Temple
@version: 2.3.0
"""

import sys
import warnings
from pathlib import Path

# Add src directory to sys.path for module imports
# This ensures icalendar_sync module is found when running as: python -m icalendar_sync
module_path = Path(__file__).parent.parent
if str(module_path) not in sys.path:
    sys.path.insert(0, str(module_path))

# Suppress RuntimeWarning about __main__ in sys.modules
warnings.filterwarnings('ignore', category=RuntimeWarning,
                       message='.*__main__.*sys.modules.*')

from .calendar import main

if __name__ == '__main__':
    main()
