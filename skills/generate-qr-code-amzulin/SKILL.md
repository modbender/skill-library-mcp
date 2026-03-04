
---
name: generate-qr-code
description: 生成二维码/条形码，支持文本、URL、WiFi 配置等内容，可自定义尺寸、颜色并指定保存路径
version: 1.0.0
author: 二码大神
permissions: 文件写入权限（用于保存二维码图片）
---

# Generate QR Code Skill（生成二维码技能）

## 1. Description
当用户需要将文本、URL、WiFi 信息等转换为可视化二维码时，使用此技能生成二维码图片，并保存到指定路径（默认保存到桌面），支持自定义尺寸和颜色。

## 2. When to use
- 用户说：“帮我把 https://openclaw.ai 生成二维码”
- 用户说：“生成一个包含 WiFi 信息的二维码，名称：MyWiFi，密码：12345678”
- 用户说：“生成黑色二维码，内容是‘Hello OpenClaw’，保存到 D 盘根目录”
- 用户说：“帮我做一个 400px 大小的二维码，内容是我的手机号 13800138000”

## 3. How to use
1. 从用户消息中提取核心参数：
   - 必选：生成内容（文本/URL/WiFi 信息，WiFi 格式需为“WIFI:S:名称;T:类型;P:密码;;”）；
   - 可选：尺寸（默认 300px）、颜色（默认黑色）、保存路径（默认桌面）；
2. 若用户未指定可选参数，使用默认值；
3. 调用 agent.py 中的 generate_qr 函数执行生成操作；
4. 返回结果：告知用户二维码保存路径，若生成失败，说明具体原因（如路径无权限、内容为空）。

## 4. Implementation（代码关联说明）
- 依赖库：qrcode（生成二维码）、Pillow（图片处理）；
- 核心函数：async def generate_qr(text: str, size: int = 300, color: str = "black", save_path: str = None)；
- 参数说明：
  - text：二维码内容（必选）；
  - size：二维码尺寸（单位 px，默认 300）；
  - color：填充颜色（默认 black，支持英文颜色名或十六进制色值，如 #FF0000）；
  - save_path：保存路径（默认桌面，文件名：qr_code.png）。

## 5. Edge cases
- 内容为空：回复“请提供需要生成二维码的内容（如文本、URL、WiFi 信息）”；
- 保存路径无权限：回复“指定路径无写入权限，请更换保存路径（如桌面）”；
- 未安装依赖库：自动尝试安装 qrcode 和 Pillow，若安装失败，提示用户手动执行“pip install qrcode pillow”；
- 特殊字符内容：自动过滤无效字符，确保二维码可正常识别。
