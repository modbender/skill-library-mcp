#!/usr/bin/env python3
"""本地验证脚本：不调用真实 API，用 Mock 客户端测试技能逻辑。"""
import sys
import os

# 确保能导入包（在项目根执行时）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import SalesOratoryMaster, setup


class MockLLMClient:
    """模拟大模型客户端：不发起网络请求，直接返回示例话术。"""

    def chat(self, system_message=None, user_message=None):
        return (
            "### 【心理博弈分析】\n"
            "客户处于预算防御状态，需先共情再平移价值。\n\n"
            "### 【建议回复话术】\n"
            "理解您对预算的考量，我们可以从 TCO 角度算一笔账……\n\n"
            "### 【话术心法拆解】\n"
            "先肯定再平移，避免正面反驳。\n\n"
            "### 【合规风险点拨】\n"
            "未使用绝对化承诺，符合红线。"
        )


def test_missing_params():
    """测试：缺少 deal_stage 或 client_persona 时应返回引导文案。"""
    master = setup(MockLLMClient())
    out = master.execute(customer_quote="太贵了")
    assert "信息不足" in out and "成交阶段" in out, "缺少参数时应提示补充信息"
    print("[OK] 缺少参数时正确返回引导文案")


def test_full_execution():
    """测试：参数齐全时能加载模板并调用 LLM（Mock）返回话术。"""
    master = setup(MockLLMClient())
    out = master.execute(
        customer_quote="你们比 XX 家贵不少",
        deal_stage="商务谈判",
        client_persona="风险规避型",
    )
    assert "心理博弈分析" in out or "建议回复话术" in out, "应返回结构化话术内容"
    print("[OK] 参数齐全时正常生成话术")


if __name__ == "__main__":
    test_missing_params()
    test_full_execution()
    print("\n全部检查通过，技能可正常工作。")
