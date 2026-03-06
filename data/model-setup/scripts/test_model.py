#!/usr/bin/env python3
"""
测试模型配置是否有效
"""
import json
import sys
import subprocess
from pathlib import Path

def test_model_config(provider_config, model_id, test_tool_calling=False, test_streaming=False):
    """
    测试模型配置是否有效

    Args:
        provider_config: 提供商配置
        model_id: 模型ID
        test_tool_calling: 是否测试工具调用
        test_streaming: 是否测试流式输出

    Returns:
        dict: 测试结果
    """
    result = {
        "success": False,
        "api_key_valid": False,
        "model_accessible": False,
        "tool_calling": False,
        "streaming": False,
        "tool_calling_error": None,
        "streaming_error": None,
        "error": None
    }

    try:
        # 检查 API key 格式
        api_key = provider_config.get("apiKey", "")
        if not api_key:
            result["error"] = "API key 为空"
            return result

        # 更灵活的 API key 格式验证
        # 有些提供商使用 key_id:secret 格式，有些使用单一 token
        # 只要 API key 不为空且长度合理，就认为有效
        if len(api_key) < 10:
            result["error"] = "API key 格式不正确（长度太短）"
            return result

        result["api_key_valid"] = True

        # 尝试调用模型进行简单测试
        # 这里使用 curl 进行测试
        base_url = provider_config.get("baseUrl", "")
        api_type = provider_config.get("api", "openai-completions")

        if not base_url:
            result["error"] = "baseUrl 为空"
            return result

        # 构建测试请求
        test_url = f"{base_url}/chat/completions"

        # 准备测试 payload
        payload = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": "测试"}
            ],
            "max_tokens": 10
        }

        # 使用 curl 测试
        curl_cmd = [
            "curl", "-s", "-X", "POST", test_url,
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {api_key}",
            "-d", json.dumps(payload),
            "--connect-timeout", "10",
            "--max-time", "30"
        ]

        try:
            output = subprocess.check_output(curl_cmd, stderr=subprocess.PIPE, text=True)
            response = json.loads(output)

            # 检查响应
            if "choices" in response and len(response["choices"]) > 0:
                result["model_accessible"] = True
                result["success"] = True
            else:
                result["error"] = f"模型响应异常: {response.get('error', '未知错误')}"
        except subprocess.CalledProcessError as e:
            result["error"] = f"请求失败: {e.stderr}"
        except json.JSONDecodeError as e:
            result["error"] = f"响应解析失败: {str(e)}"

        # 测试工具调用功能
        if test_tool_calling and result["model_accessible"]:
            try:
                tool_payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "user", "content": "现在几点了？"}
                    ],
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "get_time",
                                "description": "获取当前时间",
                                "parameters": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            }
                        }
                    ],
                    "max_tokens": 50
                }

                tool_curl_cmd = [
                    "curl", "-s", "-X", "POST", test_url,
                    "-H", "Content-Type: application/json",
                    "-H", f"Authorization: Bearer {api_key}",
                    "-d", json.dumps(tool_payload),
                    "--connect-timeout", "10",
                    "--max-time", "30"
                ]

                tool_output = subprocess.check_output(tool_curl_cmd, stderr=subprocess.PIPE, text=True)
                tool_response = json.loads(tool_output)

                # 检查是否有 tool_calls
                if "choices" in tool_response and len(tool_response["choices"]) > 0:
                    message = tool_response["choices"][0].get("message", {})
                    if "tool_calls" in message and len(message["tool_calls"]) > 0:
                        result["tool_calling"] = True
                    else:
                        result["tool_calling_error"] = "模型未返回 tool_calls"
                else:
                    result["tool_calling_error"] = "工具调用测试响应异常"
            except subprocess.CalledProcessError as e:
                result["tool_calling_error"] = f"工具调用请求失败: {e.stderr}"
            except json.JSONDecodeError as e:
                result["tool_calling_error"] = f"工具调用响应解析失败: {str(e)}"
            except Exception as e:
                result["tool_calling_error"] = f"工具调用测试出错: {str(e)}"

        # 测试流式输出功能
        if test_streaming and result["model_accessible"]:
            try:
                stream_payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "user", "content": "测试"}
                    ],
                    "max_tokens": 10,
                    "stream": True
                }

                stream_curl_cmd = [
                    "curl", "-s", "-X", "POST", test_url,
                    "-H", "Content-Type: application/json",
                    "-H", f"Authorization: Bearer {api_key}",
                    "-d", json.dumps(stream_payload),
                    "--connect-timeout", "10",
                    "--max-time", "30"
                ]

                stream_output = subprocess.check_output(stream_curl_cmd, stderr=subprocess.PIPE, text=True)

                # 检查是否是 SSE 格式（以 "data: " 开头的多行）
                lines = stream_output.strip().split('\n')
                if len(lines) > 0 and any(line.startswith("data: ") for line in lines):
                    result["streaming"] = True
                else:
                    result["streaming_error"] = "响应不是 SSE 格式"
            except subprocess.CalledProcessError as e:
                result["streaming_error"] = f"流式输出请求失败: {e.stderr}"
            except Exception as e:
                result["streaming_error"] = f"流式输出测试出错: {str(e)}"

    except Exception as e:
        result["error"] = f"测试过程出错: {str(e)}"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: test_model.py <provider_config_json> <model_id> [--test-tool-calling] [--test-streaming]")
        sys.exit(1)

    provider_config = json.loads(sys.argv[1])
    model_id = sys.argv[2]
    test_tool_calling = "--test-tool-calling" in sys.argv
    test_streaming = "--test-streaming" in sys.argv

    result = test_model_config(provider_config, model_id, test_tool_calling, test_streaming)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)