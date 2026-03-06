---
name: wps-office
description: WPS Office automation skill supporting document creation, Markdown conversion, and image-text layout.
---

# WPS Office Skill

## 简介

WPS Office 自动化操作 Skill，支持本地文档操作和 WPS 365 云端协作功能。

## ⚠️ 安全警告

### 本地自动化风险
- **GUI 自动化**：本 Skill 使用 `pyautogui` 进行键盘输入模拟，可能会与当前活动窗口交互
- **文件操作**：Skill 会创建、打开和修改文件，请确保在受信任的环境中使用
- **权限要求**：macOS 需要授予辅助功能权限才能使用自动化功能

### 云端凭证安全
- **凭证存储**：WPS 365 功能需要配置 `app_id` 和 `app_secret`，建议：
  - 不要在公共设备或共享环境中配置
  - 定期更换凭证
  - 使用环境变量而非明文配置文件（即将支持）
- **API 调用**：所有 WPS 365 API 调用使用 HTTPS 加密传输

### 建议
- 首次使用建议在沙盒环境或虚拟机中测试
- 审查 `scripts/main.py` 源码确认功能符合预期
- 如不需要 WPS 365 功能，可留空 `app_id` 和 `app_secret`

## 功能特性

### 本地文档操作（无需凭证）
- 📄 **创建文档** - 创建 Word、Excel、PPT 文档
- 📂 **打开文档** - 打开已有文档
- 📋 **文档列表** - 列出文档目录中的文件
- 🔄 **格式转换** - 支持 MD 转 Word/RTF/HTML
- 📦 **批量处理** - 批量转换文档格式

### Markdown 转换功能（新增）
- 📝 **MD → Word** - 完整 Markdown 转 Word（支持标题、列表、表格、代码块等）
- 📝 **Word → MD** - Word 文档导出为 Markdown
- 📊 **MD → Excel** - Markdown 转 Excel（表格变工作表，列表变数据）
- 📊 **Excel → MD** - Excel 转 Markdown
- 🎬 **MD → PPT** - Markdown 转 PPT（标题变幻灯片）
- 🎬 **PPT → MD** - PPT 转 Markdown
- 🖼️ **MD 含图片** - Markdown 转 Word 并处理图片

### 图片处理与图文混排（新增）
- 🖼️ **Word 图片插入** - 向 Word 文档插入图片，支持对齐和标题
- 🖼️ **Word 图片网格** - 批量插入图片形成网格布局
- 📐 **Word 图文混排** - 支持左图右文、右图左文、上图下文等布局
- 🖼️ **PPT 图片插入** - 向 PPT 幻灯片插入图片
- 📐 **PPT 图文混排** - PPT 幻灯片图文混排（4种布局）
- 🖼️ **Excel 图片插入** - 向 Excel 单元格插入图片
- 📐 **Excel 图文混排** - Excel 单元格图文混排
- 🎨 **图片处理** - 调整图片尺寸、批量压缩

### WPS 365 云端功能（需要凭证）
- 📊 **智能表单** - 表单创建、数据收集
- 📄 **智能文档** - 在线协作文档
- 📊 **多维表格** - 视图管理、字段管理、高级查询
- 📊 **流程图** - 流程图创建和导出
- 🧠 **思维导图** - 思维导图创建和导出

## 安装

### 1. 安装依赖

```bash
pip install requests pyautogui pyperclip Pillow
```

### 2. 配置 Skill

编辑 `config.json`：

```json
{
  "default_save_path": "~/Documents/WPS",
  "wps_path": "",
  "app_id": "",
  "app_secret": ""
}
```

### 3. 获取 WPS 开放平台凭证（可选）

仅在使用 WPS 365 功能时需要：

1. 访问 https://open.wps.cn
2. 注册开发者账号
3. 创建应用获取 App ID 和 App Secret
4. 将凭证填入 config.json

## 使用方法

### 本地文档操作

```bash
# 创建 Word 文档
python scripts/main.py create type=writer filename=报告.docx

# Markdown 转 Word（旧版，简单转换）
python scripts/main.py convert file=文档.md format=docx

# 批量转换
python scripts/main.py batch_convert dir=~/Documents format=pdf
```

### Markdown 转换功能（新增）

