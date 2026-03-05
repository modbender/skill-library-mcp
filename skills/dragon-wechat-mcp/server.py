import asyncio
import json
import os
import time
from pathlib import Path

import pyautogui
pyautogui.FAILSAFE = False
import pygetwindow as gw
from PIL import Image, ImageGrab
import pyperclip


def get_wechat_main_window():
    """获取微信主窗口"""
    windows = gw.getWindowsWithTitle("微信")
    for w in windows:
        if w.width > 500 and w.width < 2000:
            return w
    return None


def capture_contact_name_area():
    """截取联系人名称区域（聊天窗口顶部）"""
    win = get_wechat_main_window()
    if not win:
        return None
    
    # 联系人名称区域：搜索框下方，约在窗口顶部往下 50-80 像素
    # 从截图看，位置大约在 (10, 60) 到 (200, 90)
    left = win.left + 10
    top = win.top + 60
    right = win.left + 200
    bottom = win.top + 95
    
    bbox = (left, top, right, bottom)
    img = ImageGrab.grab(bbox=bbox)
    return img


def get_current_contact_from_window():
    """从微信窗口截图识别当前联系人名称"""
    win = get_wechat_main_window()
    if not win:
        return None
    
    # 方法1: 尝试从窗口标题获取（某些版本微信会显示）
    title = win.title
    if "微信" not in title or title == "微信":
        # 标题不包含联系人名，尝试截图识别
        pass
    else:
        # 去掉 "微信" 部分
        contact = title.replace("微信", "").strip()
        if contact and contact != "微信":
            return contact
    
    # 方法2: 截取联系人名称区域保存图片，供人工确认
    img = capture_contact_name_area()
    if img:
        img.save(str(Path(__file__).parent / "contact_name.png"))
        print(f"[DEBUG] 已保存联系人名称区域到 contact_name.png")
    
    return None  # 需要人工确认或OCR


def get_chat_window(contact_name=None):
    """获取聊天窗口"""
    if contact_name:
        windows = gw.getWindowsWithTitle(contact_name)
        for win in windows:
            if contact_name in win.title:
                return win
        return None
    
    # 没指定联系人，尝试从当前窗口获取
    win = get_wechat_main_window()
    return win


def capture_window(contact_name=None):
    """截取窗口"""
    win = get_chat_window(contact_name)
    if not win:
        # 如果没有指定窗口，尝试获取微信窗口
        windows = gw.getWindowsWithTitle("微信")
        for w in windows:
            if w.width > 500 and w.width < 2000:
                return w
        return None
    
    try:
        win.activate()
        time.sleep(0.3)
    except:
        pass
    
    bbox = (win.left, win.top, win.right, win.bottom)
    return ImageGrab.grab(bbox=bbox)


def verify_chat(contact_name=None):
    """Step 1: 确认聊天窗口"""
    win = get_chat_window(contact_name)
    if not win:
        # 尝试获取微信主窗口中的聊天
        wins = gw.getWindowsWithTitle("微信")
        for w in wins:
            if w.width > 500:
                win = w
                break
    
    if not win:
        return False, "未找到聊天窗口"
    
    print(f"聊天窗口: {win.title}")
    print(f"位置: ({win.left}, {win.top}), 大小: ({win.width}, {win.height})")
    
    # 截取窗口
    img = capture_window()
    if img:
        img.save(str(Path(__file__).parent / "verify.png"))
    
    return True, None


def input_message(message, contact_name=None):
    """Step 2-3: 输入消息并确认"""
    win = get_chat_window(contact_name)
    if not win:
        wins = gw.getWindowsWithTitle("微信")
        for w in wins:
            if w.width > 500:
                win = w
                break
    
    if not win:
        return False, "未找到聊天窗口"
    
    win_left = win.left
    win_top = win.top
    win_width = win.width
    win_height = win.height
    win_right = win.left + win_width
    win_bottom = win.top + win_height
    
    # 点击输入框
    input_x = win_left + win_width // 2
    input_y = win_bottom - 60
    pyautogui.click(input_x, input_y)
    time.sleep(0.2)
    
    # 复制消息到剪贴板
    pyperclip.copy(message)
    time.sleep(0.1)
    
    # 粘贴
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    
    # 确认输入
    input_bbox = (win_left, win_bottom - 80, win_right, win_bottom - 20)
    input_img = ImageGrab.grab(bbox=input_bbox)
    input_img.save(str(Path(__file__).parent / "input_verify.png"))
    
    return True, None


