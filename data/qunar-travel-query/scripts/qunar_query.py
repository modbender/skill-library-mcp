#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去哪儿网API查询脚本
提供统一的API调用接口，支持多种查询类型
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional
from coze_workload_identity import requests


def load_api_key() -> str:
    """
    从环境变量加载去哪儿网API Key
    
    凭证Key: COZE_QUNAR_API_KEY_7612643102733467667
    """
    skill_id = "7612643102733467667"
    api_key = os.getenv(f"COZE_QUNAR_API_KEY_{skill_id}")
    
    if not api_key:
        raise ValueError(
            "未找到去哪儿网API Key配置。请先配置凭证：\n"
            "1. 确保已通过凭证配置流程设置 qunar_api_key\n"
            "2. 重新运行查询"
        )
    
    return api_key


def query_qunar_api(
    query_type: str,
    api_endpoint: str,
    api_params: Dict[str, Any],
    method: str = "POST",
    output_format: str = "list"
) -> Dict[str, Any]:
    """
    查询去哪儿网API
    
    Args:
        query_type: 查询类型（flight/hotel/scenic/train）
        api_endpoint: API端点URL
        api_params: 查询参数字典
        method: HTTP方法（GET/POST）
        output_format: 输出格式（list/detail/conversation）
    
    Returns:
        查询结果字典，包含：
        - success: 是否成功
        - data: 返回数据
        - error: 错误信息（如有）
        - query_type: 查询类型
        - output_format: 输出格式
    """
    result = {
        "success": False,
        "data": None,
        "error": None,
        "query_type": query_type,
        "output_format": output_format,
        "api_endpoint": api_endpoint
    }
    
    try:
        # 1. 加载API Key
        api_key = load_api_key()
        
        # 2. 构建请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": api_key
        }
        
        # 3. 发起请求
        if method.upper() == "GET":
            response = requests.get(
                api_endpoint,
                headers=headers,
                params=api_params,
                timeout=30
            )
        else:
            response = requests.post(
                api_endpoint,
                headers=headers,
                json=api_params,
                timeout=30
            )
        
        # 4. 检查HTTP状态码
        if response.status_code >= 400:
            error_msg = f"HTTP请求失败: 状态码 {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f", 响应内容: {json.dumps(error_detail, ensure_ascii=False)}"
            except:
                error_msg += f", 响应内容: {response.text}"
            raise Exception(error_msg)
        
        # 5. 解析响应
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"raw_response": response.text}
        
        # 6. 检查业务错误
        if isinstance(data, dict):
            # 去哪儿网API常见的错误字段
            error_code = data.get("errcode") or data.get("code") or data.get("errorCode")
            if error_code and error_code != 0:
                error_msg = data.get("errmsg") or data.get("message") or data.get("errorMsg") or "未知错误"
                raise Exception(f"API业务错误[{error_code}]: {error_msg}")
        
        # 7. 返回成功结果
        result["success"] = True
        result["data"] = data
        
        return result
        
    except ValueError as e:
        # API Key未配置
        result["error"] = str(e)
        return result
    except requests.exceptions.RequestException as e:
        # 网络请求异常
        result["error"] = f"网络请求失败: {str(e)}"
        return result
    except Exception as e:
        # 其他异常
        result["error"] = f"查询失败: {str(e)}"
        return result


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="去哪儿网API查询工具")
    
    parser.add_argument(
        "--query_type",
        required=True,
        choices=["flight", "hotel", "scenic", "train"],
        help="查询类型：flight=机票, hotel=酒店, scenic=景点, train=火车票"
    )
    
    parser.add_argument(
        "--api_endpoint",
        required=True,
        help="API端点URL（根据去哪儿网API文档填写）"
    )
    
    parser.add_argument(
        "--api_params",
        required=True,
        help="API查询参数（JSON格式字符串），例如：'{\"fromCity\":\"北京\",\"toCity\":\"上海\",\"departDate\":\"2024-01-15\"}'"
    )
    
    parser.add_argument(
        "--method",
        default="POST",
        choices=["GET", "POST"],
        help="HTTP方法（默认：POST）"
    )
    
    parser.add_argument(
        "--output_format",
        default="list",
        choices=["list", "detail", "conversation"],
        help="输出格式：list=列表, detail=详细, conversation=对话式（默认：list）"
    )
    
    args = parser.parse_args()
    
    # 解析API参数
    try:
        api_params = json.loads(args.api_params)
    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": f"API参数格式错误，必须是有效的JSON格式：{args.api_params}"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 执行查询
    result = query_qunar_api(
        query_type=args.query_type,
        api_endpoint=args.api_endpoint,
        api_params=api_params,
        method=args.method,
        output_format=args.output_format
    )
    
    # 输出结果（JSON格式）
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 根据结果设置退出码
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
