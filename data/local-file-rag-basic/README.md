# 🚀 Local File RAG Skill - Basic Edition

一个为 OpenClaw 量身定制的高性能本地文件检索增强（RAG）工具（**基础版**）。

## ✨ 核心特性

- **🚀 零配置 & 极速**: 100% Node.js 持久化实现，内置高性能 **BM25 算法**，毫秒级响应。
- **📉 Token 节省大师**: 相比全量读文件，可节约 **80% - 95%** 的上下文 Token。
- **📦 多模态深度支持**: 
  - **代码**: JS/TS, Python, C++, Go, Java, Vue, HTML, CSS 等。
  - **文档**: PDF, Word (DOCX), Excel (XLSX, XLS), Markdown, CSV, JSON。
  - **多媒体**: 自动嗅探 PNG, JPG, SVG, MP4 等文件的元数据（尺寸、版本等）。
- **🛡️ 绝对防幻觉设计**: 
  - **100% 行号对齐**: 返回的所有片段强制携带原始行号（L123: ...）。
  - **语义聚类 (Clustering)**: 自动将物理位置相近的匹配项合并为连续的代码窗格，拒绝“煤渣式”碎片。
  - **去噪平衡**: 自动裁剪搜索结果中的边缘垃圾代码（如孤立的闭括号），确代码从逻辑入口（注释或签名）开始。
- **🔄 智能增量索引**: 基于文件指纹（mtime）的增量扫描，支持大规模工作区。

## 💎 版本对比 (Basic vs Pro)

| 特性 | Basic Edition (本项目) | Pro Edition |
| :--- | :--- | :--- |
| **检索算法** | 调优级 BM25 | 调优级 BM25 |
| **扫描限制** | 20MB / 文件 | 20MB / 文件 |
| **索引速度** | 单线程 (基础同步) | **Worker Pool 多线程并发 (极速)** |
| **多模态** | PDF/Word/Excel/多媒体 | PDF/Word/Excel/多媒体 |
| **高级接口** | 基础文本提取 | **OCR 识别、向量检索 (预留接口)** |
| **代码状态** | 100% 开源 | 授权获取 / 私有仓库 |

> [!TIP]
> 如果您在大型工程（如数万个文件）中使用，Pro 版的并发索引能力将为您节省大量的等待时间。获取 Pro 版请联系作者或查看相关渠道。

## 📦 安装

1. 将文件夹 `local-file-rag-basic` 拷贝至 OpenClaw 工程的 `.agents/skills/` 目录下。
2. 确保环境拥有 **Node.js v22+**（需原生支持 `node:sqlite`）。
3. 技能会自动处理 `pdf-parse`, `mammoth`, `xlsx` 等可选依赖。

## 🛠️ 工具能力 (`local_file_rag_search`)

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `query` | `string` | **必需**。可以是函数名、业务描述或逻辑关键词。 |
| `targetFile` | `string` | *可选*。限定在特定文件路径内进行深度搜索。 |
| `rootDir` | `string` | *可选*。可动态切换要扫描的根目录。 |

## 📖 在 OpenClaw 中使用

你可以直接对 OpenClaw 说：
- *"帮我看看这个项目里处理权限校验的逻辑在哪？"*
- *"搜索 `index.js` 中关于数据库连接的部分。"*
- *"提取并分析这个 Excel 表格里的数据。"*

## 🧪 命令行测试

在 `local-file-rag-basic` 目录下（或通过项目根目录路径）运行：
```powershell
node script/index.js "your_query" "optional_target_file"
```

## 📜 开源协议
[MIT License](LICENSE)
