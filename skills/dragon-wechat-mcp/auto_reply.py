#!/usr/bin/env python
"""微信消息监控与自动回复"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyautogui
pyautogui.FAILSAFE = False
import pygetwindow as gw
from PIL import Image, ImageGrab
import pyperclip

from server import get_wechat_main_window, get_current_contact_from_window, send_message_to_current


def capture_chat_area():
    """截取聊天区域"""
    win = get_wechat_main_window()
    if not win:
        return None
    
    # 聊天区域在窗口左侧，约2/3宽度
    chat_left = win.left
    chat_top = win.top + 50  # 标题栏下方
    chat_width = win.width * 2 // 3
    chat_height = win.height - 100
    
    bbox = (chat_left, chat_top, chat_left + chat_width, chat_top + chat_height)
    return ImageGrab.grab(bbox=bbox)


def get_last_message_info():
    """获取最新一条消息的信息"""
    win = get_wechat_main_window()
    if not win:
        return None, None
    
    # 获取当前联系人
    contact = get_current_contact_from_window()
    if not contact:
        return None, None
    
    # 截取聊天区域
    img = capture_chat_area()
    if img:
        img.save("last_chat.png")
    
    return contact, img


def auto_reply(message):
    """自动回复 - 确保发给正确的人"""
    # 先确认当前聊天窗口的联系人
    contact = get_current_contact_from_window()
    if not contact:
        print("[ERROR] 无法获取当前联系人")
        return False
    
    print(f"[INFO] 当前聊天窗口: {contact}")
    print(f"[INFO] 发送回复: {message}")
    
    success, err = send_message_to_current(message, contact)
    
    if success:
        print(f"[OK] 已回复给 {contact}")
        return True
    else:
        print(f"[ERROR] 回复失败: {err}")
        return False


def test_auto_reply():
    """测试自动回复"""
    print("=== 微信自动回复测试 ===\n")
    
    # Step 1: 获取当前状态
    print("Step 1: 检查微信状态...")
    from server import get_wechat_status
    status = get_wechat_status()
    print(f"状态: {json.dumps(status, ensure_ascii=False, indent=2)}\n")
    
    # Step 2: 获取当前联系人
    print("Step 2: 获取当前联系人...")
    contact = get_current_contact_from_window()
    print(f"当前联系人: {contact}\n")
    
    if not contact:
        print("[ERROR] 请先打开一个聊天窗口")
        return
    
    # Step 3: 发送测试消息
    print("Step 3: 发送测试回复...")
    test_msg = "测试自动回复 🐉"
    success, _ = send_message_to_current(test_msg, contact)
    
    if success:
        print(f"\n[OK] 测试成功！消息已发送给: {contact}")
    else:
        print(f"\n[ERROR] 测试失败")


if __name__ == "__main__":
    test_auto_reply()
