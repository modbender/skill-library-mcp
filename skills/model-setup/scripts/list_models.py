#!/usr/bin/env python3
"""
列出所有配置的模型
"""
import json
import sys
from pathlib import Path


def list_models(config_path):
    """
    列出所有配置的模型

    Args:
        config_path: models.json 路径

    Returns:
        dict: 列表结果
    """
    result = {
        "success": False,
        "providers": [],
        "total_models": 0,
        "error": None
    }

    try:
        if not config_path.exists():
            result["error"] = f"配置文件不存在: {config_path}"
            return result

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if "providers" not in config:
            result["error"] = "配置文件缺少 providers 字段"
            return result

        providers = config["providers"]
        total_models = 0

        for provider_id, provider_config in providers.items():
            models = provider_config.get("models", [])
            provider_info = {
                "provider_id": provider_id,
                "base_url": provider_config.get("baseUrl", "N/A"),
                "api_type": provider_config.get("api", "N/A"),
                "models": []
            }

            for model in models:
                model_info = {
                    "id": model.get("id", "N/A"),
                    "name": model.get("name", "N/A"),
                    "context_window": model.get("contextWindow", "N/A"),
                    "max_tokens": model.get("maxTokens", "N/A"),
                    "reasoning": model.get("reasoning", False),
                    "full_id": f"{provider_id}/{model.get('id', 'N/A')}"
                }
                provider_info["models"].append(model_info)
                total_models += 1

            result["providers"].append(provider_info)

        result["total_models"] = total_models
        result["success"] = True

    except json.JSONDecodeError as e:
        result["error"] = f"配置文件解析失败: {str(e)}"
    except Exception as e:
        result["error"] = f"列出模型失败: {str(e)}"

    return result


def format_output(result):
    """
    格式化输出结果

    Args:
        result: list_models 的结果

    Returns:
        str: 格式化的输出
    """
    if not result["success"]:
        return f"错误: {result['error']}"

    output = []
    output.append(f"总计 {result['total_models']} 个模型\n")

    for provider in result["providers"]:
        output.append(f"提供商: {provider['provider_id']}")
        output.append(f"  Base URL: {provider['base_url']}")
        output.append(f"  API 类型: {provider['api_type']}")
        output.append(f"  模型数量: {len(provider['models'])}")
        output.append("  模型列表:")

        for model in provider["models"]:
            output.append(f"    - {model['name']}")
            output.append(f"      ID: {model['id']}")
            output.append(f"      完整 ID: {model['full_id']}")
            output.append(f"      上下文窗口: {model['context_window']}")
            output.append(f"      最大 token: {model['max_tokens']}")
            output.append(f"      推理支持: {'是' if model['reasoning'] else '否'}")
            output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    config_path = Path("/home/yupeng/.openclaw/agents/main/agent/models.json")
    use_format = False

    # 解析参数
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--format":
            use_format = True
        elif not arg.startswith("--"):
            config_path = Path(arg)

    result = list_models(config_path)

    # 默认输出 JSON，使用 --format 时输出格式化文本
    if use_format:
        print(format_output(result))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    sys.exit(0 if result["success"] else 1)