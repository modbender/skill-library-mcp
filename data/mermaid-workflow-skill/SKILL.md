---
name: Mermaid Workflow Skill
description: 按照新的工作流程创建和处理Mermaid图表：先生成Mermaid格式的图表定义文件(.mmd)，然后调用终端命令运行mmdc
  (Mermaid CLI)将.mmd转换为PNG，最后将图片链接插入Markdown文件对应的位置。
---

# Mermaid Workflow Skill

## 描述
按照新的工作流程创建和处理Mermaid图表：先生成Mermaid格式的图表定义文件(.mmd)，然后调用终端命令运行mmdc (Mermaid CLI)将.mmd转换为PNG，最后将图片链接插入Markdown文件对应的位置。

## 激活条件
当用户需要创建或处理以下类型的图表时激活此技能：
- 技术路线图
- 系统架构图
- 流程图
- 序列图
- 类图
- 状态图
- 甘特图
- ER图
- 以及其他Mermaid支持的图表类型

## 核心工作流程
1. **创建Mermaid定义文件** (.mmd)
2. **转换为PNG图片** (使用mmdc CLI)
3. **插入Markdown文件** (替换占位符或插入到指定位置)

## 文件结构
```
mermaid-workflow-skill/
├── SKILL.md (本文件)
├── scripts/
│   ├── create_mermaid.py (创建Mermaid图表)
│   ├── convert_mermaid.py (转换Mermaid为PNG)
│   └── insert_to_md.py (插入图片到Markdown)
├── templates/
│   ├── roadmap.mmd (技术路线图模板)
│   ├── architecture.mmd (系统架构图模板)
│   ├── flowchart.mmd (流程图模板)
│   └── sequence.mmd (序列图模板)
└── examples/
    ├── example_roadmap.mmd (示例路线图)
    ├── example_architecture.mmd (示例架构图)
    └── example_output.md (示例输出)
```

## 依赖要求
- **Mermaid CLI (mmdc)**: 必须安装并配置好
- **Python 3.8+**: 用于运行脚本
- **Puppeteer配置**: 用于解决mmdc沙箱问题

## 安装和配置

### 1. 安装Mermaid CLI
```bash
# 全局安装
npm install -g @mermaid-js/mermaid-cli

# 或者使用npx
npx @mermaid-js/mermaid-cli
```

### 2. 验证安装
```bash
mmdc --version
# 应该显示版本号，如：11.12.0
```

### 3. 解决沙箱问题
创建Puppeteer配置文件：
```json
{
  "args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
```

## 使用方法

### 基本使用流程

#### 1. 创建Mermaid图表定义文件
```bash
python scripts/create_mermaid.py --type roadmap --title "技术路线图" --output roadmap.mmd
```

#### 2. 转换为PNG图片
```bash
python scripts/convert_mermaid.py --input roadmap.mmd --output roadmap.png
```

#### 3. 插入到Markdown文件
```bash
python scripts/insert_to_md.py --md-file report.md --image roadmap.png --placeholder "[ROADMAP]"
```

### 完整示例

#### 示例1: 创建技术路线图
```bash
# 1. 创建路线图定义
python scripts/create_mermaid.py \
  --type roadmap \
  --title "AI开发技术路线图" \
  --phases "2024 Q1:基础研究,2024 Q2:原型开发,2024 Q3:测试验证,2024 Q4:产品发布" \
  --output ai_roadmap.mmd

# 2. 转换为PNG
python scripts/convert_mermaid.py \
  --input ai_roadmap.mmd \
  --output ai_roadmap.png \
  --width 1200 \
  --height 800

# 3. 插入到Markdown
python scripts/insert_to_md.py \
  --md-file ai_report.md \
  --image ai_roadmap.png \
  --section "## 技术路线图"
```

#### 示例2: 创建系统架构图
```bash
# 1. 创建架构图定义
python scripts/create_mermaid.py \
  --type architecture \
  --title "微服务系统架构" \
  --layers "前端:React,网关:API Gateway,服务:UserService,OrderService,数据:MySQL,Redis" \
  --output architecture.mmd

# 2. 转换为PNG
python scripts/convert_mermaid.py --input architecture.mmd --output architecture.png

# 3. 插入到Markdown
python scripts/insert_to_md.py --md-file design.md --image architecture.png
```

## 脚本详细说明

### 1. create_mermaid.py
创建各种类型的Mermaid图表定义文件。

**参数:**
- `--type`: 图表类型 (roadmap, architecture, flowchart, sequence, class, state, gantt, er)
- `--title`: 图表标题
- `--output`: 输出文件路径
- 其他类型特定参数

**支持的图表类型:**
1. **roadmap**: 技术路线图
2. **architecture**: 系统架构图
3. **flowchart**: 流程图
4. **sequence**: 序列图
5. **class**: 类图
6. **state**: 状态图
7. **gantt**: 甘特图
8. **er**: ER图

### 2. convert_mermaid.py
将.mmd文件转换为PNG图片。

**参数:**
- `--input`: 输入.mmd文件
- `--output`: 输出.png文件
- `--width`: 图片宽度 (默认1200)
- `--height`: 图片高度 (默认800)
- `--theme`: 主题 (default, forest, dark, neutral)
- `--background`: 背景颜色 (默认白色)

### 3. insert_to_md.py
将PNG图片插入到Markdown文件。

**参数:**
- `--md-file`: Markdown文件路径
- `--image`: 图片文件路径
- `--placeholder`: 要替换的占位符 (可选)
- `--section`: 要插入的章节标题 (可选)
- `--caption`: 图片标题 (可选)
- `--position`: 插入位置 (before, after, replace)

