---
name: ppt2png
description: ppt2png
---

ppt2png

适用某个PPT，帮我生成图片和缩略图
mac版本的PPT自动按页生成每一张截图和缩略图

原理是：

基于PPT → PDF（使用 LibreOffice）
PDF → 每页 PNG（使用 Ghostscript）
每 6 张图片生成 1 张缩略拼接图（3列 × 2行）
兼容 Python 3.6
自动分目录

⚠️ 需要提前安装：
brew install ghostscript
pip3 install pillow


工作流程

主程序：Pdftp.py

配置文件：config.json

自动读取配置

支持修改 DPI、列数、行数、LibreOffice 路径、gs 路径


针对config.json
如果 which gs 输出是：
/opt/homebrew/bin/gs

就改成：

"ghostscript_path": "/opt/homebrew/bin/gs"