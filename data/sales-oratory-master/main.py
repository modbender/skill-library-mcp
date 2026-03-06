import os


class SalesOratoryMaster:
    def __init__(self, llm_client):
        self.llm_client = llm_client  # 传入你的大模型客户端 (如 OpenAI, 智谱等)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def _load_file(self, filename):
        path = os.path.join(self.base_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def execute(self, customer_quote: str, deal_stage: str = None, client_persona: str = None):
        """核心执行主逻辑"""
        # 1. 拦截缺失参数，引导用户输入
        if not deal_stage or not client_persona:
            return (
                "⚠️ **信息不足，拒绝盲目生成话术。**\n"
                "为了提供最精准的博弈建议，请补充以下信息：\n"
                "1. 当前处于哪个**【成交阶段】**？（如：增购谈判、方案评审）\n"
                "2. 客户的**【决策性格】**如何？（如：风险规避型、细节控）\n"
                "> 请补充后再次调用本技能。"
            )

        # 2. 组装 Prompt
        prompt_template = self._load_file("prompt_template.md")
        system_prompt = prompt_template.format(
            customer_quote=customer_quote,
            deal_stage=deal_stage,
            client_persona=client_persona,
        )

        # 3. 加载合规红线 (R4 哨兵)
        promise_guard = self._load_file("PROMISE_GUARD.md")
        full_system_prompt = f"{system_prompt}\n\n=== 强制合规红线 ===\n{promise_guard}"

        # 4. 调用大模型生成初步话术
        print("[Log] 正在进行心理画像分析与话术生成...")
        draft_response = self.llm_client.chat(
            system_message=full_system_prompt,
            user_message="请根据上述规则和输入，生成策略与话术。",
        )

        # 5. 返回最终结果
        return draft_response


def setup(llm_client):
    """导出供外部框架调用"""
    return SalesOratoryMaster(llm_client)
