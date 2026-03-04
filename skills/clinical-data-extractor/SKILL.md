---
name: clinical-data-extractor
description: Extract clinical trial data from pharmaceutical conference websites or PDF documents. Use when user provides a URL or PDF file containing innovative drug clinical trial data and needs structured extraction of: drug name, manufacturer, indication, clinical phase, trial name, conference, efficacy and safety data (presented as tables), and markdown output to "药品名称@适应症.md" file.
---

# Clinical Data Extractor

## Overview

This skill enables extracting structured clinical trial data from pharmaceutical conference websites (ASCO, ESMO, EHA, etc.) and saving it as a markdown file with standardized format.

## Configuration

**输出路径**: `~/.openclaw/workspace`
**命名格式**: `{药品名称}@{适应症}.md`
**文件名清理规则**:
- 替换空格为下划线
- 移除特殊字符

**常见终点缩写列表** - 以下缩写在表格中无需写中文全称：
- ORR (客观缓解率)
- cORR (确认缓解率)
- DCR (疾病控制率)
- mPFS/rPFS (中位无进展生存期)
- mOS (中位总生存期)
- mDOR (中位缓解持续时间)
- PSA50/PSA90 (PSA缓解率)
- CR (完全缓解)
- PR (部分缓解)
- SD (疾病稳定)
- PD (疾病进展)
- AE (不良事件)

⚠️ 如需修改配置，请直接编辑本配置区域
⚠️ 注意：`~` 需在执行时展开为实际用户 home directory
⚠️ 注意：不在列表中的终点数据应写中文全称以清晰说明
⚠️ 注意：本技能会尝试自动提取网页图片，但对于受限平台（微信公众号等）需要手动截图

## Requirements

This skill requires the following tools to be available in the OpenClaw runtime environment:

### Core Dependencies
- **browser**: Built-in OpenClaw tool for webpage automation and content extraction (no installation required)
  - Requires: Chrome browser installed on the host system
  - Usage: `browser action=start profile=openclaw target=host`
- **read/write**: Built-in OpenClaw tools for file operations (no installation required)

### Browser System Requirements
For browser automation to work correctly:
- **Chrome browser**: Must be installed on the host system (typically at `/usr/bin/google-chrome` or similar path)
- **Display server**: Desktop environment with X11/Wayland (for non-headless mode) or headless mode support
- **Network connectivity**: Required for loading webpages

### Optional Dependencies (For PDF Processing)
The following tools are used for PDF extraction. The skill will attempt each method in order:

1. **nano-pdf CLI** (recommended)
   - Installation: Usually pre-installed with OpenClaw
   - Alternative: If unavailable, file size reduction or OCR may be needed for scanned PDFs

2. **pdftotext** (poppler-utils)
   - Installation (Debian/Ubuntu): `sudo apt-get install poppler-utils`
   - Installation (macOS): `brew install poppler`
   - Used as fallback if nano-pdf is not available

### Filesystem Requirements
- **Write access to user home directory**: The skill creates markdown files and image files in the configured output path (default: `~/.openclaw/workspace`)

### Configuration Flexibility
All configuration options are defined in the **Configuration** section above and can be modified without reinstalling the skill:
- **输出路径** (Output path)
- **命名格式** (Filename format)
- **文件名清理规则** (Filename sanitization rules)
- **常见终点缩写列表** (Common endpoint abbreviations)

## When to Use

Use this skill when:

1. **User provides a URL** to a pharmaceutical conference website or clinical trial publication (ASCO, ESMO, EHA, WCLC, AACR, etc.) containing clinical trial data
2. **User provides a PDF file** containing clinical trial data
3. **User requests to extract structured clinical trial data** from webpages or PDFs
4. User mentions keywords like "临床数据", "临床试验", "clinical data", "clinical trial", or similar requests

**Examples of trigger phrases:**
- "提取临床数据"
- "把这份PDF里的临床试验信息整理一下"
- "Extract clinical trial data from this URL/PDF"

## Workflow

### Step 1: Detect Input Type and Extract Content

Determine if user provided a **URL** or a **PDF file**.

#### Case A: User provides a URL

Use the **built-in browser** to open and extract page content:

1. **Start browser** (if not already running):
   ```bash
   browser action=start profile=openclaw target=host
   ```

2. **Navigate to URL**:
   ```bash
   browser action=open targetUrl=<provided-url>
   ```

3. **Capture page snapshot** to extract content:
   ```bash
   browser action=snapshot format=markdown
   ```

4. **Optional: Take screenshot** for visual reference:
   ```bash
   browser action=screenshot fullPage=true
   ```

#### Case B: User provides a PDF file

Extract text content from the PDF. Two approaches available:

**Approach 1: Use nano-pdf CLI (read-only)**
```bash
nano-pdf --file <path-to-pdf> --action read
```

