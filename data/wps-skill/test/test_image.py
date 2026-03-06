#!/usr/bin/env python3
"""创建测试图片"""

from PIL import Image, ImageDraw, ImageFont

# 创建一个简单的测试图片
img = Image.new('RGB', (400, 300), color='lightblue')
draw = ImageDraw.Draw(img)

# 添加文字
draw.text((150, 130), "Test Image", fill='black')

# 保存
img.save('/Users/usali/Documents/GitHub/Maxstorm/wps-skill/test/test_image.jpg', 'JPEG')
print("测试图片已创建: test/test_image.jpg")
