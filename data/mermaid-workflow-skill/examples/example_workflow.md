# Mermaid工作流示例

本文档演示如何使用Mermaid工作流技能创建和插入图表。

## 技术路线图

[ROADMAP_PLACEHOLDER]

## 系统架构

[ARCHITECTURE_PLACEHOLDER]

## 处理流程

[FLOWCHART_PLACEHOLDER]

## 使用说明

### 1. 创建Mermaid图表定义

```bash
# 创建技术路线图
python scripts/create_mermaid.py \
  --type roadmap \
  --title "项目开发路线图" \
  --output examples/project_roadmap.mmd

# 创建系统架构图
python scripts/create_mermaid.py \
  --type architecture \
  --title "微服务架构" \
  --output examples/system_architecture.mmd

# 创建流程图
python scripts/create_mermaid.py \
  --type flowchart \
  --title "用户注册流程" \
  --output examples/user_flowchart.mmd
```

### 2. 转换为PNG图片

```bash
# 转换单个文件
python scripts/convert_mermaid.py \
  --input examples/project_roadmap.mmd \
  --output examples/project_roadmap.png

# 批量转换
python scripts/convert_mermaid.py \
  --input examples/ \
  --output examples/png/ \
  --batch
```

### 3. 插入到Markdown文件

```bash
# 替换占位符
python scripts/insert_to_md.py \
  --md-file examples/example_workflow.md \
  --image examples/project_roadmap.png \
  --placeholder "[ROADMAP_PLACEHOLDER]" \
  --caption "项目开发路线图"

# 插入到指定章节
python scripts/insert_to_md.py \
  --md-file examples/example_workflow.md \
  --image examples/system_architecture.png \
  --section "## 系统架构" \
  --caption "微服务系统架构"

# 批量插入
python scripts/insert_to_md.py \
  --md-file examples/example_workflow.md \
  --image-dir examples/png/ \
  --batch \
  --placeholder-prefix "["
```

### 4. 完整工作流脚本

```bash
#!/bin/bash
# 完整工作流示例

# 创建图表定义
python scripts/create_mermaid.py --type roadmap --title "示例路线图" --output chart1.mmd
python scripts/create_mermaid.py --type architecture --title "示例架构" --output chart2.mmd

# 转换为PNG
python scripts/convert_mermaid.py --input chart1.mmd --output chart1.png
python scripts/convert_mermaid.py --input chart2.mmd --output chart2.png

# 创建Markdown文件
cat > report.md << EOF
# 项目报告

## 路线图
[CHART_1]

## 架构图
[CHART_2]
EOF

# 插入图片
python scripts/insert_to_md.py --md-file report.md --image chart1.png --placeholder "[CHART_1]"
python scripts/insert_to_md.py --md-file report.md --image chart2.png --placeholder "[CHART_2]"

echo "✅ 工作流完成！"
```

## 注意事项

1. **文件路径**: 确保使用正确的相对路径或绝对路径
2. **占位符**: 在Markdown中使用唯一的占位符
3. **图片大小**: 根据需要调整图片尺寸
4. **版本控制**: 建议将.mmd文件纳入版本控制，PNG文件可以忽略

## 故障排除

### 问题1: mmdc命令未找到
```bash
# 检查安装
which mmdc

# 使用npx
npx @mermaid-js/mermaid-cli --version
```

### 问题2: 沙箱错误
创建`puppeteer-config.json`:
```json
{
  "args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
```

### 问题3: 中文显示问题
```bash
# 安装中文字体（Ubuntu）
sudo apt-get install fonts-wqy-zenhei

# 或在mmdc命令中指定字体
mmdc --fontFamily "WenQuanYi Zen Hei"
```

## 扩展功能

### 自定义模板
可以修改`templates/`目录中的模板文件，添加自己的样式和布局。

### 自动化脚本
可以创建自动化脚本，将图表生成集成到CI/CD流程中。

### 质量检查
可以添加图表语法检查和验证功能。