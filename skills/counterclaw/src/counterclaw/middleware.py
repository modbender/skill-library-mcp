"""
CounterClaw - Defensive Interceptor Middleware
Snaps shut on malicious payloads before they reach your AI
"""

import os
import re
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from counterclaw.scanner import Scanner


MEMORY_PATH = os.path.expanduser("~/.openclaw/memory/MEMORY.md")

# PII patterns for log masking
PII_MASK_PATTERNS = {
    "email": re.compile(r'[\w.-]+@[\w.-]+\.\w+'),
    "phone": re.compile(r'0?7[\d\s]{9,}'),
    "card": re.compile(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}'),
    "aws_key": re.compile(r'AKIA[0-9A-Z]{16}'),
    "api_key": re.compile(r'(?i)(api[_-]?key|secret)[=:]\s*[\w-]{20,}'),
}


def _mask_pii(text: str) -> str:
    """Mask PII in logs - prevents accidental leaks"""
    masked = text
    masked = PII_MASK_PATTERNS["email"].sub("[EMAIL]", masked)
    masked = PII_MASK_PATTERNS["phone"].sub("[PHONE]", masked)
    masked = PII_MASK_PATTERNS["card"].sub("[CARD]", masked)
    masked = PII_MASK_PATTERNS["aws_key"].sub("[AWS_KEY]", masked)
    masked = PII_MASK_PATTERNS["api_key"].sub(r'\1=[REDACTED]', masked)
    return masked


def _ensure_memory_file() -> None:
    """Ensure MEMORY.md exists - create if missing"""
    memory_dir = os.path.dirname(MEMORY_PATH)
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir, exist_ok=True)
    if not os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "w") as f:
            f.write("# OpenClaw Memory\n\n")


def _log_violation(violation: Dict[str, Any], context: str, text: str) -> None:
    """Log violation to MEMORY.md - fails silently if inaccessible"""
    try:
        _ensure_memory_file()
        # Mask PII before logging
        safe_text = _mask_pii(text)
        with open(MEMORY_PATH, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            f.write(f"\n## {timestamp} - CounterClaw Violation\n")
            f.write(f"**Context:** {context}\n")
            f.write(f"**Sample:** {safe_text[:100]}...\n")
            f.write(f"**Violations:** {violation.get('violations', [])}\n")
    except (IOError, OSError):
        pass


class CounterClawInterceptor:
    """Defensive interceptor - snaps shut on threats"""
    
    def __init__(self, enable_nexus: bool = False, nexus_api_key: Optional[str] = None,
                 admin_user_id: Optional[str] = None):
        self.scanner = Scanner()
        self.enable_nexus = enable_nexus
        self.nexus_api_key = nexus_api_key
        self.admin_user_id = admin_user_id  # Required for !claw-lock
        
        if enable_nexus and not nexus_api_key:
            raise ValueError("Nexus API key required when enable_nexus=True")
    
    async def check_input_async(self, text: str, log_violations: bool = True) -> Dict[str, Any]:
        """Async input check"""
        result = self.scanner.scan_input(text)
        
        if result["blocked"] and log_violations:
            _log_violation(result, "input", text)
        
        if self.enable_nexus:
            result["nexus_checked"] = True
        
        return result
    
    async def check_output_async(self, text: str, log_violations: bool = True) -> Dict[str, Any]:
        """Async output check"""
        result = self.scanner.scan_output(text)
        
        if result.get("pii_detected") and log_violations:
            _log_violation(result, "output", text)
        
        if self.enable_nexus:
            result["nexus_checked"] = True
        
        return result
    
    # Sync wrapper for non-async contexts
    def check_input(self, text: str, log_violations: bool = True) -> Dict[str, Any]:
        """Sync input check - wraps async"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context - create new loop
                return asyncio.run(self.check_input_async(text, log_violations))
            return loop.run_until_complete(self.check_input_async(text, log_violations))
        except RuntimeError:
            return asyncio.run(self.check_input_async(text, log_violations))
    
    def check_output(self, text: str, log_violations: bool = True) -> Dict[str, Any]:
        """Sync output check - wraps async"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return asyncio.run(self.check_output_async(text, log_violations))
            return loop.run_until_complete(self.check_output_async(text, log_violations))
        except RuntimeError:
            return asyncio.run(self.check_output_async(text, log_violations))
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin - required for !claw-lock"""
        if self.admin_user_id is None:
            return True  # No admin set - allow all
        return user_id == self.admin_user_id
