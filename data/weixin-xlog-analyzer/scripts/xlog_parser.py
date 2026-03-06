#!/usr/bin/env python3
"""
微信Xlog日志解析脚本

功能:
- 解析Xlog明文日志文件
- 提取时间戳、日志级别、模块名、消息内容
- 支持多种日志格式
- 输出结构化JSON数据

使用方式:
    python xlog_parser.py <log_file_path> [-o OUTPUT] [--level LEVEL] [--module MODULE]

参数说明:
    log_file_path: 日志文件路径
    -o OUTPUT: 输出文件路径（默认：parsed_logs.json）
    --level LEVEL: 过滤日志级别（ERROR, WARN, INFO, DEBUG）
    --module MODULE: 过滤模块名称
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional


# 常见日志格式正则表达式
# 格式1: [时间戳] [级别] [模块名] 消息内容
# 示例: [2024-01-01 10:00:00.123] [ERROR] [Network] Connection failed
LOG_PATTERN_1 = re.compile(
    r'^\[([\d\-:\s\.]+)\]\s+\[(\w+)\]\s+\[([^\]]+)\]\s+(.+)$'
)

# 格式2: 时间戳 级别 模块名: 消息内容
# 示例: 2024-01-01 10:00:00.123 ERROR Network: Connection failed
LOG_PATTERN_2 = re.compile(
    r'^([\d\-:\s\.]+)\s+(\w+)\s+([^:]+):\s+(.+)$'
)

# 格式3: MM/dd HH:mm:ss.vvv 级别/模块: 消息内容
# 示例: 01/01 10:00:00.123 E/Network: Connection failed
LOG_PATTERN_3 = re.compile(
    r'^(\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+([A-Z])/([^:]+):\s+(.+)$'
)

# 日志级别映射
LEVEL_MAP = {
    'E': 'ERROR',
    'W': 'WARN',
    'I': 'INFO',
    'D': 'DEBUG',
    'V': 'VERBOSE',
    'F': 'FATAL'
}


def parse_log_line(line: str) -> Optional[Dict]:
    """
    解析单行日志

    Args:
        line: 日志行内容

    Returns:
        解析后的日志字典，如果解析失败返回None
    """
    line = line.strip()
    if not line:
        return None

    # 尝试匹配格式1
    match = LOG_PATTERN_1.match(line)
    if match:
        timestamp_str, level, module, message = match.groups()
        return {
            'timestamp': timestamp_str,
            'level': level,
            'module': module,
            'message': message,
            'raw': line
        }

    # 尝试匹配格式2
    match = LOG_PATTERN_2.match(line)
    if match:
        timestamp_str, level, module, message = match.groups()
        return {
            'timestamp': timestamp_str,
            'level': level,
            'module': module.strip(),
            'message': message,
            'raw': line
        }

    # 尝试匹配格式3
    match = LOG_PATTERN_3.match(line)
    if match:
        timestamp_str, level_short, module, message = match.groups()
        level = LEVEL_MAP.get(level_short, level_short)
        return {
            'timestamp': timestamp_str,
            'level': level,
            'module': module,
            'message': message,
            'raw': line
        }

    # 如果都不匹配，作为原始消息处理
    return {
        'timestamp': '',
        'level': 'UNKNOWN',
        'module': 'UNKNOWN',
        'message': line,
        'raw': line
    }


def parse_log_file(
    file_path: str,
    level_filter: Optional[str] = None,
    module_filter: Optional[str] = None
) -> List[Dict]:
    """
    解析日志文件

    Args:
        file_path: 日志文件路径
        level_filter: 日志级别过滤
        module_filter: 模块名过滤

    Returns:
        解析后的日志列表
    """
    logs = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                parsed = parse_log_line(line)
                if parsed:
                    # 应用过滤条件
                    if level_filter and parsed['level'] != level_filter:
                        continue
                    if module_filter and parsed['module'] != module_filter:
                        continue

                    parsed['line_number'] = line_num
                    logs.append(parsed)

    except FileNotFoundError:
        print(f"错误: 文件不存在 - {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}", file=sys.stderr)
        sys.exit(1)

    return logs


def save_results(logs: List[Dict], output_path: str):
    """
    保存解析结果到JSON文件

    Args:
        logs: 解析后的日志列表
        output_path: 输出文件路径
    """
    result = {
        'total_count': len(logs),
        'logs': logs,
        'summary': {
            'by_level': {},
            'by_module': {}
        }
    }

    # 生成统计摘要
    for log in logs:
        level = log['level']
        module = log['module']

        result['summary']['by_level'][level] = \
            result['summary']['by_level'].get(level, 0) + 1
        result['summary']['by_module'][module] = \
            result['summary']['by_module'].get(module, 0) + 1

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"解析完成: 共解析 {len(logs)} 条日志")
        print(f"结果已保存到: {output_path}")
        print(f"日志级别分布: {result['summary']['by_level']}")
    except Exception as e:
        print(f"错误: 保存文件失败 - {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='解析微信Xlog日志文件'
    )
    parser.add_argument(
        'log_file',
        help='日志文件路径'
    )
    parser.add_argument(
        '-o', '--output',
        default='parsed_logs.json',
        help='输出文件路径（默认：parsed_logs.json）'
    )
    parser.add_argument(
        '--level',
        choices=['ERROR', 'WARN', 'INFO', 'DEBUG', 'VERBOSE', 'FATAL'],
        help='过滤日志级别'
    )
    parser.add_argument(
        '--module',
        help='过滤模块名称'
    )

    args = parser.parse_args()

    # 解析日志文件
    logs = parse_log_file(
        args.log_file,
        level_filter=args.level,
        module_filter=args.module
    )

    # 保存结果
    save_results(logs, args.output)


if __name__ == '__main__':
    main()
