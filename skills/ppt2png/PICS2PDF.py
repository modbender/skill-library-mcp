import os
from PIL import Image
from fpdf import FPDF

# 设置图片所在文件夹路径
folder_path =  '/Users/mw/Downloads/ChatGPT高质量prompt技巧分享'

# 获取文件夹下所有文件的名称，并根据数字排序
image_files = sorted(
    [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))],
    key=lambda x: int(os.path.splitext(x)[0]))

# 创建一个 PDF 文件
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# 循环处理每张图片
for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)

    try:
        # 打开图片并获取图片尺寸
        img = Image.open(image_path)
        img_width, img_height = img.size

        # 将图片尺寸转换为适应 PDF 页面
        pdf.add_page()
        # 将图片大小缩放到 A4 页面大小，并保持图片比例
        aspect_ratio = img_width / img_height
        pdf_width = 210  # A4 宽度（mm）
        pdf_height = 297  # A4 高度（mm）

        if aspect_ratio > 1:
            pdf_img_width = pdf_width
            pdf_img_height = pdf_width / aspect_ratio
        else:
            pdf_img_height = pdf_height
            pdf_img_width = pdf_height * aspect_ratio

        # 添加图片到 PDF
        pdf.image(image_path, x=(pdf_width - pdf_img_width) / 2, y=(pdf_height - pdf_img_height) / 2, w=pdf_img_width,
                  h=pdf_img_height)

    except Exception as e:
        print(f"无法加载图片 {image_file}: {e}")
        continue

# 输出 PDF 文件
pdf_output_path = '/Users/mw/Downloads/ChatGPT高质量prompt技巧分享.pdf'
pdf.output(pdf_output_path)

print(f'PDF 文件已生成：{pdf_output_path}')

