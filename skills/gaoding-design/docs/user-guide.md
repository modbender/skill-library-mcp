# 用户安装与使用指南

从 ClawHub 安装 gaoding-design skill，通过对话搜索稿定设计模板。

## 安装

### 1. 从 ClawHub 安装

```bash
clawhub install gaoding-design
```

skill 会安装到 `~/.openclaw/skills/gaoding-design/`。

### 2. 安装依赖

```bash
cd ~/.openclaw/skills/gaoding-design
npm install
npx playwright install chromium
```

> Chromium 浏览器约 200MB，首次安装需要下载。

### 3. 配置稿定账号

```bash
cp .env.example .env
```

编辑 `.env`，填入稿定设计的账号和密码：

```
GAODING_USERNAME=你的手机号或邮箱
GAODING_PASSWORD=你的密码
```

## 使用

安装完成后，直接在 OpenClaw 对话中使用：

```
你：帮我找一个618电商海报模板
你：搜一下简约风格的名片
你：我想做一张美食推广海报
```

OpenClaw 会自动调用搜索脚本，返回模板截图和列表。

## 验证安装

可以手动运行搜索脚本验证：

```bash
cd ~/.openclaw/skills/gaoding-design
npx tsx scripts/search.ts "电商海报"
```

正常输出示例：

```json
{
  "query": "电商海报",
  "count": 6,
  "screenshotPath": "~/.openclaw/skills/gaoding-design/output/search-result.png",
  "templates": [
    { "id": "193439734", "title": "美容美妆产品展示宣传推广电商竖版海报", "previewUrl": "https://..." }
  ]
}
```

## 常见问题

### Cookie 过期

搜索脚本会自动检测登录态。如果 `.env` 中配置了账号密码，Cookie 过期时会自动重新登录。

### 搜索结果为空

稿定网站的 DOM 结构可能会更新，导致选择器失效。可以运行冒烟测试确认：

```bash
npx tsx scripts/smoke-test.ts
```

如果测试失败，请检查是否有新版本：

```bash
clawhub update gaoding-design
```

### 前置条件

- Node.js >= 22.12.0
- OpenClaw 已安装
- 稿定设计账号
