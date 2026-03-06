# Image Utilities

"""圖片處理工具，提供裁剪、保存、編碼等功能。"""

import os
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def crop_image(
    image_path: str,
    bbox: Tuple[int, int, int, int],
    output_path: Optional[str] = None
) -> str:
    """
    裁剪圖片的指定區域。
    
    Args:
        image_path: 原始圖片路徑
        bbox: 邊界框 (x, y, width, height)
        output_path: 輸出圖片路徑（可選，預設為臨時檔案）
        
    Returns:
        裁剪後的圖片路徑
    """
    if not PILLOW_AVAILABLE:
        raise ImportError("Pillow 未安裝，請執行：uv pip install Pillow")
    
    x, y, width, height = bbox
    
    with Image.open(image_path) as img:
        # 計算裁剪區域（left, upper, right, lower）
        left = x
        upper = y
        right = x + width
        lower = y + height
        
        # 確保不超出圖片邊界
        right = min(right, img.width)
        lower = min(lower, img.height)
        
        cropped = img.crop((left, upper, right, lower))
        
        if output_path is None:
            # 生成臨時檔案路徑
            output_path = Path(image_path).parent / f"cropped_{Path(image_path).name}"
        
        cropped.save(output_path)
    
    return output_path


def save_image(
    image_path: str,
    output_path: str,
    format: Optional[str] = None,
    quality: int = 95
) -> str:
    """
    保存圖片，可轉換格式。
    
    Args:
        image_path: 原始圖片路徑
        output_path: 輸出圖片路徑
        format: 輸出格式（可選，預設從副檔名判斷）
        quality: 品質（1-100，僅對 JPEG 有效）
        
    Returns:
        輸出的圖片路徑
    """
    if not PILLOW_AVAILABLE:
        raise ImportError("Pillow 未安裝，請執行：uv pip install Pillow")
    
    with Image.open(image_path) as img:
        # 轉換格式（如果需要）
        if format:
            img.save(output_path, format=format.upper(), quality=quality)
        else:
            img.save(output_path, quality=quality)
    
    return output_path


def encode_image_to_base64(image_path: str) -> str:
    """
    將圖片編碼為 base64 字串。
    
    Args:
        image_path: 圖片路徑
        
    Returns:
        base64 編碼的字串
    """
    import base64
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_size(image_path: str) -> Tuple[int, int]:
    """
    取得圖片尺寸。
    
    Args:
        image_path: 圖片路徑
        
    Returns:
        (寬度，高度)
    """
    if PILLOW_AVAILABLE:
        with Image.open(image_path) as img:
            return img.width, img.height
    else:
        # 使用 PIL 的基本功能（不需要完整安裝）
        import struct
        
        with open(image_path, "rb") as f:
            # PNG
            if f.read(8)[:8] == b'\x89PNG\r\n\x1a\n':
                f.seek(16)
                width = struct.unpack(">I", f.read(4))[0]
                height = struct.unpack(">I", f.read(4))[0]
                return width, height
            
            # JPEG
            f.seek(0)
            data = f.read()
            if data[:2] == b'\xff\xd8':
                import re
                matches = re.finditer(b'\xff\xc0(.{7})', data)
                for match in matches:
                    height, width = struct.unpack(">HH", match.group(1)[5:9])
                    return width, height
        
        raise ValueError("無法識別圖片格式")


def resize_image(
    image_path: str,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    output_path: Optional[str] = None
) -> str:
    """
    調整圖片大小。
    
    Args:
        image_path: 原始圖片路徑
        max_width: 最大寬度
        max_height: 最大高度
        output_path: 輸出路徑（可選）
        
    Returns:
        調整後的圖片路徑
    """
    if not PILLOW_AVAILABLE:
        raise ImportError("Pillow 未安裝，請執行：uv pip install Pillow")
    
    with Image.open(image_path) as img:
        width, height = img.size
        
        # 計算縮放比例
        scale = 1.0
        if max_width and width > max_width:
            scale = min(scale, max_width / width)
        if max_height and height > max_height:
            scale = min(scale, max_height / height)
        
        if scale < 1.0:
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        if output_path is None:
            output_path = Path(image_path).parent / f"resized_{Path(image_path).name}"
        
        img.save(output_path)
    
    return output_path
