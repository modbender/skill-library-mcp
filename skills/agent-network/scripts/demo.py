#!/usr/bin/env python3
"""
Agent 群聊协作系统 - 完整演示脚本
展示所有核心功能
"""

import os
import sys
import time

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_manager import AgentManager, init_default_agents
from message_manager import MessageManager
from group_manager import GroupManager
from task_manager import TaskManager, TaskStatus
from decision_manager import DecisionManager, DecisionStatus, VoteType
from coordinator import get_coordinator


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """打印小节标题"""
    print(f"\n▶ {title}")
    print("-" * 50)


def demo():
    """运行演示"""
    
    print_header("🤖 Agent 群聊协作系统 v1.0 - 功能演示")
    
    print("""
本演示将展示系统的核心功能:
  1️⃣  Agent 管理与上线
  2️⃣  群组创建与加入
  3️⃣  消息发送与 @提及
  4️⃣  任务指派与跟踪
  5️⃣  决策提议与投票
  6️⃣  收件箱与通知
    """)
    
    input("\n按 Enter 开始演示...")
    
    # 初始化
    init_default_agents()
    coordinator = get_coordinator()
    coordinator.start()
    
    time.sleep(0.5)
    
    # ========== 1. Agent 管理 ==========
    print_header("1️⃣  Agent 管理")
    
    print_section("所有 Agent 列表")
    agents = AgentManager.get_all()
    for agent in agents:
        print(f"  ⚪ {agent.name} - {agent.role}")
    
    print_section("Agent 上线")
    lao_xing = AgentManager.get_by_name("老邢")
    xiao_xing = AgentManager.get_by_name("小邢")
    xiao_jin = AgentManager.get_by_name("小金")
    xiao_chen = AgentManager.get_by_name("小陈")
    xiao_ying = AgentManager.get_by_name("小影")
    
    for agent in [lao_xing, xiao_xing, xiao_jin, xiao_chen, xiao_ying]:
        if agent:
            coordinator.register_agent(agent.id)
            time.sleep(0.2)
    
    print_section("在线 Agent 列表")
    online = AgentManager.get_online_agents()
    for agent in online:
        print(f"  🟢 {agent.name} - {agent.role}")
    
    time.sleep(1)
    
    # ========== 2. 群组管理 ==========
    print_header("2️⃣  群组管理")
    
    print_section("创建工作群组")
    if lao_xing:
        group = GroupManager.create("核心工作群", lao_xing.id, "核心团队工作沟通")
        if group:
            print(f"  ✅ 群组 '{group.name}' 创建成功")
            
            # 添加成员
            for agent in [xiao_xing, xiao_jin, xiao_chen, xiao_ying]:
                if agent:
                    GroupManager.add_member(group.id, agent.id)
                    print(f"  ✅ {agent.name} 加入群组")
    else:
        group = GroupManager.get_by_name("核心工作群")
    
    print_section("群组列表")
    groups = GroupManager.get_all()
    for g in groups:
        member_count = GroupManager.get_member_count(g.id)
        print(f"  📁 {g.name} - {member_count} 成员")
    
    print_section("群组成员")
    if group:
        members = GroupManager.get_members(group.id)
        print(f"  '{group.name}' 成员:")
        for member in members:
            status = "🟢" if member.status == "online" else "⚪"
            print(f"    {status} {member.name} ({member.role})")
    
    time.sleep(1)
    
    # ========== 3. 消息功能 ==========
    print_header("3️⃣  消息功能")
    
    print_section("发送普通消息")
    if lao_xing and group:
        msg1 = coordinator.send_message(
            from_agent_id=lao_xing.id,
            content="大家好！今天我们来讨论一下本周的工作安排。",
            group_id=group.id
        )
        if msg1:
            print(f"  💬 老邢: {msg1.content}")
    
    time.sleep(0.5)
    
    print_section("@提及功能")
    if lao_xing and group:
        msg2 = coordinator.send_message(
            from_agent_id=lao_xing.id,
            content="@小邢 请汇报一下服务器状态，@小金 准备一下市场分析报告。",
            group_id=group.id
        )
        if msg2:
            print(f"  💬 老邢: {msg2.content}")
            print(f"  📢 检测到 @提及，已通知相关 Agent")
    
    time.sleep(0.5)
    
    print_section("群聊回复")
    if xiao_xing and group:
        msg3 = coordinator.send_message(
            from_agent_id=xiao_xing.id,
            content="@老邢 服务器运行正常，负载在20%左右，一切稳定。",
            group_id=group.id
        )
        if msg3:
            print(f"  💬 小邢: {msg3.content}")
    
    if xiao_jin and group:
        msg4 = coordinator.send_message(
            from_agent_id=xiao_jin.id,
            content="@老邢 市场分析正在整理中，预计下午完成。",
            group_id=group.id
        )
        if msg4:
            print(f"  💬 小金: {msg4.content}")
    
    time.sleep(1)
    
    # ========== 4. 任务管理 ==========
    print_header("4️⃣  任务管理")
    
    print_section("指派任务")
    tasks_created = []
    
    if lao_xing and xiao_jin and group:
        task1 = coordinator.assign_task(
            title="撰写市场分析报告",
            description="分析本周美股市场走势，重点关注科技股板块",
            assigner_id=lao_xing.id,
            assignee_id=xiao_jin.id,
            group_id=group.id,
            priority="high"
        )
        if task1:
            print(f"  ✅ 任务创建: {task1['task_id']}")
            print(f"     标题: {task1['title']}")
            print(f"     指派给: {task1['assignee_name']}")
            print(f"     优先级: {task1['priority']}")
            tasks_created.append(task1)
    
    time.sleep(0.3)
    
    if lao_xing and xiao_xing and group:
        task2 = coordinator.assign_task(
            title="系统安全扫描",
            description="对生产环境进行安全漏洞扫描",
            assigner_id=lao_xing.id,
            assignee_id=xiao_xing.id,
            group_id=group.id,
            priority="urgent"
        )
        if task2:
            print(f"  ✅ 任务创建: {task2['task_id']}")
            print(f"     标题: {task2['title']}")
            print(f"     指派给: {task2['assignee_name']}")
            print(f"     优先级: {task2['priority']}")
            tasks_created.append(task2)
    
    if lao_xing and xiao_chen and group:
        task3 = coordinator.assign_task(
            title="优化交易策略",
            description="根据最新市场数据优化自动交易策略参数",
            assigner_id=lao_xing.id,
            assignee_id=xiao_chen.id,
            group_id=group.id,
            priority="normal"
        )
        if task3:
            print(f"  ✅ 任务创建: {task3['task_id']}")
            print(f"     标题: {task3['title']}")
            print(f"     指派给: {task3['assignee_name']}")
            tasks_created.append(task3)
    
    print_section("任务列表")
    tasks = TaskManager.get_all()
    print(f"  {'任务ID':20} {'标题':22} {'状态':12} {'执行者'}")
    print("  " + "-" * 65)
    
    status_emoji = {
        TaskStatus.PENDING: "⏳",
        TaskStatus.IN_PROGRESS: "🔄",
        TaskStatus.COMPLETED: "✅",
        TaskStatus.CANCELLED: "❌"
    }
    
    for task in tasks:
        emoji = status_emoji.get(task.status, "❓")
        title = task.title[:20] + ".." if len(task.title) > 22 else task.title
        print(f"  {task.task_id:20} {title:22} {emoji} {task.status:10} {task.assignee_name}")
    
    time.sleep(1)
    
    print_section("开始执行任务")
    if tasks_created:
        task = TaskManager.get_by_task_id(tasks_created[0]['task_id'])
        if task and xiao_jin:
            TaskManager.update_status(task.task_id, TaskStatus.IN_PROGRESS, xiao_jin.id, "开始分析报告")
            print(f"  🔄 任务 {task.task_id} 状态更新为: 进行中")
    
    print_section("完成任务")
    if tasks_created and xiao_jin:
        result = coordinator.complete_task(
            task_id=tasks_created[0]['task_id'],
            agent_id=xiao_jin.id,
            result="报告已完成！科技股本周上涨3.2%，新能源板块表现突出。"
        )
        if result:
            print(f"  ✅ 任务 {tasks_created[0]['task_id']} 已完成")
    
    time.sleep(1)
    
    # ========== 5. 决策管理 ==========
    print_header("5️⃣  决策管理")
    
    print_section("提出决策")
    if lao_xing and group:
        decision = coordinator.propose_decision(
            title="是否升级服务器配置",
            description="当前服务器负载接近80%，建议升级配置以应对业务增长。预算约10万元。",
            proposer_id=lao_xing.id,
            group_id=group.id
        )
        if decision:
            print(f"  ✅ 决策提议: {decision['decision_id']}")
            print(f"     标题: {decision['title']}")
            print(f"     状态: {decision['status']}")
    
    time.sleep(0.5)
    
    print_section("投票")
    if decision:
        # 小邢投票赞成
        if xiao_xing:
            coordinator.vote_decision(
                decision_id=decision['decision_id'],
                agent_id=xiao_xing.id,
                vote="for",
                comment="同意升级，现在负载确实偏高，升级能提升稳定性"
            )
            print(f"  🗳️  小邢 投票: 👍 赞成")
        
        time.sleep(0.2)
        
        # 小金投票赞成
        if xiao_jin:
            coordinator.vote_decision(
                decision_id=decision['decision_id'],
                agent_id=xiao_jin.id,
                vote="for",
                comment="支持升级，业务增长需要更好的基础设施"
            )
            print(f"  🗳️  小金 投票: 👍 赞成")
        
        time.sleep(0.2)
        
        # 小陈投票反对
        if xiao_chen:
            coordinator.vote_decision(
                decision_id=decision['decision_id'],
                agent_id=xiao_chen.id,
                vote="against",
                comment="建议先优化代码和缓存策略，目前还有优化空间"
            )
            print(f"  🗳️  小陈 投票: 👎 反对")
    
    print_section("决策状态")
    if decision:
        updated = DecisionManager.get_by_decision_id(decision['decision_id'])
        if updated:
            print(f"  📊 {updated.title}")
            print(f"     赞成: {updated.votes_for} 票")
            print(f"     反对: {updated.votes_against} 票")
            print(f"     通过率: {updated.pass_rate:.1f}%")
    
    time.sleep(0.5)
    
    print_section("结束决策")
    if decision:
        final = coordinator.finalize_decision(decision['decision_id'])
        if final:
            result_text = "✅ 通过" if final['status'] == DecisionStatus.APPROVED else "❌ 未通过"
            print(f"  {result_text}")
            print(f"     最终状态: {final['status']}")
    
    time.sleep(1)
    
    # ========== 6. 收件箱与历史 ==========
    print_header("6️⃣  收件箱与消息历史")
    
    print_section("消息历史")
    if group:
        messages = MessageManager.get_group_messages(group.id, limit=10)
        print(f"  💬 '{group.name}' 最近消息:")
        print("  " + "-" * 60)
        
        for msg in reversed(messages[-5:]):  # 最近5条
            from_name = msg.from_agent_name or f"Agent-{msg.from_agent_id}"
            content = msg.content[:45]
            print(f"    [{from_name:8}] {content}...")
    
    print_section("任务统计")
    task_stats = TaskManager.get_statistics()
    print(f"  总任务: {task_stats['total']}")
    print(f"  ⏳ 待处理: {task_stats['pending']}")
    print(f"  🔄 进行中: {task_stats['in_progress']}")
    print(f"  ✅ 已完成: {task_stats['completed']}")
    
    print_section("决策统计")
    decision_stats = DecisionManager.get_statistics()
    print(f"  总决策: {decision_stats['total']}")
    print(f"  📝 提议中: {decision_stats['proposed']}")
    print(f"  💬 讨论中: {decision_stats['discussing']}")
    print(f"  ✅ 已通过: {decision_stats['approved']}")
    print(f"  ❌ 已拒绝: {decision_stats['rejected']}")
    
    # 结束
    print_header("✨ 演示完成")
    
    print("""
演示结束！系统的核心功能都已展示：

  ✅ Agent 管理与在线状态
  ✅ 群组创建与成员管理  
  ✅ 消息发送与 @提及通知
  ✅ 任务指派、进度跟踪、完成
  ✅ 决策提议、投票、结果统计
  ✅ 消息历史与统计信息

接下来你可以：
  1. 运行 'python chat.py' 进入交互式 CLI 体验
  2. 运行 'python main.py' 使用命令行工具
  3. 查看 README.md 了解更多使用方法
    """)
    
    coordinator.stop()


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n演示已取消")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
