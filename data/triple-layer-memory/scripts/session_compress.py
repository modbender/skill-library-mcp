"""
session_compress.py — Session 自动压缩引擎
当 session token 使用量达到阈值时，自动总结旧对话并写入记忆文件
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"
COMPRESS_THRESHOLD = 150000  # 达到 150k tokens 时触发压缩
KEEP_RECENT_TOKENS = 50000   # 保留最近 50k tokens 的原始对话


def should_compress(current_tokens: int) -> bool:
    """判断是否需要压缩"""
    return current_tokens >= COMPRESS_THRESHOLD


def compress_session(session_summary: str, channel: str = "boss") -> dict:
    """
    压缩 session 并写入记忆文件
    
    Args:
        session_summary: LLM 生成的对话总结
        channel: 频道名称
    
    Returns:
        压缩统计信息
    """
    today = date.today()
    log_file = MEMORY_DIR / f"{today.isoformat()}.md"
    
    # 确保日志文件存在
    if not log_file.exists():
        log_file.write_text(f"# {today.isoformat()}\n\n", encoding="utf-8")
    
    # 追加压缩记录
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n## {timestamp} Session 自动压缩（由 token 阈值触发）\n\n"
    entry += f"【项目：Session 管理】 自动压缩对话历史\n"
    entry += f"结果：{session_summary}\n"
    entry += f"检索标签：#session #自动压缩 #记忆管理\n"
    entry += f"<!-- meta: importance=7 access=0 created={today.isoformat()} "
    entry += f"last_accessed={today.isoformat()} channel={channel} -->\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    return {
        "compressed": True,
        "log_file": str(log_file),
        "timestamp": datetime.now().isoformat(),
    }


def get_compress_prompt(current_tokens: int) -> str:
    """
    生成压缩提示词
    
    返回给 LLM 的提示，要求总结对话历史
    """
    return f"""当前 session 已使用 {current_tokens} tokens，达到压缩阈值。

请总结本次对话中的关键信息：
1. 完成的任务和结果
2. 做出的重要决策
3. 配置变更和路径信息
4. 待办事项和未完成的工作
5. 遇到的问题和解决方案

要求：
- 只保留关键信息，去除过程细节
- 使用简洁的语言，每项 1-2 句话
- 按重要性排序
- 如果没有重要信息，回复"本次对话无需记录关键信息"

请开始总结："""


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python session_compress.py <current_tokens> [channel]")
        print("Example: python session_compress.py 155000 boss")
        sys.exit(1)
    
    current_tokens = int(sys.argv[1])
    channel = sys.argv[2] if len(sys.argv) > 2 else "boss"
    
    if should_compress(current_tokens):
        print(f"[COMPRESS_NEEDED] Current tokens: {current_tokens}")
        print(f"[COMPRESS_PROMPT] {get_compress_prompt(current_tokens)}")
    else:
        print(f"[COMPRESS_NOT_NEEDED] Current tokens: {current_tokens} < {COMPRESS_THRESHOLD}")


if __name__ == "__main__":
    main()
