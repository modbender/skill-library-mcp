# 小红书发布 Skill 配置指南

## 目录结构

```
xiaohongshu-publisher/
├── SKILL.md              # 技能主文档
├── scripts/
│   └── publish.js        # 发布脚本
└── references/
    └── config.md         # 配置说明
```

## 安装步骤

### 1. 复制 Skill 到 OpenClaw 技能目录

```powershell
# 复制到 OpenClaw 技能目录
Copy-Item -Recurse `  
  C:\Users\90781\.openclaw\workspace\skills\xiaohongshu-publisher `  
  C:\Users\90781\.openclaw\skills\
```

### 2. 配置 mcporter

编辑 `~/.mcporter/mcporter.json`:

```json
{
  "mcpServers": {
    "xiaohongshu": {
      "url": "http://localhost:18060/mcp"
    }
  }
}
```

### 3. 启动 MCP 服务端

```powershell
cd C:\Users\90781\.openclaw\workspace\xiaohongshu-mcp-1
.\xiaohongshu-mcp-windows-amd64.exe
```

### 4. 登录小红书

首次使用需要先登录：

```bash
node scripts/publish.js --check
```

如果显示未登录，需要使用登录工具扫码登录。

## 使用方法

### 命令行使用

```bash
# 基本发布
node scripts/publish.js -t "标题" -c "内容" -i "图片路径"

# 完整示例
node scripts/publish.js \
  --title "OpenClaw体验分享" \
  --content "openclaw太好用啦！" \
  --image "C:\\image.jpg" \
  --tags "openclaw,AI工具,效率神器"
```

### 程序化调用

```javascript
const { publish } = require('./scripts/publish');

await publish({
  title: '我的标题',
  content: '我的内容',
  images: ['C:\\image.jpg'],
  tags: ['标签1', '标签2']
});
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| MCP_URL | MCP 服务端地址 | http://localhost:18060/mcp |

## 故障排除

### MCP 连接失败

1. 检查 MCP 服务端是否运行
2. 检查端口 18060 是否被占用
3. 检查防火墙设置

### 登录失败

1. 运行 `node scripts/publish.js --check` 检查状态
2. 使用登录工具重新扫码
3. 检查 cookies 文件是否存在

### 发布失败

1. 检查图片路径是否正确
2. 检查内容是否超过字数限制
3. 查看 MCP 服务端日志