```bash
# Markdown 转 Word（完整版）
python3 scripts/main.py md_to_docx file=文档.md output=文档.docx title="我的文档"

# Word 转 Markdown
python3 scripts/main.py docx_to_md file=文档.docx output=文档.md

# Markdown 转 Excel（表格变工作表）
python3 scripts/main.py md_to_xlsx file=数据.md output=数据.xlsx title="销售数据"

# Excel 转 Markdown
python3 scripts/main.py xlsx_to_md file=数据.xlsx output=数据.md

# Markdown 转 PPT（标题变幻灯片）
python3 scripts/main.py md_to_pptx file=汇报.md output=汇报.pptx title="项目汇报"

# PPT 转 Markdown
python3 scripts/main.py pptx_to_md file=汇报.pptx output=汇报.md

# Markdown 转 Word（含图片处理）
python3 scripts/main.py md_with_images_to_docx file=文档.md output=文档.docx image_width=4
```

### 图片处理与图文混排（新增）

#### Word 图文混排

```bash
# 向 Word 文档插入图片
python3 scripts/main.py insert_image docx=文档.docx image=图片.png width=4 align=center caption="图片标题"

# 插入图片网格
python3 scripts/main.py insert_image_grid images="1.png,2.png,3.png" cols=2 width=3 output=相册.docx

# 创建图文混排布局
python3 scripts/main.py create_text_image_layout text="说明文字" image=图片.png layout=left output=图文.docx
```

#### PPT 图文混排（新增）

```bash
# 向 PPT 幻灯片插入图片
python3 scripts/main.py insert_image_to_ppt pptx=汇报.pptx slide=1 image=图片.jpg left=1 top=1 width=4

# 创建 PPT 图文混排
python3 scripts/main.py create_ppt_text_image_layout \
  pptx=汇报.pptx \
  slide=1 \
  text="这是说明文字" \
  image=图片.jpg \
  layout=left \
  image_width=4
```

#### Excel 图文混排（新增）

```bash
# 向 Excel 单元格插入图片
python3 scripts/main.py insert_image_to_excel \
  xlsx=数据.xlsx \
  sheet=Sheet1 \
  cell=A1 \
  image=图片.jpg \
  width=100

# 创建 Excel 图文混排
python3 scripts/main.py create_excel_text_image_layout \
  xlsx=数据.xlsx \
  sheet=Sheet1 \
  cell=A1 \
  text="说明文字" \
  image=图片.jpg \
  layout=right \
  image_width=100
```

**布局方式说明：**
- `layout=left` - 图片左，文字右
- `layout=right` - 图片右，文字左
- `layout=top` - 图片上，文字下
- `layout=bottom` - 文字上，图片下

### WPS 365 云端功能

```bash
# 智能表单
python scripts/main.py form_list

# 智能文档
python scripts/main.py doc_list

# 多维表格
python scripts/main.py sheet_list
python scripts/main.py sheet_views sheet_id=sheet_001

# 流程图
python scripts/main.py flow_list

# 思维导图
python scripts/main.py mind_list
```

## API 实现说明

### 本地功能实现
- 使用 `subprocess` 调用 WPS Office 应用程序
- 使用 `pyautogui` 模拟键盘输入（创建带内容的文档）
- 文件格式转换使用本地 WPS 引擎或 Python 库

### WPS 365 云端功能实现
- 使用 WPS 开放平台 REST API
- OAuth 2.0 认证流程
- 所有 API 调用使用 HTTPS 加密
- 支持自动 token 刷新

### API 端点
- 认证: `POST /auth/v1/token`
- 表单: `/forms/v1/*`
- 文档: `/docs/v1/*`
- 表格: `/sheets/v1/*`
- 流程图: `/flows/v1/*`
- 思维导图: `/minds/v1/*`

## 故障排除

### 本地功能问题
- **WPS 无法打开**：检查 WPS 是否已安装
- **自动化无响应**：检查 macOS 辅助功能权限
- **格式转换失败**：确保文件格式受支持

### WPS 365 功能问题
- **API 调用失败**：检查 app_id 和 app_secret 是否正确
- **网络超时**：检查网络连接，API 服务器是否可访问
- **权限不足**：检查应用是否有足够的 API 权限

## 版本信息

- **版本**: 1.0.0
- **作者**: MaxStorm Team
- **许可证**: MIT
- **源码**: https://github.com/maxstorm/wps-skill
