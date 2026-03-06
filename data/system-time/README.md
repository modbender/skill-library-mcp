# System Time Skill

获取系统当前时间的 MCP (Model Context Protocol) Skill。

## 功能特性

这个 Skill 提供了三个强大的时间工具：

### 1. get_current_time - 获取当前时间
支持多种格式输出当前系统时间：
- `iso`: ISO 8601 标准格式
- `date`: 仅日期 (YYYY-MM-DD)
- `time`: 仅时间 (HH:MM:SS)
- `datetime`: 日期时间 (YYYY-MM-DD HH:MM:SS)
- `full`: 完整中文格式 (2026年02月13日 星期五 07:30:00)
- `timestamp`: Unix 时间戳
- `detailed`: 详细中文格式（包含毫秒）

可选参数：
- `timezone`: 指定时区（如 Asia/Shanghai, America/New_York）

### 2. get_time_info - 获取详细时间信息
返回完整的时间信息，包括：
- 年、月、日
- 星期
- 小时、分钟、秒、毫秒
- 时间戳
- ISO 格式
- 本地时间和 UTC 时间

### 3. calculate_time_diff - 计算时间差
计算两个时间点之间的差值，支持：
- ISO 8601 格式
- Unix 时间戳
- 自动计算到当前时间的差值

## 安装

```bash
npm install
npm run build
```

## 使用

### 启动 MCP Server

```bash
npm start
```

### 配置到 Claude Desktop

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "system-time": {
      "command": "node",
      "args": ["D:/SkillTest/system-time/dist/index.js"]
    }
  }
}
```

### 使用示例

在 Claude 中可以这样使用：

```
请获取当前时间（完整中文格式）
请告诉我详细的时间信息
计算从 2026-01-01 到现在过了多久
```

## 开发

项目结构：
```
system-time/
├── src/
│   └── index.ts          # 主要的 MCP server 代码
├── dist/                 # 编译后的 JavaScript 文件
├── package.json          # 项目配置
├── tsconfig.json         # TypeScript 配置
└── README.md            # 本文档
```

修改代码后重新构建：
```bash
npm run build
```

## 技术栈

- Node.js
- TypeScript
- @modelcontextprotocol/sdk

## 许可证

MIT
