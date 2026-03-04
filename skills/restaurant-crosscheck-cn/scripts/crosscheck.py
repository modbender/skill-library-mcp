#!/usr/bin/env python3
"""
本地生活交叉验证 — 大众点评 × 小红书
基于原始 crosscheck.py + crosscheck_base.py 重构

用法:
    python3 crosscheck.py '深圳南山区' '粤菜'
    python3 crosscheck.py '广州天河区' '早茶'
    python3 crosscheck.py '上海静安区' '按摩'
"""
import sys
import os
import json
from typing import List

from config import SCORING_WEIGHTS, OUTPUT_CONFIG, DEFAULT_THRESHOLDS
from models import MatchedRestaurant, RecommendationResult
from fetch_dianping import fetch_dianping
from fetch_xiaohongshu import fetch_xiaohongshu
from match_restaurants import match_and_score, normalize_engagement, calculate_consistency


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  评分逻辑（来自原始 crosscheck_base.py.CrossCheckBase）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_recommendation(match: MatchedRestaurant) -> RecommendationResult:
    """
    计算最终推荐评分（来自原始 CrossCheckBase.calculate_recommendation）
    """
    dp = match.dianping_data
    xhs = match.xhs_data
    w = SCORING_WEIGHTS

    # 归一化小红书互动量到 0-5
    xhs_rating = normalize_engagement(xhs)

    # 一致性
    consistency = calculate_consistency(dp.rating, xhs_rating, xhs.sentiment_score)

    # 综合评分 0-10（来自原始公式）
    raw_score = (
        (dp.rating * w['dianping_rating']) +
        (xhs_rating * w['xhs_engagement']) +
        (consistency * 5 * w['consistency'])
    ) * 2
    recommendation_score = round(max(0.0, min(10.0, raw_score)), 1)

    # 一致性等级
    if consistency >= 0.7:
        consistency_level = "高"
    elif consistency >= 0.5:
        consistency_level = "中"
    else:
        consistency_level = "低"

    return RecommendationResult(
        name=dp.name,
        dianping_rating=dp.rating,
        dianping_reviews=dp.review_count,
        dianping_tags=dp.tags,
        dianping_address=dp.address,
        dianping_price=dp.price_range,
        xhs_engagement_display=f"{xhs_rating:.1f}⭐ ({xhs.likes}赞)",
        xhs_keywords=xhs.keywords,
        recommendation_score=recommendation_score,
        consistency_level=consistency_level,
        consistency_score=round(consistency, 2),
        similarity_score=round(match.similarity_score, 2),
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  主流程
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def crosscheck(location: str, cuisine: str):
    """执行交叉验证"""
    print(f"\n{'=' * 60}")
    print(f"🔍 本地生活交叉验证: {location} - {cuisine}")
    print(f"{'=' * 60}")
    print(f"💡 会弹出浏览器窗口，请不要操作它们\n")

    # 抓取两个平台
    dp_restaurants = fetch_dianping(location, cuisine)
    print(f"  ✅ 大众点评: {len(dp_restaurants)} 家\n")

    xhs_posts = fetch_xiaohongshu(location, cuisine)
    print(f"  ✅ 小红书: {len(xhs_posts)} 家")

    if not dp_restaurants and not xhs_posts:
        print("\n❌ 两个平台都没数据")
        print("💡 排查步骤:")
        print("  1. python3 session_manager.py all  重新登录")
        print("  2. 查看 ~/Downloads/ 下的截图")
        print("  3. 海外用户需开国内 VPN")
        return

    # 交叉匹配
    threshold = DEFAULT_THRESHOLDS['similarity_threshold']
    matches = match_and_score(dp_restaurants, xhs_posts, threshold)

    # 计算推荐评分
    results = [calculate_recommendation(m) for m in matches]
    results.sort(key=lambda r: r.recommendation_score, reverse=True)

    # ── 输出结果 ──
    print(f"\n{'=' * 60}")
    print(f"📊 交叉验证结果")
    print(f"{'=' * 60}")

    max_show = OUTPUT_CONFIG['max_restaurants']

    if results:
        print(f"\n  🎯 两平台共同推荐 ({len(results)} 家):\n")
        for i, r in enumerate(results[:max_show], 1):
            score = r.recommendation_score
            if score >= 8:
                level = "🔥 强推"
            elif score >= 6:
                level = "👍 推荐"
            else:
                level = "🤔 可以试试"

            print(f"  {i}. 【{r.name}】 {score}/10 {level}")
            print(f"     大众点评: {r.dianping_rating}分 | {r.dianping_reviews}条评论 | {r.dianping_price or '价格未知'}")
            print(f"     小红书: {r.xhs_engagement_display} | 匹配度{r.similarity_score}")
            print(f"     一致性: {r.consistency_level} ({r.consistency_score})")
            if r.dianping_address:
                print(f"     📍 {r.dianping_address}")
            if r.dianping_tags:
                print(f"     🏷️  {', '.join(r.dianping_tags)}")
            if r.xhs_keywords:
                print(f"     💬 小红书热词: {', '.join(r.xhs_keywords)}")
            print()

    # 未匹配的也列出
    matched_dp_names = {r.name for r in results}
    matched_xhs_names = {m.xhs_data.restaurant_name for m in matches}
    unmatched_dp = [r for r in dp_restaurants if r.name not in matched_dp_names]
    unmatched_xhs = [p for p in xhs_posts if p.restaurant_name not in matched_xhs_names]

    if not results:
        print("\n  ⚠️ 未找到交叉匹配\n")

    if unmatched_dp:
        print(f"  📍 仅大众点评 ({len(unmatched_dp)} 家):")
        for i, r in enumerate(unmatched_dp[:8], 1):
            print(f"    {i}. {r.name} — {r.rating}分 {r.review_count}评 {r.price_range}")
        print()

    if unmatched_xhs:
        print(f"  📕 仅小红书 ({len(unmatched_xhs)} 家):")
        for i, p in enumerate(unmatched_xhs[:8], 1):
            print(f"    {i}. {p.restaurant_name} — 提及{p.mention_count}次 好评度{p.sentiment_score:.2f}")
        print()

    print(f"{'=' * 60}")

    # 保存 JSON 结果
    _save_results(location, cuisine, results, unmatched_dp, unmatched_xhs)


def _save_results(location, cuisine, results, unmatched_dp, unmatched_xhs):
    """保存详细结果到 JSON"""
    data = {
        "query": {"location": location, "cuisine": cuisine},
        "matches": [
            {
                "name": r.name,
                "score": r.recommendation_score,
                "dianping_rating": r.dianping_rating,
                "dianping_reviews": r.dianping_reviews,
                "dianping_price": r.dianping_price,
                "dianping_address": r.dianping_address,
                "consistency": r.consistency_level,
                "similarity": r.similarity_score,
            }
            for r in results
        ],
        "dianping_only": [
            {"name": r.name, "rating": r.rating, "reviews": r.review_count, "price": r.price_range}
            for r in unmatched_dp
        ],
        "xiaohongshu_only": [
            {"name": p.restaurant_name, "mentions": p.mention_count, "sentiment": p.sentiment_score}
            for p in unmatched_xhs
        ],
    }
    out_path = os.path.expanduser(f"~/Downloads/crosscheck_{location}_{cuisine}.json")
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 详细结果已保存: {out_path}")
    except Exception:
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CLI 入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("🔍 本地生活交叉验证工具")
        print()
        print("用法: python3 crosscheck.py <位置> <类型>")
        print()
        print("示例:")
        print("  python3 crosscheck.py '深圳南山区' '粤菜'")
        print("  python3 crosscheck.py '广州天河区' '早茶'")
        print("  python3 crosscheck.py '上海静安区' '日料'")
        print("  python3 crosscheck.py '成都锦江区' '火锅'")
        print("  python3 crosscheck.py '深圳福田区' '按摩'")
        sys.exit(1)

    crosscheck(sys.argv[1], sys.argv[2])
