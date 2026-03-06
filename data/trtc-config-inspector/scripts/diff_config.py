#!/usr/bin/env python3
"""
对比巡检结果与场景配置模板，输出差异项。

用法:
  python3 diff_config.py <inspect_excel> <config_excel>

输出: JSON 格式的差异报告，每项包含:
  - config_name: 配置名称
  - section: 所属分区
  - current_value: 当前巡检值
  - target_value: 模板目标值
  - match: 是否匹配
  - suggestion: 修改建议
"""

import json
import sys
import os
import re

try:
    import openpyxl
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'openpyxl', '-q'])
    import openpyxl

# 复用 parse_excel 的逻辑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_excel import parse_config_excel, parse_inspect_excel


def normalize_value(val):
    """归一化值，方便对比。"""
    val = val.strip().lower()
    val = re.sub(r'\s+', ' ', val)
    val = re.sub(r'\(.*?\)', '', val)
    val = val.strip()
    return val


# 场景配置项名到巡检结果项名的映射
CONFIG_NAME_MAPPING = {
    "进房模式 scene": "进房模式 scene",
    "音质类型": "音质类型",
    "系统音量类型": "系统音量类型",
    "视频编码参数": "视频编码参数",
}

# 值的等价映射（场景配置值 -> 巡检结果可能的表达）
VALUE_EQUIVALENCE = {
    "live": ["live", "trtc_app_scene_live"],
    "videocall": ["videocall", "trtc_app_scene_videocall"],
    "audiocall": ["audiocall", "trtc_app_scene_audiocall"],
    "voice_chatroom": ["voice_chatroom", "trtc_app_scene_voice_chatroom"],
    "music": ["music", "trtc_audio_quality_music"],
    "default": ["default", "defalut", "trtc_audio_quality_default"],
    "speech": ["speech", "trtc_audio_quality_speech"],
    "全程媒体音量": ["媒体音量", "media", "trtcsystemvolumetypemedia"],
    "全程通话音量": ["通话音量", "voip", "trtcsystemvolumetypevoip"],
    "自动模式": ["auto", "trtcsystemvolumetypeauto"],
}


def values_match(target_val, current_val):
    """判断目标值与当前值是否匹配（模糊匹配）。"""
    t = normalize_value(target_val)
    c = normalize_value(current_val)

    if not t or not c:
        return None  # 无法判断

    # 直接包含
    if t in c or c in t:
        return True

    # 等价映射
    for key, aliases in VALUE_EQUIVALENCE.items():
        if t == key or t in aliases:
            if c == key or any(a in c for a in aliases):
                return True

    return False


def extract_video_params(value_str):
    """从巡检结果的视频编码参数值中提取具体参数。"""
    params = {}
    val = value_str.lower()

    # 提取分辨率
    res_match = re.search(r'宽:(\d+)\s*高:(\d+)', val)
    if res_match:
        params['width'] = int(res_match.group(1))
        params['height'] = int(res_match.group(2))

    # 提取帧率
    fps_match = re.search(r'帧率:(\d+)', val)
    if fps_match:
        params['fps'] = int(fps_match.group(1))

    # 提取码率
    br_match = re.search(r'码率:(\d+)', val)
    if br_match:
        params['bitrate'] = int(br_match.group(1))

    # 分辨率模式
    if '竖屏' in val:
        params['mode'] = 'portrait'
    elif '横屏' in val:
        params['mode'] = 'landscape'

    return params


def parse_target_video_param(target_value):
    """
    从场景配置的 target_value 中解析视频编码子参数类型和数值。
    场景配置中视频编码参数会拆成多行，每行的 target_value 格式不同：
      - 分辨率: "720p" / "1080p" / "540p" 或 "1280x720" 等
      - 帧率: "25帧" / "15fps" / "25" 等
      - 码率: "720p-1800kbps，1080p-3000kbps，540p-1300kbps" 或 "1800kbps" 等
    返回 (param_type, parsed_value) 元组列表，param_type 为 'resolution'/'fps'/'bitrate'/None
    """
    val = target_value.strip().lower()

    # 帧率: 匹配 "25帧" / "15fps" / 纯数字+帧
    fps_match = re.match(r'^(\d+)\s*(?:帧|fps)?$', val)
    if fps_match:
        return 'fps', int(fps_match.group(1))

    # 分辨率: 匹配 "720p" / "1080p" / "540p"
    res_match = re.match(r'^(\d+)p$', val)
    if res_match:
        return 'resolution', int(res_match.group(1))

    # 码率（含分辨率映射）: "720p-1800kbps，1080p-3000kbps"
    if 'kbps' in val or '码率' in val:
        return 'bitrate', val

    return None, val


