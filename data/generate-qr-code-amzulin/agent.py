
import qrcode
from PIL import Image
import os
import subprocess
import sys

# 自动安装依赖库（若用户未安装）
def install_dependencies():
    required_packages = ["qrcode", "pillow"]
    for package in required_packages:
        try:
            __import__(package)  # 检查库是否已安装
        except ImportError:
            # 自动安装缺失的库
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 初始化：安装依赖库
install_dependencies()

async def generate_qr(text: str, size: int = 300, color: str = "black", save_path: str = None) -> str:
    """
    生成二维码并保存到指定路径，返回生成结果
    
    参数：
    text: 二维码内容（必选，文本/URL/WiFi 信息等）
    size: 二维码尺寸（px，默认 300）
    color: 填充颜色（默认 black，支持英文或十六进制色值）
    save_path: 保存路径（默认桌面 qr_code.png）
    """
    # 1. 校验必填参数
    if not text or text.strip() == "":
        return "生成失败：请提供需要生成二维码的内容（如文本、URL、WiFi 信息）"
    
    # 2. 处理默认保存路径（适配 Windows/macOS/Linux 多系统）
    if not save_path:
        if sys.platform == "win32":
            # Windows 桌面路径
            save_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "qr_code.png")
        else:
            # macOS/Linux 桌面路径
            save_path = os.path.expanduser("~/Desktop/qr_code.png")
    
    # 3. 生成二维码
    try:
        # 配置二维码参数（version：1-40，box_size：方块大小，border：边框宽度）
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # 中等容错率（30% 错误可识别）
            box_size=10,
            border=4,
        )
        qr.add_data(text.strip())  # 添加二维码内容
        qr.make(fit=True)  # 自动适配内容大小
        
        # 生成图片并调整尺寸
        img = qr.make_image(fill_color=color, back_color="white")
        img = img.resize((size, size), Image.Resampling.LANCZOS)  # 高质量缩放
        
        # 确保保存目录存在（若路径不存在则创建）
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 保存图片
        img.save(save_path)
        return f"二维码生成成功！已保存到：{save_path}\n提示：若无法找到文件，可复制路径到文件管理器直接打开"
    
    except PermissionError:
        return f"生成失败：无权限写入指定路径（{save_path}），请更换保存路径（如桌面）或提升文件权限"
    except Exception as e:
        return f"生成失败：未知错误 - {str(e)}"
