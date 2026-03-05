#!/bin/bash
# Markdown to PDF with CJK support - 稳定版本 (v4)
# 自动处理：
# 1. Emoji 替换（避免乱码）
# 2. 粗体后添加空行（修复列表渲染）
# 3. 中文字体配置（Droid Sans Fallback）
# 4. 列表符号（textcomp 文本符号）
#
# 用法：./md2pdf.sh <input.md> <output.pdf> [额外 pandoc 参数]

INPUT="$1"
OUTPUT="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "用法：$0 <input.md> <output.pdf>"
    exit 1
fi

# 创建临时文件
TEMP_FILE=$(mktemp --suffix=.md)

# 预处理步骤 1: 在粗体文本后添加空行（修复列表渲染）
# 匹配：**文本** 后没有空行的情况
sed -E 's/^\*\*(.+)\*\*$/**\1**\n/' "$INPUT" > "$TEMP_FILE"

# 预处理步骤 2: 替换 emoji 和特殊字符（避免乱码）
TEMP_FILE2=$(mktemp --suffix=.md)
sed -E '
    # Check marks
    s/✅/\\textbf{[Correct]}/g
    s/❌/\\textbf{[Wrong]}/g
    
    # Warning
    s/⚠️/\\textbf{[Note]}/g
    
    # Icons
    s/📋/\\textbf{[}Table\\textbf{]}/g
    s/📚/\\textbf{Book}/g
    s/📝/\\textbf{Note}/g
    s/🍀/\\textbf{Good Luck}/g
    s/🎯/\\textbf{Target}/g
    s/🔧/\\textbf{Fix}/g
    s/🔍/\\textbf{Search}/g
    s/📌/\\textbf{Pin}/g
    s/📖/\\textbf{Read}/g
    s/📁/\\textbf{Folder}/g
    s/📄/\\textbf{Doc}/g
    s/📂/\\textbf{Open}/g
    s/🗂️/\\textbf{Files}/g
    s/⏰/\\textbf{Time}/g
    s/⏭️/\\textbf{Next}/g
    s/⏸️/\\textbf{Pause}/g
    s/⏹️/\\textbf{Stop}/g
    s/▶️/\\textbf{Play}/g
    s/◀️/\\textbf{Rewind}/g
    s/⬆️/UP/g
    s/⬇️/DOWN/g
    s/➡️/RIGHT/g
    s/⬅️/LEFT/g
    s/🔄/Refresh/g
    s/🚀/Launch/g
    s/💡/Idea/g
    s/💻/PC/g
    s/🖥️/Desktop/g
    s/📱/Mobile/g
    s/🔑/Key/g
    s/🔒/Lock/g
    s/🔓/Unlock/g
    s/❓/Q/g
    s/❕/!/g
    s/❔/?/g
    s/〰️/---/g
    s/▪️/-/g
    s/➤/>/g
    s/→/to/g
    s/←/from/g
    s/↑/up/g
    s/↓/down/g
    s/•/-/g
    
    # Em-dash replacement
    s/—/--/g
    s/–/-/g
' "$TEMP_FILE" > "$TEMP_FILE2"

# CJK header 文件路径（v4 稳定版本）
CJK_HEADER="/home/yuno/.openclaw/workspace/skills/md2pdf-fix/cjk_header_v4.tex"

# 如果 header 不存在，使用基本配置
if [ ! -f "$CJK_HEADER" ]; then
    CJK_HEADER=$(mktemp --suffix=.tex)
    cat > "$CJK_HEADER" << 'EOF'
\usepackage{xeCJK}
\setCJKmainfont{Droid Sans Fallback}
\usepackage{amsmath}
\usepackage{textcomp}
\usepackage{enumitem}
\setlist[itemize,1]{label=\textbullet, leftmargin=*}
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=cyan}
EOF
    CJK_HEADER_TMP="$CJK_HEADER"
fi

# 生成 PDF
pandoc "$TEMP_FILE2" -o "$OUTPUT" \
    --pdf-engine=xelatex \
    -f markdown-smart \
    -H "$CJK_HEADER" \
    -V mainfont="DejaVu Sans" \
    -V monofont="DejaVu Sans Mono" \
    -V papersize=a4 \
    -V geometry:margin=25mm \
    -V fontsize=11pt \
    -V colorlinks=true \
    --highlight-style=tango \
    "${@:3}"

RESULT=$?

# 清理临时文件
rm -f "$TEMP_FILE" "$TEMP_FILE2"
if [ -n "$CJK_HEADER_TMP" ]; then
    rm -f "$CJK_HEADER_TMP"
fi

if [ $RESULT -eq 0 ]; then
    echo "✅ PDF 已生成：$OUTPUT ($(ls -lh "$OUTPUT" | awk '{print $5}'))"
else
    echo "❌ PDF 生成失败"
    exit 1
fi
