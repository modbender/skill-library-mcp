"""
Doubao Skill for Openclaw - Python 实现
支持文生图、文生视频和任务状态查询
"""

import asyncio
import subprocess
import json
import os
from typing import Dict, Any


class DoubaoSkill:
    """Doubao Skill 主类"""
    
    def __init__(self):
        self.api_key = os.getenv("ARK_API_KEY")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.doubao_demo = os.path.join(self.script_dir, "doubao_demo.py")

        if not self.api_key:
            raise ValueError("ARK_API_KEY 环境变量未设置")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        主执行方法

        Args:
            context: 包含以下字段：
                - action: 操作类型 ("img" / "edit" / "vid" / "status")
                - prompt: 生成提示词（img/edit/vid 时必需）
                - sync_mode: 同步模式 ("sync" / "async")，仅 vid 使用
                - image_url: 图片 URL（edit 时必需，vid 时可选）
                - task_id: 任务 ID（status 时必需）

        Returns:
            包含结果的字典
        """
        action = context.get("action")

        if action == "img":
            return await self._generate_image(context)
        elif action == "edit":
            return await self._edit_image(context)
        elif action == "vid":
            return await self._generate_video(context)
        elif action == "status":
            return await self._check_status(context)
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}. Supported: img, edit, vid, status"
            }

    async def _edit_image(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """编辑图片（去除水印等）"""
        image_url = context.get("image_url")
        prompt = context.get("prompt", "remove watermark, keep main content")

        if not image_url:
            return {
                "status": "error",
                "error": "Missing required parameter: image_url"
            }

        return await self._run_python_script("edit", image_url, prompt)

    async def _generate_image(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成图片"""
        prompt = context.get("prompt")

        if not prompt:
            return {
                "status": "error",
                "error": "Missing required parameter: prompt"
            }

        return await self._run_python_script("img", prompt)

    async def _generate_video(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成视频"""
        prompt = context.get("prompt")
        sync_mode = context.get("sync_mode", "async")
        image_url = context.get("image_url")
        
        if not prompt:
            return {
                "status": "error",
                "error": "Missing required parameter: prompt"
            }
        
        if image_url:
            return await self._run_python_script("vid", prompt, sync_mode, image_url)
        else:
            return await self._run_python_script("vid", prompt, sync_mode)
    
    async def _check_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查任务状态"""
        task_id = context.get("task_id")
        
        if not task_id:
            return {
                "status": "error",
                "error": "Missing required parameter: task_id"
            }
        
        return await self._run_python_script("status", task_id)
    
    async def _run_python_script(self, *args) -> Dict[str, Any]:
        """
        异步运行 Python 脚本
        
        Args:
            *args: 传递给 doubao_demo.py 的参数
        
        Returns:
            解析后的 JSON 响应
        """
        try:
            # 构建命令
            doubao_demo = os.path.join(self.script_dir, "doubao_demo.py")
            cmd = ["python3", doubao_demo] + list(args)
            
            # 设置环境变量
            env = os.environ.copy()
            env["ARK_API_KEY"] = self.api_key
            
            # 异步执行
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=600  # 10 分钟超时
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                return {
                    "status": "error",
                    "error": error_msg or "Script execution failed"
                }
            
            # 解析输出
            output = stdout.decode('utf-8')
            try:
                result = json.loads(output)
                return result
            except json.JSONDecodeError:
                return {
                    "status": "success",
                    "raw_output": output
                }
            
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "error": "Request timeout (10 minutes exceeded)"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# 全局 Skill 实例
skill = DoubaoSkill()


async def handler(context: Dict[str, Any]) -> Dict[str, Any]:
    """Openclaw Skill 处理函数"""
    return await skill.execute(context)


if __name__ == "__main__":
    # 测试示例
    async def test():
        # 测试文生图
        result = await handler({
            "action": "img",
            "prompt": "一只可爱的小猫"
        })
        print("Image Generation:", json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(test())
