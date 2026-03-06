#!/usr/bin/env python3
"""
微信Xlog日志统计分析脚本

功能:
- 统计日志级别分布
- 提取错误和警告信息
- 按模块分类统计
- 分析时间分布
- 生成结构化统计报告

使用方式:
    python log_analyzer.py <parsed_data_file> [-o OUTPUT] [--module MODULE]

参数说明:
    parsed_data_file: 解析后的日志JSON文件路径
    -o OUTPUT: 输出文件路径（默认：analysis_result.json）
    --module MODULE: 分析特定模块
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List


def load_parsed_data(file_path: str) -> Dict:
    """
    加载解析后的日志数据

    Args:
        file_path: 日志JSON文件路径

    Returns:
        日志数据字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}", file=sys.stderr)
        sys.exit(1)


def analyze_by_level(logs: List[Dict]) -> Dict:
    """
    按日志级别统计分析

    Args:
        logs: 日志列表

    Returns:
        级别统计结果
    """
    level_stats = Counter()
    level_logs = defaultdict(list)

    for log in logs:
        level = log['level']
        level_stats[level] += 1
        level_logs[level].append(log)

    return {
        'counts': dict(level_stats),
        'details': {level: len(items) for level, items in level_logs.items()}
    }


def analyze_by_module(logs: List[Dict], module_filter: str = None) -> Dict:
    """
    按模块统计分析

    Args:
        logs: 日志列表
        module_filter: 模块名过滤

    Returns:
        模块统计结果
    """
    module_stats = Counter()
    module_logs = defaultdict(list)

    for log in logs:
        module = log['module']
        if module_filter and module != module_filter:
            continue
        module_stats[module] += 1
        module_logs[module].append(log)

    # 排序模块（按日志数量降序）
    sorted_modules = sorted(module_stats.items(), key=lambda x: x[1], reverse=True)

    return {
        'counts': dict(sorted_modules),
        'total_modules': len(module_stats),
        'top_modules': sorted_modules[:10],  # Top 10模块
        'details': {module: items[:100] for module, items in module_logs.items()}
    }


def extract_errors(logs: List[Dict]) -> Dict:
    """
    提取错误和警告信息

    Args:
        logs: 日志列表

    Returns:
        错误信息统计
    """
    error_logs = []
    warn_logs = []
    fatal_logs = []

    for log in logs:
        level = log['level']
        if level == 'ERROR':
            error_logs.append(log)
        elif level == 'WARN':
            warn_logs.append(log)
        elif level == 'FATAL':
            fatal_logs.append(log)

    return {
        'error_count': len(error_logs),
        'error_samples': error_logs[:50],  # 前50个错误
        'warn_count': len(warn_logs),
        'warn_samples': warn_logs[:50],    # 前50个警告
        'fatal_count': len(fatal_logs),
        'fatal_samples': fatal_logs[:20]   # 前20个致命错误
    }


def analyze_time_distribution(logs: List[Dict]) -> Dict:
    """
    分析时间分布

    Args:
        logs: 日志列表

    Returns:
        时间分布统计
    """
    time_buckets = defaultdict(int)
    hourly_stats = defaultdict(int)

    for log in logs:
        timestamp_str = log.get('timestamp', '')
        if not timestamp_str:
            continue

        try:
            # 尝试解析时间戳（多种格式）
            # 格式1: 2024-01-01 10:00:00.123
            if '-' in timestamp_str:
                dt = datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                hour_key = dt.strftime('%Y-%m-%d %H:00')
            # 格式2: 01/01 10:00:00.123
            elif '/' in timestamp_str:
                dt = datetime.strptime(timestamp_str.split('.')[0], '%m/%d %H:%M:%S')
                hour_key = f"{dt.month:02d}/{dt.day:02d} {dt.hour:02d}:00"
            else:
                continue

            hourly_stats[hour_key] += 1

            # 按小时分桶
            bucket = f"{dt.hour:02d}:00"
            time_buckets[bucket] += 1

        except (ValueError, IndexError):
            continue

    return {
        'hourly_distribution': dict(hourly_stats),
        'time_bucket': dict(time_buckets)
    }


