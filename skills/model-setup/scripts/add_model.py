#!/usr/bin/env python3
"""
安全地添加模型配置到 models.json
"""
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime


def backup_config(config_path):
    """
    备份配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        Path: 备份文件路径
    """
    backup_path = config_path.with_suffix(f".json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(config_path, backup_path)
    return backup_path


def load_config(config_path):
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        dict: 配置内容
    """
    if not config_path.exists():
        return {"providers": {}}

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config_path, config):
    """
    保存配置文件

    Args:
        config_path: 配置文件路径
        config: 配置内容
    """
    # 先写入临时文件
    temp_path = config_path.with_suffix('.json.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # 原子性替换
    temp_path.replace(config_path)


def validate_model_config(model_config):
    """
    验证模型配置

    Args:
        model_config: 模型配置

    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ["id", "name", "contextWindow", "maxTokens"]

    for field in required_fields:
        if field not in model_config:
            return False, f"缺少必需字段: {field}"

    # 验证数值类型
    if not isinstance(model_config["contextWindow"], int) or model_config["contextWindow"] <= 0:
        return False, "contextWindow 必须是正整数"

    if not isinstance(model_config["maxTokens"], int) or model_config["maxTokens"] <= 0:
        return False, "maxTokens 必须是正整数"

    if model_config["maxTokens"] > model_config["contextWindow"]:
        return False, "maxTokens 不能超过 contextWindow"

    # 验证成本配置（如果存在）
    if "cost" in model_config:
        cost = model_config["cost"]
        cost_fields = ["input", "output", "cacheRead", "cacheWrite"]

        for field in cost_fields:
            if field in cost:
                if not isinstance(cost[field], (int, float)) or cost[field] < 0:
                    return False, f"cost.{field} 必须是非负数"

    return True, None


def add_model(config_path, provider_id, provider_config, model_config, set_as_default=False, agent_path=None):
    """
    添加模型配置

    Args:
        config_path: models.json 路径
        provider_id: 提供商ID
        provider_config: 提供商配置
        model_config: 模型配置
        set_as_default: 是否设为默认模型
        agent_path: agent 路径（如果需要配置给特定 agent）

    Returns:
        dict: 操作结果
    """
    result = {
        "success": False,
        "backup_path": None,
        "message": "",
        "error": None
    }

    try:
        # 验证模型配置
        is_valid, error_msg = validate_model_config(model_config)
        if not is_valid:
            result["error"] = error_msg
            return result

        # 备份配置文件
        result["backup_path"] = str(backup_config(config_path))

        # 加载现有配置
        config = load_config(config_path)

        # 添加或更新提供商
        if provider_id not in config["providers"]:
            config["providers"][provider_id] = {}

        # 更新提供商配置（保留现有配置）
        provider = config["providers"][provider_id]
        for key, value in provider_config.items():
            provider[key] = value

        # 确保有 models 列表
        if "models" not in provider:
            provider["models"] = []

        # 检查模型是否已存在
        model_exists = False
        for i, existing_model in enumerate(provider["models"]):
            if existing_model["id"] == model_config["id"]:
                # 更新现有模型
                provider["models"][i] = model_config
                model_exists = True
                result["message"] = f"模型 {model_config['id']} 已更新"
                break

        if not model_exists:
            # 添加新模型
            provider["models"].append(model_config)
            result["message"] = f"模型 {model_config['id']} 已添加"

        # 保存配置
        save_config(config_path, config)

        # 如果需要设为默认模型
        if set_as_default:
            default_config_path = config_path.parent / "config.json"
            if default_config_path.exists():
                try:
                    with open(default_config_path, 'r', encoding='utf-8') as f:
                        default_config = json.load(f)

                    # 设置默认模型
                    default_config["model"] = f"{provider_id}/{model_config['id']}"

                    # 保存默认配置
                    temp_path = default_config_path.with_suffix('.json.tmp')
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(default_config, f, indent=2, ensure_ascii=False)
                    temp_path.replace(default_config_path)

                    result["message"] += "，已设为默认模型"
                except Exception as e:
                    result["message"] += f"（设置默认模型失败: {str(e)}）"

        # 如果需要配置给特定 agent
        if agent_path:
            agent_config_path = Path(agent_path) / "agent" / "config.json"
            if agent_config_path.exists():
                try:
                    with open(agent_config_path, 'r', encoding='utf-8') as f:
                        agent_config = json.load(f)

                    # 设置 agent 的默认模型
                    agent_config["model"] = f"{provider_id}/{model_config['id']}"

                    # 保存 agent 配置
                    temp_path = agent_config_path.with_suffix('.json.tmp')
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(agent_config, f, indent=2, ensure_ascii=False)
                    temp_path.replace(agent_config_path)

                    result["message"] += f"，已配置给 agent: {agent_path}"
                except Exception as e:
                    result["message"] += f"（配置 agent 失败: {str(e)}）"

        result["success"] = True

    except Exception as e:
        result["error"] = f"添加模型失败: {str(e)}"
        # 如果有备份，尝试恢复
        if result["backup_path"]:
            try:
                shutil.copy2(result["backup_path"], config_path)
                result["message"] += "（已从备份恢复）"
            except:
                pass

    return result


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: add_model.py <config_path> <provider_id> <provider_config_json> <model_config_json> [--default] [--agent <agent_path>]")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    provider_id = sys.argv[2]
    provider_config = json.loads(sys.argv[3])
    model_config = json.loads(sys.argv[4])

    set_as_default = "--default" in sys.argv
    agent_path = None
    if "--agent" in sys.argv:
        idx = sys.argv.index("--agent")
        if idx + 1 < len(sys.argv):
            agent_path = sys.argv[idx + 1]

    result = add_model(config_path, provider_id, provider_config, model_config, set_as_default, agent_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)