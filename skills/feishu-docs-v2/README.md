# feishu-docs

飞书文档管理命令行工具，基于飞书开放平台 API 实现文档的读取、创建、更新、删除和导入等功能。

## 技术原理

### 认证机制

本项目使用飞书开放平台的**自建应用**模式进行认证：

1. **Tenant Access Token**: 通过 `app_id` 和 `app_secret` 获取租户访问令牌
   - 令牌有效期为 2 小时
   - 内置缓存机制，提前 5 分钟刷新，避免频繁请求

2. **权限模型**: 需要在飞书开放平台为应用配置以下权限：
   - `docx:document` - 查看、编辑、创建文档
   - `drive:drive` - 查看、删除云空间文件
   - `drive:file` - 上传文件
   - `drive:importTask` - 导入文件为文档
   - `auth:tenant` - 获取租户访问凭证

### 核心 API

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 获取 Token | `auth/v3/tenantAccessToken/internal` | 应用级别认证 |
| 读取文档 | `docx/document/get` | 获取文档元数据 |
| 读取内容 | `docx/document/rawContent/get` | 获取纯文本内容 |
| 获取块列表 | `docx/document/block/list` | 获取结构化块数据 |
| 创建文档 | `docx/document/create` | 在指定文件夹创建文档 |
| 内容转换 | `docx/document/convert` | Markdown/HTML 转飞书块 |
| 添加块 | `docx/documentBlockDescendant/create` | 批量添加内容块 |
| 上传文件 | `drive/v1/file/uploadAll` | 上传文件到云空间 |
| 导入任务 | `drive/v1/importTask/create` | 创建文件导入任务 |
| 查询任务 | `drive/v1/importTask/get` | 轮询导入任务状态 |
| 列出文件 | `drive/v1/file/list` | 列出文件夹内容 |
| 删除文件 | `drive/v1/file/delete` | 删除文档或文件 |

### 技术栈

- **Node.js** - 运行时环境
- **[@larksuiteoapi/node-sdk](https://github.com/larksuite/node-sdk)** - 飞书官方 Node.js SDK
- **[commander](https://github.com/tj/commander.js)** - CLI 框架，支持子命令和参数解析
- **[dotenv](https://github.com/motdotla/dotenv)** - 环境变量管理

### 内容处理流程

1. **Markdown 导入**: Markdown → 飞书 API 转换 → 块创建 → 文档生成
2. **文件导入**: 本地文件 → 上传至云空间 → 创建导入任务 → 轮询状态 → 生成文档
3. **内容更新**: 获取现有块 → 删除旧块（覆盖模式）→ 创建新块

## 安装

```bash
npm install
```

## 配置

在项目根目录创建 `.env` 文件：

```env
FEISHU_APP_ID=cli_xxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxx
FEISHU_DOMAIN=https://open.feishu.cn
```

### 获取应用凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建"企业自建应用"
3. 在"凭证与基础信息"中获取 App ID 和 App Secret
4. 在"权限管理"中添加上方列出的权限
5. 发布应用（需要管理员审批）

## 使用方法

### 读取文档

```bash
# 读取文档内容（JSON 格式，包含元数据和内容）
node index.js get -d doccxxxxxxxxxxxxxx

# 保存为 Markdown 文件
node index.js get -d doccxxxxxxxxxxxxxx -o output.md --format markdown

# 纯文本格式
node index.js get -d doccxxxxxxxxxxxxxx --format text

# 获取文档块结构（JSON）
node index.js get-blocks -d doccxxxxxxxxxxxxxx -o blocks.json
```

### 创建文档

```bash
# 创建空文档
node index.js create -f foldxxxxxxxxxxxxxx -t "我的文档"

# 从文件创建（自动识别 Markdown 格式）
node index.js create -f foldxxxxxxxxxxxxxx -t "我的文档" --file content.md

# 直接指定内容
node index.js create -f foldxxxxxxxxxxxxxx -t "我的文档" --content "文档内容"
```

创建成功后，文档信息会保存到 `doc-{documentId}.json` 文件。

### 导入本地文件

支持格式：txt, docx, xlsx, csv, md 等

```bash
# 导入 Markdown 为飞书文档
node index.js import-file -f ./document.md --folder-token foldxxxxxxxxxxxxxx --type docx --ext md

# 导入 CSV 为表格
node index.js import-file -f ./data.csv --folder-token foldxxxxxxxxxxxxxx --type sheet --ext csv

# 导入 Excel 为多维表格
node index.js import-file -f ./data.xlsx --folder-token foldxxxxxxxxxxxxxx --type bitable --ext xlsx
```

导入流程：上传文件 → 创建任务 → 自动轮询状态 → 完成

### 列出文件夹

```bash
# 列出根目录内容
node index.js list

# 列出指定文件夹
node index.js list --folder-token foldxxxxxxxxxxxxxx
```

### 更新文档

```bash
# 覆盖文档内容（先删除所有块，再添加新内容）
node index.js update -d doccxxxxxxxxxxxxxx --file new-content.md

# 追加内容到文档末尾
node index.js update -d doccxxxxxxxxxxxxxx --content "追加的文本" --append
```

### 删除文档

```bash
# 删除文档（需要 --force 确认）
node index.js delete -d doccxxxxxxxxxxxxxx --force
```

## 命令参考

```
Usage: feishu-docs [options] [command]

Options:
  -V, --version   output the version number
  -h, --help      display help for command

Commands:
  get             读取飞书文档内容
  get-blocks      获取文档块内容（结构化数据）
  create          创建新的飞书文档
  import-file     将本地文件导入为飞书文档
  list            列出文件夹内容
  delete          删除飞书文档
  update          更新文档内容
  help [command]  display help for command
```

## Token 说明

- **文档 Token**: 以 `docc` 开头，标识飞书文档
- **文件夹 Token**: 以 `fold` 开头，标识云空间文件夹
- **文件 Token**: 以 `file` 开头，标识上传的文件

获取方式：
1. 在飞书文档页面 URL 中查找
2. 使用 `list` 命令列出文件夹内容

## 调试

设置环境变量启用调试输出：

```bash
DEBUG=1 node index.js get -d doccxxxxxxxxxxxxxx
```

## License

MIT
