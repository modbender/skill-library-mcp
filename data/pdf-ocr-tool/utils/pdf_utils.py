# PDF Utilities

"""PDF 處理工具，提供 PDF 轉圖片、頁數計算等功能。"""

import os
import subprocess
import glob
from pathlib import Path
from typing import List, Optional


def pdf_to_images(
    pdf_path: str,
    output_prefix: Optional[str] = None,
    dpi: int = 150
) -> List[str]:
    """
    將 PDF 轉換為圖片序列。
    
    Args:
        pdf_path: PDF 檔案路徑
        output_prefix: 輸出圖片前綴名（預設為 PDF 檔名）
        dpi: 解析度（DPI）
        
    Returns:
        圖片檔案路徑列表
    """
    pdf_path = Path(pdf_path)
    
    if output_prefix is None:
        output_prefix = pdf_path.stem
    
    # 建立臨時輸出目錄
    output_dir = pdf_path.parent
    output_base = str(output_dir / output_prefix)
    
    try:
        # 使用 pdftoppm 轉換
        cmd = [
            "pdftoppm",
            "-png",
            "-r", str(dpi),
            str(pdf_path),
            output_base
        ]
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        # 找出所有生成的圖片
        images = sorted(glob.glob(f"{output_base}*.png"))
        return images
        
    except subprocess.CalledProcessError as e:
        error_msg = f"PDF 轉換失敗：{e}"
        if e.stderr:
            error_msg += f"\n{e.stderr}"
        raise RuntimeError(error_msg)
    
    except FileNotFoundError:
        raise RuntimeError(
            "未找到 pdftoppm，請安裝 poppler-utils:\n"
            "  sudo apt install poppler-utils  # Debian/Ubuntu\n"
            "  brew install poppler  # macOS"
        )


def get_pdf_page_count(pdf_path: str) -> int:
    """
    取得 PDF 頁數。
    
    Args:
        pdf_path: PDF 檔案路徑
        
    Returns:
        頁數
    """
    try:
        # 使用 pdfinfo 取得頁數
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("Pages:"):
                    return int(line.split(":")[1].strip())
        
        # 如果 pdfinfo 失敗，嘗試用 pdftoppm 間接計算
        images = pdf_to_images(pdf_path, output_prefix="temp_count_")
        # 清理臨時檔案
        for img in images:
            os.remove(img)
        return len(images)
        
    except FileNotFoundError:
        # 如果 pdfinfo 和 pdftoppm 都沒有，嘗試用 pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except:
            raise RuntimeError(
                "無法取得 PDF 頁數，請安裝 poppler-utils 或 pdfplumber"
            )


def get_pdf_info(pdf_path: str) -> dict:
    """
    取得 PDF 詳細資訊。
    
    Args:
        pdf_path: PDF 檔案路徑
        
    Returns:
        PDF 資訊字典
    """
    info = {
        "path": str(pdf_path),
        "pages": 0,
        "title": None,
        "author": None,
        "subject": None,
        "creator": None,
        "producer": None,
        "creation_date": None,
        "mod_date": None,
    }
    
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    
                    if key == "pages":
                        info["pages"] = int(value)
                    elif key in info:
                        info[key] = value
    except:
        pass
    
    return info


def is_pdf_valid(pdf_path: str) -> bool:
    """
    檢查 PDF 是否有效。
    
    Args:
        pdf_path: PDF 檔案路徑
        
    Returns:
        是否有效
    """
    try:
        # 嘗試取得頁數
        page_count = get_pdf_page_count(pdf_path)
        return page_count > 0
    except:
        return False
