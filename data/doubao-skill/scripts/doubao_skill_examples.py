"""
Doubao Skill 使用示例
演示如何使用 Doubao Skill 进行图像和视频生成
"""

import asyncio
import json
import os
from doubao_skill import handler


async def example_text_to_image():
    """示例 1: 文本生成图像"""
    print("\n=== 示例 1: 文本生成图像 ===")
    
    result = await handler({
        "action": "img",
        "prompt": "一只可爱的金色检验犬在海滩上，午后阳光"
    })
    
    print("结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("status") == "success":
        print(f"\n✅ 图像已生成: {result.get('image_url')}")
    else:
        print(f"\n❌ 生成失败: {result.get('error')}")
    
    return result


async def example_text_to_video_async():
    """示例 2: 异步文本生成视频（返回任务 ID）"""
    print("\n=== 示例 2: 异步文本生成视频 ===")
    
    result = await handler({
        "action": "vid",
        "prompt": "一个人在现代城市中跳舞，夜景",
        "sync_mode": "async"
    })
    
    print("结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("status") == "success":
        task_id = result.get("task_id")
        print(f"\n✅ 视频生成已启动，任务 ID: {task_id}")
        return task_id
    else:
        print(f"\n❌ 启动失败: {result.get('error')}")
        return None


async def example_text_to_video_sync():
    """示例 3: 同步文本生成视频（等待完成）"""
    print("\n=== 示例 3: 同步文本生成视频（等待完成） ===")
    print("注意: 这个示例会等待视频生成完成，可能需要 1-3 分钟...")
    
    result = await handler({
        "action": "vid",
        "prompt": "一只狐狸在雪地中奔跑，冬季风景",
        "sync_mode": "sync"
    })
    
    print("结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("status") == "success":
        print(f"\n✅ 视频已生成: {result.get('result_url')}")
    else:
        print(f"\n❌ 生成失败: {result.get('error')}")
    
    return result


async def example_check_status(task_id: str):
    """示例 4: 检查任务状态"""
    print(f"\n=== 示例 4: 检查任务状态 (Task ID: {task_id}) ===")
    
    result = await handler({
        "action": "status",
        "task_id": task_id
    })
    
    print("结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    status = result.get("status")
    print(f"\n当前状态: {status}")
    
    return result


async def example_complete_workflow():
    """示例 5: 完整工作流 - 生成视频并监控进度"""
    print("\n=== 示例 5: 完整工作流 - 生成视频并监控进度 ===")
    
    # 第一步: 异步启动视频生成
    print("\n步骤 1: 启动视频生成...")
    result = await handler({
        "action": "vid",
        "prompt": "一条龙在云彩中飞舞，奇幻场景",
        "sync_mode": "async"
    })
    
    if result.get("status") != "success":
        print(f"❌ 启动失败: {result.get('error')}")
        return None
    
    task_id = result.get("task_id")
    print(f"✅ 视频生成已启动 (Task ID: {task_id})")
    
    # 第二步: 监控进度
    print("\n步骤 2: 监控生成进度...")
    for i in range(3):
        await asyncio.sleep(5)  # 等待 5 秒
        
        status_result = await handler({
            "action": "status",
            "task_id": task_id
        })
        
        status = status_result.get("status")
        progress = status_result.get("progress", 0)
        
        print(f"  检查 {i+1}: 状态 = {status}, 进度 = {progress}%")
        
        if status == "succeeded":
            print(f"\n✅ 视频已完成！")
            print(f"   URL: {status_result.get('result_url')}")
            return status_result.get("result_url")
        elif status == "failed":
            print(f"\n❌ 视频生成失败: {status_result.get('error')}")
            return None
    
    print("\n⚠️ 超时：继续等待中... (请稍后手动检查状态)")
    print(f"   任务 ID: {task_id}")
    return task_id


async def main():
    """运行所有示例"""
    print("=" * 60)
    print("Doubao Skill 使用示例")
    print("=" * 60)
    
    # 检查 API Key
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("\n❌ 错误: ARK_API_KEY 环境变量未设置")
        print("请先设置: export ARK_API_KEY='your_api_key'")
        return
    
    print(f"\n✅ ARK_API_KEY 已设置")
    
    try:
        # 运行示例
        # await example_text_to_image()
        # task_id = await example_text_to_video_async()
        # if task_id:
        #     await example_check_status(task_id)
        # await example_complete_workflow()
        
        print("\n" + "=" * 60)
        print("可用示例函数:")
        print("  1. example_text_to_image() - 文本生成图像")
        print("  2. example_text_to_video_async() - 异步文本生成视频")
        print("  3. example_text_to_video_sync() - 同步文本生成视频")
        print("  4. example_check_status(task_id) - 检查任务状态")
        print("  5. example_complete_workflow() - 完整工作流")
        print("\n取消注释相应的函数调用来运行示例")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