def compare_video_params(inspect_items, config_items, report):
    """
    专门处理"视频编码参数"的逐项对比。
    巡检结果中视频编码参数通常合并在一个值里（如 "宽:640 高:480 帧率:15 码率:900"），
    而场景配置中视频编码参数拆成多行（分辨率一行、帧率一行、码率一行）。

    【关键】必须对每一个子参数（分辨率、帧率、码率）逐一独立对比，
    确保不遗漏任何一项差异，尤其是帧率。
    """
    # 从巡检结果中提取当前视频参数
    current_params = {}
    inspect_code_example = ""
    for item in inspect_items:
        extracted = extract_video_params(item["current_value"])
        current_params.update(extracted)
        if not inspect_code_example:
            inspect_code_example = item.get("code_example", "")

    # 逐一对比场景配置中的每个视频编码参数行
    for config_item in config_items:
        target_value = config_item["target_value"]
        param_type, parsed = parse_target_video_param(target_value)
        code_example = config_item.get("code_example", "")

        entry_base = {
            "config_name": config_item["config_name"],
            "section": "视频参数",
            "target_value": target_value,
            "code_example": code_example,
        }

        if param_type == 'fps':
            current_fps = current_params.get('fps')
            entry = {**entry_base, "current_value": f"{current_fps}帧" if current_fps else "未检测到"}
            if current_fps is None:
                entry["reason"] = "巡检结果中未找到帧率信息"
                report["unable_to_compare"].append(entry)
            elif current_fps != parsed:
                entry["suggestion"] = f"需要将 [视频帧率] 从当前值 [{current_fps}帧] 修改为 [{parsed}帧]"
                report["diffs"].append(entry)
            else:
                report["matches"].append(entry)

        elif param_type == 'resolution':
            # 将 720p 转换为宽高进行对比
            res_map = {540: (960, 540), 720: (1280, 720), 1080: (1920, 1080)}
            target_wh = res_map.get(parsed)
            current_w = current_params.get('width')
            current_h = current_params.get('height')
            current_res_str = f"{current_w}x{current_h}" if current_w and current_h else "未检测到"
            entry = {**entry_base, "current_value": current_res_str}
            if current_w is None or current_h is None:
                entry["reason"] = "巡检结果中未找到分辨率信息"
                report["unable_to_compare"].append(entry)
            elif target_wh and (current_w, current_h) != target_wh:
                entry["suggestion"] = f"需要将 [视频分辨率] 从当前值 [{current_res_str}] 修改为 [{target_wh[0]}x{target_wh[1]}]"
                report["diffs"].append(entry)
            else:
                report["matches"].append(entry)

        elif param_type == 'bitrate':
            current_br = current_params.get('bitrate')
            entry = {**entry_base, "current_value": f"{current_br}kbps" if current_br else "未检测到"}
            # 码率 target 可能包含多个分辨率映射，取当前分辨率对应的
            target_br = None
            current_h = current_params.get('height')
            br_matches = re.findall(r'(\d+)p[—\-](\d+)', target_value.lower())
            if br_matches:
                for res_p, br in br_matches:
                    res_map = {540: 540, 720: 720, 1080: 1080}
                    if current_h and int(res_p) == current_h:
                        target_br = int(br)
                        break
                # 如果未匹配到当前分辨率，取 720p 作为默认
                if target_br is None:
                    for res_p, br in br_matches:
                        if int(res_p) == 720:
                            target_br = int(br)
                            break
            else:
                br_single = re.search(r'(\d+)\s*kbps', target_value.lower())
                if br_single:
                    target_br = int(br_single.group(1))

            if current_br is None:
                entry["reason"] = "巡检结果中未找到码率信息"
                report["unable_to_compare"].append(entry)
            elif target_br and current_br != target_br:
                entry["suggestion"] = f"需要将 [视频码率] 从当前值 [{current_br}kbps] 修改为 [{target_br}kbps]"
                report["diffs"].append(entry)
            elif target_br and current_br == target_br:
                report["matches"].append(entry)
            else:
                entry["reason"] = "码率目标值格式无法解析，需人工确认"
                report["unable_to_compare"].append(entry)

        else:
            # 未识别的子参数类型，走通用对比
            entry = {**entry_base}
            if inspect_items:
                entry["current_value"] = inspect_items[0]["current_value"]
                match_result = values_match(target_value, entry["current_value"])
                if match_result is True:
                    report["matches"].append(entry)
                elif match_result is False:
                    entry["suggestion"] = f"需要将 [{config_item['config_name']}] 从当前值 [{entry['current_value']}] 修改为 [{target_value}]"
                    report["diffs"].append(entry)
                else:
                    entry["reason"] = "值格式不同，需人工确认"
                    report["unable_to_compare"].append(entry)
            else:
                entry["reason"] = "巡检结果中未找到对应配置项"
                report["unable_to_compare"].append(entry)


