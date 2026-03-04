---
name: paper-research-assistant
description: 科研论文研读与复现自动化助手。使用当用户需要：(1) 研读论文 PDF 并提取核心内容，(2) 生成结构化研读报告，(3) 查找官方代码/数据集，(4) 编写复现代码框架，(5) 设计实验方案复现论文结果
---

# Paper Research Assistant - 科研论文研读与复现助手

## 核心工作流

### 1. 论文接收与解析
- 接收用户提供的论文 PDF 文件路径或 arXiv/期刊链接
- 使用 `scripts/parse_paper.py` 提取论文元数据（标题、作者、摘要、关键词）
- 识别论文类型：理论研究/实验研究/综述/方法论文

### 2. 深度研读与报告生成
- 提取核心贡献（通常位于 Introduction 最后一段或 Conclusion）
- 识别方法论框架（模型架构、算法流程、关键公式）
- 整理实验配置（数据集、基线方法、评估指标、超参数）
- 生成结构化研读报告（使用 `references/report_template.md`）

### 3. 资源收集
- 搜索官方代码仓库（GitHub、GitLab、项目主页）
- 查找配套数据集（HuggingFace、Kaggle、论文中提到的数据源）
- 验证资源可用性与许可证

### 4. 复现代码生成
- 根据论文方法描述生成代码骨架（PyTorch/TensorFlow）
- 实现核心算法模块
- 配置训练循环与评估流程
- 生成可运行的实验脚本

### 5. 实验方案设计
- 列出环境依赖（Python 版本、关键库）
- 设计对比实验（消融实验、基线对比）
- 配置超参数搜索空间
- 预估计算资源需求

## 脚本使用

### parse_paper.py
```bash
python scripts/parse_paper.py --pdf /path/to/paper.pdf --output /tmp/paper_metadata.json
```
提取论文结构化元数据

### generate_report.py
```bash
python scripts/generate_report.py --metadata /tmp/paper_metadata.json --template references/report_template.md --output /tmp/research_report.md
```
生成研读报告

### scaffold_code.py
```bash
python scripts/scaffold_code.py --paper-json /tmp/paper_metadata.json --framework pytorch --output-dir /tmp/repo
```
生成复现代码骨架

## 参考文档

- `references/report_template.md` - 研读报告标准模板
- `references/code_style.md` - 复现代码规范
- `references/experiment_design.md` - 实验设计指南

## 输出规范

### 研读报告结构
```markdown
# 论文研读报告

## 基本信息
- 标题：
- 作者/机构：
- 发表 venue：
- 日期：

## 核心贡献
1. ...
2. ...

## 方法论
- 问题定义：
- 核心思路：
- 关键公式：

## 实验配置
- 数据集：
- 基线方法：
- 评估指标：
- 超参数：

## 复现可行性
- 官方代码：[有/无] [链接]
- 数据集：[公开/需申请] [链接]
- 计算需求：
- 预计复现难度：[低/中/高]

## 待澄清问题
- ...
```

## 注意事项

1. **PDF 解析限制**：复杂公式可能识别不准确，需人工核对
2. **代码复现范围**：生成骨架代码，完整实现需根据实际调试
3. **资源验证**：所有链接需验证有效性，标注最后访问时间
4. **许可证合规**：注明原论文/代码的许可证类型

## 工具依赖

- PyMuPDF / pdfplumber - PDF 解析
- arxiv API - 论文元数据查询
- GitHub API - 代码仓库搜索
- HuggingFace API - 数据集查询
