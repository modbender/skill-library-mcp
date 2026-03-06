#!/usr/bin/env python3
"""
InvestmentTracker技能激活测试
模拟OpenClaw技能激活场景
"""

import re
from simple_skill import InvestmentTrackerSkill

class SkillActivationTester:
    """技能激活测试器"""
    
    def __init__(self):
        self.skill = InvestmentTrackerSkill()
        self.activation_patterns = [
            # 投资组合相关
            r'(查看|显示|获取|我的)?投资组合',
            r'投资(概况|概览|情况)',
            r'portfolio',
            r'持仓(情况|分析)',
            
            # 交易记录相关
            r'(查看|显示|最近|历史)?交易(记录|历史)',
            r'transactions',
            r'买卖记录',
            
            # 投资分析相关
            r'投资(分析|表现|回报)',
            r'收益(分析|情况)',
            r'analysis',
            r'表现(如何|怎么样)',
            
            # 综合查询
            r'我的投资',
            r'投资情况',
            r'investment',
            r'InvestmentTracker'
        ]
    
    def test_activation(self, user_input: str) -> bool:
        """测试技能是否应该激活"""
        user_input_lower = user_input.lower()
        
        for pattern in self.activation_patterns:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                return True
        
        return False
    
    def get_response(self, user_input: str) -> str:
        """获取技能响应"""
        user_input_lower = user_input.lower()
        
        # 判断用户意图
        if any(word in user_input_lower for word in ['组合', 'portfolio', '持仓', '概况']):
            return self.skill.format_portfolio()
        
        elif any(word in user_input_lower for word in ['交易', 'transaction', '买卖', '记录']):
            # 提取数量限制
            limit = 5
            match = re.search(r'(\d+)[笔条个]', user_input)
            if match:
                limit = int(match.group(1))
            return self.skill.format_transactions(limit)
        
        elif any(word in user_input_lower for word in ['分析', 'analysis', '表现', '收益', '回报']):
            return self.skill.format_analysis()
        
        else:
            # 默认显示所有
            return f"{self.skill.format_portfolio()}\n\n{'='*60}\n\n{self.skill.format_transactions()}\n\n{'='*60}\n\n{self.skill.format_analysis()}"
    
    def run_interactive_test(self):
        """运行交互式测试"""
        print("🔧 InvestmentTracker技能激活测试")
        print("=" * 60)
        print("输入用户消息，测试技能是否激活并查看响应")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 60)
        
        while True:
            user_input = input("\n👤 用户输入: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("测试结束")
                break
            
            if not user_input:
                continue
            
            # 测试激活
            should_activate = self.test_activation(user_input)
            
            print(f"🔍 激活检测: {'✅ 激活' if should_activate else '❌ 不激活'}")
            
            if should_activate:
                print("\n🤖 技能响应:")
                print("-" * 40)
                response = self.get_response(user_input)
                print(response)
            else:
                print("💡 提示: 技能不会激活，用户可能需要其他帮助")

def test_example_scenarios():
    """测试示例场景"""
    tester = SkillActivationTester()
    
    test_cases = [
        ("查看我的投资组合", True, "portfolio"),
        ("投资情况怎么样", True, "portfolio"),
        ("显示最近的交易记录", True, "transactions"),
        ("最近5笔交易", True, "transactions"),
        ("分析我的投资表现", True, "analysis"),
        ("投资回报率是多少", True, "analysis"),
        ("今天天气如何", False, None),
        ("帮我写个邮件", False, None),
        ("InvestmentTracker", True, "all"),
        ("portfolio analysis", True, "analysis"),
    ]
    
    print("📋 示例场景测试")
    print("=" * 60)
    
    for user_input, expected_activation, expected_response_type in test_cases:
        activation = tester.test_activation(user_input)
        status = "✅" if activation == expected_activation else "❌"
        
        print(f"{status} 输入: {user_input}")
        print(f"   预期激活: {expected_activation}, 实际: {activation}")
        
        if activation:
            response = tester.get_response(user_input)
            lines = response.split('\n')
            preview = ' '.join(lines[:3])[:50] + "..."
            print(f"   响应预览: {preview}")
        
        print()

def main():
    """主函数"""
    print("InvestmentTracker Skill 完整测试")
    print("=" * 60)
    
    # 测试示例场景
    test_example_scenarios()
    
    print("\n" + "=" * 60)
    print("交互式测试模式")
    print("=" * 60)
    
    # 运行交互式测试
    tester = SkillActivationTester()
    tester.run_interactive_test()
    
    print("\n" + "=" * 60)
    print("技能状态总结")
    print("=" * 60)
    
    # 显示技能能力
    skill = InvestmentTrackerSkill()
    print("📊 可用功能:")
    print("1. 投资组合查看")
    print("2. 交易记录查询")
    print("3. 投资分析报告")
    print("4. 多格式输出（文本/JSON）")
    print("5. 模拟数据支持")
    print("6. API集成准备")
    
    print("\n🔧 技术特性:")
    print("• 无外部依赖")
    print("• 模块化设计")
    print("• 易于扩展")
    print("• 完整错误处理")
    
    print("\n🚀 下一步:")
    print("1. 部署MCP API")
    print("2. 集成真实数据")
    print("3. 添加更多分析功能")
    print("4. 优化用户体验")

if __name__ == "__main__":
    main()