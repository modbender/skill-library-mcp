#!/usr/bin/env python3
"""
TRTC Config Inspector 主入口脚本。
串联完整流程：下载资源 → 解析 Excel → 对比差异 → 扫描代码 → 输出修改建议。

用法:
  python3 run_inspector.py \
    --config-url "场景配置Excel的URL或本地路径" \
    --inspect-url "巡检结果Excel的URL或本地路径" \
    --code-url "代码压缩包的URL或本地目录路径" \
    --output-dir "./workspace"

输出: JSON 格式的完整巡检报告，包含差异项、代码定位和修改建议。
"""

import argparse
import glob
import json
import os
import re
import sys

# 确保能导入同目录下的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_files import download_and_extract
from parse_excel import parse_config_excel, parse_inspect_excel
from diff_config import diff_configs


def find_source_files(code_dir, extensions=None):
    """在代码目录中递归查找源码文件。"""
    if extensions is None:
        extensions = ['.kt', '.java', '.swift', '.m', '.mm']

    source_files = []
    for root, dirs, files in os.walk(code_dir):
        # 跳过构建目录
        dirs[:] = [d for d in dirs if d not in ('build', '.gradle', '.idea', 'node_modules', '__pycache__')]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in extensions:
                source_files.append(os.path.join(root, f))
    return source_files


def detect_platform(filepath):
    """根据文件扩展名检测平台。"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.kt', '.java'):
        return 'android'
    elif ext in ('.swift', '.m', '.mm'):
        return 'ios'
    return 'unknown'


def scan_trtc_calls(filepath):
    """扫描文件中的 TRTC API 调用，返回调用信息列表。"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    calls = []
    lines = content.split('\n')

    # 匹配 TRTC 相关 API 调用
    patterns = {
        'enterRoom': r'\.enterRoom\s*\(',
        'startLocalAudio': r'\.startLocalAudio\s*\(',
        'setSystemVolumeType': r'\.setSystemVolumeType\s*\(',
        'setVideoEncoderParam': r'\.setVideoEncoderParam\s*\(',
        'startLocalPreview': r'\.startLocalPreview\s*\(',
        'callExperimentalAPI': r'\.callExperimentalAPI\s*\(',
        'setAudioCaptureVolume': r'\.setAudioCaptureVolume\s*\(',
        'setAudioPlayoutVolume': r'\.setAudioPlayoutVolume\s*\(',
        'sharedInstance': r'(?:TRTCCloud\.sharedInstance|sharedInstance)\s*\(',
        'setListener': r'\.setListener\s*\(',
    }

    for line_num, line in enumerate(lines, 1):
        for api_name, pattern in patterns.items():
            if re.search(pattern, line):
                calls.append({
                    'api': api_name,
                    'line': line_num,
                    'code': line.strip(),
                })

    return calls


def analyze_code(code_dir):
    """分析代码目录，返回 TRTC 配置使用情况。"""
    source_files = find_source_files(code_dir)

    analysis = {
        "source_files": [],
        "trtc_files": [],
        "api_calls": {},
        "platform": "unknown"
    }

    for filepath in source_files:
        rel_path = os.path.relpath(filepath, code_dir)
        analysis["source_files"].append(rel_path)

        calls = scan_trtc_calls(filepath)
        if calls:
            platform = detect_platform(filepath)
            analysis["platform"] = platform
            analysis["trtc_files"].append({
                "file": rel_path,
                "absolute_path": filepath,
                "platform": platform,
                "calls": calls
            })

            for call in calls:
                api = call['api']
                if api not in analysis["api_calls"]:
                    analysis["api_calls"][api] = []
                analysis["api_calls"][api].append({
                    "file": rel_path,
                    "line": call['line'],
                    "code": call['code']
                })

    return analysis


def generate_modification_plan(diff_report, code_analysis):
    """根据差异报告和代码分析，生成修改计划。"""
    plan = {
        "modifications": [],
        "new_calls_needed": [],
        "optional_items": [],
        "warnings": []
    }

    for diff_item in diff_report.get("diffs", []):
        config_name = diff_item["config_name"]
        target_value = diff_item.get("target_value", "")
        current_value = diff_item.get("current_value", "")

        mod = {
            "config_name": config_name,
            "section": diff_item.get("section", ""),
            "current_value": current_value,
            "target_value": target_value,
            "suggestion": diff_item.get("suggestion", ""),
            "code_locations": [],
            "action": "modify"
        }

        # 映射配置项到 API 调用
        api_mapping = {
            "进房模式 scene": "enterRoom",
            "进房模式": "enterRoom",
            "音质类型": "startLocalAudio",
            "系统音量类型": "setSystemVolumeType",
            "视频编码参数": "setVideoEncoderParam",
            "采集音量": "setAudioCaptureVolume",
            "远端播放音量": "setAudioPlayoutVolume",
        }

        config_key = config_name.lower().strip()
        target_api = None
        for key, api in api_mapping.items():
            if key in config_key:
                target_api = api
                break

        if target_api and target_api in code_analysis.get("api_calls", {}):
            mod["code_locations"] = code_analysis["api_calls"][target_api]
        elif target_api:
            mod["action"] = "add"
            mod["code_locations"] = []
            plan["new_calls_needed"].append({
                "api": target_api,
                "config_name": config_name,
                "target_value": target_value
            })

        plan["modifications"].append(mod)

    # 处理可选项
    for item in diff_report.get("unable_to_compare", []):
        target_value = item.get("target_value", "")
        if "可选" in target_value or "optional" in target_value.lower():
            plan["optional_items"].append(item)

    return plan


