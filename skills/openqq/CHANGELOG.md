# Changelog

All notable changes to this project will be documented in this file.

---

## [0.0.4] - 2026-02-26

### 🎯 Added

- 配置优化（简化模板）
- 删除不必要的文件（LICENSE, config examples）
- 纯文本文件发布（符合 ClawHub 要求）

### 🗑️ Removed

- LICENSE 文件（ClawHub 不需要）
- open-qq-config.full.example
- open-qq-config.json.example
- .env.example

---

## [0.0.3] - 2026-02-26

### 🎯 Added

- **npm 命令增强** - 新增 7 个实用命令
  - `npm run setup` - 一键初始化配置
  - `npm run health` - 完整健康检查
  - `npm run test-msg` - 测试消息（模拟）
  - `npm run version` - 查看版本号
  - `npm run restart` - 重启提示
  - `npm run stop` - 停止服务
  
- **文档增强**
  - FAQ 章节（8 个常见问题）
  - 启动完成提示（"已就绪"）
  - 健康检查输出示例
  
- **配置备选方案**
  - `.env.example` - 环境变量配置模板

- **可靠性提升**
  - LICENSE 文件（MIT）
  - Graceful Shutdown（SIGTERM/SIGINT 处理）
  - 消息发送重试机制（最多 2 次）

### 🔧 Changed

- **日志系统优化**
  - 新增 `shouldLog()` 方法，统一日志级别控制
  - 更清晰的日志级别判断逻辑
  
- **代码优化**
  - 清理冗余注释（保留关键注释）
  - Token 获取重试机制（最多 3 次，指数退避）
  - WebSocket 错误事件监听
  - 断开连接原因记录
  
- **文档定位优化**
  - README.md - 详细使用教程
  - SKILL.md - 技术参考文档

### 🐛 Fixed

- **健康检查脚本**
  - 修复整数比较错误（`[: 0\n0: integer expression expected`）
  - 添加错误处理和默认值
  
- **WebSocket 处理**
  - 添加 `error` 事件监听
  - 记录断开连接代码和原因

### 📝 Documentation

- README.md 新增 FAQ 章节
- CHANGELOG.md 格式优化
- .gitignore 添加 `.env`
- **新增 CONFIG.md** - 详细配置指南
- **新增 open-qq-config.full.example** - 完整配置模板
- 简化 open-qq-config.json.example（只保留核心配置）

---

## [0.0.2] - 2026-02-26

### 🎯 Added

- **健康检查脚本**
  - `scripts/health-check.sh` - 检查进程、日志、配置状态
  
- **npm 命令**
  - `npm run status` - 检查运行状态
  - `npm run logs` - 查看今日日志
  - `npm run dev` - 开发模式（热重载）
  
- **配置管理**
  - `open-qq-config.json.example` 移到 skill 目录
  - Node.js 版本要求（>=16.0.0）

### 🔧 Changed

- **代码优化**（精简 30%）
  - 统一 require（axios、spawn 移到顶部）
  - 提取通用函数（`handleMessage`）
  - 简化条件判断（三元表达式）
  - 合并群聊/私聊逻辑
  
- **日志系统简化**
  - 移除 gzip 压缩（容易失败且不需要）
  - 简化 writeLog 异步回退逻辑
  - 简化日志轮转逻辑
  
- **文档优化**
  - SKILL.md 精简 41%
  - README.md 精简 46%
  - package.json 简化

### 🐛 Fixed

- 会话 ID 生成逻辑
- 日志写入错误处理

### 🗑️ Removed

- **未使用的方法**
  - `healthCheck()` 
  - `logRawEvent()`
  
- **冗余内容**
  - node_modules（按需安装）
  - package-lock.json
  - 冗余注释和文档

### 📊 Stats

| 文件 | 优化前 | 优化后 | 减少 |
|------|--------|--------|------|
| qq-bot.js | 356 行 | 307 行 | -14% |
| logger.js | 274 行 | 194 行 | -29% |
| SKILL.md | ~200 行 | 118 行 | -41% |
| README.md | ~200 行 | 109 行 | -46% |
| **总计** | ~1081 行 | 757 行 | **-30%** |

---

## [0.0.1] - 2026-02-26

### 🎯 Added

- **核心功能**
  - QQ 私聊消息处理（`C2C_MESSAGE_CREATE`）
  - QQ 群@消息处理（`GROUP_AT_MESSAGE_CREATE`）
  - OpenClaw session 隔离
  - 自动心跳和重连
  
- **日志系统**
  - 中国时区（Asia/Shanghai）
  - 日志轮转（按大小和天数）
  - 敏感数据过滤
  - INFO/DEBUG/ERROR 分级
  
- **配置管理**
  - 集中配置文件（`open-qq-config.json`）
  - 移除环境变量依赖
  
- **安全加固**
  - 命令注入防护（`spawn` 而非 `exec`）
  - 会话 ID 白名单过滤
  - 配置文件权限管理

### 📁 Files

- `qq-bot.js` - 主程序
- `logger.js` - 日志系统
- `start-qq-bot.sh` - 启动脚本
- `package.json` - 依赖配置
- `SKILL.md` - 技术文档
- `README.md` - 使用说明

### 🔧 Technical Details

- **WebSocket 连接**: `wss://api.sgroup.qq.com/websocket`
- **Intents**: `(1 << 0) | (1 << 25)` - 私域完整权限
- **Session 命名**: `qq-private-{openid}` / `qq-group-{groupid}`
- **心跳间隔**: 30 秒
- **重连延迟**: 5 秒

---

## Version Summary

| 版本 | 日期 | 主要更新 | 代码行数 |
|------|------|----------|----------|
| **0.0.3** | 2026-02-26 | 7 个新命令、FAQ、重试机制 | ~550 |
| **0.0.2** | 2026-02-26 | 代码精简 30%、健康检查 | ~750 |
| **0.0.1** | 2026-02-26 | 初始版本 | ~1080 |

---

## Upcoming (v0.0.4)

- [ ] 添加单元测试
- [ ] 支持群聊非@消息（可选）
- [ ] 添加消息队列（防止并发过高）
- [ ] 支持多机器人配置

---

**格式说明：** 本 changelog 遵循 [Keep a Changelog](https://keepachangelog.com/) 规范。
