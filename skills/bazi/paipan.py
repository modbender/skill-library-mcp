#!/usr/bin/env python3
import argparse
import requests
import json
import sys


def paipan_api(name="张三", gender=None, birthday_str=None):
    """
    调用 bagezi.top 的排盘API
    
    Args:
        name: 姓名，默认为"张三"
        gender: 性别（必填）
        birthday_str: 出生日期字符串（必填）
    
    Returns:
        API响应的JSON数据
    """
    # 验证必填参数
    if gender is None:
        raise ValueError("gender 是必填参数")
    if birthday_str is None:
        raise ValueError("birthday_str 是必填参数")
    
    # 设置请求头
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Host": "bagezi.top",
        "Connection": "keep-alive"
    }
    
    # 设置请求体
    body = {
        "name": name,
        "gender": gender,
        "birthday_str": birthday_str
    }
    
    # 发送POST请求
    response = requests.post(
        'http://bagezi.top/api/paipan',
        headers=headers,
        json=body
    )
    
    # 检查响应状态
    response.raise_for_status()
    
    # 返回JSON格式的响应
    return response.json()


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description='调用 bagezi.top 排盘API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python script.py -g 男 -b "1990-01-01 12:00"
  python script.py -n 李四 -g 女 -b "1995-05-20 08:30"
  python script.py --gender 男 --birthday_str "1988-12-12"
        """
    )
    
    # 添加参数
    parser.add_argument(
        '-n', '--name',
        type=str,
        default='张三',
        help='姓名 (默认: 张三)'
    )
    
    parser.add_argument(
        '-g', '--gender',
        type=str,
        required=True,
        help='性别 (必填)'
    )
    
    parser.add_argument(
        '-b', '--birthday_str',
        type=str,
        required=True,
        help='出生日期字符串 (必填)'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    try:
        # 调用API
        result = paipan_api(
            name=args.name,
            gender=args.gender,
            birthday_str=args.birthday_str
        )
        
        # 美化输出JSON结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except ValueError as e:
        print(f"参数错误: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout as e:
        print(f"请求超时: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()