## 模板系统

### 路线图模板 (roadmap.mmd)
```mermaid
%%{init: {'theme': 'default', 'themeVariables': { 'primaryColor': '#007bff', 'primaryTextColor': '#fff', 'primaryBorderColor': '#0056b3', 'lineColor': '#333', 'tertiaryColor': '#f8f9fa'}}}%%
gantt
    title {{TITLE}}
    dateFormat YYYY-MM
    axisFormat %Y年%m月
    
    section 第一阶段
    任务1 :a1, {{START_DATE}}, {{DURATION_1}}
    
    section 第二阶段
    任务2 :after a1, {{DURATION_2}}
    
    section 第三阶段
    任务3 :after a2, {{DURATION_3}}
```

### 架构图模板 (architecture.mmd)
```mermaid
graph TB
    subgraph "{{FRONTEND_TITLE}}"
        A[{{FRONTEND_COMPONENT}}]
    end
    
    subgraph "{{API_TITLE}}"
        B[{{API_COMPONENT}}]
    end
    
    subgraph "{{SERVICE_TITLE}}"
        C[{{SERVICE_1}}]
        D[{{SERVICE_2}}]
    end
    
    subgraph "{{DATA_TITLE}}"
        E[({{DATABASE}})]
        F[{{CACHE}}]
    end
    
    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    C --> F
    D --> F
```

## 集成到OpenClaw工作流

### 作为独立技能使用
```python
# 在OpenClaw会话中调用
exec("python /path/to/mermaid-workflow-skill/scripts/create_mermaid.py --type roadmap --output roadmap.mmd")
```

### 作为其他技能的组件
```python
# 在其他技能中集成Mermaid图表生成
def generate_technical_report():
    # 1. 创建路线图
    create_mermaid_chart("roadmap", "项目路线图")
    
    # 2. 转换为图片
    convert_to_png("roadmap.mmd", "roadmap.png")
    
    # 3. 插入到报告
    insert_image_to_md("report.md", "roadmap.png", "## 项目路线图")
```

## 故障排除

### 常见问题

#### 1. mmdc命令找不到
```bash
# 检查是否安装
which mmdc

# 如果使用npx
npx @mermaid-js/mermaid-cli --version
```

#### 2. 沙箱错误
```
Error: Failed to launch the browser process! No usable sandbox!
```
**解决方案:** 使用Puppeteer配置文件
```bash
mmdc -i input.mmd -o output.png -p puppeteer-config.json
```

#### 3. 中文显示问题
**解决方案:** 确保系统安装了中文字体
```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei

# 或者在mmdc命令中指定字体
mmdc -i input.mmd -o output.png --fontFamily "WenQuanYi Zen Hei"
```

#### 4. 图片质量不佳
**解决方案:** 增加图片尺寸和DPI
```bash
mmdc -i input.mmd -o output.png -w 2000 -H 1400 --scale 2
```

## 最佳实践

### 1. 文件命名规范
- 使用有意义的文件名: `project_roadmap.mmd`, `system_architecture.png`
- 包含版本信息: `v1.0_architecture.mmd`
- 使用日期戳: `20240302_roadmap.mmd`

### 2. 版本控制
- 将.mmd文件纳入版本控制
- PNG图片可以忽略（可重新生成）
- 在README中记录图表生成命令

### 3. 文档化
- 为每个图表添加注释说明
- 在Markdown中提供图表说明文字
- 维护图表变更日志

### 4. 自动化集成
- 在CI/CD中集成图表生成
- 使用Makefile或脚本自动化流程
- 设置图表生成触发器

## 扩展功能

### 批量处理
```bash
# 批量转换所有.mmd文件
for file in *.mmd; do
    python scripts/convert_mermaid.py --input "$file" --output "${file%.mmd}.png"
done
```

### 监控和日志
```python
# 添加日志记录
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

### 质量检查
```python
# 检查图表语法
def validate_mermaid_syntax(mmd_content):
    # 实现语法检查逻辑
    pass
```

## 示例项目

### 完整工作流示例
```bash
# 创建项目目录
mkdir -p my_project/charts
cd my_project

# 1. 创建技术路线图
python ../mermaid-workflow-skill/scripts/create_mermaid.py \
  --type roadmap \
  --title "产品开发路线图" \
  --output charts/product_roadmap.mmd

# 2. 创建系统架构图
python ../mermaid-workflow-skill/scripts/create_mermaid.py \
  --type architecture \
  --title "系统架构" \
  --output charts/system_architecture.mmd

# 3. 转换为PNG
for mmd in charts/*.mmd; do
    python ../mermaid-workflow-skill/scripts/convert_mermaid.py \
      --input "$mmd" \
      --output "${mmd%.mmd}.png"
done

# 4. 创建Markdown报告
cat > report.md << EOF
# 项目报告

## 技术路线图
![产品开发路线图](charts/product_roadmap.png)

## 系统架构
![系统架构图](charts/system_architecture.png)
EOF

# 5. 插入图片（如果需要自动化插入）
python ../mermaid-workflow-skill/scripts/insert_to_md.py \
  --md-file report.md \
  --image charts/product_roadmap.png \
  --section "## 技术路线图"
```

## 更新日志

### v1.0.0 (2026-03-02)
- 初始版本发布
- 支持8种Mermaid图表类型
- 完整的创建-转换-插入工作流
- 模板系统和示例

## 贡献指南
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证
MIT License