def run_inspector(config_url=None, inspect_url=None, code_url=None, output_dir=None):
    """执行完整巡检流程。"""
    result = {
        "status": "success",
        "steps": {},
        "diff_report": None,
        "code_analysis": None,
        "modification_plan": None,
        "errors": []
    }

    # Step 1: 下载资源
    print("=" * 60, file=sys.stderr)
    print("Step 1: 下载资源文件", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    download_result = download_and_extract(
        config_url=config_url,
        inspect_url=inspect_url,
        code_url=code_url,
        output_dir=output_dir
    )
    result["steps"]["download"] = download_result

    if download_result.get("errors"):
        for err in download_result["errors"]:
            result["errors"].append(f"下载阶段: {err}")

    config_path = download_result.get("config_excel")
    inspect_path = download_result.get("inspect_excel")
    code_dir = download_result.get("code_dir")

    # Step 2: 解析对比
    print("\n" + "=" * 60, file=sys.stderr)
    print("Step 2: 解析并对比配置", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if config_path and inspect_path:
        try:
            config_data = parse_config_excel(config_path)
            inspect_data = parse_inspect_excel(inspect_path)
            diff_report = diff_configs(inspect_data, config_data)
            result["diff_report"] = diff_report
            result["steps"]["diff"] = {
                "status": "success",
                "diffs_count": len(diff_report.get("diffs", [])),
                "matches_count": len(diff_report.get("matches", [])),
                "unable_count": len(diff_report.get("unable_to_compare", []))
            }
            print(f"对比完成: {len(diff_report.get('diffs', []))} 项差异, "
                  f"{len(diff_report.get('matches', []))} 项匹配", file=sys.stderr)
        except Exception as e:
            result["errors"].append(f"解析对比阶段: {str(e)}")
            result["steps"]["diff"] = {"status": "error", "message": str(e)}
    elif config_path:
        try:
            config_data = parse_config_excel(config_path)
            result["diff_report"] = {"config_only": config_data, "diffs": [], "matches": [], "unable_to_compare": []}
            result["steps"]["diff"] = {"status": "partial", "message": "仅有场景配置，无巡检结果可对比"}
            print("仅解析场景配置（无巡检结果）", file=sys.stderr)
        except Exception as e:
            result["errors"].append(f"解析配置阶段: {str(e)}")
    else:
        result["errors"].append("缺少场景配置 Excel，无法进行对比")

    # Step 3: 分析代码
    print("\n" + "=" * 60, file=sys.stderr)
    print("Step 3: 分析项目代码", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if code_dir and os.path.isdir(code_dir):
        try:
            code_analysis = analyze_code(code_dir)
            result["code_analysis"] = code_analysis
            result["steps"]["code_analysis"] = {
                "status": "success",
                "total_source_files": len(code_analysis["source_files"]),
                "trtc_files_count": len(code_analysis["trtc_files"]),
                "platform": code_analysis["platform"],
                "api_calls_found": list(code_analysis["api_calls"].keys())
            }
            print(f"代码分析完成: {len(code_analysis['trtc_files'])} 个 TRTC 相关文件, "
                  f"平台: {code_analysis['platform']}", file=sys.stderr)
        except Exception as e:
            result["errors"].append(f"代码分析阶段: {str(e)}")
            result["steps"]["code_analysis"] = {"status": "error", "message": str(e)}
    else:
        result["steps"]["code_analysis"] = {"status": "skipped", "message": "无代码目录"}

    # Step 4: 生成修改计划
    print("\n" + "=" * 60, file=sys.stderr)
    print("Step 4: 生成修改计划", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if result.get("diff_report") and result.get("code_analysis"):
        modification_plan = generate_modification_plan(result["diff_report"], result["code_analysis"])
        result["modification_plan"] = modification_plan
        result["steps"]["modification_plan"] = {
            "status": "success",
            "modifications_count": len(modification_plan["modifications"]),
            "new_calls_count": len(modification_plan["new_calls_needed"]),
            "optional_count": len(modification_plan["optional_items"])
        }
        print(f"修改计划生成: {len(modification_plan['modifications'])} 项修改, "
              f"{len(modification_plan['new_calls_needed'])} 项新增", file=sys.stderr)

    if result["errors"]:
        result["status"] = "partial" if result.get("diff_report") else "error"

    return result


def main():
    parser = argparse.ArgumentParser(description="TRTC Config Inspector - 完整巡检流程")
    parser.add_argument('--config-url', required=True, help='场景配置 Excel 的 URL 或本地路径')
    parser.add_argument('--inspect-url', help='巡检结果 Excel 的 URL 或本地路径')
    parser.add_argument('--code-url', help='代码压缩包的 URL 或本地目录路径')
    parser.add_argument('--output-dir', default='./workspace', help='工作目录 (默认: ./workspace)')

    args = parser.parse_args()

    result = run_inspector(
        config_url=args.config_url,
        inspect_url=args.inspect_url,
        code_url=args.code_url,
        output_dir=args.output_dir
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
