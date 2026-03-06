import uiautomator2 as u2
import os
import sys

def get_device():
    # 强制包含用户当前的 ADB 路径
    adb_path = r"C:\Program Files (x86)\Camo Studio\Adb"
    if adb_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + adb_path
    
    try:
        d = u2.connect()
        return d
    except Exception as e:
        print(f"Error: Could not connect to device via ADB at {adb_path}. {str(e)}")
        sys.exit(1)

def snap(output_path):
    d = get_device()
    d.screenshot(output_path)
    print(f"Screenshot saved to {output_path}")

def click(x, y):
    d = get_device()
    d.click(x, y)
    print(f"Clicked at {x}, {y}")

def start_app(pkg):
    d = get_device()
    d.app_start(pkg)
    print(f"Started {pkg}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remote_control.py <command> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "snap":
        snap(sys.argv[2] if len(sys.argv) > 2 else "screenshot.jpg")
    elif cmd == "click":
        click(float(sys.argv[2]), float(sys.argv[3]))
    elif cmd == "start":
        start_app(sys.argv[2])