**Approach 2: Use nano-pdf with natural language instructions**
```bash
nano-pdf --file <path-to-pdf> --action edit --instruction "Extract all text content from this PDF, focusing on clinical trial data including drug name, indication, phase, efficacy, and safety results"
```

Note: The extracted PDF content will be in raw text format. You may need to clean up formatting before proceeding to extraction.

### Step 2: Extract Key Information

Analyze the fetched content and extract the following fields. Leave blank if information is not available:

1. **药品名称** (Drug Name)
2. **生产厂家** (Manufacturer)
3. **适应症** (Indication)
4. **临床阶段** (Clinical Phase)
5. **临床名称** (Trial Name)
6. **学术会议** (Academic Conference)
7. **药品有效性和安全性** (Efficacy and Safety)

#### Handling Clinical Data Images

**网页图片**：
- **公开网站（ASCO、ESMO、EHA 等）**：识别网页中直接显示的临床数据图片（如疗效曲线、安全性图表），尝试提取图片 URL 并引用
  ```markdown
  ![临床数据描述](图片URL)
  ```
- **受限平台（微信公众号等）**：这些平台通常会禁止图片链接的外部访问，无法直接提取图片 URL。在此情况下：
  - 在文档中添加图片说明，提示用户手动截图
  - 提供参考图片的描述（如"疗效数据图"、"安全性汇总表"等）
  - 如果需要获取原图，建议用户手动截图保存

**图片处理的两种方式**：

**方式一：自动提取（适用于公开网站）**
```markdown
![疗效曲线图](https://esmo.org/.../survival_curve.png)
```

**方式二：手动截图（适用于受限平台或提取失败时）**
```markdown
## 临床数据图片

⚠️ 无法自动提取图片（受限平台或提取失败），建议手动截图保存。

参考图片描述：
1. 疗效数据图（如 rPFS 曲线、OS 曲线）
2. 安全性汇总表（AE 发生率、严重 AE）

截图保存路径示例：
```markdown
![疗效曲线](./药品名称_疗效曲线.png)
```

**PDF 图片**：
- 识别 PDF 中直接显示临床数据的图片页面
- **重要**：PDF 中的图片无法自动提取，需要手动截图保存
- 使用截图工具保存图片到输出目录（与 markdown 文件同目录）
- 在 markdown 中用本地路径引用：
  ```markdown
  ![临床数据描述](./图片文件名.png)
  ```

For effectiveness and safety data, present findings in **markdown table format**:

```markdown
## 药品有效性和安全性

| 指标 | ABC001 | 对照组 | HR | p-value |
|------|----------------|--------|------|------|
| N | 100 | 50 | - | - |
| ORR | 41.4% | 25.3% | - | <0.0001 |
| cORR | 34.5% | - | - | <0.0001 |
| DCR | 87.9% | - | - | <0.0001 |
| mPFS | 11.3 | 6.8 |  0.62  | <0.0001 |
| mOS | 22.1 | 14.2 |  0.73  | <0.0001 |
| 最常见AE | 恶心、血液事件（1-2级） | - | - | - |
```

**多剂量组示例**：
```markdown
| 指标 |  AAB001 2mg | AAB001 4mg | AAB001 6mg |  Placebo |
|------|----------|--------------|--------------|--------------|
| N | 50 | 50 | 50 | 50 |
| OS | 12.1 | 14.2 | 17.3 | 0.2 |
| OS p-value | <0.0001 | <0.0001 | <0.0001 | - |
| PFS | 12.1 | 14.2 | 17.3 | 0.2 |
| PFS p-value | <0.0001 | <0.0001 | <0.0001 | - |
```

**表格格式规范**：
- 表格内容第一行必须列出各组入组人数，指标列写"N"
- **关键原则**：确保同一列的数据与该列标题对应的cohort一致
- **重要规则**：必须明确标注cohort的具体信息（如剂量组、治疗方案等），避免使用"最大剂量组"、"高剂量组"等笼统表述
  - ❌ 错误：`AAB001 (最大效果)` 或 `高剂量组`
  - ✅ 正确：`AAB001 6mg` 或 `对照组`
- 不同终点可能基于不同分析人群（如总人群 vs 可评估人群），需分别分列
- 缺乏的数据标注 "N/A"，不要将不同人群的数据混用
- 合并主要终点、次要终点、安全性到一个表格
- 列名：`["指标", "实验组1", "实验组2", ...]` 或 `["指标", "实验组", "对照组"]`（如有对照）
- 常见终点使用英文缩写（见 **Configuration** 中的"常见终点缩写列表"）
- 不常见的终点写中文全称
- 不要写95% CI置信区间
- 时间指标（PFS/OS/DOR等）只写数字，不写单位（如 `11.3` 而非 `11.3个月`）
- 百分比保留一位小数（如 `41.4%`）
- 数值不存在的用 `N/A` 或 `NE`（未成熟/未评估）表示
- 可在数值后用括号标注实际样本量（如 `11.3 (N=82)`）

### Step 3: Save as Markdown File

Generate output file using the configuration from **Configuration** section:

1. **Filename format**: Follow the **命名格式** from Configuration section
2. **Sanitize filename**:
   - Replace spaces with underscores
   - Remove special characters
3. **Final save path**: Use the **输出路径** from Configuration section, followed by the generated `{filename}`, then expand `~` to actual home directory.

### Step 4: Generate Expert Commentary (Optional but Recommended)

From a medical/pharmaceutical expert perspective, provide a concise analysis of the clinical trial data. This section should be clearly marked as "（仅供参考）" (For reference only).

Key aspects to analyze:

1. **Efficacy Evaluation**
   - Did primary endpoints reach statistical significance?
   - Are the effect sizes clinically meaningful?
   - How does it compare to existing therapies in the same indication?

2. **Safety Considerations**
   - Is the safety profile acceptable?
   - Any concerning AEs?
   - How does it compare to the drug class safety profile?

3. **Study Design Assessment**
   - Is the trial design appropriate?
   - Is sample size adequate?
   - Are control groups appropriate?
   - Any limitations?

4. **Clinical Prospects**
   - What's the potential for FDA/NMPA approval?
   - Commercial potential?
   - What clinical development pathway comes next?

5. **Cautions & Limitations**
   - Data limitations
   - What still needs to be validated

Provide concise, objective analysis (3-6 bullet points). Avoid over-optimistic language.

### Step 5: File Content Structure

The generated markdown file should follow this template:

```markdown
# {药品名称} - {适应症} 临床数据

