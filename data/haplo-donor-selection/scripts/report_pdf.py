#!/usr/bin/env python3
"""
HLA DFS Report PDF Generator
=============================
将 haplo_dfs.py 的文本报告转为 PDF，支持中文。
使用 fpdf2 + 文泉驿正黑字体。

用法：
  python3 report_pdf.py --text report.txt --output 崔营_DFS.pdf
  或在工作流中直接调用 generate_pdf(text, output_path)
"""

import argparse
import sys
import os

from fpdf import FPDF


# 文泉驿正黑 (WenQuanYi Zen Hei) — 系统自带中文字体
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
FONT_NAME = "WenQuanYi"


class HLAReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font(FONT_NAME, "", FONT_PATH)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font(FONT_NAME, "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, "HLA Haplo Donor Selection Report", align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT_NAME, "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _classify_line(line: str):
    """判断行的类型，返回 (font_size, is_bold_sim, color_rgb)"""
    stripped = line.strip()

    # 主标题
    if stripped.startswith("📊") or stripped.startswith("🔄"):
        return 13, True, (0, 51, 102)
    # 节标题
    if stripped.startswith("🏆") or stripped.startswith("🧭"):
        return 11, True, (0, 51, 102)
    # 供者名 (medal lines)
    if any(stripped.startswith(m) for m in ["🥇", "🥈", "🥉", "#"]):
        return 11, True, (0, 0, 0)
    # 分隔线
    if stripped.startswith("=" * 10) or stripped.startswith("-" * 10) or stripped.startswith("─" * 5):
        return 9, False, (180, 180, 180)
    # 推荐行
    if "📌 推荐" in stripped or "💡" in stripped:
        return 10, True, (0, 100, 0)
    # 警告
    if stripped.startswith("⚠️"):
        return 9, False, (180, 80, 0)
    # 参考文献
    if stripped.startswith("📖") or stripped.startswith("   ["):
        return 8, False, (100, 100, 100)
    # 表头行 (供者类型 / OS / NRM...)
    if "供者类型" in stripped or "─────" in stripped:
        return 9, False, (60, 60, 60)
    # 星标行
    if "⭐" in stripped:
        return 10, True, (0, 80, 0)
    # 默认
    return 9, False, (0, 0, 0)


def generate_pdf(report_text: str, output_path: str, patient_name: str = ""):
    """将文本报告转为 PDF"""
    pdf = HLAReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # 标题页
    pdf.set_font(FONT_NAME, "", 16)
    pdf.set_text_color(0, 51, 102)
    title = f"单倍体供者选择报告"
    if patient_name:
        title = f"{patient_name} — {title}"
    pdf.cell(0, 12, title, align="C")
    pdf.ln(15)

    # 逐行渲染
    lines = report_text.split("\n")
    for line in lines:
        if not line and not line.strip():
            pdf.ln(3)
            continue

        size, is_bold, color = _classify_line(line)
        pdf.set_font(FONT_NAME, "", size)
        pdf.set_text_color(*color)

        # 处理缩进
        indent = len(line) - len(line.lstrip())
        x_offset = min(indent * 1.5, 30)

        pdf.set_x(10 + x_offset)

        # 替换一些无法渲染的特殊字符
        clean = line.rstrip()
        # 替换 emoji 为文字标记 (字体不支持 emoji)
        emoji_map = {
            "📊": "[报告]", "📖": "[参考]", "👤": "[患者]",
            "🏆": "[排名]", "🥇": "[#1]", "🥈": "[#2]", "🥉": "[#3]",
            "📈": "[预测]", "🔬": "[KIR]", "📋": "[分组]",
            "🎂": "[年龄]", "📌": "[推荐]", "💡": "[结论]",
            "🧭": "[选择]", "🛡️": "[GVHD]", "🛡": "[GVHD]",
            "🔄": "[比较]", "🥟": "",
            "⭐": "[*]", "✅": "[V]", "⚠️": "[!]", "⚠": "[!]",
            "🟢": "[MSD-Y]", "🟡": "[MSD-O]", "🔵": "[MMUD-M]", "🟠": "[MMUD-MM]",
            "🟰": "[=]", "️": "",
        }
        for emo, txt in emoji_map.items():
            clean = clean.replace(emo, txt)
        # fpdf2 的 multi_cell 处理长行自动换行
        pdf.multi_cell(0, 5, clean)

    pdf.output(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="HLA Report PDF Generator")
    parser.add_argument("--text", help="Input text file path")
    parser.add_argument("--input-text", help="Direct text input (alternative to --text)")
    parser.add_argument("--output", help="Output PDF path (default: ~/openclaw-reports/HLA/{patient}_DFS.pdf)")
    parser.add_argument("--patient", default="", help="Patient name for title")
    args = parser.parse_args()

    if args.text:
        with open(args.text, "r", encoding="utf-8") as f:
            report = f.read()
    elif args.input_text:
        report = args.input_text
    else:
        report = sys.stdin.read()

    # Default output path
    if args.output:
        out_path = args.output
    else:
        default_dir = os.path.expanduser("~/openclaw-reports/HLA")
        os.makedirs(default_dir, exist_ok=True)
        name = args.patient if args.patient else "report"
        out_path = os.path.join(default_dir, f"{name}_DFS.pdf")

    out = generate_pdf(report, out_path, args.patient)
    print(f"✅ PDF 生成: {out}")


if __name__ == "__main__":
    main()
