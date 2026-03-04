"""
auto_memory_write.py — 自动记忆写入辅助函数
在关键决策点自动写入记忆，避免等到 session 结束才记录
"""
import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"


def auto_write_memory(
    summary: str,
    importance: int,
    channel: str = "boss",
    tags: Optional[list[str]] = None,
    project: Optional[str] = None,
    files: Optional[list[str]] = None,
    lessons: Optional[str] = None,
) -> dict:
    """
    自动写入记忆到日志文件
    
    Args:
        summary: 记忆摘要（一句话）
        importance: 重要性（1-10）
        channel: 频道名称
        tags: 检索标签列表
        project: 项目名称
        files: 相关文件列表
        lessons: 经验教训
    
    Returns:
        写入结果
    """
    today = date.today()
    log_file = MEMORY_DIR / f"{today.isoformat()}.md"
    
    # 确保日志文件存在
    if not log_file.exists():
        log_file.write_text(f"# {today.isoformat()}\n\n", encoding="utf-8")
    
    # 构建记忆条目
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n## {timestamp} "
    
    if project:
        entry += f"{project}\n\n"
        entry += f"【项目：{project}】 {summary}\n"
    else:
        entry += f"自动记录\n\n"
        entry += f"{summary}\n"
    
    if files:
        entry += f"相关文件：{', '.join(files)}\n"
    
    if lessons:
        entry += f"经验教训：{lessons}\n"
    
    # 添加标签
    if tags:
        tag_str = " ".join([f"#{tag}" for tag in tags])
        entry += f"检索标签：{tag_str}\n"
    
    # 添加元数据
    entry += f"<!-- meta: importance={importance} access=0 created={today.isoformat()} "
    entry += f"last_accessed={today.isoformat()} channel={channel} -->\n"
    
    # 写入文件
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    return {
        "written": True,
        "log_file": str(log_file),
        "timestamp": datetime.now().isoformat(),
        "importance": importance,
    }


def should_auto_write(context: dict) -> bool:
    """
    判断是否应该自动写入记忆
    
    Args:
        context: 当前上下文信息
            - task_completed: 是否完成任务
            - decision_made: 是否做出决策
            - config_changed: 是否变更配置
            - problem_solved: 是否解决问题
            - importance: 重要性评分（1-10）
    
    Returns:
        是否应该写入
    """
    # 重要性 >= 7 的必须写入
    if context.get("importance", 0) >= 7:
        return True
    
    # 完成关键任务
    if context.get("task_completed") and context.get("importance", 0) >= 5:
        return True
    
    # 做出重要决策
    if context.get("decision_made"):
        return True
    
    # 配置变更
    if context.get("config_changed"):
        return True
    
    # 解决问题
    if context.get("problem_solved") and context.get("importance", 0) >= 5:
        return True
    
    return False


# 预定义的记忆模板
MEMORY_TEMPLATES = {
    "task_completed": {
        "importance": 7,
        "tags": ["任务完成"],
    },
    "decision_made": {
        "importance": 8,
        "tags": ["决策"],
    },
    "config_changed": {
        "importance": 8,
        "tags": ["配置变更"],
    },
    "problem_solved": {
        "importance": 7,
        "tags": ["问题解决"],
    },
    "deployment": {
        "importance": 8,
        "tags": ["部署"],
    },
    "architecture": {
        "importance": 9,
        "tags": ["架构"],
    },
}


def get_template(template_name: str) -> dict:
    """获取记忆模板"""
    return MEMORY_TEMPLATES.get(template_name, {
        "importance": 5,
        "tags": [],
    })


if __name__ == "__main__":
    # 测试
    result = auto_write_memory(
        summary="测试自动记忆写入功能",
        importance=5,
        channel="boss",
        tags=["测试", "自动写入"],
        project="记忆系统优化",
        lessons="自动写入功能可以减少记忆丢失风险",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
