# gaoding-design

OpenClaw Skill — 通过自然语言对话在[稿定设计](https://www.gaoding.com)搜索模板、编辑设计并导出成品。

## 前置条件

- Node.js >= 22.12.0
- [OpenClaw](https://github.com/nicepkg/openclaw) 已安装
- 稿定设计账号（用于浏览器自动化）

## 安装

```bash
git clone git@git.intra.gaoding.com:editor/gaoding-claw.git
cd gaoding-claw
npm install
npx playwright install chromium
cp .env.example .env  # 编辑 .env 填入凭证
npm run build
```

## 使用

### 作为 OpenClaw Skill

```bash
openclaw skill install ./
openclaw chat "帮我找一个618电商海报模板"
```

### 独立脚本调用

```bash
npx tsx scripts/search.ts "电商海报"
```

输出 JSON 包含 `templates` 数组和 `screenshotPath` 截图路径。

## 配置

编辑 `.env` 文件：

| 变量 | 说明 | 必填 |
|------|------|------|
| `GAODING_USERNAME` | 稿定账号（手机号或邮箱） | 是 |
| `GAODING_PASSWORD` | 稿定密码 | 是 |
| `ANTHROPIC_API_KEY` | Anthropic API Key | 是（或用 OpenAI） |
| `FEISHU_APP_ID` | 飞书应用 ID | 否（飞书集成时需要） |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 否（飞书集成时需要） |

## 项目结构

```
├── SKILL.md              # OpenClaw Skill 定义
├── src/
│   ├── index.ts          # 入口：意图解析 + 流程编排
│   ├── browser/
│   │   ├── auth.ts       # 登录态管理（Cookie 持久化）
│   │   ├── search.ts     # 模板搜索
│   │   ├── preview.ts    # 模板预览
│   │   ├── edit.ts       # 模板编辑
│   │   └── export.ts     # 设计导出
│   ├── llm/
│   │   └── intent.ts     # 意图解析
│   └── utils/
│       ├── image.ts      # 图片处理
│       └── feishu.ts     # 飞书消息卡片
└── scripts/
    ├── search.ts         # 独立搜索脚本
    └── smoke-test.ts     # 冒烟测试
```

## 已知限制

- 搜索依赖稿定网页 DOM 结构，网站改版可能导致选择器失效
- 仅支持中文关键词搜索
- 需要有效的稿定登录态（Cookie 过期后需重新登录：`npm run login`）
