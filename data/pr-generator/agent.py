import qrcode
import os
import tempfile
import base64
import mimetypes
from PIL import Image

MAX_QR_BYTES = 2953

def file_to_base64(file_path):
    """将本地文件转换为 base64 字符串（含 data URL 头）"""
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('utf-8')
    mime = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    return f"data:{mime};base64,{b64}"

def image_to_qr_data(image_path):
    """处理图片，返回要编码的数据"""
    base64_str = file_to_base64(image_path)
    if len(base64_str) <= MAX_QR_BYTES:
        return base64_str
    else:
        return f"图片太大无法直接存储，请上传至图床后使用 URL 生成二维码。"

def generate_qr(data: str) -> str:
    """生成二维码，返回图片路径"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"qr_{hash(data)}.png")
    img.save(file_path)
    return file_path

def handle_call(args: dict):
    """技能入口函数"""
    content = args.get("content", "")
    image_path = args.get("image", "")

    # 优先处理图片
    if image_path:
        if not os.path.exists(image_path):
            return {"error": f"图片文件不存在：{image_path}"}
        file_size = os.path.getsize(image_path)
        if file_size > 10 * 1024 * 1024:
            return {"error": "图片太大，请选择小于10MB的图片"}
        qr_data = image_to_qr_data(image_path)
        if qr_data.startswith("图片太大"):
            return {"message": qr_data}
    elif content:
        qr_data = content
    else:
        return {"error": "没有提供任何内容或图片"}

    try:
        path = generate_qr(qr_data)
        return {"image_path": path}
    except Exception as e:
        return {"error": str(e)}
