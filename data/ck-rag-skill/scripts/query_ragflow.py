#!/usr/bin/env python3
"""
RAGFlow知识库查询脚本

使用方法:
    python3 query_ragflow.py "你的问题"

示例:
    python3 query_ragflow.py "容器挂了怎么办"

选项:
    -v, --verbose: 显示详细调试信息
"""

import sys
import json
import requests
from time import time, time as timestamp

# RAGFlow API配置
API_URL = "http://172.28.20.46:30001/v1/conversation/completion"
AUTHORIZATION = "IjQxYThhZGYyMDZlYjExZjFhZDE1ODJkYzljOWQ1YmJmIg.aYvfEw.ElppYHks0F5ETowUlvqA1Th-XHE"
COOKIE = "session=.elxVyzOegCAMAMC_dHagCgh8hIDaRleQyfh3jYmD4w13Qh5dWt4ZEizixBmNxgsbKkbknKkcxcy43siB/MyNqkb5CONuTR2yyWQKbarxVe7a9dNywRHnEaYvfEw66dir-0J0wYtii0IOGJ11861RtRtxp4"

# 固定的conversation_id，保持对话上下文
CONVERSATION_ID = "0e18393f0b6042f2bbf6b391c82835d1"

# 流式输出配置
STREAM_NO_DATA_TIMEOUT = 15.0    # 15秒无新数据则认为完成（给流式生成足够时间）
STREAM_MAX_TIMEOUT = 60.0        # 最大总等待时间60秒


def query_ragflow(question, verbose=False):
    """
    查询RAGFlow知识库

    Args:
        question (str): 用户问题
        verbose (bool): 是否输出调试信息

    Returns:
        dict: API响应结果
    """
    # 构建请求体
    payload = {
        "conversation_id": CONVERSATION_ID,
        "messages": [
            {
                "content": "你好！ 我是你的助理，有什么可以帮到你的吗？",
                "role": "assistant"
            },
            {
                "id": f"msg_{int(timestamp())}",
                "content": question,
                "role": "user",
                "files": [],
                "conversationId": CONVERSATION_ID
            }
        ]
    }

    # 请求头
    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": "application/json",
        "Cookie": COOKIE
    }

    if verbose:
        print(f"[调试] 发送请求到: {API_URL}")
        print(f"[调试] 请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    try:
        # 发送POST请求（启用流式传输，设置较长超时）
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            stream=True,
            timeout=120  # 120秒连接超时
        )
        response.raise_for_status()

        if verbose:
            print(f"[调试] 响应状态码: {response.status_code}")
            print("[调试] 开始接收流式数据...")
            print("[调试] 等待完整响应生成，请稍候...")

        # 解析SSE流
        full_answer = ""
        references = []
        message_id = None
        last_answer_length = 0
        last_activity_time = time()
        start_time = time()
        line_count = 0
        chunk_count = 0

        for line in response.iter_lines(decode_unicode=True):
            line_count += 1

            # 检查是否超过最大超时时间
            if time() - start_time > STREAM_MAX_TIMEOUT:
                if verbose:
                    print(f"\n[调试] 达到最大超时时间 ({STREAM_MAX_TIMEOUT}秒)")
                break

            # 更新活动时间
            last_activity_time = time()

            if line.startswith('data:'):
                try:
                    # 去掉"data:"前缀并解析JSON
                    json_str = line[5:].strip()
                    if json_str and json_str != '[DONE]':  # 跳过结束标记
                        data = json.loads(json_str)

                        # 确保data是dict类型
                        if not isinstance(data, dict):
                            continue

                        # 提取答案
                        if "data" in data and isinstance(data["data"], dict) and "answer" in data["data"]:
                            # 只在第一次出现消息ID时记录
                            if message_id is None and "id" in data["data"]:
                                message_id = data["data"]["id"]
                                if verbose:
                                    print(f"[调试] 消息ID: {message_id}")

                            # 累积答案内容（流式输出）
                            answer_chunk = data["data"]["answer"]
                            full_answer += answer_chunk
                            chunk_count += 1

                            # 打印进度（每100个字符打印一个点）
                            if len(full_answer) - last_answer_length > 100:
                                print(f".", end="", flush=True)
                                last_answer_length = len(full_answer)

                        # 提取引用
                        if "data" in data and isinstance(data["data"], dict) and "reference" in data["data"]:
                            chunks = data["data"]["reference"].get("chunks", [])
                            if isinstance(chunks, list):
                                references.extend(chunks)

                except (json.JSONDecodeError, TypeError) as e:
                    if verbose:
                        print(f"\n[调试] 跳过无效数据行: {e}")
                    continue

            # 检查是否超时（长时间无新数据）
            if time() - last_activity_time > STREAM_NO_DATA_TIMEOUT:
                if verbose:
                    print(f"\n[调试] {STREAM_NO_DATA_TIMEOUT}秒无新数据，接收完成")
                break

        # 如果有点没换行，换行
        if len(full_answer) - last_answer_length > 0:
            print()

        if verbose:
            print(f"[调试] 共处理 {line_count} 行数据，{chunk_count} 个数据块")
            print(f"[调试] 总耗时: {time() - start_time:.2f}秒")
            print(f"[调试] 答案长度: {len(full_answer)} 字符")

        return {
            "error": False,
            "answer": full_answer,
            "references": references,
            "message_id": message_id,
            "stats": {
                "lines": line_count,
                "chunks": chunk_count,
                "duration": time() - start_time
            }
        }

    except requests.exceptions.Timeout as e:
        return {
            "error": True,
            "message": f"API请求超时: {str(e)}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": f"API请求失败: {str(e)}"
        }


def format_response(result, verbose=False):
    """
    格式化API响应结果

    Args:
        result (dict): API响应结果
        verbose (bool): 是否输出调试信息

    Returns:
        str: 格式化后的文本
    """
    if result.get("error"):
        print(f"[错误] {result['message']}")
        return None

    # 返回答案
    answer = result.get("answer", "")

    # 如果有引用，显示引用信息
    references = result.get("references", [])
    if references and references[0]:  # 确保引用列表不为空
        answer += "\n\n[引用文档]"
        for ref in references:
            if isinstance(ref, dict):
                doc_name = ref.get("doc_name", "未知文档")
                answer += f"\n- {doc_name}"

    return answer if answer.strip() else None


def main():
    """主函数"""
    # 检查参数
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # 提取问题（跳过-v选项）
    args = [arg for arg in sys.argv[1:] if arg not in ["--verbose", "-v"]]

    if not args:
        print("使用方法: python3 query_ragflow.py \"你的问题\" [选项]")
        print("示例:")
        print("  python3 query_ragflow.py \"容器挂了怎么办\"")
        print("  python3 query_ragflow.py \"容器挂了怎么办\" -v")
        sys.exit(1)

    question = " ".join(args)

    print(f"[查询] {question}")
    print("-" * 80)

    # 查询RAGFlow
    result = query_ragflow(question, verbose)

    # 格式化输出
    answer = format_response(result, verbose)

    if answer:
        print(answer)
        print("-" * 80)
        stats = result.get("stats", {})
        duration = stats.get("duration", 0)
        print(f"[成功] 查询完成 (耗时: {duration:.2f}秒)")
    else:
        print("[失败] 未获取到有效回答")

    # 输出完整响应（调试用）
    if verbose:
        print("\n[完整响应]")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
