#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TokFlow 查询脚本 - OpenClaw Skill 入口

通过命令行调用 TokFlow API，返回 JSON 格式数据。
供 OpenClaw AI 在对话中查询 Token 消耗和优化建议。

用法：
    python3 tokflow_query.py <command> [options]

命令：
    dashboard           总览数据
    models              所有模型列表
    providers           渠道统计
    model-detail <id>   单模型详情
    balance             渠道余额
    suggestions         优化建议
    generate            生成新建议
    analysis            消耗分析
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8001/api"


def api_get(path: str) -> dict:
    """GET 请求 TokFlow API"""
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": f"无法连接 TokFlow 服务: {e}", "hint": "请确保 TokFlow 后端在 localhost:8001 运行"}
    except Exception as e:
        return {"error": str(e)}


def api_post(path: str) -> dict:
    """POST 请求 TokFlow API"""
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, data=b"", method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": f"无法连接 TokFlow 服务: {e}"}
    except Exception as e:
        return {"error": str(e)}


def cmd_dashboard():
    """查询总览数据"""
    data = api_get("/dashboard")
    if "error" in data:
        return data

    return {
        "今日Token消耗": data.get("today_tokens", {}).get("value", 0),
        "今日环比": f"{data.get('today_tokens', {}).get('change_pct', 0)}%",
        "本月Token消耗": data.get("month_tokens", {}).get("value", 0),
        "活跃模型数": data.get("active_models", {}).get("value", 0),
        "已配置模型总数": data.get("active_models", {}).get("configured", 0),
        "付费渠道数": data.get("active_models", {}).get("providers", 0),
        "本月费用_元": data.get("month_cost", {}).get("value", 0),
        "费用环比": f"{data.get('month_cost', {}).get('change_pct', 0)}%",
        "模型分布": [
            {"模型": m["model"], "渠道": m["provider"], "Token": m["total_tokens"], "占比": f"{m['percentage']}%"}
            for m in data.get("model_distribution", [])
        ],
    }


def cmd_models(days: int = 30):
    """查询所有模型"""
    data = api_get(f"/models?days={days}")
    if "error" in data:
        return data

    models = []
    for m in data.get("models", []):
        models.append({
            "模型": m["display_name"],
            "渠道": m["provider"],
            "model_id": m["model"],
            "状态": "活跃" if m["status"] == "active" else "待使用",
            "调用次数": m["call_count"],
            "总Token": m["total_tokens"],
            "费用_元": m["total_cost"],
            "效率评分": m["efficiency_score"],
            "最后使用": m.get("last_used"),
        })

    return {
        "总模型数": data.get("total_models", 0),
        "活跃模型": data.get("active_models", 0),
        "待使用模型": data.get("configured_models", 0),
        "时间范围_天": days,
        "模型列表": models,
    }


def cmd_providers(days: int = 30):
    """查询渠道统计"""
    data = api_get(f"/models/providers?days={days}")
    if "error" in data:
        return data

    providers = []
    for p in data.get("providers", []):
        providers.append({
            "渠道": p["provider"],
            "状态": "活跃" if p["status"] == "active" else "未使用",
            "已配置模型": p["total_configured_models"],
            "使用中模型": p["active_models"],
            "调用次数": p["call_count"],
            "总Token": p["total_tokens"],
            "费用_元": p["total_cost"],
            "费用占比": f"{p['cost_percentage']}%",
            "模型列表": [m["display_name"] for m in p.get("models", [])],
        })

    return {
        "总渠道数": data.get("total_providers", 0),
        "活跃渠道": data.get("active_providers", 0),
        "渠道列表": providers,
    }


def cmd_model_detail(model_id: str, days: int = 7):
    """查询单模型详情"""
    data = api_get(f"/models/{urllib.parse.quote(model_id, safe='')}/detail?days={days}")
    if "error" in data:
        return data

    stats = data.get("statistics", {})
    return {
        "模型": model_id,
        "时间范围_天": days,
        "调用次数": stats.get("call_count", 0),
        "总Token": stats.get("total_tokens", 0),
        "平均每次Token": stats.get("avg_tokens_per_call", 0),
        "P95_Token": stats.get("p95_tokens", 0),
        "最大单次": stats.get("max_tokens_single", 0),
        "缓存命中率": f"{stats.get('cache_hit_rate', 0)}%",
        "输出占比": f"{stats.get('output_ratio', 0)}%",
        "费用_元": stats.get("total_cost", 0),
    }


