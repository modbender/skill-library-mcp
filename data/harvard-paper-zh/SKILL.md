---
name: harvard-paper-zh
description: 将中文需求快速改写并排版为哈佛格式论文（含摘要、关键词、目录、分级标题、参考文献），并导出 .docx。用户提到“写论文、哈佛格式、学术润色、生成Word论文、参考文献Harvard”时使用。
---

# harvard-paper-zh

用此技能把口语化内容或素材稿，整理为中文学术论文并输出 Word。

## 执行步骤

1. 明确输入：论文题目、用途（课程/作业/投稿）、篇幅要求、是否已有素材。
2. 先产出学术化正文结构：摘要、关键词、引言、文献回顾、方法、结果与讨论、结论、参考文献。
3. 参考文献统一使用 Harvard 风格：
   - 图书：Author, A. (Year) *Title*. Place: Publisher.
   - 期刊：Author, A. and Author, B. (Year) ‘Article title’, *Journal*, Volume(Issue), pp. xx–xx.
4. 生成 docx：优先调用 `scripts/make_harvard_paper.sh`。
5. 交付时给出输出路径，并提醒可在 Word 中“更新目录”。

## 脚本用法

```bash
scripts/make_harvard_paper.sh <标题> <输入素材txt/md路径> <输出docx路径> [作者] [日期]
```

示例：

```bash
scripts/make_harvard_paper.sh \
"数字社交时代的亲密关系沟通研究" \
"/path/to/material.txt" \
"/path/to/output.docx" \
"张三" \
"2026-03-02"
```

## 质量标准

- 避免口语化、煽动性和低俗表达。
- 论点—论据—结论链路清晰，段落不过长。
- 保持中性、可验证、可提交。
- 若用户提供了院校模板要求，按其优先覆盖本技能默认格式。
