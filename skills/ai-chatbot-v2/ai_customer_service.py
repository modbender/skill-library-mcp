#!/usr/bin/env python3
"""
AI Customer Service Tool for OpenClaw
智能客服系统 - FAQ匹配、意图识别、多轮对话
"""
import json
import sys
import re
from datetime import datetime

# 对话历史（会话级）
conversation_history = []

# 内置FAQ知识库
FAQ_DB = [
    {
        "question": "退货",
        "keywords": ["退货", "退款", "不想要", "换货"],
        "answer": """📦 退货政策说明：

• 7天内无理由退货（商品未拆封）
• 质量问题30天内可退换
• 退货需保持原包装和配件完整

请问您是因为什么原因要退货呢？
1. 商品质量问题
2. 不喜欢/不想要了
3. 尺寸/规格不合适
4. 其他原因"""
    },
    {
        "question": "物流",
        "keywords": ["物流", "快递", "到哪里", "发货", "到货"],
        "answer": """📦 物流相关：

• 正常情况下24小时内发货
• 快递时效：省内1-2天，省外2-4天
• 可以通过"我的订单"查看物流详情
• 快递单号会在发货后自动发送短信给您

请问您是需要查询物流还是想了解发货时间？"""
    },
    {
        "question": "支付",
        "keywords": ["支付", "付款", "怎么付", "支付宝", "微信", "银行卡"],
        "answer": """💳 支持的支付方式：

• 微信支付
• 支付宝
• 银行卡（支持所有主流银行）
• 花呗/分期付款
• 货到付款（部分地区）

所有支付方式都安全可靠，请放心使用！"""
    },
    {
        "question": "运费",
        "keywords": ["运费", "邮费", "谁承担"],
        "answer": """🚚 运费说明：

• 订单满39元免运费
• 不足39元需支付8元运费
• 非人为质量问题导致的退货，运费由商家承担
• 偏远地区可能有额外费用"""
    },
    {
        "question": "7天无理由",
        "keywords": ["7天", "无理由", "七天"],
        "answer": """✅ 7天无理由退货：

• 支持7天内无理由退货（商品未拆封、使用）
• 退货商品需保持全新状态
• 退货邮费根据具体情况由买家或商家承担
• 退款在收到商品后3个工作日内处理"""
    },
    {
        "question": "售后",
        "keywords": ["售后", "客服", "电话", "联系"],
        "answer": """📞 售后服务：

• 客服热线：400-888-8888（工作日9:00-18:00）
• 在线客服：APP内点击"联系客服"
• 微信客服：关注公众号，点击"客服"
• 紧急问题优先处理"""
    },
    {
        "question": "店铺",
        "keywords": ["店铺", "实体店", "专卖店", "在哪"],
        "answer": """🏪 店铺信息：

• 目前为线上销售模式，暂无实体店
• 全国各地均可配送，大部分地区隔日达
• 官方商城：xxx.com
• 体验店正在筹备中，敬请期待"""
    }
]

# 意图识别规则
INTENT_PATTERNS = {
    "退货": ["退货", "退款", "不想要", "换货", "取消订单"],
    "物流": ["物流", "快递", "到哪里", "发货", "到货", "物流信息"],
    "支付": ["支付", "付款", "怎么付", "分期", "花呗"],
    "运费": ["运费", "邮费", "要钱吗", "免运费"],
    "售后": ["客服", "电话", "联系", "售后", "投诉"],
    "查询": ["查", "看", "订单", "物流"],
}

# 情绪关键词
SENTIMENT_POSITIVE = ["谢谢", "满意", "太好了", "很好", "喜欢", "棒"]
SENTIMENT_NEGATIVE = ["生气", "失望", "太差", "垃圾", "投诉", "差评", "怒"]


def detect_intent(message):
    """检测用户意图"""
    message = message.lower()
    for intent, keywords in INTENT_PATTERNS.items():
        for kw in keywords:
            if kw in message:
                return intent
    return "general"


def detect_sentiment(message):
    """检测情绪"""
    message = message.lower()
    for kw in SENTIMENT_NEGATIVE:
        if kw in message:
            return "negative"
    for kw in SENTIMENT_POSITIVE:
        if kw in message:
            return "positive"
    return "neutral"


def search_faq(keywords):
    """搜索FAQ"""
    keywords = keywords.lower()
    results = []
    for faq in FAQ_DB:
        # 检查问题标题
        if keywords in faq["question"]:
            results.append(faq)
            continue
        # 检查关键词
        for kw in faq["keywords"]:
            if kw in keywords:
                results.append(faq)
                break
    return results


