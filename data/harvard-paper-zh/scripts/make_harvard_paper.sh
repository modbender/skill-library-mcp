#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "用法: $0 <标题> <输入素材txt/md路径> <输出docx路径> [作者] [日期]" >&2
  exit 1
fi

TITLE="$1"
SOURCE="$2"
OUT_DOCX="$3"
AUTHOR="${4:-}"
DATE_VAL="${5:-$(date +%Y-%m-%d)}"

if [[ ! -f "$SOURCE" ]]; then
  echo "输入文件不存在: $SOURCE" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "未安装 pandoc，请先安装后重试。" >&2
  exit 1
fi

TMP_MD="$(mktemp /tmp/harvard-paper-XXXXXX.md)"
trap 'rm -f "$TMP_MD"' EXIT

cat > "$TMP_MD" <<EOF
---
title: "$TITLE"
author: "$AUTHOR"
date: "$DATE_VAL"
lang: zh-CN
...

# 摘要

（根据素材提炼：研究背景、方法、核心结论与实践意义，150–300字。）

**关键词：** 关键词1；关键词2；关键词3；关键词4

# 目录

\\tableofcontents

# 引言

（说明研究问题、现实意义与文章结构。）

# 文献回顾

## 理论基础

（引用相关研究，建立分析框架。）

## 研究现状与不足

（总结现有观点，并指出本文切入点。）

# 研究方法与分析框架

（说明方法：文献分析/案例分析/比较分析等；定义变量或分析维度。）

# 结果与讨论

## 主要发现

（按逻辑分点讨论。）

## 机制解释

（解释为何会出现上述结果。）

## 局限性

（说明样本、方法或外推范围的限制。）

# 结论与建议

（总结核心结论并给出可执行建议。）

# 参考文献（Harvard）

（示例）

Smith, J. (2021) *Research Methods in Social Science*. London: Routledge.

Brown, A. and Green, T. (2023) ‘Digital communication and trust building’, *Journal of Social Studies*, 12(3), pp. 44–61.

---

# 素材原文（用于改写，不直接保留）

EOF

cat "$SOURCE" >> "$TMP_MD"

pandoc "$TMP_MD" \
  -o "$OUT_DOCX" \
  --toc \
  --number-sections \
  -V papersize:a4 \
  -V fontsize=12pt \
  -V geometry:margin=2.54cm

echo "已生成: $OUT_DOCX"
