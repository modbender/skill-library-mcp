#!/usr/bin/env python3
"""
Semantic Router Setup Wizard - 模型池智能配置向导
步骤：
  0. 帮助用户定义任务类型
  1. 扫描用户已有模型
  2. 建议模型池配置及与任务类型的匹配
  3. 用户修改模型池配置并确认
"""

import json
import os
import sys
from pathlib import Path

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}▶ {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─'*50}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

# 步骤 0: 定义任务类型
def step0_define_task_types():
    print_section("步骤 0: 定义您的任务类型")
    
    print("\n请定义您的主要任务类型。例如：")
    print("  1. 代码开发 (development)")
    print("  2. 信息检索 (info_retrieval)")
    print("  3. 内容创作 (content_generation)")
    print("  4. 数据分析 (data_analysis)")
    print("  5. 系统运维 (system_ops)")
    print("  6. 其他 (请自定义)")
    
    task_types = []
    print(f"\n{Colors.BLUE}输入任务类型，每行一个，空行结束：{Colors.ENDC}")
    
    while True:
        task = input(f"{Colors.CYAN}  任务类型: {Colors.ENDC}").strip()
        if not task:
            break
        task_types.append(task)
    
    if not task_types:
        # 默认任务类型
        task_types = [
            "development",
            "info_retrieval",
            "content_generation"
        ]
        print_warning("使用默认任务类型")
    
    print_success(f"已定义 {len(task_types)} 个任务类型")
    return task_types

# 步骤 1: 扫描已有模型
def step1_scan_models():
    print_section("步骤 1: 扫描可用模型")
    
    # 从 openclaw.json 读取可用模型
    openclaw_home = Path.home() / '.openclaw'
    config_file = openclaw_home / 'openclaw.json'
    
    available_models = []
    
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
            # 尝试从配置中提取模型列表
            if 'auth' in config and 'profiles' in config['auth']:
                for provider, profiles in config['auth']['profiles'].items():
                    for profile_name in profiles.keys():
                        available_models.append(f"{provider}:{profile_name}")
        except Exception as e:
            print_warning(f"读取配置失败: {e}")
    
    # 如果没有找到，使用常见模型列表
    if not available_models:
        print_warning("从配置文件未找到模型，使用推荐列表")
        available_models = [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai-codex/gpt-5.3-codex",
            "kimi-coding/k2p5",
            "zai/glm-5",
            "lovbrowser/claude-opus-4.6",
            "lovbrowser/claude-haiku-4.5",
            "lovbrowser/claude-sonnet-4.6",
            "google/gemini-2.5-pro",
            "google/gemini-2.5-flash"
        ]
    
    print(f"\n{Colors.BLUE}发现的可用模型:{Colors.ENDC}")
    for i, model in enumerate(available_models, 1):
        print(f"  {i}. {model}")
    
    print_success(f"共发现 {len(available_models)} 个模型")
    return available_models

# 步骤 2: 建议模型池配置
def step2_suggest_pools(task_types, available_models):
    print_section("步骤 2: 智能建议模型池配置")
    
    # 默认池配置模板
    default_pools = {
        "Intelligence": {
            "name": "智能池",
            "description": "代码开发、系统运维、自动化任务",
            "suitable_for": ["development", "system_ops", "automation"],
            "primary": None,
            "fallback_1": None,
            "fallback_2": None
        },
        "Highspeed": {
            "name": "高速池", 
            "description": "信息检索、快速查询、协调沟通",
            "suitable_for": ["info_retrieval", "coordination", "search"],
            "primary": None,
            "fallback_1": None,
            "fallback_2": None
        },
        "Humanities": {
            "name": "人文池",
            "description": "内容创作、教育培训、多模态识别",
            "suitable_for": ["content_generation", "training", "multimodal"],
            "primary": None,
            "fallback_1": None,
            "fallback_2": None
        }
    }
    
    # 模型推荐映射
    model_recommendations = {
        "Intelligence": ["openai-codex/gpt-5.3-codex", "lovbrowser/claude-opus-4.6", "kimi-coding/k2p5"],
        "Highspeed": ["openai/gpt-4o-mini", "lovbrowser/claude-haiku-4.5", "google/gemini-2.5-flash"],
        "Humanities": ["openai/gpt-4o", "lovbrowser/claude-sonnet-4.6", "google/gemini-2.5-pro"]
    }
    
    suggested_pools = {}
    
    for pool_name, pool_config in default_pools.items():
        print(f"\n{Colors.BOLD}{pool_name} - {pool_config['name']}{Colors.ENDC}")
        print(f"  适用: {', '.join(pool_config['suitable_for'])}")
        
        # 从可用模型中匹配合适的
        recommended = model_recommendations.get(pool_name, [])
        matched = [m for m in recommended if m in available_models]
        
        # 填充建议
        suggested_pools[pool_name] = {
            "name": pool_config["name"],
            "description": pool_config["description"],
            "primary": matched[0] if len(matched) > 0 else available_models[0] if available_models else None,
            "fallback_1": matched[1] if len(matched) > 1 else available_models[1] if len(available_models) > 1 else None,
            "fallback_2": matched[2] if len(matched) > 2 else available_models[2] if len(available_models) > 2 else None
        }
        
        print(f"  {Colors.GREEN}建议配置:{Colors.ENDC}")
        print(f"    Primary: {suggested_pools[pool_name]['primary']}")
        print(f"    Fallback 1: {suggested_pools[pool_name]['fallback_1']}")
        print(f"    Fallback 2: {suggested_pools[pool_name]['fallback_2']}")
    
    return suggested_pools

# 步骤 3: 用户修改并确认
def step3_user_modify(suggested_pools, available_models):
    print_section("步骤 3: 修改并确认模型池配置")
    
    print(f"\n{Colors.BLUE}当前建议配置:{Colors.ENDC}")
    print(json.dumps(suggested_pools, ensure_ascii=False, indent=2))
    
    print(f"\n{Colors.WARNING}您可以修改配置。格式: 池名 字段 值{Colors.ENDC}")
    print("字段: primary, fallback_1, fallback_2, description")
    print("或输入 'done' 完成，'reset' 重置为建议值")
    
    final_pools = suggested_pools.copy()
    
    while True:
        user_input = input(f"\n{Colors.CYAN}> {Colors.ENDC}").strip()
        
        if user_input.lower() == 'done':
            break
        elif user_input.lower() == 'reset':
            final_pools = suggested_pools.copy()
            print_success("已重置为建议值")
            continue
        
        parts = user_input.split(maxsplit=2)
        if len(parts) == 3:
            pool_name, field, value = parts
            if pool_name in final_pools and field in ['primary', 'fallback_1', 'fallback_2', 'description', 'name']:
                final_pools[pool_name][field] = value
                print_success(f"已更新: {pool_name}.{field} = {value}")
            else:
                print_warning("无效的池名或字段")
        else:
            print_warning("格式错误。示例: Intelligence primary openai/gpt-4o")
    
    print_section("最终确认")
    print(json.dumps(final_pools, ensure_ascii=False, indent=2))
    
    confirm = input(f"\n{Colors.CYAN}确认保存此配置? (y/n): {Colors.ENDC}").strip().lower()
    
    if confirm == 'y':
        return final_pools
    else:
        print_warning("配置未保存")
        return None

# 保存配置
def save_config(pools, task_types):
    print_section("保存配置")
    
    config_dir = Path.home() / '.openclaw' / 'workspace' / 'skills' / 'semantic-router' / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存 pools.json
    pools_file = config_dir / 'pools.json'
    with open(pools_file, 'w', encoding='utf-8') as f:
        json.dump(pools, f, ensure_ascii=False, indent=2)
    print_success(f"已保存: {pools_file}")
    
    # 生成 tasks.json
    tasks_config = {}
    for task in task_types:
        # 智能匹配到合适的池
        if any(kw in task.lower() for kw in ['开发', '代码', '编程', 'debug']):
            pool = "Intelligence"
        elif any(kw in task.lower() for kw in ['搜索', '查询', '检索', '找']):
            pool = "Highspeed"
        elif any(kw in task.lower() for kw in ['写作', '创作', '内容', '文章']):
            pool = "Humanities"
        else:
            pool = "Highspeed"  # 默认
        
        tasks_config[task] = {
            "pool": pool,
            "keywords": [task]
        }
    
    tasks_file = config_dir / 'tasks.json'
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks_config, f, ensure_ascii=False, indent=2)
    print_success(f"已保存: {tasks_file}")
    
    return pools_file, tasks_file

def main():
    print_header("SEMANTIC ROUTER 模型池配置向导")
    
    # 步骤 0: 定义任务类型
    task_types = step0_define_task_types()
    
    # 步骤 1: 扫描模型
    available_models = step1_scan_models()
    
    # 步骤 2: 建议配置
    suggested_pools = step2_suggest_pools(task_types, available_models)
    
    # 步骤 3: 用户修改确认
    final_pools = step3_user_modify(suggested_pools, available_models)
    
    if final_pools:
        # 保存配置
        pools_file, tasks_file = save_config(final_pools, task_types)
        
        print_header("配置完成")
        print(f"{Colors.GREEN}您的语义路由配置已就绪！{Colors.ENDC}")
        print(f"\n配置文件:")
        print(f"  - {pools_file}")
        print(f"  - {tasks_file}")
        print(f"\n{Colors.BLUE}使用方法:{Colors.ENDC}")
        print(f"  python3 semantic_check.py \"您的消息\" \"当前池\"")
    else:
        print_warning("配置已取消")
        return 1
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}已取消{Colors.ENDC}")
        sys.exit(130)
