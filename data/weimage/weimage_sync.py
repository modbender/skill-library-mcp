import os
import shutil
import json
import sys
import subprocess
import re

# 这个脚本的目标是：在一个特定的 Python 环境中运行一个生成图片的脚本（gen.py），
# 欢迎访问 莲汇全球AI  https://lianhuiai.com

# --- 1. 环境强制切换与加载 ---
TARGET_PYTHON = "/root/pythonenv/bin/python3"

def ensure_env():
    # 确保在指定的 pythonenv 环境下运行
    if os.path.exists(TARGET_PYTHON) and sys.executable != TARGET_PYTHON:
        os.execv(TARGET_PYTHON, [TARGET_PYTHON] + sys.argv)

def load_dotenv():
    # 加载 API KEY
    dotenv_path = "/root/.openclaw/.env"
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = value.strip('"').strip("'")

ensure_env()
load_dotenv()

# --- 2. 核心配置 ---
OUTPUT_DIR = "/opt/1panel/www/sites/voice.robotmusk.com/index"
BASE_URL = "https://voice.robotmusk.com"
GEN_SCRIPT = "/root/.openclaw/workspace/skills/gemini-image-gen/scripts/gen.py"
WORKSPACE_DIR = "/root/.openclaw/workspace"

def main(params):
    # 多渠道获取 prompt：1.字典字段 2.环境变量
    prompt = params.get("prompt") or os.environ.get("prompt") or os.environ.get("PROMPT")
    
    if not prompt:
        return {
            "success": False, 
            "error": "Prompt 不能为空", 
            "debug_params": params,
            "debug_env_keys": list(os.environ.keys())
        }

    prompt = str(prompt).strip()

    try:
        # 1. 构造执行命令 (列表传参，彻底解决引号转义问题)
        cmd = [
            sys.executable, GEN_SCRIPT,
            "--prompt", prompt,
            "--count", "1",
            "--engine", "gemini"
        ]
        
        # 2. 阻塞运行并捕获输出
        process = subprocess.run(cmd, cwd=WORKSPACE_DIR, capture_output=True, text=True)
        # 合并标准输出和错误输出，防止信息漏掉
        output_text = process.stdout + process.stderr
        
        # 3. 精准解析 gen.py 的输出内容
        # 匹配输出目录：Output: tmp/gemini-image-gen-xxxx
        dir_match = re.search(r"Output:\s+(\S+)", output_text)
        # 匹配文件名：-> 001-xxxx.png
        fn_match = re.search(r"->\s+([\w\-\.]+\.png)", output_text)

        if not dir_match or not fn_match:
            return {"success": False, "error": "未能解析脚本输出路径", "log": output_text[-500:]}

        # 去除可能的终端颜色代码
        rel_dir = re.sub(r'\x1b\[[0-9;]*m', '', dir_match.group(1).strip())
        filename = fn_match.group(1).strip()
        
        src_file = os.path.join(WORKSPACE_DIR, rel_dir, filename)

        if not os.path.exists(src_file):
            return {"success": False, "error": f"找到路径但文件不存在: {src_file}"}
        
        # 4. 物理搬运至 1Panel 静态目录
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
        dest_file = os.path.join(OUTPUT_DIR, filename)
        shutil.copy2(src_file, dest_file)

        # 5. 返回最终 URL
        return {
            "success": True,
            "url": f"{BASE_URL}/{filename}",
            "filename": filename,
            "prompt_used": prompt
        }

    except Exception as e:
        return {"success": False, "error": f"系统崩溃: {str(e)}"}

if __name__ == "__main__":
    try:
        # 核心改进：兼容 JSON 格式和 Agent 直接传递的字符串
        if len(sys.argv) > 1:
            raw_input = sys.argv[1].strip()
            if raw_input.startswith("{"):
                try:
                    args = json.loads(raw_input)
                except:
                    args = {"prompt": raw_input}
            else:
                args = {"prompt": raw_input}
        else:
            args = {}
            
        # 执行并打印结果，供 Agent 后续步骤抓取
        print(json.dumps(main(args)))
    except Exception as e:
        print(json.dumps({"success": False, "error": f"入口异常: {str(e)}"}))