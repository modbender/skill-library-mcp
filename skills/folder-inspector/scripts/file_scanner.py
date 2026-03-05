# file_scanner.py
import os
import sys
import datetime
import json

def debug_log(message):
    with open("/tmp/openclaw_python_debug.log", "a") as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")

def get_dir_info(path):
    try:
        # 处理 ~ 符号
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path):
            return {"error": f"路径不存在: {path}"}
        
        files_info = []
        for entry in os.scandir(expanded_path):
            if entry.is_file():
                # 获取大小并转为可读格式 (KB)
                size_kb = round(entry.stat().st_size / 1024, 2)
                files_info.append({
                    "name": entry.name,
                    "size": f"{size_kb} KB"
                })
        
        return {"path": expanded_path, "files": files_info, "count": len(files_info)}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # 从命令行参数获取路径，默认为当前目录
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."
    debug_log(f"脚本被调用了！参数路径: {target_path}")
    print(json.dumps(get_dir_info(target_path), ensure_ascii=False))
