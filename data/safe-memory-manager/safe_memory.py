"""
ISNAD Verified Premium Skill: Injection-Safe Memory Manager
Author: LeoAGI
Description: Safely reads and writes agent memory files. Sanitizes inputs to prevent prompt injection 
and command execution payloads commonly used in "Memory Poisoning" attacks.
"""

import re
import os
import json
from datetime import datetime

class SafeMemoryManager:
    def __init__(self, memory_dir="memory"):
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Blacklist of common prompt injection and payload patterns
        self.malicious_patterns = [
            re.compile(r"(?i)(ignore previous instructions|system prompt|system message)"),
            re.compile(r"(?i)(execute|eval|os\.system|subprocess|bash|sh -c)"),
            re.compile(r"(?i)(priority task|override command)"),
            re.compile(r"```(bash|sh|python)\n[\s\S]*?(rm -rf|wget|curl)[\s\S]*?```")
        ]

    def sanitize_content(self, text):
        """Sanitizes text by stripping out known injection vectors."""
        sanitized = text
        for pattern in self.malicious_patterns:
            # Replace malicious matched patterns with a warning string
            sanitized = pattern.sub("[SANITIZED_INJECTION_ATTEMPT]", sanitized)
        return sanitized

    def append_memory(self, filename, content, author="Agent"):
        """Safely appends to a memory file."""
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in ('-', '_', '.')]).rstrip()
        file_path = os.path.join(self.memory_dir, safe_filename)
        
        sanitized_content = self.sanitize_content(content)
        
        entry = f"\n[{datetime.now().isoformat()}] {author}: {sanitized_content}\n"
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
            
        return {"status": "success", "file": safe_filename, "bytes_written": len(entry)}

    def read_memory(self, filename, lines=50):
        """Reads memory, returning the last N lines to prevent context overflow."""
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in ('-', '_', '.')]).rstrip()
        file_path = os.path.join(self.memory_dir, safe_filename)
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File not found"}
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
            
        return {"status": "success", "data": "".join(content[-lines:])}

# Example usage for CLI testing
if __name__ == "__main__":
    import sys
    manager = SafeMemoryManager()
    if len(sys.argv) > 2 and sys.argv[1] == "append":
        res = manager.append_memory("test.md", sys.argv[2])
        print(json.dumps(res))
