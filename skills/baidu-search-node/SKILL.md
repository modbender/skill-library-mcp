# Baidu Search Skill

百度搜索命令行工具，通过 Node.js 脚本爬取百度搜索结果（无需 API key）。

## 激活条件

当用户提到：
- 百度搜索
- 用百度搜一下
- baidu search
- 使用 `baidu_search` 工具

## 工具实现

使用 `baidusearch.js` 脚本，位于 `/Users/mac/.openclaw/workspace/skills/baidu-search/baidusearch.js`

### 使用方式

```bash
# 基本搜索
node baidusearch.js "搜索内容"

# 指定结果数量
node baidusearch.js "搜索内容" -n 10

# 调试模式
node baidusearch.js "搜索内容" -n 5 -d 1
```

### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `[keyword]` | string | 是 | - | 搜索关键字 |
| `-n, --num` | number | 否 | 10 | 返回结果数量 |
| `-d, --debug` | number | 否 | 0 | 调试模式（0-关闭，1-打开） |

### 返回格式

每条搜索结果包含：
- `rank` - 排名
- `title` - 标题
- `abstract` - 摘要/描述
- `url` - 链接

## 与百度官方 API 技能对比

| 功能 | baidu-search-node (本技能) | baidu-search (官方 API) |
|------|---------------------------|------------------------|
| API Key | ❌ 不需要 | ✅ 需要 BAIDU_API_KEY |
| 资源类型过滤 | ❌ 仅网页 | ✅ web/video/image/aladdin |
| 时间过滤 | ❌ 不支持 | ✅ week/month/semiyear/year |
| 网站过滤 | ❌ 不支持 | ✅ 匹配/屏蔽网站 |
| 安全搜索 | ❌ 不支持 | ✅ 支持 |
| 实现方式 | 网页爬虫 | 百度千帆 API |

## 配置

在 `openclaw.json` 中添加：

```json5
{
  tools: {
    baiduSearch: {
      enabled: true,
      scriptPath: "/Users/mac/.openclaw/workspace/skills/baidu-search/baidusearch.js",
      defaultCount: 5,
      timeout: 30000,
    },
  },
}
```

## 使用方法

```javascript
// 执行百度搜索
const { execSync } = require('child_process');

function baiduSearch(query, count = 5) {
  const scriptPath = '/Users/mac/.openclaw/workspace/skills/baidu-search/baidusearch.js';
  const cmd = `node "${scriptPath}" "${query}" -n ${count}`;
  const output = execSync(cmd, { encoding: 'utf-8' });
  return parseOutput(output);
}
```

## 依赖安装

```bash
# 进入 skill 目录
cd /Users/mac/.openclaw/workspace/skills/baidu-search

# 安装依赖
npm install axios cheerio commander
```

## 注意事项

- 需要 Node.js 环境
- 依赖 axios、cheerio、commander 包
- 搜索结果来自百度网页，可能包含广告
- 建议设置合理的 timeout 避免请求超时
- 无需 API key，开箱即用
