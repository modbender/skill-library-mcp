#!/usr/bin/env python3
"""ComfyUI 自动关闭：超过配置时间无使用则关闭进程"""

import json
import time
from pathlib import Path

CONFIG = json.loads((Path(__file__).parent.parent / "config.json").read_text())
LAST_USED = Path(__file__).parent.parent / ".last_used"
TIMEOUT_MIN = CONFIG.get("auto_shutdown_minutes", 15)


def check_and_shutdown() -> str:
    """检查是否需要关闭 ComfyUI"""
    from comfyui_manager import is_running, stop

    if not is_running():
        return "not_running"

    if not LAST_USED.exists():
        # 没有记录，执行关闭
        stop()
        return "shutdown_no_record"

    last_ts = float(LAST_USED.read_text().strip())
    elapsed_min = (time.time() - last_ts) / 60

    if elapsed_min >= TIMEOUT_MIN:
        stop()
        LAST_USED.unlink(missing_ok=True)
        return f"shutdown_idle_{elapsed_min:.0f}min"
    else:
        return f"active_last_used_{elapsed_min:.0f}min_ago"


if __name__ == "__main__":
    result = check_and_shutdown()
    print(result)