## 基本信息

| 字段 | 内容 |
|------|------|
| 药品名称 | {药品名称} |
| 生产厂家 | {生产厂家} |
| 适应症 | {适应症} |
| 临床阶段 | {临床阶段} |
| 临床名称 | {临床名称} |
| 学术会议 | {学术会议} |

## 药品有效性和安全性

| 指标 | {实验组名称} |
|------|--------------|
| 主要终点数据... | 值 |
| 次要终点数据... | 值 |
| 安全性数据... | 值 |

## 试验设计

| 设计要素 | 内容 |
|----------|------|
| 研究类型 | ... |
| 入组人数 | ... |

## 临床数据图片

{网页图片链接或PDF截图引用}

## 专家点评
（仅供参考）

从药学/医学专家角度分析该临床数据的意义：

- **疗效评价**：[分析主要终点结果是否达到临床意义，对比同类药物]
- **安全性考量**：[分析安全性概况，关注关键AE]
- **研究设计评价**：[研究设计是否合理、样本量是否充足、对照组选择等]
- **临床前景**：[基于当前数据评估药物商业化潜力及后续研究方向]
- **注意事项**：[数据的局限性、需要进一步验证的点等]

## 数据来源

{URL或PDF路径}
提取时间: {当前日期}
```

## Tips

- **配置修改**: 输出路径、命名格式、常见缩写列表在 **Configuration** 区域定义，直接编辑即可修改
- **输出文件位置**: 查看 **Configuration** 区域的 `输出路径` 设置
- **终点缩写规则**: 只对 **Configuration** 中"常见终点缩写列表"内的缩写使用英文，其他终点写中文全称
- **浏览器使用**: 网页提取使用内置浏览器，启动时指定 `target=host` 参数。如果浏览器未运行，skill 会自动启动
- Use memory_search to check if similar drugs have been processed before extracting
- If the content (webpage or PDF) contains multiple drugs or trials, clarify with user which one to extract
- For complex clinical endpoints, preserve original terminology and units
- **图片处理注意事项**:
  - 网页图片：提取原始 URL，在 markdown 中直接引用 `![描述](URL)` 或 `<URL>`（避免大图预览）
  - PDF 图片：截图保存到与 markdown 同目录，使用相对路径引用 `![描述](./文件名.png)`
  - 图片命名：使用药品名称+序号，如 `PD-1抑制剂_图表1.png`
  - 只有临床数据相关的图片需要保存，装饰性图片可以忽略
- **PDF 处理注意事项**:
  - PDF 提取的文本格式可能比较混乱，需要适当清理换行和空格
  - 表格数据在 PDF 中可能无法完整保留，需要根据上下文推断
  - 如果 PDF 是扫描图片，nano-pdf 可能无法提取文本，需要先 OCR 处理
  - 对于大型 PDF 文件，可以先使用 `--action read` 快速提取全文内容
---

**Not every skill requires all three types of resources.**
