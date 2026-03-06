#!/usr/bin/env python3
"""
FIS 3.2.0 多 Worker + Reviewer 工作流示例
演示复杂任务的分解与并行执行
"""

import json
import subprocess
import sys
from pathlib import Path

# 添加 lifecycle 模块路径
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "skills" / "fis-architecture" / "lib"))
from fis_lifecycle import SubAgentLifecycle

def multi_worker_workflow():
    """
    多 Worker 并行任务示例：
    - Worker-1: 研究 MCP 扩展
    - Worker-2: 研究 QMD 内存
    - Worker-3: 研究 Session 概念
    - Reviewer: 汇总三个报告
    """
    
    lifecycle = SubAgentLifecycle("cybermao")
    
    print("=" * 60)
    print("🚀 FIS 3.2.0 多 Worker + Reviewer 工作流")
    print("=" * 60)
    
    # ========== Phase 1: 创建 3 个 Worker 任务 ==========
    print("\n📋 Phase 1: 创建 Worker 任务")
    
    workers = []
    worker_configs = [
        {
            "agent_name": "Worker-MCP",
            "task_desc": "研究 MCP (Model Context Protocol) 协议：AI能力扩展机制、核心组件、使用场景",
            "role": "worker",
            "outputs": ["mcp研究.md", "关键发现.json"],
            "url": "https://www.nodeseek.com/post-607748-1"
        },
        {
            "agent_name": "Worker-QMD",
            "task_desc": "研究 OpenClaw QMD 内存系统：混合搜索机制、三重回溯、配置方法",
            "role": "worker",
            "outputs": ["qmd研究.md", "关键发现.json"],
            "url": "https://www.josecasanova.com/blog/openclaw-qmd-memory"
        },
        {
            "agent_name": "Worker-Session",
            "task_desc": "研究 OpenClaw Session 概念：会话生命周期、DM隔离模式、安全设计",
            "role": "worker",
            "outputs": ["session研究.md", "关键发现.json"],
            "url": "https://docs.openclaw.ai/concepts/session"
        }
    ]
    
    for config in worker_configs:
        ticket_id, task = lifecycle.create_task(
            agent_name=config["agent_name"],
            task_desc=config["task_desc"],
            role=config["role"],
            output_requirements=config["outputs"],
            deadline_days=1
        )
        workers.append({
            "name": config["agent_name"],
            "ticket": ticket_id,
            "url": config["url"],
            "role": config["role"],
            "task_desc": config["task_desc"],
            "outputs": config["outputs"]
        })
    
    print(f"\n✅ 已创建 {len(workers)} 个 Worker 任务")
    
    # ========== Phase 1.5: 生成拼接工牌并发送 ==========
    print("\n🎨 Phase 1.5: 生成多工牌拼接图")
    
    # 导入拼接功能
    sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "skills" / "fis-architecture" / "lib"))
    from badge_generator_v7 import generate_multi_badge
    
    cards_data = [
        {
            "agent_name": w["name"],
            "role": w["role"],
            "task_desc": w["task_desc"],
            "task_requirements": w["outputs"]
        }
        for w in workers
    ]
    
    multi_badge_path = generate_multi_badge(cards_data, "multi_worker_badges.png")
    print(f"✅ 拼接工牌: {multi_badge_path}")
    
    # 发送到 WhatsApp
    print("\n📱 发送拼接工牌到 WhatsApp...")
    allowed_dir = Path.home() / ".openclaw" / "workspace" / "output"
    allowed_dir.mkdir(parents=True, exist_ok=True)
    
    import shutil
    dst = allowed_dir / "multi_worker_badges.png"
    shutil.copy2(multi_badge_path, dst)
    
    # 使用 openclaw CLI 发送
    send_cmd = [
        "openclaw", "message", "send",
        "--channel", "whatsapp",
        "--target", "+8618009073880",
        "--media", str(dst),
        "--message", f"🎫 多 Worker 任务工牌 ({len(workers)}个)\n任务: 并行研究 MCP/QMD/Session\n点击放大查看各Worker任务详情"
    ]
    try:
        subprocess.run(send_cmd, capture_output=True, text=True, timeout=30)
        print("✅ 拼接工牌已发送!")
    except Exception as e:
        print(f"📱 发送命令: {' '.join(send_cmd)}")
    
    # ========== Phase 2: 并行启动 Workers ==========
    print("\n🔄 Phase 2: 并行启动 Workers")
    
    for w in workers:
        print(f"\n  📤 Spawning {w['name']}...")
        print(f"     Ticket: {w['ticket']}")
        print(f"     Target: {w['url']}")
        # 实际使用时调用 sessions_spawn
        # sessions_spawn(task=..., label=w['name'])
    
    # ========== Phase 3: 等待 Workers 完成 ==========
    print("\n⏳ Phase 3: 等待所有 Workers 完成...")
    print("   (实际场景中，等待所有子代理返回)")
    
    # ========== Phase 4: 创建 Reviewer 任务 ==========
    print("\n🔍 Phase 4: 创建 Reviewer 汇总任务")
    
    reviewer_ticket, reviewer_task = lifecycle.create_task(
        agent_name="Reviewer-Master",
        task_desc="汇总三个Worker的研究报告，生成综合分析与对比",
        role="reviewer",
        output_requirements=["综合分析.md", "对比图表.png", "执行摘要.json"],
        deadline_days=1
    )
    
    print(f"\n✅ Reviewer 任务已创建")
    print(f"   Ticket: {reviewer_ticket}")
    
    # ========== Phase 5: 输出工作流信息 ==========
    print("\n" + "=" * 60)
    print("📊 工作流摘要")
    print("=" * 60)
    
    workflow = {
        "workflow_id": f"WF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "workers": workers,
        "reviewer": {
            "name": "Reviewer-Master",
            "ticket": reviewer_ticket
        },
        "status": "pending"
    }
    
    for i, w in enumerate(workers, 1):
        print(f"\n  Worker-{i}: {w['name']}")
        print(f"    🎫 {w['ticket']}")
        print(f"    🌐 {w['url']}")
    
    print(f"\n  Reviewer: Reviewer-Master")
    print(f"    🎫 {reviewer_ticket}")
    
    print("\n" + "=" * 60)
    print("💡 使用命令:")
    print("=" * 60)
    print("\n# 启动 Workers:")
    for w in workers:
        print(f"sessions_spawn(task='研究 {w['url']}', label='{w['name']}')")
    
    print("\n# Workers 完成后，验证交付物:")
    for w in workers:
        print(f"fis_lifecycle verify --ticket-id {w['ticket']}")
    
    print("\n# 完成 Workers:")
    for w in workers:
        print(f"fis_lifecycle complete --ticket-id {w['ticket']}")
    
    print("\n# 启动 Reviewer:")
    print(f"sessions_spawn(task='汇总分析', label='Reviewer-Master')")
    
    print("\n# 完成 Reviewer:")
    print(f"fis_lifecycle complete --ticket-id {reviewer_ticket}")
    
    return workflow


if __name__ == "__main__":
    from datetime import datetime
    workflow = multi_worker_workflow()
