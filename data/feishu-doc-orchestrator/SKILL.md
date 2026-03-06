---
name: feishu-doc-orchestrator
description: 飞书文档创建技能 - 将Markdown文件转换为飞书文档，支持25种块类型，完整权限管理。当用户需要将Markdown文档转换为飞书文档、创建协作文档、批量处理文档内容时激活此技能。
---

# 飞书文档创建技能

将Markdown文件转换为飞书文档的完整解决方案，支持25种飞书文档块类型，包括表格、代码块、待办事项、高亮块等复杂格式。

## 功能特性

- ✅ **25种块类型支持**：标题（H1-H9）、文本、列表、表格、代码、引用、待办事项、高亮块、分割线等
- ✅ **Markdown到飞书格式转换**：自动解析Markdown并转换为飞书块结构
- ✅ **权限管理**：智能Token模式选择，自动添加协作者权限
- ✅ **批量处理**：分批添加块，避免API限制
- ✅ **图片上传**：支持本地图片自动上传到飞书文档
- ✅ **表格转换**：Markdown表格转换为飞书原生表格
- ✅ **错误恢复**：部分块失败不影响整体流程

## 使用场景

**触发时机**：
- 用户需要将Markdown文档转换为飞书文档
- 用户需要创建协作文档并分配权限
- 用户需要批量处理文档内容到飞书
- 用户需要保留复杂格式（表格、代码、列表等）的文档转换

**示例请求**：
- "帮我把`报告.md`转换为飞书文档"
- "将这个Markdown文档发布到飞书"
- "创建一个飞书文档，包含这些表格和列表"
- "批量处理这些文档到飞书协作空间"

## 使用前准备

### 1. 配置飞书应用
需要飞书开放平台应用凭证：

```bash
# 创建配置文件
cat > ~/.openclaw/feishu-config.env << EOF
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxx
FEISHU_API_DOMAIN=https://open.feishu.cn
EOF
```

### 2. 检查配置
```bash
python ~/.openclaw/skills/feishu-doc-orchestrator/scripts/check_config.py
```

## 工作流程

1. **Markdown解析**：使用`feishu-md-parser`解析Markdown文件，生成块数据
2. **文档创建**：使用`feishu-doc-creator-with-permission`创建文档并处理权限
3. **块添加**：使用`feishu-block-adder`批量添加块到文档
4. **结果验证**：返回文档链接和添加统计

## 快速开始

### 命令行使用
```bash
# 转换单个Markdown文件
python scripts/feishu_doc_cli.py --input 报告.md --title "文档标题"

# 使用现有文档ID（追加内容）
python scripts/feishu_doc_cli.py --input 内容.md --doc-id DJ8QdybJboi1EJxrndLchPtEnoh
```

### OpenClaw Agent调用
技能会自动激活当用户请求Markdown到飞书文档转换。

## 技能架构

```
feishu-doc-orchestrator/      # 主编排技能
├── feishu-md-parser/         # 子技能1：Markdown解析
├── feishu-doc-creator-with-permission/  # 子技能2：创建+权限
├── feishu-block-adder/       # 子技能3：块添加
├── feishu-doc-verifier/      # 子技能4：文档验证
└── feishu-logger/            # 子技能5：日志记录
```

## 配置文件说明

### feishu-config.env
```ini
# 必需配置
FEISHU_APP_ID = "cli_xxxxxxxxxxxxx"
FEISHU_APP_SECRET = "xxxxxxxxxxxxxxxxxx"
FEISHU_API_DOMAIN = "https://open.feishu.cn"

# 可选配置
FEISHU_AUTO_COLLABORATOR_ID = "ou_xxx"    # 自动添加协作者
FEISHU_DEFAULT_FOLDER = "folder_token"    # 默认文件夹
```

## 支持的块类型

| 块类型 | 名称 | Markdown对应 |
|--------|------|--------------|
| 2 | 文本 | 普通段落 |
| 3-8 | 标题1-6 | # - ###### |
| 12 | 无序列表 | `- item` |
| 13 | 有序列表 | `1. item` |
| 14 | 代码块 | ```代码``` |
| 15 | 引用块 | `> 引用` |
| 17 | 待办事项 | `- [ ] todo` |
| 19 | 高亮块 | `> [!NOTE]` |
| 22 | 分割线 | `---` |
| 27 | 图片块 | `![alt](path)` |
| 31 | 表格 | Markdown表格 |
| 32 | 表格单元格 | 自动生成 |

## 性能表现

- **小文档**（32个块）：10-15秒，成功率>95%
- **大文档**（160个块，含表格）：45-60秒，成功率>80%
- **图片上传**：支持本地图片自动上传

## 注意事项

1. **权限要求**：
   - 需要飞书开放平台应用权限：`docx:document`、`docx:document.block:convert`、`drive:drive`
   - Tenant Token创建的文档需添加协作者权限
   - User Token创建的文档无需权限转移

2. **文件路径**：
   - 本地图片需使用绝对路径
   - Markdown文件路径支持相对/绝对路径

3. **API限制**：
   - 批量处理自动分批，每批20个块
   - 每块间隔50ms避免限流

4. **错误处理**：
   - 单个块失败不影响整体流程
   - 失败信息记录到日志文件
   - 可重试失败块

## 故障排除

### 常见问题
1. **API权限不足**：检查应用权限配置
2. **图片上传失败**：确认图片路径正确且文件存在
3. **表格转换失败**：检查Markdown表格格式
4. **Token过期**：重新获取token

### 调试模式
```bash
python scripts/feishu_doc_cli.py --input test.md --title "测试" --verbose
```

## 更新日志

- **v1.0.0** (2026-02-24)：初始版本，基于rosalynYANG/feishu-doc-creator-skill打包
- 支持25种飞书块类型
- 完整权限管理
- 批量处理优化

## 致谢

基于 [rosalynYANG/feishu-doc-creator-skill](https://github.com/rosalynYANG/feishu-doc-creator-skill) 开发，感谢原作者的优秀工作。