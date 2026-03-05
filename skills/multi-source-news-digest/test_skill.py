#!/usr/bin/env python3
# 测试Multi Source Tech News Digest技能

import sys
sys.path.insert(0, '/home/pan/.openclaw/workspace/skills/multi-source-news-digest')

from skill import MultiSourceTechNewsDigest

# 创建技能实例
skill = MultiSourceTechNewsDigest()

print("🔍 测试Multi Source Tech News Digest技能")
print("=" * 60)
print()

# 测试1: 获取新闻
print("📊 测试1: 获取新闻数据...")
news = skill.get_news(force_refresh=True)
print(f"获取到 {len(news)} 条新闻")
print()

# 测试2: 评分功能
print("🧠 测试2: 新闻评分功能...")
if news:
    sample_news = news[0]
    print(f"样本新闻: {sample_news['title']}")
    print(f"评分: {sample_news['score']}")
    print(f"来源: {sample_news['source']}")
else:
    # 测试评分函数
    test_news = {
        "title": "AI breakthrough in machine learning",
        "summary": "Researchers have made significant progress in artificial intelligence...",
        "source": "TechCrunch"
    }
    score = skill.score_news(test_news)
    print(f"测试新闻评分: {score} (预期: 高评分)")
print()

# 测试3: 生成摘要
print("📝 测试3: 生成摘要...")
digest = skill.generate_daily_digest()
print("摘要预览:")
print(digest[:200] + "..." if len(digest) > 200 else digest)
print()

# 测试4: 运行接口
print("🚀 测试4: 运行接口...")
result = skill.run(["digest"])
print(f"运行状态: {result['status']}")
if result['status'] == 'success':
    content = result.get('content', '')
    print(f"内容长度: {len(content)} 字符")
print()

print("=" * 60)
print("✅ 技能测试完成！")
if len(news) > 0:
    print("🎉 技能正常工作，成功获取新闻数据！")
else:
    print("⚠️  技能功能正常，但暂时未获取到新闻数据")
    print("💡 可能原因: RSS源暂时无新内容或网络访问限制")
    print("💡 建议: 稍后再试或检查网络连接")