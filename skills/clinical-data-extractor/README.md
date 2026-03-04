# Clinical Data Extractor

Clinical Data Extractor 是一个专业的临床数据提取技能，可以从制药会议网站（如 ASCO、ESMO）或 PDF 文档中提取结构化临床试验数据，并生成标准化的 Markdown 报告。

## 功能特性

- 📄 **多源数据提取**：支持 URL 网页和 PDF 文档
- 📊 **结构化数据整理**：自动提取药品名称、生产厂家、适应症、临床阶段、疗效和安全性数据
- 📋 **标准表格格式**：生成符合临床研究规范的 Markdown 表格
- 🎯 **专家点评生成**：从医学专家角度提供专业分析
- 🏷️ **灵活配置**：自定义输出路径、常见终点缩写列表等

## 使用场景

当你需要：
- 提取 ASCO、ESMO 等会议的临床试验摘要数据
- 从 PDF 公告中提取药物临床结果
- 生成标准化的临床试验数据报告
- 分析新药的疗效和安全 性数据

## 输入格式

- **URL**：提供制药会议网站或学术文章链接
- **PDF**：上传包含临床数据的 PDF 文档

## 输出格式

生成标准化的 Markdown 文件，包含：

```markdown
# {药品名称} - {适应症} 临床数据

## 基本信息
| 药品名称 | ... |
| 生产厂家 | ... |
| 适应症 | ... |
| 临床阶段 | ... |
| 临床名称 | ... |
| 学术会议 | ... |

## 药品有效性和安全性
| 指标 | 实验组 | 对照组 |
|------|--------|--------|
| N | ... | ... |
| ORR | ... | ... |
| ...

## 试验设计
...
## 专家点评
...
## 数据来源
...
```

## 表格格式规范

- 表格内容第一行必须列出各组入组人数（列名：N）
- 必须明确标注 cohort 的具体信息（如剂量组），避免使用"最大剂量组"等笼统表述
- 不同终点基于不同分析人群时，需分别分列
- 常见终点使用英文缩写（ORR、cORR、DCR、mPFS、mOS 等）
- 不要写 95% CI 置信区间
- 时间指标只写数字，不写单位
- 缺失数据标注为 N/A

## 安装方法

### 方法 1：通过 ClawHub 安装（推荐）

1. 访问 [ClawHub.com](https://clawhub.com)
2. 搜索 "clinical-data-extractor"
3. 点击安装

### 方法 2：手动安装

1. 将本仓库下载到 skills 目录：
```bash
git clone https://github.com/abinww/clinical-data-extractor.git ~/.openclaw/skills/clinical-data-extractor
```

2. 重启 OpenClaw 或重新加载技能

## 使用示例

### 提取网页数据
```
提取 https://mp.weixin.qq.com/s/example 的临床数据
```

### 提取 PDF 数据
发送 PDF 文件，然后说：
```
提取临床数据
```

## 配置

可以在 SKILL.md 的 Configuration 部分自定义：

- **输出路径**：默认 `~/obsidian/AI`
- **文件命名格式**：`{药品名称}@{适应症}.md`
- **常见终点缩写列表**：可自定义需要使用英文的缩写

## 技术特点

- 使用**内置浏览器**进行网页自动化和内容提取，支持复杂网页
- 使用 `pdftotext` 或 `nano-pdf` 处理 PDF
- 对受限平台（如微信公众号）提供手工截图引导
- 支持临床数据图片的引用（公开网站 URL 或手动截图）

## 已支持的会议来源

- ASCO (American Society of Clinical Oncology)
- ASCO GU (Genitourinary Cancers Symposium)
- ESMO (European Society for Medical Oncology)
- EHA (European Hematology Association)
- 会议摘要和公告

## 示例输出

已处理的数据文件：

- `DB-1311_BNT324@前列腺癌.md` - B7H3 ADC 在前列腺癌的临床数据
- `UBT251@超重_肥胖.md` - GLP-1 三靶点激动剂的肥胖症 II 期数据
- `Sacituzumab_tirumotecan@尿路上皮癌.md` - TROP2 ADC 联合 PD-1 的尿路上皮癌数据

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

abinww

## 链接

- [ClawHub](https://clawhub.com)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [Discord 社区](https://discord.com/invite/clawd)
