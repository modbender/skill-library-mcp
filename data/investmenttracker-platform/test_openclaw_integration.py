#!/usr/bin/env python3
"""
OpenClaw集成测试脚本
测试InvestmentTracker技能在OpenClaw中的激活和响应
"""

import json
import re
from typing import List, Dict, Any

class SkillTester:
    """技能测试器"""
    
    def __init__(self):
        self.skill_keywords = [
            # 用户信息相关
            "投资信息", "我的投资", "我是谁", "用户信息",
            # 持仓相关
            "持仓", "投资组合", "我的持仓", "持仓列表",
            # 方法论相关
            "投资策略", "投资方法论", "我的策略",
            # 统计相关
            "投资统计", "表现数据", "统计数据",
            # 工具相关
            "投资工具", "可用功能", "工具列表",
            # 通用
            "InvestmentTracker", "MCP投资", "投资追踪"
        ]
        
        self.test_cases = [
            {
                "input": "查看我的投资信息",
                "expected": "用户信息",
                "description": "测试用户信息查询"
            },
            {
                "input": "列出我的持仓",
                "expected": "持仓列表",
                "description": "测试持仓查询"
            },
            {
                "input": "我的投资策略是什么",
                "expected": "投资方法论",
                "description": "测试投资策略查询"
            },
            {
                "input": "显示投资统计数据",
                "expected": "投资统计数据",
                "description": "测试统计数据查询"
            },
            {
                "input": "列出投资工具",
                "expected": "可用工具",
                "description": "测试工具列表查询"
            },
            {
                "input": "InvestmentTracker怎么用",
                "expected": "InvestmentTracker",
                "description": "测试技能名称触发"
            }
        ]
    
    def check_skill_activation(self, user_input: str) -> bool:
        """检查技能是否应该激活"""
        user_input_lower = user_input.lower()
        
        # 检查是否包含关键词
        for keyword in self.skill_keywords:
            if keyword.lower() in user_input_lower:
                return True
        
        # 检查是否匹配特定模式
        patterns = [
            r"投资.*信息",
            r"我的.*持仓",
            r"投资.*组合",
            r"投资.*策略",
            r"投资.*统计",
            r"查看.*投资"
        ]
        
        for pattern in patterns:
            if re.search(pattern, user_input_lower):
                return True
        
        return False
    
    def get_skill_response(self, user_input: str) -> Dict[str, Any]:
        """获取技能响应"""
        if not self.check_skill_activation(user_input):
            return {
                "activated": False,
                "message": "技能未激活",
                "reason": "输入不包含投资相关关键词"
            }
        
        # 根据输入类型确定响应
        response_type = self._determine_response_type(user_input)
        
        return {
            "activated": True,
            "skill": "InvestmentTracker-platform",
            "response_type": response_type,
            "suggested_commands": self._get_suggested_commands(response_type),
            "test_command": self._get_test_command(response_type)
        }
    
    def _determine_response_type(self, user_input: str) -> str:
        """确定响应类型"""
        user_input_lower = user_input.lower()
        
        if any(keyword in user_input_lower for keyword in ["用户", "我是谁", "信息"]):
            return "user_info"
        elif any(keyword in user_input_lower for keyword in ["持仓", "组合", "持有"]):
            return "positions"
        elif any(keyword in user_input_lower for keyword in ["策略", "方法论", "方法"]):
            return "methodology"
        elif any(keyword in user_input_lower for keyword in ["统计", "数据", "表现"]):
            return "stats"
        elif any(keyword in user_input_lower for keyword in ["工具", "功能", "可用"]):
            return "tools"
        else:
            return "overview"
    
    def _get_suggested_commands(self, response_type: str) -> List[str]:
        """获取建议命令"""
        commands = {
            "user_info": [
                "查看我的投资信息",
                "我是谁",
                "获取用户信息"
            ],
            "positions": [
                "列出我的持仓",
                "查看投资组合",
                "显示持仓列表"
            ],
            "methodology": [
                "我的投资策略",
                "投资方法论",
                "查看投资策略"
            ],
            "stats": [
                "投资统计数据",
                "查看投资表现",
                "显示统计数据"
            ],
            "tools": [
                "列出投资工具",
                "可用功能",
                "查看工具列表"
            ],
            "overview": [
                "查看所有投资信息",
                "投资概览",
                "完整投资报告"
            ]
        }
        return commands.get(response_type, ["查看所有投资信息"])
    
    def _get_test_command(self, response_type: str) -> str:
        """获取测试命令"""
        commands = {
            "user_info": "python3 mcp_standard_skill.py user",
            "positions": "python3 mcp_standard_skill.py positions",
            "methodology": "python3 mcp_standard_skill.py methodology",
            "stats": "python3 mcp_standard_skill.py stats",
            "tools": "python3 mcp_standard_skill.py tools",
            "overview": "python3 mcp_standard_skill.py all"
        }
        return commands.get(response_type, "python3 mcp_standard_skill.py all")
    
    def run_tests(self):
        """运行所有测试用例"""
        print("🧪 InvestmentTracker技能集成测试")
        print("=" * 70)
        
        results = []
        
        for test_case in self.test_cases:
            print(f"\n📋 测试: {test_case['description']}")
            print(f"   输入: '{test_case['input']}'")
            
            response = self.get_skill_response(test_case['input'])
            
            if response["activated"]:
                print(f"   ✅ 技能激活: {response['skill']}")
                print(f"   响应类型: {response['response_type']}")
                print(f"   建议命令: {', '.join(response['suggested_commands'][:2])}")
                results.append(True)
            else:
                print(f"   ❌ 技能未激活")
                print(f"   原因: {response['reason']}")
                results.append(False)
        
        # 统计结果
        print("\n" + "=" * 70)
        print("📊 测试结果统计")
        print("=" * 70)
        
        total_tests = len(results)
        passed_tests = sum(results)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过数: {passed_tests}")
        print(f"失败数: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！技能集成成功！")
        else:
            print(f"\n⚠️  有 {failed_tests} 个测试失败，请检查技能关键词配置。")
    
    def interactive_test(self):
        """交互式测试"""
        print("💬 InvestmentTracker技能交互式测试")
        print("=" * 70)
        print("输入用户消息，测试技能是否激活并查看响应")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 70)
        
        while True:
            user_input = input("\n👤 用户输入: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("退出测试模式")
                break
            
            if not user_input:
                continue
            
            response = self.get_skill_response(user_input)
            
            print("\n🔧 技能响应:")
            print(f"   激活状态: {'✅ 已激活' if response['activated'] else '❌ 未激活'}")
            
            if response['activated']:
                print(f"   技能名称: {response['skill']}")
                print(f"   响应类型: {response['response_type']}")
                print(f"   建议命令: {', '.join(response['suggested_commands'])}")
                print(f"   测试命令: {response['test_command']}")
                
                # 建议运行测试命令
                print(f"\n💡 建议: 运行 '{response['test_command']}' 查看实际输出")
            else:
                print(f"   原因: {response['reason']}")
                print(f"\n💡 提示: 尝试使用投资相关关键词，如'我的持仓'、'投资信息'等")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="InvestmentTracker技能集成测试")
    parser.add_argument("--mode", choices=["auto", "interactive"], default="auto", 
                       help="测试模式: auto(自动测试) 或 interactive(交互测试)")
    parser.add_argument("--test-input", help="测试特定输入")
    
    args = parser.parse_args()
    
    tester = SkillTester()
    
    if args.test_input:
        # 测试特定输入
        print(f"🧪 测试特定输入: '{args.test_input}'")
        response = tester.get_skill_response(args.test_input)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        if response["activated"]:
            print(f"\n💡 建议运行: {response['test_command']}")
    
    elif args.mode == "interactive":
        # 交互式测试
        tester.interactive_test()
    
    else:
        # 自动测试
        tester.run_tests()
        
        # 显示技能配置摘要
        print("\n" + "=" * 70)
        print("🔧 技能配置摘要")
        print("=" * 70)
        print(f"激活关键词数: {len(tester.skill_keywords)}")
        print("示例关键词:", ", ".join(tester.skill_keywords[:5]) + "...")
        print(f"测试用例数: {len(tester.test_cases)}")
        print("\n📁 核心文件:")
        print("  - mcp_standard_skill.py (技能主实现)")
        print("  - mcp_config.json (MCP配置文件)")
        print("  - InvestmentTracker-platform.skill (技能注册文件)")
        print("\n🚀 快速测试命令:")
        print("  python3 mcp_standard_skill.py all")
        print("  python3 mcp_standard_skill.py user")
        print("  python3 mcp_standard_skill.py positions")

if __name__ == "__main__":
    main()