#!/usr/bin/env python3
"""
Generate raw data/text for LLM cost monitoring
"""
import os
import sys
from datetime import datetime, timedelta

# Find store.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import UsageStore

def fmt_cost(c):
    return f"${c:.2f}"

def fmt_tokens(t):
    if t >= 1000000:
        return f"{t/1000000:.1f}M"
    elif t >= 1000:
        return f"{t/1000:.1f}K"
    return str(t)

def main():
    store = UsageStore()
    today = datetime.now()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    daily_data = store.get_usage(start_date, end_date)
    total_cost = store.get_total_cost(start_date, end_date)
    by_model = store.get_cost_by_model(start_date, end_date)
    
    # Total tokens
    total_tokens = sum(r['input_tokens'] + r['output_tokens'] for r in daily_data)
    
    # By model tokens
    by_model_tokens = {}
    for r in daily_data:
        m = r['model']
        if m not in by_model_tokens: by_model_tokens[m] = 0
        by_model_tokens[m] += r['input_tokens'] + r['output_tokens']

    print(f"📊 本月用量报告 ({start_date} ~ {end_date})")
    print(f"总消耗: {fmt_cost(total_cost)} (约 {fmt_tokens(total_tokens)} tokens)")
    print("-" * 20)
    print("模型分布 (Top 5):")
    
    sorted_models = sorted(by_model.keys(), key=lambda x: -by_model[x])[:5]
    for model in sorted_models:
        cost = by_model[model]
        tokens = by_model_tokens.get(model, 0)
        print(f"- {model[:15]}: {fmt_cost(cost)} ({fmt_tokens(tokens)})")
        
if __name__ == "__main__":
    main()