def diff_configs(inspect_data, config_data):
    """对比巡检结果与场景配置模板。"""
    report = {
        "scene_name": config_data["basic_info"].get("场景名称", "未知"),
        "sdk_appid": inspect_data["basic_info"].get("SDK AppID", "未知"),
        "diffs": [],
        "matches": [],
        "unable_to_compare": []
    }

    # 构建巡检结果的查找表
    inspect_items = {}
    for section, items in inspect_data["sections"].items():
        for item in items:
            key = normalize_value(item["config_name"])
            if key not in inspect_items:
                inspect_items[key] = []
            inspect_items[key].append({**item, "section": section})

    # 收集场景配置中的视频编码参数项（可能有多行），统一处理
    video_param_config_items = []

    # 遍历场景配置的每个项
    for section, items in config_data["sections"].items():
        for config_item in items:
            config_name = config_item["config_name"]
            target_value = config_item["target_value"]
            config_key = normalize_value(config_name)

            # 【关键】视频编码参数需要收集所有行后统一做逐项对比
            if config_key == "视频编码参数":
                video_param_config_items.append(config_item)
                continue

            # 在巡检结果中查找对应项
            matched_inspects = inspect_items.get(config_key, [])

            if not matched_inspects:
                report["unable_to_compare"].append({
                    "config_name": config_name,
                    "section": section,
                    "target_value": target_value,
                    "reason": "巡检结果中未找到对应配置项",
                    "code_example": config_item.get("code_example", "")
                })
                continue

            for inspect_item in matched_inspects:
                current_value = inspect_item["current_value"]
                match_result = values_match(target_value, current_value)

                entry = {
                    "config_name": config_name,
                    "section": section,
                    "current_value": current_value,
                    "target_value": target_value,
                    "code_example": config_item.get("code_example", "")
                }

                if match_result is True:
                    report["matches"].append(entry)
                elif match_result is False:
                    entry["suggestion"] = f"需要将 [{config_name}] 从当前值 [{current_value}] 修改为 [{target_value}]"
                    report["diffs"].append(entry)
                else:
                    entry["reason"] = "值格式不同，需人工确认"
                    report["unable_to_compare"].append(entry)

    # 【关键】对视频编码参数做逐项（分辨率、帧率、码率）独立对比，确保不遗漏任何子参数
    if video_param_config_items:
        video_inspect_items = inspect_items.get("视频编码参数", [])
        compare_video_params(video_inspect_items, video_param_config_items, report)

    return report


def main():
    if len(sys.argv) < 3:
        print("用法: python3 diff_config.py <inspect_excel> <config_excel>")
        sys.exit(1)

    inspect_file = sys.argv[1]
    config_file = sys.argv[2]

    inspect_data = parse_inspect_excel(inspect_file)
    config_data = parse_config_excel(config_file)

    report = diff_configs(inspect_data, config_data)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
