"""
MiniTimeBot 启动器
打包成 exe 后，双击即调用同目录下的 run.bat。
仅作为快捷方式的入口，不包含任何业务逻辑。
"""
import os
import sys
import subprocess


def main():
    # exe 所在目录（打包后）或脚本所在目录（开发时）
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # run.bat 在项目根目录（exe 放在根目录时直接同级；放在 packaging/ 时往上一级）
    run_bat = os.path.join(exe_dir, "run.bat")
    if not os.path.exists(run_bat):
        run_bat = os.path.join(os.path.dirname(exe_dir), "run.bat")

    if not os.path.exists(run_bat):
        input("错误：找不到 run.bat，请确认文件完整性。按回车退出...")
        sys.exit(1)

    # 用 cmd 执行 run.bat，工作目录设为 run.bat 所在目录
    work_dir = os.path.dirname(run_bat)
    subprocess.call(["cmd", "/c", run_bat], cwd=work_dir)


if __name__ == "__main__":
    main()
