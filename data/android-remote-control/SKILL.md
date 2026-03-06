---
name: android-remote-control
description: 远程控制 Android 设备，支持截图、点击、滑动及 App 管理。使用 uiautomator2 作为底层引擎，通过 ADB 连接设备。当用户需要：(1) 查看手机屏幕，(2) 自动化操作手机 App，(3) 远程安装/卸载软件，(4) 跨设备协作时，使用此技能。
---

# Android Remote Control (安卓远程分身)

本技能通过 `uiautomator2` 库实现对 Android 设备的远程操控。

## ?? 核心工具脚本

- **位置**: `scripts/remote_control.py`
- **功能**:
  - `snap [path]`: 获取屏幕截图。
  - `click <x> <y>`: 在指定坐标点击。
  - `start <package_name>`: 启动指定 App。

## ? 操作指南

### 1. 设备连接
确保手机已开启“USB 调试”，且电脑已识别设备。
本环境默认 ADB 路径为：`C:\Program Files (x86)\Camo Studio\Adb`

### 2. 常用操作指令
- **截图预览**: 
  ```bash
  python scripts/remote_control.py snap workspace/last_snap.jpg
  ```
- **视觉引导点击**:
  先截图并使用视觉模型（如 Qwen-VL）定位坐标，再执行：
  ```bash
  python scripts/remote_control.py click 0.5 0.5
  ```

### 3. 注意事项
- 首次使用可能需要在手机端确认“允许 USB 调试”。
- 如遇到 `node command not allowed` 错误，请检查 Gateway 的安全策略。
