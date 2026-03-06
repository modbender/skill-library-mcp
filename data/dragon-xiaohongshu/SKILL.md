---
name: xiaohongshu-publisher
description: 自动发布内容到小红书平台。支持发布图文、检查登录状态、获取登录二维码。使用场景：自动化小红书内容发布、批量发布、定时发布等。
---

# 小红书自动发布 Skill

自动化发布内容到小红书平台，支持图文发布、登录管理和批量操作。

## 功能特性

- ✅ 自动发布图文内容到小红书
- ✅ 检查登录状态
- ✅ 自动获取登录二维码
- ✅ 支持自定义标题、内容、图片和标签
- ✅ 支持 HTTP MCP 服务端模式

## 前置要求

1. **小红书 MCP 服务端**
   - 文件：`xiaohongshu-mcp-windows-amd64.exe`
   - 端口：18060
   - 启动方式：运行 exe 文件

2. **mcporter CLI**
   ```bash
   npm install -g mcporter
   ```

3. **已登录小红书账号**
   - 首次使用需要先扫码登录

## 快速开始

### 1. 启动 MCP 服务端

```powershell
# 在 xiaohongshu-mcp 目录下运行
.\xiaohongshu-mcp-windows-amd64.exe
```

### 2. 检查登录状态

```bash
node scripts/publish.js --check
```

### 3. 发布内容

```bash
# 使用默认配置
node scripts/publish.js

# 自定义内容
node scripts/publish.js \
  --title "我的标题" \
  --content "正文内容..." \
  --image "C:\\path\\to\\image.png" \
  --tags "tag1,tag2,tag3"
```

## 配置说明

### mcporter 配置

配置文件：`~/.mcporter/mcporter.json`

```json
{
  "mcpServers": {
    "xiaohongshu": {
      "url": "http://localhost:18060/mcp"
    }
  }
}
```

### 发布参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 标题（最多20字） |
| content | string | 是 | 正文内容（最多1000字） |
| images | array | 是 | 图片路径数组 |
| tags | array | 否 | 标签数组 |

## 使用示例

### 示例 1：发布产品推广

```javascript
const publish = require('./scripts/publish');

await publish({
  title: '新品推荐！超好用',
  content: '今天给大家推荐一款超好用的产品...',
  images: ['C:\\product.jpg'],
  tags: ['好物推荐', '新品', '种草']
});
```

### 示例 2：发布生活分享

```bash
node scripts/publish.js \
  --title "今天的心情日记" \
  --content "今天天气真好，出去散步..." \
  --image "C:\\photos\\today.jpg" \
  --tags "生活,日常,心情"
```

## 注意事项

1. **登录状态**：发布前必须已登录小红书
2. **图片格式**：支持 jpg、png 格式
3. **内容限制**：
   - 标题最多 20 个中文字
   - 正文最多 1000 字
   - 图片最多 9 张
4. **频率限制**：小红书有每日发帖限制（约50篇）

## 故障排除

### 问题：MCP 连接失败

**解决**：
1. 检查 MCP 服务端是否运行
2. 检查端口 18060 是否被占用
3. 重启 MCP 服务端

### 问题：未登录

**解决**：
1. 运行 `node scripts/publish.js --check` 检查状态
2. 使用登录工具扫码登录
3. 或运行 `node scripts/login.js` 获取二维码

### 问题：发布失败

**解决**：
1. 检查图片路径是否正确
2. 检查内容是否超过字数限制
3. 查看 MCP 服务端日志

## 参考资料

- [小红书 MCP 项目](https://github.com/xpzouying/xiaohongshu-mcp)
- [mcporter 文档](http://mcporter.dev)
- 详细配置见 `references/config.md`
