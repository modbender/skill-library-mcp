#!/usr/bin/env python3
"""
Sensitive Data Masker - OpenClaw Hook Wrapper
"""

import sys
import json
from pathlib import Path

# Import masker
sys.path.insert(0, str(Path(__file__).parent))
from sensitive_masker import ChannelSensitiveMasker

def mask_message(content: str) -> dict:
    """Mask message content."""
    masker = ChannelSensitiveMasker()
    masked_text, replacements = masker.mask_message(content)
    
    return {
        "masked": masked_text,
        "count": len(replacements),
        "types": list(set([r['type'] for r in replacements]))
    }

def restore_message(masked_content: str) -> str:
    """Restore sensitive data in message."""
    masker = ChannelSensitiveMasker()
    return masker.restore_message(masked_content)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <command> <content>")
        print("Commands:")
        print("  mask <content>    - Mask message")
        print("  restore <content> - Restore message")
        sys.exit(1)
    
    command = sys.argv[1]
    content = ' '.join(sys.argv[2:])
    
    if command == 'mask':
        result = mask_message(content)
        print(json.dumps(result, ensure_ascii=False))
    elif command == 'restore':
        restored = restore_message(content)
        print(restored)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