def build_response(user_message, intent=None, sentiment=None):
    """构建回复"""
    # 检测意图
    if intent is None:
        intent = detect_intent(user_message)
    
    # 检测情绪
    if sentiment is None:
        sentiment = detect_sentiment(user_message)
    
    # 问候语
    greetings = ["你好", "hi", "hello", "在吗", "在不"]
    for g in greetings:
        if g in user_message.lower():
            return """👋 您好！欢迎光临！

我是AI智能客服，很高兴为您服务～

我可以帮您解答：
📦 订单物流相关问题
💰 支付及退款问题
📋 售后服务指南
❓ 常见问题解答

请告诉我您想咨询什么？"""
    
    # 负面情绪处理
    if sentiment == "negative":
        return f"""😔 非常抱歉给您带来不好的体验！

我已经记录下您的问题，将立即转交专业人员处理。
您的反馈对我们非常重要，我们会尽快改进。

如果您有紧急问题，欢迎拨打客服热线：400-888-8888

请问还有什么可以帮您的？"""
    
    # 搜索FAQ
    faqs = search_faq(user_message)
    if faqs:
        return faqs[0]["answer"]
    
    # 通用回答
    if intent != "general":
        # 根据意图返回对应FAQ
        for faq in FAQ_DB:
            if intent in faq["keywords"]:
                return faq["answer"]
    
    # 默认回复
    return """🤔 感谢您的咨询！

目前知识库中没有找到完全匹配的信息。
您可以尝试：
• 拨打客服热线：400-888-8888
• 描述更详细的问题
• 直接说明您想了解"退货"、"物流"、"支付"等

请问还有其他可以帮您的吗？"""


def cmd_chat(args):
    """对话命令"""
    if not args:
        print("请输入您的问题，例如：/ai-customer-service chat 你好")
        return
    
    user_message = ' '.join(args)
    
    # 添加到历史
    conversation_history.append({
        "role": "user",
        "message": user_message,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # 检测意图和情绪
    intent = detect_intent(user_message)
    sentiment = detect_sentiment(user_message)
    
    # 构建回复
    response = build_response(user_message, intent, sentiment)
    
    print(response)
    
    # 添加AI回复到历史
    conversation_history.append({
        "role": "assistant",
        "message": response[:100] + "...",
        "time": datetime.now().strftime("%H:%M")
    })


def cmd_add(args):
    """添加FAQ"""
    if len(args) < 2:
        print("用法: /ai-customer-service add <问题> <答案>")
        return
    
    # 简单解析：找到第一个？或。作为分隔
    sep = len(args)
    for i, a in enumerate(args):
        if '？' in a or '?' in a or '。' in a:
            sep = i
            break
    
    question = ' '.join(args[:sep])
    answer = ' '.join(args[sep:])
    
    # 提取关键词
    keywords = [question[:2], question[2:4]] if len(question) >= 4 else [question[:2]]
    
    new_faq = {
        "question": question,
        "keywords": keywords,
        "answer": answer
    }
    FAQ_DB.append(new_faq)
    
    print(f"✅ 已添加FAQ:")
    print(f"  问题: {question}")
    print(f"  答案: {answer[:50]}...")


def cmd_list(args):
    """列出知识库"""
    print("📚 知识库内容\n" + "=" * 40)
    for i, faq in enumerate(FAQ_DB, 1):
        print(f"{i}. {faq['question']}")
    print(f"\n共 {len(FAQ_DB)} 条FAQ")


def cmd_stats(args):
    """查看统计"""
    print("📊 客服统计数据\n" + "=" * 40)
    print(f"知识库条目: {len(FAQ_DB)}")
    print(f"对话轮数: {len(conversation_history) // 2}")
    print(f"用户消息: {len([h for h in conversation_history if h['role'] == 'user'])}")
    
    if conversation_history:
        print(f"\n最近对话:")
        for h in conversation_history[-4:]:
            role = "👤" if h['role'] == "user" else "🤖"
            print(f"  {role} {h['message'][:40]}")


def cmd_clear(args):
    """清空对话历史"""
    global conversation_history
    conversation_history = []
    print("✅ 对话历史已清空")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 50)
        print("💬 AI Smart Customer Service 智能客服")
        print("=" * 50)
        print("")
        print("用法: /ai-customer-service <命令> [参数]")
        print("")
        print("命令:")
        print("  chat <消息>    - 开始对话")
        print("  add <问题> <答案> - 添加FAQ")
        print("  list          - 查看知识库")
        print("  stats         - 查看统计")
        print("  clear         - 清空对话历史")
        print("")
        print("示例:")
        print("  /ai-customer-service chat 你好")
        print("  /ai-customer-service chat 我想退货")
        print("  /ai-customer-service list")
        return
    
    cmd = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    command_map = {
        'chat': cmd_chat,
        'add': cmd_add,
        'list': cmd_list,
        'stats': cmd_stats,
        'clear': cmd_clear,
    }
    
    if cmd in command_map:
        command_map[cmd](args)
    else:
        print(f"未知命令: {cmd}")
        print("可用命令: chat, add, list, stats, clear")


if __name__ == '__main__':
    main()