def cmd_balance():
    """查询渠道余额"""
    return api_get("/balance")


def cmd_suggestions():
    """查询优化建议"""
    data = api_get("/optimization/suggestions")
    if "error" in data:
        return data

    suggestions = []
    for s in data.get("suggestions", []):
        suggestions.append({
            "标题": s["title"],
            "类型": s["type"],
            "描述": s["description"],
            "影响级别": s["impact_level"],
            "预估月省_元": s.get("estimated_saving", 0),
            "状态": s["status"],
        })

    return {
        "总建议数": data.get("total", 0),
        "建议列表": suggestions,
    }


def cmd_generate():
    """生成新的优化建议"""
    return api_post("/optimization/generate")


def cmd_analysis(days: int = 30):
    """消耗分析"""
    data = api_get(f"/analysis/overview?days={days}")
    if "error" in data:
        return data

    summary = data.get("summary", {})
    period = data.get("period_comparison", {})

    return {
        "总费用_元": summary.get("total_cost", 0),
        "总Token": summary.get("total_tokens", 0),
        "总调用次数": summary.get("total_calls", 0),
        "当期": period.get("current_period", {}),
        "上期": period.get("previous_period", {}),
        "变化": period.get("changes", {}),
    }


def cmd_prompt_stats(days: int = 30):
    """提问方式统计（v0.5.0）"""
    data = api_get(f"/prompt-stats?days={days}")
    if "error" in data:
        return data

    stats = data.get("stats", {})
    saving = data.get("saving_estimate", {})

    return {
        "提问轮次": stats.get("total_turns", 0),
        "平均提问长度_字": stats.get("avg_prompt_chars", 0),
        "中位提问长度_字": stats.get("median_prompt_chars", 0),
        "平均链调用次数": stats.get("avg_assistant_count", 0),
        "总费用_元": stats.get("sum_cost", 0),
        "预估月省Token": saving.get("estimated_saving_tokens_per_month", 0),
        "预估月省_元": saving.get("estimated_saving_cny_per_month", 0),
        "说明": saving.get("assumption", ""),
        "可优化轮次占比_%": saving.get("optimizable_turns_pct", 0),
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请指定命令", "可用命令": [
            "dashboard", "models", "providers", "model-detail",
            "balance", "suggestions", "generate", "analysis", "prompt-stats"
        ]}, ensure_ascii=False, indent=2))
        sys.exit(1)

    cmd = sys.argv[1]
    days = 30

    # 解析 --days 参数
    for i, arg in enumerate(sys.argv):
        if arg == "--days" and i + 1 < len(sys.argv):
            try:
                days = int(sys.argv[i + 1])
            except ValueError:
                pass

    if cmd == "dashboard":
        result = cmd_dashboard()
    elif cmd == "models":
        result = cmd_models(days)
    elif cmd == "providers":
        result = cmd_providers(days)
    elif cmd == "model-detail":
        if len(sys.argv) < 3:
            result = {"error": "请指定模型ID，例如: tokflow_query.py model-detail deepseek-chat"}
        else:
            import urllib.parse
            result = cmd_model_detail(sys.argv[2], days)
    elif cmd == "balance":
        result = cmd_balance()
    elif cmd == "suggestions":
        result = cmd_suggestions()
    elif cmd == "generate":
        result = cmd_generate()
    elif cmd == "analysis":
        result = cmd_analysis(days)
    elif cmd == "prompt-stats":
        result = cmd_prompt_stats(days)
    else:
        result = {"error": f"未知命令: {cmd}", "可用命令": [
            "dashboard", "models", "providers", "model-detail",
            "balance", "suggestions", "generate", "analysis", "prompt-stats"
        ]}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
