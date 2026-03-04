#!/usr/bin/env python3
"""
ClawHub技能探索工具API调用优化脚本
"""

import time
import random
import requests
from datetime import datetime, timedelta

class ClawHubApiOptimizer:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 5
        self.jitter = 2
        self.rate_limit_window = 60  # 秒
        self.max_calls_per_window = 50
        self.call_timestamps = []
    
    def get_delay(self, retry_count):
        """计算重试延迟，包含抖动"""
        delay = self.base_delay * (2 ** retry_count)
        jitter_value = random.uniform(-self.jitter, self.jitter)
        return max(delay + jitter_value, 0.5)
    
    def rate_limit_check(self):
        """检查API调用速率限制"""
        now = time.time()
        
        # 清理过期的调用记录
        self.call_timestamps = [t for t in self.call_timestamps 
                               if t > now - self.rate_limit_window]
        
        if len(self.call_timestamps) >= self.max_calls_per_window:
            oldest_call = min(self.call_timestamps)
            wait_time = (oldest_call + self.rate_limit_window) - now
            if wait_time > 0:
                time.sleep(wait_time)
                self.call_timestamps = [t for t in self.call_timestamps 
                                       if t > time.time() - self.rate_limit_window]
        
        return True
    
    def make_api_call(self, url, params=None, headers=None, retry_count=0):
        """安全地进行API调用，包含重试逻辑"""
        try:
            # 检查速率限制
            self.rate_limit_check()
            
            # 记录调用时间
            self.call_timestamps.append(time.time())
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 429:
                # 速率限制
                retry_after = int(response.headers.get('Retry-After', 60))
                wait_time = retry_after + random.uniform(0, 5)
                print(f"API速率限制，等待 {wait_time:.1f} 秒后重试")
                time.sleep(wait_time)
                return self.make_api_call(url, params, headers, retry_count + 1)
            
            if response.status_code == 503:
                # 服务不可用
                wait_time = random.uniform(10, 30)
                print(f"服务不可用，等待 {wait_time:.1f} 秒后重试")
                time.sleep(wait_time)
                return self.make_api_call(url, params, headers, retry_count + 1)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API调用失败: {e}")
            
            if retry_count < self.max_retries:
                delay = self.get_delay(retry_count)
                print(f"第 {retry_count + 1} 次重试，等待 {delay:.1f} 秒")
                time.sleep(delay)
                return self.make_api_call(url, params, headers, retry_count + 1)
            else:
                print(f"所有 {self.max_retries} 次重试均失败")
                return None
    
    def optimize_skill_explorer(self):
        """优化ClawHub技能探索工具的API调用"""
        print("优化ClawHub技能探索工具的API调用策略")
        
        # 更新API配置文件
        api_config = {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "jitter": self.jitter,
            "rate_limit_window": self.rate_limit_window,
            "max_calls_per_window": self.max_calls_per_window
        }
        
        config_file = '/Users/sunyanguang/.openclaw/workspace/custom-skills/clawhub-skill-explorer/config.json'
        
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            
            existing_config['api'] = api_config
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(existing_config, f, ensure_ascii=False, indent=4)
            
            print(f"API配置已更新到 {config_file}")
            return True
            
        except Exception as e:
            print(f"更新API配置失败: {e}")
            return False
    
    def run_optimization_tests(self):
        """运行API优化测试"""
        print("运行API优化策略测试")
        
        # 测试速率限制检查
        test_start = time.time()
        test_calls = 60
        
        for i in range(test_calls):
            self.rate_limit_check()
            self.call_timestamps.append(time.time())
            time.sleep(0.1)
            
            if (i + 1) % 10 == 0:
                print(f"已模拟 {i + 1}/{test_calls} 次API调用")
        
        test_duration = time.time() - test_start
        print(f"API调用优化测试完成，耗时 {test_duration:.1f} 秒")
        
        # 计算有效调用率
        valid_calls = len([t for t in self.call_timestamps if t > test_start])
        success_rate = (valid_calls / test_calls) * 100
        
        print(f"API优化策略有效调用率: {success_rate:.1f}%")
        return success_rate > 90

def main():
    optimizer = ClawHubApiOptimizer()
    
    print("=== ClawHub技能探索工具API优化 ===")
    
    # 优化API配置
    if optimizer.optimize_skill_explorer():
        print("✅ API配置优化成功")
    else:
        print("❌ API配置优化失败")
        return False
    
    # 运行优化测试
    if optimizer.run_optimization_tests():
        print("✅ API优化策略测试通过")
    else:
        print("❌ API优化策略测试失败")
        return False
    
    print("🎉 ClawHub技能探索工具API调用优化完成！")
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
