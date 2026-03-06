# 在导入部分添加PyPDF2库
import os
import re
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side, Font
import PyPDF2  # 添加PyPDF2库用于文本型PDF处理

def clean_text_for_excel(text):
    """清理文本中Excel不支持的字符"""
    if not isinstance(text, str):
        return text
    
    # 替换已知的非法字符
    replacements = {
        '\x00': '', '\x01': '', '\x02': '', '\x03': '', '\x04': '', '\x05': '', '\x06': '', '\x07': '',
        '\x08': '', '\x0b': '', '\x0c': '', '\x0e': '', '\x0f': '', '\x10': '', '\x11': '', '\x12': '',
        '\x13': '', '\x14': '', '\x15': '', '\x16': '', '\x17': '', '\x18': '', '\x19': '', '\x1a': '',
        '\x1b': '', '\x1c': '', '\x1d': '', '\x1e': '', '\x1f': '',
        '×': 'x',  # 替换乘号
        '÷': '/',  # 替换除号
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # 移除其他可能的控制字符
    text = ''.join(ch for ch in text if ord(ch) >= 32 or ch in '\r\n\t')
    
    # 截断过长的文本
    if len(text) > 32000:  # Excel单元格字符限制
        text = text[:32000] + "..."
    
    return text

def extract_date_from_filename(filename):
    """从文件名中提取日期时间信息"""
    # 尝试匹配常见的日期格式，如20230101、2023-01-01、2023.01.01等
    date_patterns = [
        r'(\d{4}[-_\.年]\d{1,2}[-_\.月]\d{1,2}[日]?)',  # 2023-01-01、2023.01.01、2023年01月01日
        r'(\d{8})',  # 20230101
        r'(\d{4}[-_\.]\d{2})',  # 2023-01、2023.01
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
    
    return "未识别"

def extract_text_from_pdf_image(pdf_path):
    """从PDF图片中提取文本"""
    try:
        # 将PDF转换为图像
        images = convert_from_path(pdf_path)
        
        # 处理第一页（假设表格在第一页）
        if images:
            image = images[0]
            
            # 转换为OpenCV格式进行处理
            img_np = np.array(image)
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # 转为灰度图
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # 使用pytesseract进行OCR识别
            text = pytesseract.image_to_string(gray, lang='chi_sim')
            return text
        else:
            print(f"无法从PDF提取图像: {pdf_path}")
            return ""
    except Exception as e:
        print(f"从PDF图像提取文本时出错: {e}")
        return ""

def parse_table_data_from_image(text, pdf_path):
    """从图像提取的文本中解析表格数据"""
    data = {}
    
    # 注意：已移除姓名、身份证号和借据号的识别
    
    # 项目名称 - 保留原有逻辑，但可能不适用于债权转让证明
    project_name_pattern = r"项目名称\s*(.*?)(?=\s*项目编码|\s*项目编号|\s*出让方全称|\n\s*\n)"
    project_name_match = re.search(project_name_pattern, text, re.DOTALL)
    if project_name_match:
        data["项目名称"] = clean_text_for_excel(project_name_match.group(1).strip().replace('\n', ' '))
    else:
        # 尝试从整个文本中提取项目名称
        full_name_pattern = r"关于\s*(.*?)不良贷款转让"
        full_name_match = re.search(full_name_pattern, text, re.DOTALL)
        if full_name_match:
            data["项目名称"] = clean_text_for_excel(full_name_match.group(1).strip().replace('\n', ' '))
        else:
            data["项目名称"] = "未识别"
    
    # 项目编码/项目编号 - 确保在项目名称之后单独匹配
    project_code_pattern = r"(项目编号|项目编码)\s*([A-Za-z0-9\-_]+)"
    project_code_match = re.search(project_code_pattern, text, re.DOTALL)
    if project_code_match:
        data["项目编码"] = project_code_match.group(2).strip()
    else:
        data["项目编码"] = "未识别"
    
    # 出让方全称
    seller_pattern = r"出让方全称\s*(.*?)(?=\n|$)"
    seller_match = re.search(seller_pattern, text, re.DOTALL)
    if seller_match:
        data["出让方全称"] = clean_text_for_excel(seller_match.group(1).strip())
    else:
        # 尝试匹配债权转让证明中的银行名称
        bank_pattern = r"与([\u4e00-\u9fa5]+银行[\u4e00-\u9fa5]*公司).*?签订"
        bank_match = re.search(bank_pattern, text, re.DOTALL)
        if bank_match:
            data["出让方全称"] = clean_text_for_excel(bank_match.group(1).strip())
        else:
            data["出让方全称"] = "未识别"
    
    # 受让方全称
    buyer_pattern = r"受让方全称\s*(.*?)(?=\n|$)"
    buyer_match = re.search(buyer_pattern, text, re.DOTALL)
    if buyer_match:
        data["受让方全称"] = clean_text_for_excel(buyer_match.group(1).strip())
    else:
        # 尝试匹配债权转让证明中的受让方
        new_buyer_pattern = r"转让至([\u4e00-\u9fa5]+(?:有限公司|有限责任公司|企业))"
        new_buyer_match = re.search(new_buyer_pattern, text, re.DOTALL)
        if new_buyer_match:
            data["受让方全称"] = clean_text_for_excel(new_buyer_match.group(1).strip())
        else:
            data["受让方全称"] = "未识别"
    
    # 转让协议签署日期
    date_pattern = r"转让协议签署日期\s*(\d{4}年\d{1,2}月\d{1,2}日)"
    date_match = re.search(date_pattern, text, re.DOTALL)
    if date_match:
        data["转让协议签署日期"] = date_match.group(1).strip()
    else:
        # 尝试匹配债权转让证明中的日期格式
        new_date_pattern = r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
        new_date_match = re.search(new_date_pattern, text)
        if new_date_match:
            year = new_date_match.group(1)
            month = new_date_match.group(2)
            day = new_date_match.group(3)
            data["转让协议签署日期"] = f"{year}年{month}月{day}日"
        else:
            data["转让协议签署日期"] = "未识别"
    
    # 添加文件名
    filename = os.path.basename(pdf_path)
    data["文件名"] = filename
    
    # 获取PDF所在文件夹的名称
    parent_folder = os.path.basename(os.path.dirname(pdf_path))
    data["文件夹"] = parent_folder
    # 从PDF右下角提取时间
    # 匹配PDF中的日期格式（如：2024年9月23日），优先选择靠近文本末尾的日期
    footer_date_pattern = r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
    # 查找所有匹配项
    footer_date_matches = list(re.finditer(footer_date_pattern, text))
    
    if footer_date_matches:
        # 选择最后一个匹配项（通常是PDF右下角的日期）
        last_match = footer_date_matches[-1]
        year = last_match.group(1)
        month = last_match.group(2)
        day = last_match.group(3)
        data["文件时间"] = f"{year}年{month}月{day}日"
        print(f"从PDF提取到日期: {data['文件时间']}")
    else:
        # 如果在PDF中没有找到日期，则尝试从文件名提取
        file_date = extract_date_from_filename(parent_folder)
        data["文件时间"] = file_date
        print(f"未从PDF提取到日期，使用文件名日期: {file_date}")
    
    # 提取欠款金额信息
    amount_pattern = r"([0-9]+\.[0-9]+)\s*元\s*\(大写[^)]+\)"
    amount_match = re.search(amount_pattern, text)
    if amount_match:
        data["欠款金额"] = amount_match.group(1).strip()
    else:
        data["欠款金额"] = "未识别"
    
    return data

def is_text_pdf(pdf_path):
    """检测PDF是否为文本型PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            page = reader.pages[0]  # 检查第一页
            text = page.extract_text()
            
            # 如果提取的文本长度超过一定阈值，认为是文本型PDF
            # 这里设置100个字符作为阈值，可以根据实际情况调整
            if len(text) > 100:
                return True, text
            return False, ""
    except Exception as e:
        print(f"检测PDF类型时出错: {e}")
        return False, ""

def extract_text_from_text_pdf(pdf_path):
    """从文本型PDF中提取文本"""
    try:
        all_text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # 提取所有页面的文本
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                all_text += text + "\n"
        return all_text
    except Exception as e:
        print(f"从文本型PDF提取文本时出错: {e}")
        return ""

def process_pdf(pdf_path):
    """处理PDF文件并提取表格信息，自动区分文本型和图像型PDF"""
    # 首先检测PDF类型
    is_text, text = is_text_pdf(pdf_path)
    
    if is_text and text:
        print(f"检测到文本型PDF: {pdf_path}")
        # 对于文本型PDF，直接使用提取的文本
        full_text = extract_text_from_text_pdf(pdf_path)
    else:
        print(f"检测到图像型PDF或无法确定类型: {pdf_path}")
        # 对于图像型PDF或无法确定类型的PDF，使用OCR方法
        full_text = extract_text_from_pdf_image(pdf_path)
    
    if not full_text:
        print(f"无法从PDF提取文本: {pdf_path}")
        return None
    
    # 解析表格数据
    data = parse_table_data_from_image(full_text, pdf_path)
    
    return data

def find_all_pdfs(directory):
    """递归查找目录及其子目录中的所有PDF文件"""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def save_to_combined_excel(all_data, output_path):
    """将所有数据保存到一个Excel文件中"""
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 创建DataFrame
    columns = ["文件名", "文件时间", "文件夹", "项目名称", "项目编码", "出让方全称", "受让方全称", "转让协议签署日期"]
    
    # 清理所有数据中的非法字符
    cleaned_data = []
    for item in all_data:
        if item:  # 确保数据不为None
            cleaned_item = {}
            for key, value in item.items():
                if key in columns:  # 只保留需要的列
                    cleaned_item[key] = clean_text_for_excel(value)
            cleaned_data.append(cleaned_item)
    
    df = pd.DataFrame(cleaned_data, columns=columns)
    
    # 尝试使用xlsxwriter引擎保存，这可能有助于处理特殊字符
    try:
        df.to_excel(output_path, index=False, sheet_name="不良贷款转让信息", engine='xlsxwriter')
    except Exception as e:
        print(f"使用xlsxwriter保存Excel失败: {e}")
        # 如果xlsxwriter失败，尝试使用默认引擎
        try:
            df.to_excel(output_path, index=False, sheet_name="不良贷款转让信息")
        except Exception as e2:
            print(f"使用默认引擎保存Excel也失败: {e2}")
            # 最后尝试保存为CSV
            csv_path = output_path.replace('.xlsx', '.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"已将数据保存为CSV格式: {csv_path}")
            return
    
    print(f"所有数据已保存到: {output_path}")

def main():
    # 设置固定的输入和输出路径
    pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "银登结果爬取记录")
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "债权转让证明信息汇总.xlsx")
    
    print(f"正在查找 {pdf_dir} 目录下的所有PDF文件...")
    
    # 查找所有PDF文件
    pdf_files = find_all_pdfs(pdf_dir)
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 存储所有PDF的处理结果
    all_data = []
    
    # 处理所有找到的PDF文件
    for pdf_path in pdf_files:
        print(f"正在处理: {pdf_path}")
        
        try:
            # 提取数据
            data = process_pdf(pdf_path)
            if data:
                all_data.append(data)
                print(f"成功处理: {os.path.basename(pdf_path)}")
            else:
                print(f"处理失败，无法提取数据: {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"处理 {pdf_path} 时出错: {e}")
    
    # 将所有数据保存到一个Excel文件
    if all_data:
        save_to_combined_excel(all_data, output_file)
        print(f"所有数据已合并保存到: {output_file}")
    else:
        print("没有成功处理任何PDF文件，未生成Excel文件")

if __name__ == "__main__":
    main()