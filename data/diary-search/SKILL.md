---
name: diary-search
description: "日记全文检索插件，支持中文分词、BM25搜索、时间衰减排序。适用于喜欢写日记的 OpenClaw 用户，或因 memory-lancedb 插件替换后需要查找日记的场景。"
metadata:
  openclaw:
    emoji: "📔"
    requires:
      bins: []
    install:
      - id: npm
        kind: node
        package: "diary-search"
        label: "Install via npm"
      - id: clawhub
        kind: clawhub
        slug: diary-search
        label: "Install via ClawHub"
---

# Diary Search

日记全文检索插件，让你可以搜索 OpenClaw 记录的日记内容。

## 安装步骤

**第一步：安装插件**

```bash
npm install -g diary-search
```

**第二步：更新配置**

在 `~/.openclaw/openclaw.json` 的 `plugins.load.paths` 中添加：

```json
"~/.npm-global/lib/node_modules/diary-search"
```

完整示例：

```json
{
  "plugins": {
    "enabled": true,
    "load": {
      "paths": [
        "~/.npm-global/lib/node_modules/diary-search"
      ]
    }
  }
}
```

**第三步：重启 Gateway**

```bash
openclaw gateway restart
```

## 使用方法

安装完成后，直接对我说：

```
搜索我上周关于"项目架构"的日记
搜索 2026-02 月关于"数据库优化"的讨论
查找昨天提到的"bug"
查看我的日记统计
```

## 工具说明

### diary_search

搜索日记内容。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✅ | 搜索关键词 |
| limit | number | ❌ | 返回条数，默认 5 |
| time_filter | string | ❌ | 时间过滤器 |

**time_filter 可选值：**
- `today` / `yesterday` / `last_week` / `last_month` / `this_month`
- `YYYY-MM`（如 2026-02）
- `YYYY-MM-DD`（如 2026-02-28）

### diary_stats

获取日记统计信息。

## 日记格式

支持 `.md`、`.txt`、`.markdown` 文件，文件名建议使用 `YYYY-MM-DD.md` 格式。