def send_message(contact_name=None):
    """Step 4: 发送消息"""
    win = get_chat_window(contact_name)
    if not win:
        wins = gw.getWindowsWithTitle("微信")
        for w in wins:
            if w.width > 500:
                win = w
                break
    
    if not win:
        return False, "未找到聊天窗口"
    
    # 发送
    pyautogui.press('enter')
    time.sleep(0.3)
    
    # 确认发送结果
    img = capture_window()
    if img:
        img.save(str(Path(__file__).parent / "result.png"))
    
    return True, None


def send_message_to_current(message, contact_name=None):
    """给指定联系人发送消息"""
    print(f"发送消息: {message}")
    if contact_name:
        print(f"目标联系人: {contact_name}")
    
    # Step 1: 确认聊天窗口
    print("\n=== Step 1: 确认聊天窗口 ===")
    success, err = verify_chat(contact_name)
    if not success:
        return False, err
    
    # Step 2-3: 输入消息
    print("\n=== Step 2-3: 输入消息 ===")
    success, err = input_message(message, contact_name)
    if not success:
        return False, err
    
    # Step 4: 发送
    print("\n=== Step 4: 发送 ===")
    success, err = send_message(contact_name)
    if not success:
        return False, err
    
    print("\n=== 发送完成! ===")
    return True, None


def get_wechat_status():
    """获取微信状态"""
    win = get_wechat_main_window()
    if not win:
        return {"status": "not_running", "message": "微信未运行"}
    
    contact = get_current_contact_from_window()
    
    return {
        "status": "running",
        "current_contact": contact,
        "title": win.title,
        "position": {"x": win.left, "y": win.top},
        "size": {"width": win.width, "height": win.height}
    }


# MCP 工具定义
TOOLS = [
    {
        "name": "wechat_get_status",
        "description": "获取微信状态",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "wechat_send_message",
        "description": "给当前聊天窗口发送消息，不传contact则自动识别",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "消息内容"},
                "contact": {"type": "string", "description": "联系人名称（可选，默认自动从窗口获取）"}
            },
            "required": ["message"]
        }
    }
]


async def handle_tool(name, arguments):
    """处理工具调用"""
    if name == "wechat_get_status":
        result = get_wechat_status()
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
    
    elif name == "wechat_send_message":
        message = arguments.get("message")
        contact = arguments.get("contact")  # 可选的联系人参数
        
        if not message:
            return {"content": [{"type": "text", "text": "错误: 需要指定消息内容"}]}
        
        # 如果没指定联系人，自动从当前窗口获取
        if not contact:
            contact = get_current_contact_from_window()
            if not contact:
                return {"content": [{"type": "text", "text": "[ERROR] 无法获取当前联系人，请确保微信聊天窗口已打开"}]}
        
        success, err = send_message_to_current(message, contact)
        
        if success:
            return {"content": [{"type": "text", "text": f"[OK] 消息已发送到 {contact}\n内容: {message}"}]}
        else:
            return {"content": [{"type": "text", "text": f"[ERROR] 错误: {err}"}]}
    
    return {"content": [{"type": "text", "text": "未知命令"}]}


async def main():
    """MCP 主循环"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            
            if request.get("method") == "tools/list":
                response = {"jsonrpc": "2.0", "id": request.get("id"), "result": {"tools": TOOLS}}
                print(json.dumps(response), flush=True)
            
            elif request.get("method") == "tools/call":
                tool_name = request.get("name")
                tool_args = request.get("arguments", {})
                result = await handle_tool(tool_name, tool_args)
                response = {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
                print(json.dumps(response), flush=True)
        
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": str(e)}), flush=True)


if __name__ == "__main__":
    import sys
    asyncio.run(main())
