"""
OpenClaw CLI - 用于快速测试 Doubao Skill
"""

import sys
import os
import asyncio
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from doubao_skill import handler


def print_help():
    """打印帮助信息"""
    print("""
用法: python cli.py <command> [options]

命令:
  img <prompt>              生成图像
  edit <image_url> [prompt] 编辑图像（去除水印等）
  vid <prompt> [sync|async] 生成视频 (默认: async)
  status <task_id>          检查任务状态
  help                      显示此帮助信息

示例:
  python cli.py img "一只可爱的小猫"
  python cli.py edit "https://..." "remove watermark"
  python cli.py vid "一个人在跳舞" sync
  python cli.py status "task_xxxxx"
""")


async def main():
    """CLI 主函数"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    try:
        if command == "img":
            if len(sys.argv) < 3:
                print("错误: 缺少 prompt 参数")
                print_help()
                return
            
            prompt = sys.argv[2]
            result = await handler({
                "action": "img",
                "prompt": prompt
            })
            
        elif command == "edit":
            if len(sys.argv) < 3:
                print("错误: 缺少 image_url 参数")
                print_help()
                return
            
            image_url = sys.argv[2]
            prompt = sys.argv[3] if len(sys.argv) > 3 else "remove watermark, keep main content"
            
            result = await handler({
                "action": "edit",
                "image_url": image_url,
                "prompt": prompt
            })
            
        elif command == "vid":
            if len(sys.argv) < 3:
                print("错误: 缺少 prompt 参数")
                print_help()
                return
            
            prompt = sys.argv[2]
            sync_mode = sys.argv[3] if len(sys.argv) > 3 else "async"
            
            result = await handler({
                "action": "vid",
                "prompt": prompt,
                "sync_mode": sync_mode
            })
            
        elif command == "status":
            if len(sys.argv) < 3:
                print("错误: 缺少 task_id 参数")
                print_help()
                return
            
            task_id = sys.argv[2]
            result = await handler({
                "action": "status",
                "task_id": task_id
            })
            
        elif command == "help":
            print_help()
            return
            
        else:
            print(f"错误: 未知命令 '{command}'")
            print_help()
            return
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
