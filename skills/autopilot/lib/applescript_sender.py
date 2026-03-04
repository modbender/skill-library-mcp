#!/usr/bin/env python3
"""
AppleScript-based message sender for Codex Desktop.

Uses osascript + System Events to:
1. Activate Codex
2. Set clipboard
3. Paste (Cmd+V) via System Events keystroke
4. Press Enter via System Events keystroke

This avoids CGEvent (which may hit wrong window) and instead
uses System Events keystroke targeting the Codex process directly.
"""

import logging
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)


def send_via_applescript(text: str, project_name: str = "Codex") -> bool:
    """
    Send text to Codex Desktop via AppleScript System Events.
    
    Steps:
    1. Set clipboard via pbcopy
    2. Activate Codex
    3. Paste via System Events keystroke "v" using {command down}
    4. Press Enter via System Events keystroke return
    
    Args:
        text: Message to send
        project_name: Project name (for logging)
    
    Returns:
        True if osascript succeeded
    """
    logger.info(f"AppleScript sender: sending {len(text)} chars to {project_name}")
    
    # 1. Set clipboard
    try:
        proc = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=text, timeout=5)
        if proc.returncode != 0:
            logger.error("AppleScript sender: pbcopy failed")
            return False
    except Exception as e:
        logger.error(f"AppleScript sender: pbcopy error: {e}")
        return False
    
    # 2. Activate + Paste + Enter via single osascript
    script = '''
    tell application "Codex" to activate
    delay 1
    tell application "System Events"
        tell process "Codex"
            set frontmost to true
            delay 0.3
            keystroke "v" using {command down}
            delay 0.5
            keystroke return
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            logger.info("AppleScript sender: sent successfully")
            return True
        
        stderr = result.stderr.strip()
        logger.warning(f"AppleScript sender: System Events failed ({stderr})")
        
        # Fallback: activate + CGEvent paste+enter (no System Events needed)
        logger.info("AppleScript sender: trying CGEvent fallback")
        return _send_via_cgevent(text, project_name)
        
    except subprocess.TimeoutExpired:
        logger.error("AppleScript sender: osascript timeout")
        return False
    except Exception as e:
        logger.error(f"AppleScript sender: error: {e}")
        return False


def _send_via_cgevent(text: str, project_name: str) -> bool:
    """
    Fallback: activate via osascript, then paste+enter via CGEvent.
    """
    import ctypes
    import ctypes.util
    
    # Activate
    try:
        subprocess.run(
            ['osascript', '-e', 'tell application "Codex" to activate'],
            capture_output=True, timeout=5
        )
        time.sleep(1.0)
    except Exception:
        pass
    
    # Clipboard already set from caller
    
    try:
        cg_path = ctypes.util.find_library('CoreGraphics')
        cg = ctypes.cdll.LoadLibrary(
            cg_path or '/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics'
        )
        cf = ctypes.cdll.LoadLibrary(
            '/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation'
        )
        
        cg.CGEventSourceCreate.restype = ctypes.c_void_p
        cg.CGEventSourceCreate.argtypes = [ctypes.c_int]
        source = cg.CGEventSourceCreate(0)
        if not source:
            logger.error("CGEvent: cannot create source")
            return False
        
        cg.CGEventCreateKeyboardEvent.restype = ctypes.c_void_p
        cg.CGEventCreateKeyboardEvent.argtypes = [
            ctypes.c_void_p, ctypes.c_uint16, ctypes.c_bool
        ]
        cg.CGEventSetFlags.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        cg.CGEventPost.argtypes = [ctypes.c_int, ctypes.c_void_p]
        cf.CFRelease.argtypes = [ctypes.c_void_p]
        
        def _key(code, cmd=False):
            down = cg.CGEventCreateKeyboardEvent(source, code, True)
            up = cg.CGEventCreateKeyboardEvent(source, code, False)
            if cmd:
                cg.CGEventSetFlags(down, 0x100000)
                cg.CGEventSetFlags(up, 0x100000)
            cg.CGEventPost(0, down)
            time.sleep(0.05)
            cg.CGEventPost(0, up)
            cf.CFRelease(down)
            cf.CFRelease(up)
        
        # Cmd+V
        _key(9, cmd=True)
        time.sleep(0.5)
        # Enter
        _key(36)
        
        cf.CFRelease(source)
        logger.info("AppleScript sender (CGEvent fallback): sent")
        return True
        
    except Exception as e:
        logger.error(f"CGEvent fallback error: {e}")
        return False
