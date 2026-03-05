#!/bin/bash
# 学习笔记生成示例

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
MD2PDF="${SKILL_DIR}/scripts/md2pdf.sh"

# 创建学习笔记
cat > lecture_notes.md << 'EOF'
# Lecture X - Topic Name

**Course:** Course Name  
**Date:** YYYY-MM-DD

---

## 🎯 核心问题

这节课要解决什么问题？

---

## 📖 主要内容

### 定义

$$
\text{公式}
$$

### 性质

| 性质 | 公式 |
|------|------|
| 性质 1 | 公式 1 |
| 性质 2 | 公式 2 |

---

## 📝 例题

**问题：** 描述问题

**解答：**

$$
\begin{aligned}
\text{步骤 1} &= \text{结果 1} \\
\text{步骤 2} &= \text{结果 2}
\end{aligned}
$$

---

## 🔑 总结

核心要点总结。
EOF

# 生成 PDF
if [ -f "$MD2PDF" ]; then
    echo "生成学习笔记 PDF..."
    "$MD2PDF" lecture_notes.md lecture_notes.pdf
    echo "✅ 完成：lecture_notes.pdf"
else
    echo "错误：md2pdf.sh 不存在"
fi

# 清理
rm -f lecture_notes.md
