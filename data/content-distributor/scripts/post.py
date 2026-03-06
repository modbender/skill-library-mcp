#!/usr/bin/env python3
"""
多平台内容发布工具
用法: python3 post.py --platform zhihu --type answer --question-url "..." --content "..."
"""

import argparse
import sys
from pathlib import Path

# 添加 platforms 模块路径
sys.path.insert(0, str(Path(__file__).parent))

from platforms import get_platform, list_platforms, PlatformError


def main():
    parser = argparse.ArgumentParser(description="多平台内容发布工具")
    parser.add_argument("--platform", "-p", required=True, 
                        help=f"目标平台 ({'/'.join(list_platforms())})")
    parser.add_argument("--type", "-t", required=True,
                        help="发布类型 (answer/article/pin/diary/status/group)")
    
    # 内容参数
    parser.add_argument("--title", help="标题 (文章/日记/帖子)")
    parser.add_argument("--content", help="正文内容")
    parser.add_argument("--content-file", help="从文件读取内容")
    
    # 平台特定参数
    parser.add_argument("--question-url", help="知乎问题 URL (回答时需要)")
    parser.add_argument("--group-id", help="豆瓣小组 ID")
    parser.add_argument("--column", help="知乎专栏 ID")
    
    # 选项
    parser.add_argument("--dry-run", action="store_true", help="仅验证，不实际发布")
    parser.add_argument("--validate", action="store_true", help="仅验证凭据")
    
    args = parser.parse_args()
    
    try:
        # 获取平台实例
        platform = get_platform(args.platform)
        
        # 仅验证凭据
        if args.validate:
            if platform.validate_credentials():
                print(f"✅ {args.platform} 凭据有效")
            return
        
        # 获取内容
        content = args.content
        if args.content_file:
            with open(args.content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        if not content:
            print("❌ 错误: 必须提供 --content 或 --content-file")
            sys.exit(1)
        
        # 构建发布参数
        kwargs = {"content": content}
        
        if args.title:
            kwargs["title"] = args.title
        if args.question_url:
            kwargs["question_url"] = args.question_url
        if args.group_id:
            kwargs["group_id"] = args.group_id
        if args.column:
            kwargs["column"] = args.column
        
        # 干运行
        if args.dry_run:
            print(f"🔍 干运行模式")
            print(f"   平台: {args.platform}")
            print(f"   类型: {args.type}")
            print(f"   参数: {kwargs}")
            
            if platform.validate_credentials():
                print(f"   凭据: ✅ 有效")
            return
        
        # 发布
        print(f"📤 正在发布到 {args.platform}...")
        result = platform.post(args.type, **kwargs)
        
        if result.get("success"):
            print(f"✅ 发布成功!")
            if result.get("url"):
                print(f"   链接: {result['url']}")
        else:
            print(f"❌ 发布失败: {result}")
            sys.exit(1)
            
    except PlatformError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
