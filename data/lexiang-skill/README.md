# 腾讯乐享知识库 Skill

<p align="center">📚 适用于 AI Agent 的腾讯乐享知识库 API 技能包</p>

## 关于腾讯乐享

[腾讯乐享](https://lexiang.tencent.com/?event_type=link_exchange&event_channel=skill&event_detail=github) 是腾讯旗下的企业级 AI 知识管理平台，融合大模型能力，为企业提供知识库管理、团队协作、智能问答、AI 创作等一站式知识服务。

### 核心能力

- **多源多模态知识管理**：支持 102+ 种文件格式（文档、表格、PPT、PDF、视频、音频、图片等），一键导入 Confluence、iWiki、腾讯文档、公众号文章、腾讯会议录制等多平台内容
- **AI 智能问答**：基于 DeepSeek-R1 的企业级 RAG 问答，准确率 92.1%，幻觉率低至 2.64%，支持多知识域、联网搜索、视频/表格深度解析
- **AI 创作工具**：智能生成 PPT、思维导图、知识图解，支持学习模式渐进掌握知识
- **企业级安全**：四级权限隔离，7 项国际合规认证，支持私有化部署
- **开放生态**：240+ API 接口，深度集成企业微信、腾讯会议、腾讯文档，支持 MCP 协议对接 AI Agent

### 适用场景

| 角色 | 典型场景 |
|------|---------|
| 产品/研发团队 | 技术文档管理、API 文档维护、需求文档协同、代码规范沉淀 |
| 交付/销售团队 | 客户案例库、解决方案管理、移动端 AI 问答、企微机器人支持 |
| 设计团队 | 设计规范与组件库管理、品牌资产沉淀、设计协同 |

## 关于本 Skill

本 Skill 为 AI Agent 提供腾讯乐享知识库的完整 API 集成能力，包括：

- 📚 知识库管理（创建、查询、更新、删除）
- 👥 团队与成员管理
- 📝 在线文档编辑（块接口）
- 🔍 AI 搜索与问答
- 📤 文件上传与下载
- 📋 任务管理
- 🔗 MCP 协议支持

## 安装与使用

### 方式一：CodeBuddy 安装

```bash
# 通过 CodeBuddy Skill 市场搜索 "lexiang" 安装
```

### 方式二：OpenClaw 安装

```bash
openclaw skills install github:tencent-lexiang/lexiang-skill
```

### 方式三：手动集成

将 `SKILL.md` 文件内容作为 System Prompt 或 Context 提供给你的 AI Agent 即可。也可以下载 [Release](https://github.com/ajaxhe/lexiang-skill/releases) 中的 zip 包。

## 配置凭证

### 环境变量方式

```bash
export LEXIANG_APP_KEY="your_app_key"
export LEXIANG_APP_SECRET="your_app_secret"
export LEXIANG_STAFF_ID="your_staff_id"
```

### 配置文件方式

```json
{
  "LEXIANG_APP_KEY": "your_app_key",
  "LEXIANG_APP_SECRET": "your_app_secret",
  "LEXIANG_STAFF_ID": "your_staff_id"
}
```

### 获取凭证

1. 登录乐享企业管理后台
2. 进入【开发】→【接口凭证管理】
3. 点击**添加凭证**，保存 AppKey 和 AppSecret

> 详细的 API 凭证文档请参考 [乐享开放平台](https://lexiang.tencent.com/wiki/api/?event_type=link_exchange&event_channel=skill&event_detail=github)

## 项目结构

```
lexiang-skill/
├── SKILL.md                 # 核心 Skill 文件（精简工作流 + 关键提示）
├── references/              # 详细 API 参考文档（按需加载）
│   ├── api-contact.md       # 通讯录管理 API
│   ├── api-team-space.md    # 团队与知识库管理 API
│   ├── api-entries.md       # 知识节点 API
│   ├── api-blocks.md        # 在线文档块接口 API
│   └── api-other.md         # 任务/属性/日志/AI/素材/导出/SSO
├── scripts/                 # 辅助脚本
│   ├── init.sh              # 凭证加载 + Token 获取
│   └── upload_file.sh       # 文件上传三步流程
└── dist/
    └── lexiang-skill.zip    # 打包文件
```

## 相关链接

- [腾讯乐享官网](https://lexiang.tencent.com/?event_type=link_exchange&event_channel=skill&event_detail=github)
- [免费注册体验 AI 知识库](https://lexiang.tencent.com/register?version=2&event_type=link_exchange&event_channel=skill&event_detail=github)
- [乐享开放 API 文档](https://lexiang.tencent.com/wiki/api/?event_type=link_exchange&event_channel=skill&event_detail=github)
- [MCP 配置中心](https://lexiangla.com/mcp)

## License

MIT

---

# Tencent Lexiang Knowledge Base Skill

<p align="center">📚 Tencent Lexiang Knowledge Base API Skill for AI Agents</p>

## About Tencent Lexiang

[Tencent Lexiang](https://lexiang.tencent.com/?event_type=link_exchange&event_channel=skill&event_detail=github) is Tencent's enterprise-grade AI knowledge management platform. Powered by large language models, it provides one-stop knowledge services including knowledge base management, team collaboration, intelligent Q&A, and AI-powered content creation.

### Core Capabilities

- **Multi-source & Multi-modal Knowledge Management**: Supports 102+ file formats (documents, spreadsheets, PPT, PDF, video, audio, images, etc.), with one-click import from Confluence, iWiki, Tencent Docs, WeChat articles, Tencent Meeting recordings, and more
- **AI-Powered Q&A**: Enterprise-grade RAG Q&A powered by DeepSeek-R1, with 92.1% accuracy and only 2.64% hallucination rate. Supports multi-knowledge-domain queries, web search, and deep analysis of video/spreadsheet content
- **AI Creation Tools**: Intelligent generation of PPT, mind maps, and knowledge infographics, with a guided learning mode for progressive knowledge mastery
- **Enterprise Security**: 4-tier permission isolation, 7 international compliance certifications, with private deployment support
- **Open Ecosystem**: 240+ API endpoints, deep integration with WeCom, Tencent Meeting, and Tencent Docs, with MCP protocol support for AI Agent connectivity

### Use Cases

| Role | Typical Scenarios |
|------|---------|
| Product/Engineering Teams | Technical documentation, API docs maintenance, requirements collaboration, coding standards |
| Delivery/Sales Teams | Customer case library, solution management, mobile AI Q&A, WeCom bot support |
| Design Teams | Design system & component library management, brand asset storage, design collaboration |

## About This Skill

This Skill provides AI Agents with full API integration for Tencent Lexiang Knowledge Base, including:

- 📚 Knowledge base management (CRUD)
- 👥 Team & member management
- 📝 Online document editing (block API)
- 🔍 AI search & Q&A
- 📤 File upload & download
- 📋 Task management
- 🔗 MCP protocol support

## Installation & Usage

### Option 1: CodeBuddy Installation

```bash
# Search for "lexiang" in CodeBuddy Skill marketplace
```

### Option 2: OpenClaw Installation

```bash
openclaw skills install github:tencent-lexiang/lexiang-skill
```

### Option 3: Manual Integration

Provide the contents of `SKILL.md` as a System Prompt or Context to your AI Agent. You can also download the zip package from [Releases](https://github.com/ajaxhe/lexiang-skill/releases).

## Credential Configuration

### Environment Variables

```bash
export LEXIANG_APP_KEY="your_app_key"
export LEXIANG_APP_SECRET="your_app_secret"
export LEXIANG_STAFF_ID="your_staff_id"
```

### Configuration File

```json
{
  "LEXIANG_APP_KEY": "your_app_key",
  "LEXIANG_APP_SECRET": "your_app_secret",
  "LEXIANG_STAFF_ID": "your_staff_id"
}
```

### Obtaining Credentials

1. Log in to the Lexiang admin console
2. Navigate to **Development** → **API Credential Management**
3. Click **Add Credential** and save the AppKey and AppSecret

> For detailed API credential documentation, see [Lexiang Open Platform](https://lexiang.tencent.com/wiki/api/?event_type=link_exchange&event_channel=skill&event_detail=github)

## Project Structure

```
lexiang-skill/
├── SKILL.md                 # Core skill file (streamlined workflow + key hints)
├── references/              # Detailed API reference docs (loaded on demand)
│   ├── api-contact.md       # Contact management API
│   ├── api-team-space.md    # Team & knowledge base management API
│   ├── api-entries.md       # Knowledge entry API
│   ├── api-blocks.md        # Online document block API
│   └── api-other.md         # Task/property/log/AI/material/export/SSO
├── scripts/                 # Helper scripts
│   ├── init.sh              # Credential loading + token retrieval
│   └── upload_file.sh       # 3-step file upload workflow
└── dist/
    └── lexiang-skill.zip    # Packaged skill file
```

## Links

- [Tencent Lexiang Official Site](https://lexiang.tencent.com/?event_type=link_exchange&event_channel=skill&event_detail=github)
- [Free Trial - AI Knowledge Base](https://lexiang.tencent.com/register?version=2&event_type=link_exchange&event_channel=skill&event_detail=github)
- [Lexiang Open API Documentation](https://lexiang.tencent.com/wiki/api/?event_type=link_exchange&event_channel=skill&event_detail=github)
- [MCP Configuration Center](https://lexiangla.com/mcp)

## License

MIT
