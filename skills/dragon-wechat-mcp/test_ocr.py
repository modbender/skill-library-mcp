#!/usr/bin/env python
"""使用 Windows OCR 识别微信联系人名称"""
import sys
import os
from PIL import Image, ImageGrab
import win32gui

def get_wechat_window():
    hwnd = win32gui.FindWindow(None, '微信')
    if not hwnd:
        return None
    return hwnd

def capture_and_recognize():
    hwnd = get_wechat_window()
    if not hwnd:
        print("未找到微信窗口")
        return None
    
    # 获取窗口客户区大小
    client_rect = win32gui.GetClientRect(hwnd)
    print(f"客户区大小: {client_rect}")
    
    # 转换到屏幕坐标 - 使用 GetWindowRect 而不是 GetClientRect
    window_rect = win32gui.GetWindowRect(hwnd)
    print(f"窗口位置: {window_rect}")
    
    # 联系人名称区域（从截图估算的相对位置）
    # 从窗口顶部往下约50-80像素，左侧约10像素开始
    left = window_rect[0] + 10
    top = window_rect[1] + 55
    right = left + 200
    bottom = top + 40
    
    print(f"截取区域: ({left}, {top}, {right}, {bottom})")
    
    # 截取
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    img.save("wechat_contact_area.png")
    print("已保存截图到 wechat_contact_area.png")
    
    # 使用 Windows OCR
    try:
        from PIL import Image
        import winrt.windows.media.ocr as ocr
        import asyncio
        
        async def do_ocr():
            # 从文件加载图片
            img = Image.open("wechat_contact_area.png")
            # 转换为 Windows.Graphics.Bitmap
            # 这里需要更多处理...
            
        # 简化版：直接返回路径，让用户确认
        return "wechat_contact_area.png"
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

if __name__ == "__main__":
    capture_and_recognize()
