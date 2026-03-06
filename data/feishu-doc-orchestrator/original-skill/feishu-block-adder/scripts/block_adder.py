#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
块添加器 - 子技能3
将解析后的块数据添加到飞书文档
输出：add_result.json
"""

import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
import requests


def load_config():
    """加载飞书配置"""
    config_path = Path(__file__).parent.parent.parent.parent / "feishu-config.env"
    if not config_path.exists():
        config_path = Path(".claude/feishu-config.env")

    config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"\'')
    return config


def get_access_token(config, use_user_token=False):
    """获取访问令牌"""
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    payload = {
        "app_id": config['FEISHU_APP_ID'],
        "app_secret": config['FEISHU_APP_SECRET']
    }
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    if result.get("code") == 0:
        return result["tenant_access_token"]
    else:
        raise Exception(f"获取 token 失败: {result}")


def clean_cell_content(content):
    """清理单元格内容"""
    if not content:
        return ""
    content = str(content).strip()
    content = content.replace('\u200b', '')
    content = content.replace('\u200c', '')
    content = content.replace('\u200d', '')
    content = content.replace('\ufeff', '')
    content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
    if '\n' in content:
        content = content.split('\n')[0].strip()
    return content


def create_table_with_style(token, config, document_id, rows_data):
    """
    创建表格并填充内容 - 使用 descendant API

    根据飞书官方规范，使用 /descendant 端点一次性创建表格和所有单元格

    关键点：
    1. children_id 只包含直接添加到文档的块（table_id）
    2. descendants 包含所有块的详细信息（表格、单元格、单元格内容）
    3. 表格的 children 引用单元格的 block_id
    4. 单元格的 children 引用内容块的 block_id
    """
    import uuid

    row_size = len(rows_data)
    col_size = len(rows_data[0]) if rows_data else 0

    # 生成唯一的 block_id
    table_id = f"table_{uuid.uuid4().hex[:16]}"

    # 生成所有单元格和内容块的 block_id
    cell_ids = []
    cell_content_ids = []
    for i in range(row_size * col_size):
        cell_ids.append(f"cell_{uuid.uuid4().hex[:16]}")
        cell_content_ids.append(f"cellcontent_{uuid.uuid4().hex[:16]}")

    # 构建完整的 descendants 列表
    descendants = []

    # 1. 添加表格块
    descendants.append({
        "block_id": table_id,
        "block_type": 31,
        "table": {
            "property": {
                "row_size": row_size,
                "column_size": col_size,
                "header_row": True
            }
        },
        "children": cell_ids
    })

    # 2. 添加所有单元格块和内容块
    for row_idx, row in enumerate(rows_data):
        for col_idx, cell_content in enumerate(row):
            cell_index = row_idx * col_size + col_idx
            cell_id = cell_ids[cell_index]
            cell_content_id = cell_content_ids[cell_index]

            # 清理单元格内容
            cell_content = clean_cell_content(cell_content)

            # 单元格块
            descendants.append({
                "block_id": cell_id,
                "block_type": 32,
                "table_cell": {},
                "children": [cell_content_id]
            })

            # 单元格内容块（文本）
            descendants.append({
                "block_id": cell_content_id,
                "block_type": 2,
                "text": {
                    "elements": [{"text_run": {"content": cell_content}}],
                    "style": {}
                },
                "children": []
            })

    # 发送请求 - children_id 只包含 table_id
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/descendant?document_revision_id=-1"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}

    payload = {
        "index": -1,
        "children_id": [table_id],
        "descendants": descendants
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"创建表格失败: {result}")

    return table_id


def create_callout_with_children(token, config, document_id, callout_style, callout_content):
    """创建高亮块

    ⚠️ 关键修复：callout 块的颜色字段必须直接在 callout 对象下，不能嵌套在 style 中

    错误格式示例：
        "callout": {
            "elements": [...],
            "style": {"emoji_id": "...", "background_color": 1}  # ❌ 错误
        }

    正确格式示例：
        "callout": {
            "elements": [...],
            "emoji_id": "...",          # ✓ 直接在 callout 下
            "background_color": 1        # ✓ 直接在 callout 下
        }

    调试经验：
        - 如果 API 返回的 callout 只有 emoji_id，说明格式错误
        - 验证方法：检查响应 data.children[0].callout 是否包含颜色字段
    """
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 使用 **callout_style 展开操作符，将样式字段直接展开到 callout 对象下
    payload = {
        "children": [{
            "block_type": 19,
            "callout": {
                "elements": [{"text_run": {"content": callout_content}}],
                **callout_style  # 关键：展开样式字段到 callout 对象下，不要嵌套在 style 中
            }
        }],
        "index": -1
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"创建 callout 块失败: {result}")

    # 验证：检查返回的 callout 是否包含颜色字段
    returned_callout = result["data"]["children"][0].get("callout", {})
    if "background_color" not in returned_callout and "border_color" not in returned_callout:
        print(f"[WARN] Callout 创建成功但可能缺少颜色字段，返回: {returned_callout}")

    return result["data"]["children"][0]["block_id"]


def add_children_to_block(token, config, document_id, parent_block_id, children):
    """添加子块到指定块"""
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents/{document_id}/blocks/{parent_block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "children": children,
        "index": -1
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"添加子块失败: {result}")

    return result


def upload_image_file(token, config, image_block_id, image_path):
    """
    上传图片文件到图片块

    根据飞书官方文档的三步流程：
    1. 创建图片 Block (已完成)
    2. 上传图片素材
    3. 设置图片 Block 的 token
    """
    if not Path(image_path).exists():
        raise Exception(f"图片文件不存在: {image_path}")

    file_size = Path(image_path).stat().st_size
    file_name = Path(image_path).name

    # 正确的 API 端点
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/drive/v1/medias/upload_all"

    with open(image_path, 'rb') as f:
        files = {
            'file': (file_name, f, 'image/png')
        }
        data = {
            'file_name': file_name,
            'parent_type': 'docx_image',
            'parent_node': image_block_id,
            'size': str(file_size)
        }
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code != 200:
            raise Exception(f"上传图片失败: HTTP {response.status_code}\n{response.text[:500]}")

        try:
            result = response.json()
        except Exception as e:
            raise Exception(f"解析响应失败: {e}\n响应内容: {response.text[:500]}")

        if result.get("code") != 0:
            raise Exception(f"上传图片失败: {result}")

        file_token = result["data"]["file_token"]
        print(f"  [OK] 图片上传成功: {file_token}")
        return file_token


def update_image_block_token(token, config, document_id, image_block_id, file_token):
    """
    设置图片 Block 的素材 token

    第三步：调用更新块 API，设置 replace_image 操作
    """
    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/docx/v1/documents/{document_id}/blocks/{image_block_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "replace_image": {
            "token": file_token
        }
    }

    response = requests.patch(url, json=payload, headers=headers)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"设置图片素材失败: {result}")

    print(f"  [OK] 图片素材设置成功")
    return result


def main():
    """
    主函数 - 修复版本

    修复问题：块的顺序问题
    原因：表格单独创建（使用专门API），其他块批量添加，导致顺序混乱

    解决方案：改为顺序添加，每个块（包括表格）都按顺序添加到文档末尾
    """
    if len(sys.argv) < 3:
        print("Usage: python block_adder.py <blocks.json> <doc_info.json> [output_dir]")
        sys.exit(1)

    blocks_file = Path(sys.argv[1])
    doc_info_file = Path(sys.argv[2])

    if len(sys.argv) >= 4:
        output_dir = Path(sys.argv[3])
    else:
        output_dir = Path("output")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载块数据
    print(f"[feishu-block-adder] Loading blocks from: {blocks_file}")
    with open(blocks_file, 'r', encoding='utf-8') as f:
        blocks_data = json.load(f)
    blocks = blocks_data["blocks"]
    metadata = blocks_data.get("metadata", {})

    # 加载文档信息
    print(f"[feishu-block-adder] Loading doc info from: {doc_info_file}")
    with open(doc_info_file, 'r', encoding='utf-8') as f:
        doc_info = json.load(f)
    doc_id = doc_info["document_id"]

    # 加载配置
    config = load_config()
    token = get_access_token(config, use_user_token=False)

    print(f"[feishu-block-adder] Document ID: {doc_id}")
    print(f"[feishu-block-adder] Total blocks: {len(blocks)}")
    print(f"[feishu-block-adder] Mode: Sequential (逐块添加，保持顺序)")

    # 统计变量
    table_count = 0
    callout_count = 0
    regular_blocks = 0
    start_time = time.time()

    # ========== 修复：改为顺序添加，保持块的原始顺序 ==========
    # 每个块都按顺序添加到文档末尾，使用 index=-1
    for i, block in enumerate(blocks):
        try:
            if block.get("type") == "table":
                # 表格块：使用专门的创建函数
                print(f"  [{i+1}/{len(blocks)}] Creating table with {len(block['data'])} rows...")
                create_table_with_style(token, config, doc_id, block["data"])
                table_count += 1
                print(f"  [OK] Table created")
            elif block.get("type") == "image" or block.get("block_type") == 27:
                # 图片块：需要三步流程
                # 第一步：创建空的图片块
                print(f"  [{i+1}/{len(blocks)}] Creating image block...")
                image_block_response = add_children_to_block(token, config, doc_id, doc_id, [{
                    "block_type": 27,
                    "image": {}
                }])
                image_block_id = image_block_response["data"]["children"][0]["block_id"]
                print(f"  [OK] Image block created: {image_block_id}")

                # 第二步：上传图片文件（如果有本地路径）
                image_path = block.get("local_path")
                if image_path and Path(image_path).exists():
                    print(f"  [{i+1}/{len(blocks)}] Uploading image file: {image_path}")
                    file_token = upload_image_file(token, config, image_block_id, image_path)

                    # 第三步：设置图片 token
                    print(f"  [{i+1}/{len(blocks)}] Setting image token...")
                    update_image_block_token(token, config, doc_id, image_block_id, file_token)
                    print(f"  [OK] Image upload completed")
                else:
                    # 没有本地文件，可能是网络图片 URL，直接设置
                    image_url = image_data.get("url", "")
                    if image_url:
                        print(f"  [SKIP] Network image URL: {image_url} (not uploaded)")
                    else:
                        print(f"  [WARN] No valid image source found")

                regular_blocks += 1
                print(f"  [{i+1}/{len(blocks)}] Added image")
            else:
                # 其他块：添加到文档末尾
                block_copy = {k: v for k, v in block.items() if k != "type"}

                # 支持的块类型：25 种飞书文档块
                if block_copy.get("block_type") in [
                    2, 3, 4, 5, 6, 7, 8, 9, 10, 11,  # text, heading1-9
                    12, 13, 17,                             # bullet, ordered, todo
                    14, 15, 19, 22,                         # code, quote, callout, divider
                    27,                                     # image (created above, don't create again)
                    34, 35                                  # quote_container, task
                ]:
                    add_children_to_block(token, config, doc_id, doc_id, [block_copy])
                    if block_copy.get("block_type") == 19:
                        callout_count += 1
                    regular_blocks += 1

                    block_type = block_copy.get("block_type", "unknown")
                    type_name = {
                        2: "文本", 3: "H1", 4: "H2", 5: "H3", 6: "H4",
                        12: "列表", 13: "有序列表", 14: "代码", 15: "引用",
                        17: "待办", 19: "高亮", 22: "分割线", 27: "图片"
                    }.get(block_type, f"类型{block_type}")
                    print(f"  [{i+1}/{len(blocks)}] Added {type_name}")

        except Exception as e:
            print(f"  [{i+1}/{len(blocks)}] FAIL: {str(e)[:80]}")

        # 控制请求速率，避免触发限流
        time.sleep(0.05)

    duration = time.time() - start_time

    # 保存结果
    result = {
        "success": True,
        "document_id": doc_id,
        "total_blocks": len(blocks),
        "tables_created": table_count,
        "callouts_created": callout_count,
        "regular_blocks": regular_blocks,
        "mode": "sequential",  # 新增：标识使用顺序模式
        "duration_seconds": round(duration, 2),
        "completed_at": datetime.now().isoformat()
    }

    result_file = output_dir / "add_result.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[feishu-block-adder] Completed in {duration:.2f}s")
    print(f"[feishu-block-adder] Tables created: {table_count}")
    print(f"[feishu-block-adder] Callouts created: {callout_count}")
    print(f"[feishu-block-adder] Regular blocks: {regular_blocks}")
    print(f"[feishu-block-adder] Output: {result_file}")
    print(f"\n[OUTPUT] {result_file}")


if __name__ == "__main__":
    main()