def generate_report(data: Dict, module_filter: str = None) -> Dict:
    """
    生成完整分析报告

    Args:
        data: 解析后的日志数据
        module_filter: 模块名过滤

    Returns:
        分析报告
    """
    logs = data.get('logs', [])

    # 执行各项分析
    level_analysis = analyze_by_level(logs)
    module_analysis = analyze_by_module(logs, module_filter)
    error_analysis = extract_errors(logs)
    time_analysis = analyze_time_distribution(logs)

    # 生成报告
    report = {
        'summary': {
            'total_logs': len(logs),
            'error_count': error_analysis['error_count'],
            'warn_count': error_analysis['warn_count'],
            'fatal_count': error_analysis['fatal_count'],
            'total_modules': module_analysis['total_modules'],
            'time_range': len(time_analysis['hourly_distribution'])
        },
        'level_analysis': level_analysis,
        'module_analysis': module_analysis,
        'error_analysis': error_analysis,
        'time_analysis': time_analysis,
        'recommendations': generate_recommendations(
            level_analysis,
            error_analysis,
            module_analysis
        )
    }

    return report


def generate_recommendations(level_analysis: Dict,
                            error_analysis: Dict,
                            module_analysis: Dict) -> List[str]:
    """
    生成分析建议

    Args:
        level_analysis: 级别分析结果
        error_analysis: 错误分析结果
        module_analysis: 模块分析结果

    Returns:
        建议列表
    """
    recommendations = []

    # 错误数量检查
    error_count = error_analysis['error_count']
    if error_count > 100:
        recommendations.append(
            f"错误数量较多({error_count}条)，建议重点排查错误日志"
        )
    elif error_count > 0:
        recommendations.append(
            f"发现{error_count}条错误日志，建议检查错误详情"
        )

    # 致命错误检查
    fatal_count = error_analysis['fatal_count']
    if fatal_count > 0:
        recommendations.append(
            f"发现{fatal_count}条致命错误，需立即处理"
        )

    # 警告数量检查
    warn_count = error_analysis['warn_count']
    if warn_count > error_count * 5:
        recommendations.append(
            f"警告数量({warn_count}条)远超错误数量，可能存在潜在问题"
        )

    # 模块分布检查
    top_modules = module_analysis.get('top_modules', [])
    if top_modules and len(top_modules) > 0:
        top_module = top_modules[0]
        top_count = top_module[1]
        total = module_analysis.get('counts', {}).get(top_module[0], 0)

        if top_count > total * 0.5:
            recommendations.append(
                f"模块'{top_module[0]}'日志占比过高({top_count}条)，可能是问题集中点"
            )

    # 日志级别分布检查
    level_counts = level_analysis.get('counts', {})
    if 'DEBUG' in level_counts and 'INFO' in level_counts:
        debug_ratio = level_counts['DEBUG'] / max(level_counts['INFO'], 1)
        if debug_ratio > 10:
            recommendations.append(
                "DEBUG级别日志过多，建议在生产环境减少DEBUG输出"
            )

    if not recommendations:
        recommendations.append("日志状态良好，未发现明显异常")

    return recommendations


def save_report(report: Dict, output_path: str):
    """
    保存分析报告

    Args:
        report: 分析报告
        output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"分析完成")
        print(f"报告已保存到: {output_path}")
        print(f"\n摘要:")
        print(f"  总日志数: {report['summary']['total_logs']}")
        print(f"  错误数: {report['summary']['error_count']}")
        print(f"  警告数: {report['summary']['warn_count']}")
        print(f"  模块数: {report['summary']['total_modules']}")
        print(f"\n建议:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    except Exception as e:
        print(f"错误: 保存报告失败 - {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='分析解析后的Xlog日志数据'
    )
    parser.add_argument(
        'data_file',
        help='解析后的日志JSON文件路径'
    )
    parser.add_argument(
        '-o', '--output',
        default='analysis_result.json',
        help='输出文件路径（默认：analysis_result.json）'
    )
    parser.add_argument(
        '--module',
        help='分析特定模块'
    )

    args = parser.parse_args()

    # 加载数据
    data = load_parsed_data(args.data_file)

    # 生成报告
    report = generate_report(data, module_filter=args.module)

    # 保存报告
    save_report(report, args.output)


if __name__ == '__main__':
    main()
