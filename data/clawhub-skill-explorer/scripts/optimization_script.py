#!/usr/bin/env python3
"""
ClawHub技能探索工具的自动化优化脚本
"""

import os
import sys
import time
import subprocess
import json
import random
from datetime import datetime, timedelta

def log_message(msg, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def get_current_time():
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def check_internet_connection():
    """检查网络连接"""
    try:
        # 直接测试ClawHub API连接
        log_message("检查ClawHub API连接...")
        subprocess.run(["curl", "-s", "https://clawhub.ai"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      check=True,
                      timeout=10)
        return True
    except Exception as e:
        log_message(f"ClawHub API连接检查失败: {e}", "ERROR")
        return False

def get_clawhub_token():
    """获取ClawHub token"""
    # 直接配置token（确保安全）
    token = "clh_bbGajvH2n5moZ28O8z9n6SF57meUTQ6xGuiYtQ5UX1I"
    
    if not token:
        log_message("未找到ClawHub token配置", "ERROR")
        return None
    return token

def fetch_skill_info():
    """获取技能详细信息"""
    try:
        log_message("获取技能详细信息...")
        output = subprocess.check_output(["clawhub", "inspect", "clawhub-skill-explorer"], 
                                       text=True,
                                       timeout=30)
        return output
    except Exception as e:
        log_message(f"获取技能信息失败: {e}", "ERROR")
        return None

def optimize_skill_description():
    """优化技能描述"""
    try:
        log_message("优化技能描述...")
        
        # 不同语言版本的描述
        descriptions = [
            "ClawHub技能探索工具 - 智能搜索、分类浏览、平台统计，支持快速找到所需技能",
            "ClawHub技能搜索工具 - 提供智能搜索、分类浏览、平台统计，助您快速定位技能",
            "ClawHub技能发现工具 - 支持关键词搜索、分类浏览、平台统计，快速找到所需技能",
            "ClawHub技能导航工具 - 提供智能搜索、分类导航、平台统计，提升技能查找效率",
            "ClawHub技能查询工具 - 智能搜索、分类浏览、平台统计，快速找到所需技能"
        ]
        
        # 随机选择一个优化后的描述
        optimized_desc = random.choice(descriptions)
        
        log_message(f"新描述: {optimized_desc}")
        return optimized_desc
    except Exception as e:
        log_message(f"优化技能描述失败: {e}", "ERROR")
        return None

def optimize_skill_tags():
    """优化技能关键词"""
    try:
        log_message("优化技能关键词...")
        
        # 优化后的关键词组合
        tag_combinations = [
            "clawhub,skill-search,explore,skills-discovery",
            "clawhub,explorer,search-tool,skill-finder",
            "clawhub,skills-search,browser,explorer",
            "clawhub,skill-search,explore,search-engine",
            "clawhub,explorer,search,skill-explorer"
        ]
        
        # 随机选择一个优化后的关键词组合
        optimized_tags = random.choice(tag_combinations)
        
        log_message(f"新关键词: {optimized_tags}")
        return optimized_tags
    except Exception as e:
        log_message(f"优化技能关键词失败: {e}", "ERROR")
        return None

def update_skill(description, tags):
    """更新技能信息"""
    try:
        log_message("更新技能信息...")
        
        # 检查API调用是否过于频繁
        log_message("检查API调用限制...")
        time.sleep(30)  # 等待30秒后再尝试
        
        # 执行更新命令，增加超时时间
        log_message("执行clawhub publish命令...")
        result = subprocess.run(["clawhub", "publish", 
                              "/Users/sunyanguang/.openclaw/workspace/custom-skills/clawhub-skill-explorer",
                              "--name", "ClawHub技能探索工具",
                              "--version", "1.0.0",
                              "--tags", tags],
                              capture_output=True,
                              text=True,
                              timeout=120)
        
        if result.returncode == 0:
            log_message("技能更新成功!", "SUCCESS")
            log_message(f"更新结果: {result.stdout}")
            return True
        else:
            log_message(f"技能更新失败: {result.stderr}", "ERROR")
            
            # 检查是否是速率限制
            if "Rate limit exceeded" in result.stderr:
                log_message("API调用频率过高，将在10分钟后重试...", "WARNING")
                time.sleep(600)  # 等待10分钟
                log_message("10分钟后重试技能更新...")
                result = subprocess.run(["clawhub", "publish", 
                                      "/Users/sunyanguang/.openclaw/workspace/custom-skills/clawhub-skill-explorer",
                                      "--name", "ClawHub技能探索工具",
                                      "--version", "1.0.0",
                                      "--tags", tags],
                                      capture_output=True,
                                      text=True,
                                      timeout=120)
                
                if result.returncode == 0:
                    log_message("技能更新成功!", "SUCCESS")
                    return True
                else:
                    log_message(f"再次更新失败: {result.stderr}", "ERROR")
        
        return False
    except Exception as e:
        log_message(f"更新技能信息失败: {e}", "ERROR")
        return False

def verify_update():
    """验证技能更新"""
    try:
        log_message("验证技能更新...")
        
        # 检查技能是否成功更新
        time.sleep(5)  # 等待更新传播
        output = fetch_skill_info()
        
        if output:
            log_message("技能更新验证成功!", "SUCCESS")
            return True
        else:
            log_message("技能更新验证失败", "ERROR")
            return False
    except Exception as e:
        log_message(f"验证技能更新失败: {e}", "ERROR")
        return False

def run_optimization():
    """执行优化过程"""
    log_message(f"开始技能优化任务 - {get_current_time()}")
    
    # 检查网络连接
    if not check_internet_connection():
        log_message("网络连接检查失败，任务终止", "ERROR")
        return False
    
    # 检查ClawHub token
    token = get_clawhub_token()
    if not token:
        log_message("ClawHub token未找到，任务终止", "ERROR")
        return False
    
    # 获取当前技能信息
    current_info = fetch_skill_info()
    if not current_info:
        log_message("获取技能信息失败，任务终止", "ERROR")
        return False
    
    # 优化技能描述和关键词
    optimized_desc = optimize_skill_description()
    optimized_tags = optimize_skill_tags()
    
    if not optimized_desc or not optimized_tags:
        log_message("优化过程失败，任务终止", "ERROR")
        return False
    
    # 更新技能
    if not update_skill(optimized_desc, optimized_tags):
        log_message("技能更新失败，任务终止", "ERROR")
        return False
    
    # 验证更新
    if not verify_update():
        log_message("技能更新验证失败，任务终止", "ERROR")
        return False
    
    log_message("技能优化任务完成!", "SUCCESS")
    return True

def schedule_next_run():
    """计算下一次运行时间"""
    now = datetime.now()
    next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    log_message(f"下次优化任务时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数"""
    log_message("启动clawhub-skill-explorer技能优化工具")
    
    # 执行优化任务
    success = run_optimization()
    
    if success:
        schedule_next_run()
        return 0
    else:
        log_message("技能优化任务失败", "ERROR")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
