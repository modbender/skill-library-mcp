#!/usr/bin/env python3
"""
使用示例 - 展示如何在 OpenClaw Skill 中使用 feishu_smart_doc_writer
"""

# 示例 1: 在 Skill 中写入长文档
async def example_write_long_doc(ctx):
    """
    在 OpenClaw Skill 中写入长文档
    
    ctx 是 OpenClaw 提供的上下文对象
    """
    from feishu_smart_doc_writer import FeishuDocWriter, ChunkConfig
    
    # 创建写入器，传入 ctx
    config = ChunkConfig(
        chunk_size=2000,      # 每块2000字符
        show_progress=True,   # 显示进度
        max_retries=3         # 失败重试3次
    )
    writer = FeishuDocWriter(ctx, config)
    
    # 准备长内容
    long_content = """
# 项目策划文档

## 一、项目背景

这是项目的详细背景介绍...

## 二、技术方案

| 技术 | 说明 | 优势 |
|------|------|------|
| Python | 编程语言 | 生态丰富 |
| OpenClaw | 自动化框架 | 功能强大 |

## 三、实施计划

1. 第一阶段...
2. 第二阶段...
3. 第三阶段...

""" * 100  # 重复100次，生成约50000字符的长内容
    
    # 写入文档
    doc_url = await writer.write_document(
        title="项目策划 - 完整版",
        content=long_content,
        folder_token=None  # 可选：指定文件夹
    )
    
    print(f"✅ 文档创建成功: {doc_url}")
    return doc_url


# 示例 2: 追加内容到现有文档
async def example_append_to_doc(ctx, doc_url):
    """
    向已有文档追加内容
    """
    from feishu_smart_doc_writer import FeishuDocWriter
    
    writer = FeishuDocWriter(ctx)
    
    # 追加内容
    append_content = """
## 四、补充说明

这是后来补充的内容...
""" * 50
    
    success = await writer.append_to_document(
        doc_url=doc_url,
        content=append_content
    )
    
    if success:
        print("✅ 内容追加成功")
    else:
        print("❌ 内容追加失败")
    
    return success


# 示例 3: 在 Skill 定义中使用
SKILL_DEFINITION = {
    "name": "my_skill",
    "tools": [
        {
            "name": "create_project_doc",
            "description": "创建项目文档",
            "handler": "create_project_doc_handler"
        }
    ]
}

async def create_project_doc_handler(ctx, args):
    """
    Skill 工具处理函数
    """
    from feishu_smart_doc_writer import FeishuDocWriter
    
    title = args.get("title", "未命名文档")
    content = args.get("content", "")
    
    writer = FeishuDocWriter(ctx)
    doc_url = await writer.write_document(title, content)
    
    return {
        "doc_url": doc_url,
        "message": "文档创建成功"
    }


# 示例 4: 直接使用同步函数（简化版）
def example_sync_usage(ctx):
    """
    同步方式使用（在不需要async的环境中）
    """
    from feishu_smart_doc_writer import write_document_sync
    
    doc_url = write_document_sync(
        ctx=ctx,
        title="同步创建的文档",
        content="# 标题\n\n大量内容..." * 1000
    )
    
    return doc_url


if __name__ == "__main__":
    print("Feishu Smart Doc Writer 使用示例")
    print("=" * 50)
    print()
    print("在 OpenClaw Skill 中使用:")
    print()
    print("1. 导入:")
    print("   from feishu_smart_doc_writer import FeishuDocWriter")
    print()
    print("2. 创建写入器:")
    print("   writer = FeishuDocWriter(ctx)")
    print()
    print("3. 写入长文档:")
    print("   doc_url = await writer.write_document(title, content)")
    print()
    print("4. 追加内容:")
    print("   await writer.append_to_document(doc_url, content)")
