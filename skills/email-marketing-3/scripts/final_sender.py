import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import json
import os
import random
import string
import re
from typing import Optional, Dict, Tuple

# --- 配置信息 (从环境变量读取) ---
SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.corp.netease.com")
SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "465"))
SMTP_USER = os.getenv("EMAIL_SMTP_USER", "")
SMTP_PASS = os.getenv("EMAIL_SMTP_PASS", "")
TEST_EMAIL = os.getenv("EMAIL_TEST_TARGET", "")

EXCEL_PATH = os.path.expanduser(os.getenv("EMAIL_EXCEL_PATH", "~/Desktop/邮箱.xlsx"))
HTML_PATH = os.path.expanduser(os.getenv("EMAIL_HTML_PATH", "~/Desktop/邮件内容.html"))
TITLE_TXT_PATH = os.path.expanduser(os.getenv("EMAIL_TITLE_PATH", "~/Desktop/邮件标题.txt"))

# 获取脚本目录，构建资源文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")
LOG_FILE = os.path.join(ASSETS_DIR, "email_status.json")

BATCH_SIZE = 135  # 每个批次的收件人数量
MIN_DELAY = 3.0  # 最小发送间隔
MAX_DELAY = 8.0  # 最大发送间隔
LONG_REST_MIN = 10  # 长休息最小时间
LONG_REST_MAX = 20  # 长休息最大时间
LONG_REST_INTERVAL = 10  # 每发送N封进行长休息

def get_title_from_txt(path: str) -> str:
    """从文本文件读取邮件标题"""
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                title = f.read().strip()
                return title if title else "你好"
        print(f"警告: 标题文件不存在 {path}, 使用默认标题")
        return "你好"
    except Exception as e:
        print(f"读取 TXT 标题失败: {e}, 使用默认标题")
        return "你好"


def generate_random_tag() -> str:
    """生成随机隐藏标识符，干扰反垃圾扫描"""
    chars = string.ascii_letters + string.digits
    tag = ''.join(random.choice(chars) for _ in range(8))
    return f'<div style="display:none !important; color:transparent; visibility:hidden; opacity:0; font-size:0px;">ID:{tag}</div>'

def get_email_data() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """读取 Excel 并识别标题行和数据列"""
    if not os.path.exists(EXCEL_PATH):
        print(f"错误: Excel 文件不存在 {EXCEL_PATH}")
        return None, None

    try:
        # 先读取前几行看是否有标题
        peek = pd.read_excel(EXCEL_PATH, nrows=5)
        # 简单判断首行是否包含邮箱格式特征
        has_header = not any("@" in str(col) for col in peek.columns)

        if has_header:
            df = pd.read_excel(EXCEL_PATH)
        else:
            df = pd.read_excel(EXCEL_PATH, header=None)
            # 给第一列起个默认名
            df.columns = ["email"] + [f"col_{i}" for i in range(1, len(df.columns))]

        # 寻找包含邮箱的那一列
        email_col = None
        for col in df.columns:
            if df[col].astype(str).str.contains("@", na=False).any():
                email_col = col
                break

        if email_col is None:
            print("错误: Excel 中未找到有效的邮箱地址列")
            return None, None

        return df, email_col
    except Exception as e:
        print(f"读取 Excel 数据失败: {e}")
        return None, None

def replace_placeholders(text: str, row_data: pd.Series) -> str:
    """将文本中的 【变量名】 替换为行数据中的对应值"""
    if not isinstance(text, str):
        return text

    # 查找所有 【...】 格式的占位符
    placeholders = re.findall(r"【(.*?)】", text)
    for p in placeholders:
        # 在列名中寻找匹配（不区分大小写，去掉空格）
        match_col = None
        clean_p = p.strip().lower()
        for col in row_data.index:
            if str(col).strip().lower() == clean_p:
                match_col = col
                break

        if match_col is not None:
            val = str(row_data[match_col])
            if val.lower() == "nan":
                val = ""
            text = text.replace(f"【{p}】", val)
    return text

def send_bulk_emails(test_mode: bool = True, test_email: Optional[str] = None) -> Optional[Dict]:
    """批量发送邮件"""
    # 验证环境变量
    if not SMTP_USER or not SMTP_PASS:
        print("错误: 未配置 EMAIL_SMTP_USER 或 EMAIL_SMTP_PASS")
        return None

    # 加载数据
    df, email_col = get_email_data()
    if df is None:
        return None

    # 获取基础标题
    subject_template = get_title_from_txt(TITLE_TXT_PATH)

    # 读取 HTML 模板
    if not os.path.exists(HTML_PATH):
        print(f"错误: HTML 文件不存在 {HTML_PATH}")
        return None

    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html_template = f.read()
    except Exception as e:
        print(f"读取 HTML 失败: {e}")
        return None

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    results = {
        "total": 1 if test_mode else len(df),
        "success": 0,
        "failed": [],
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # 准备任务列表
    if test_mode:
        if not test_email:
            print("错误: 测试模式需要提供测试邮箱")
            return None
        # 测试模式下，取第一行数据（如果有）来模拟替换效果，但发送给 test_email
        row = df.iloc[0].copy()
        row[email_col] = test_email
        task_list = [row]
    else:
        task_list = [row for _, row in df.iterrows()]

    # 分批发送
    for i in range(0, len(task_list), BATCH_SIZE):
        batch = task_list[i:i + BATCH_SIZE]
        print(f"正在发送批次 {i//BATCH_SIZE + 1}，包含 {len(batch)} 个收件人...")

        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASS)

                for row in batch:
                    addr = str(row[email_col]).strip()

                    # 验证邮箱地址格式
                    if not addr or '@' not in addr:
                        print(f"跳过无效邮箱: {addr}")
                        results["failed"].append({"email": addr, "reason": "无效邮箱地址"})
                        continue

                    try:
                        # 执行变量替换
                        final_subject = replace_placeholders(subject_template, row)
                        final_html = replace_placeholders(html_template, row)

                        # 插入干扰码
                        final_html += generate_random_tag()

                        msg = MIMEMultipart()
                        msg['From'] = f"Youdao Ads <{SMTP_USER}>"
                        msg['To'] = addr
                        msg['Subject'] = final_subject
                        msg.attach(MIMEText(final_html, 'html', 'utf-8'))

                        server.send_message(msg)
                        results["success"] += 1
                        print(f"成功发送至: {addr}")

                        # 降低发信频率，增加随机性
                        if not test_mode:
                            # 基础间隔 + 随机波动
                            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                            # 每发送 10 封进行一次长休息
                            if results["success"] % LONG_REST_INTERVAL == 0:
                                rest_time = random.uniform(LONG_REST_MIN, LONG_REST_MAX)
                                print(f"休息 {rest_time:.1f} 秒...")
                                time.sleep(rest_time)

                    except Exception as e:
                        print(f"发送至 {addr} 失败: {e}")
                        results["failed"].append({"email": addr, "reason": str(e)})

                if not test_mode:
                    time.sleep(2)

        except smtplib.SMTPException as e:
            print(f"SMTP 连接失败: {e}")
        except Exception as e:
            print(f"批次发送失败: {e}")

    results["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        send_bulk_emails(test_mode=False)
    else:
        test_addr = TEST_EMAIL
        if not test_addr:
            print("错误: 未配置 EMAIL_TEST_TARGET 环境变量")
            sys.exit(1)
        print(f"准备发送测试邮件至: {test_addr}")
        send_bulk_emails(test_mode=True, test_email=test_addr)
