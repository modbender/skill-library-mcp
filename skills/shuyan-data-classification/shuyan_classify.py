#!/usr/bin/env python3
"""
数安云智数据分类分级同步接口
用法: python shuyan_classify.py <command> [args...]

安装依赖:
    pip install requests

环境变量:
    SHUYAN_API_KEY   - API认证密钥
    SHUYAN_API_URL  - API地址 (默认: http://localhost:8080)
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, List, Dict, Any

API_KEY = os.environ.get("SHUYAN_API_KEY", "sk-secret-key")
API_URL = os.environ.get("SHUYAN_API_URL", "http://localhost:8080")
ENDPOINT = "/api/llm_infer_zh_and_cls_and_type_v2_batchdata_sync"


class ShuyanClassifier:
    """数安云智数据分类分级接口封装"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or API_KEY
        self.api_url = api_url or API_URL
        self.endpoint = f"{self.api_url}{ENDPOINT}"
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def classify_single(
        self,
        col_name_ch: str,
        col_name_comment: str,
        col_name_en: str = "",
        project_name: str = "default",
        standard_code: str = "llm_infer_zh_and_cls_and_type_v2_test",
        sensitivity_key: str = "fenji_standard",
        **kwargs
    ) -> Dict[str, Any]:
        """单字段分类"""
        data = {
            "colNameCh": col_name_ch,
            "colNameComment": col_name_comment,
            "colNameEn": col_name_en,
            "projectName": project_name,
            "standardCode": standard_code,
            "sensitivityLevelRedisKey": sensitivity_key,
        }
        # 添加其他可选字段
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        
        response = requests.post(
            self.endpoint,
            headers=self._headers(),
            json=[data],
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def classify_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """批量分类"""
        response = requests.post(
            self.endpoint,
            headers=self._headers(),
            json=items,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


def cmd_classify(args):
    """单字段分类命令"""
    classifier = ShuyanClassifier(args.api_key, args.api_url)
    
    try:
        result = classifier.classify_single(
            col_name_ch=args.column_ch,
            col_name_comment=args.comment,
            col_name_en=args.column_en or "",
            project_name=args.project or "default"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_classify_batch(args):
    """批量分类命令"""
    classifier = ShuyanClassifier(args.api_key, args.api_url)
    
    # 读取JSON文件
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件不存在: {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON格式错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = classifier.classify_batch(items)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_test(args):
    """测试连接"""
    classifier = ShuyanClassifier(args.api_key, args.api_url)
    
    test_data = [{
        "colNameCh": "测试字段",
        "colNameComment": "测试用字段",
        "colNameEn": "test_field",
        "projectName": "测试系统",
        "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
        "sensitivityLevelRedisKey": "fenji_standard"
    }]
    
    try:
        result = classifier.classify_batch(test_data)
        print("✅ API连接成功!")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接失败: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_health(args):
    """健康检查"""
    classifier = ShucanClassifier(args.api_key, args.api_url)
    
    if classifier.health_check():
        print("✅ 服务健康")
    else:
        print("❌ 服务不可用")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="数安云智数据分类分级同步接口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s classify 用户姓名 用户真实姓名 user_name 用户系统
  %(prog)s classify-batch data.json
  %(prog)s test
  %(prog)s health

环境变量:
  SHUYAN_API_KEY   API认证密钥 (默认: sk-secret-key)
  SHUYAN_API_URL  API地址 (默认: http://localhost:8080)
        """
    )
    
    parser.add_argument(
        "--api-key",
        default=None,
        help="API认证密钥"
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="API服务地址"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # classify 命令
    parser_classify = subparsers.add_parser(
        "classify",
        help="单字段分类"
    )
    parser_classify.add_argument("column_ch", help="字段中文名")
    parser_classify.add_argument("comment", help="字段含义/注释")
    parser_classify.add_argument("column_en", nargs="?", default="", help="字段英文名")
    parser_classify.add_argument("project", nargs="?", default="default", help="项目/系统名称")
    parser_classify.set_defaults(func=cmd_classify)
    
    # classify-batch 命令
    parser_batch = subparsers.add_parser(
        "classify-batch",
        help="批量字段分类"
    )
    parser_batch.add_argument("file", help="JSON文件路径")
    parser_batch.set_defaults(func=cmd_classify_batch)
    
    # test 命令
    parser_test = subparsers.add_parser(
        "test",
        help="测试API连接"
    )
    parser_test.set_defaults(func=cmd_test)
    
    # health 命令
    parser_health = subparsers.add_parser(
        "health",
        help="健康检查"
    )
    parser_health.set_defaults(func=cmd_health)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
