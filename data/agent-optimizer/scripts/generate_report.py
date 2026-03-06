#!/usr/bin/env python3
"""
Agent Optimizer - 生成优化报告

用法:
    python3 generate_report.py --agent <agent_id>
"""

import json
import argparse
from datetime import datetime

def load_data(agent_id):
    """加载轨迹和奖励数据"""
    trajectories = []
    rewards = []
    
    try:
        with open(f'/workspace/subagents/{agent_id}/optimizer/trajectories.jsonl', 'r') as f:
            for line in f:
                trajectories.append(json.loads(line))
    except FileNotFoundError:
        pass
    
    try:
        with open(f'/workspace/subagents/{agent_id}/optimizer/rewards.jsonl', 'r') as f:
            for line in f:
                rewards.append(json.loads(line))
    except FileNotFoundError:
        pass
    
    return trajectories, rewards

def generate_report(agent_id):
    """生成优化报告"""
    trajectories, rewards = load_data(agent_id)
    
    if not trajectories:
        print("无轨迹数据，无法生成报告")
        return
    
    # 计算基本统计
    total_trajectories = len(trajectories)
    total_rewards = len(rewards)
    avg_reward = sum(r['reward_value'] for r in rewards) / total_rewards if total_rewards > 0 else 0
    
    # 按任务类型分组
    task_stats = defaultdict(lambda: {'count': 0, 'rewards': []})
    for traj in trajectories:
        task_type = traj.get('task', 'unknown')[:50]  # 截断长任务名
        task_stats[task_type]['count'] += 1
    
    for reward in rewards:
        # 简单匹配，实际应该用 trajectory_id
        pass
    
    # 生成报告
    report = {
        "agent_id": agent_id,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_trajectories": total_trajectories,
            "total_rewards": total_rewards,
            "average_reward": round(avg_reward, 2)
        },
        "task_breakdown": dict(task_stats),
        "suggestions": []
    }
    
    # 生成建议
    if avg_reward < 3.0:
        report["suggestions"].append("平均奖励较低，建议检查提示词或任务难度")
    if total_trajectories < 10:
        report["suggestions"].append("数据量不足，建议收集更多轨迹")
    if total_rewards < total_trajectories * 0.5:
        report["suggestions"].append("奖励反馈率低，建议增加反馈收集")
    
    # 保存报告
    report_path = f'/workspace/subagents/{agent_id}/optimizer/optimization_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"优化报告已保存：{report_path}")
    print(f"\n摘要:")
    print(f"  轨迹数：{total_trajectories}")
    print(f"  奖励数：{total_rewards}")
    print(f"  平均奖励：{avg_reward:.2f}")
    
    if report["suggestions"]:
        print(f"\n建议:")
        for suggestion in report["suggestions"]:
            print(f"  - {suggestion}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成 Agent 优化报告')
    parser.add_argument('--agent', required=True, help='Agent ID')
    
    args = parser.parse_args()
    generate_report(args.agent)
