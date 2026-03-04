#!/usr/bin/env python3
"""
Agent Optimizer - 趋势分析脚本

用法:
    python3 analyze_trends.py --agent <agent_id> [--days <num_days>]
"""

import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

def load_trajectories(agent_id):
    """加载轨迹数据"""
    trajectories = []
    try:
        with open(f'/workspace/subagents/{agent_id}/optimizer/trajectories.jsonl', 'r') as f:
            for line in f:
                trajectories.append(json.loads(line))
    except FileNotFoundError:
        print(f"未找到轨迹文件：/workspace/subagents/{agent_id}/optimizer/trajectories.jsonl")
    return trajectories

def load_rewards(agent_id):
    """加载奖励数据"""
    rewards = []
    try:
        with open(f'/workspace/subagents/{agent_id}/optimizer/rewards.jsonl', 'r') as f:
            for line in f:
                rewards.append(json.loads(line))
    except FileNotFoundError:
        print(f"未找到奖励文件：/workspace/subagents/{agent_id}/optimizer/rewards.jsonl")
    return rewards

def analyze_trends(agent_id, days=7):
    """分析奖励趋势"""
    trajectories = load_trajectories(agent_id)
    rewards = load_rewards(agent_id)
    
    if not trajectories or not rewards:
        print("数据不足，无法分析")
        return
    
    # 按日期分组奖励
    daily_rewards = defaultdict(list)
    for reward in rewards:
        date = reward['timestamp'][:10]  # YYYY-MM-DD
        daily_rewards[date].append(reward['reward_value'])
    
    # 计算每日平均奖励
    print(f"\n{'='*60}")
    print(f"Agent: {agent_id}")
    print(f"分析周期：最近 {days} 天")
    print(f"{'='*60}\n")
    
    print("每日平均奖励趋势:")
    print("-" * 40)
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    for date in sorted(daily_rewards.keys()):
        if date >= cutoff_date:
            avg_reward = sum(daily_rewards[date]) / len(daily_rewards[date])
            print(f"{date}: {avg_reward:.2f} ({len(daily_rewards[date])} 条)")
    
    # 总体统计
    total_avg = sum(r['reward_value'] for r in rewards) / len(rewards)
    print(f"\n{'='*60}")
    print(f"总体统计:")
    print(f"  总轨迹数：{len(trajectories)}")
    print(f"  总奖励数：{len(rewards)}")
    print(f"  平均奖励：{total_avg:.2f}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='分析 Agent 性能趋势')
    parser.add_argument('--agent', required=True, help='Agent ID')
    parser.add_argument('--days', type=int, default=7, help='分析天数')
    
    args = parser.parse_args()
    analyze_trends(args.agent, args.days)
