# 微信Xlog格式说明

## 概览
微信Xlog是微信客户端的调试日志格式，通常用于问题诊断和性能分析。Xlog文件可能经过加密，需要先使用外部工具（如QXLog）解密才能分析。

## 日志格式

### 常见格式1（标准格式）
```
[时间戳] [级别] [模块名] 消息内容
```
示例:
```
[2024-01-01 10:00:00.123] [ERROR] [Network] Connection failed
[2024-01-01 10:00:01.456] [INFO] [UI] Activity started
```

### 常见格式2（紧凑格式）
```
时间戳 级别 模块名: 消息内容
```
示例:
```
2024-01-01 10:00:00.123 ERROR Network: Connection failed
2024-01-01 10:00:01.456 INFO UI: Activity started
```

### 常见格式3（Android日志格式）
```
MM/dd HH:mm:ss.vvv 级别/模块: 消息内容
```
示例:
```
01/01 10:00:00.123 E/Network: Connection failed
01/01 10:00:01.456 I/UI: Activity started
```

## 日志级别

| 级别 | 含义 | 严重程度 |
|------|------|----------|
| FATAL | 致命错误 | 最高 |
| ERROR | 错误 | 高 |
| WARN | 警告 | 中 |
| INFO | 信息 | 低 |
| DEBUG | 调试信息 | 最低 |
| VERBOSE | 详细输出 | 最低 |

## 常见模块

| 模块名 | 说明 |
|--------|------|
| Network | 网络相关 |
| UI | 界面相关 |
| Storage | 存储/数据库 |
| Media | 多媒体 |
| Chat | 聊天功能 |
| Contact | 联系人 |
| Setting | 设置 |
| Auth | 认证授权 |
| Payment | 支付 |
| Crash | 崩溃相关 |

## 时间戳格式

### 完整时间戳
```
2024-01-01 10:00:00.123
```
格式: `YYYY-MM-DD HH:MM:SS.mmm`

### 简化时间戳
```
01/01 10:00:00.123
```
格式: `MM/dd HH:MM:SS.mmm`

## 示例日志

### 正常流程日志
```
[2024-01-01 10:00:00.123] [INFO] [Network] Request started: GET /api/user/info
[2024-01-01 10:00:00.456] [INFO] [Network] Response received: 200 OK
[2024-01-01 10:00:00.457] [INFO] [UI] Update user info view
```

### 错误日志
```
[2024-01-01 10:00:01.123] [ERROR] [Network] Request failed: timeout
[2024-01-01 10:00:01.124] [ERROR] [UI] Show error dialog: Network timeout
```

### 警告日志
```
[2024-01-01 10:00:02.123] [WARN] [Storage] Disk space low: 500MB remaining
[2024-01-01 10:00:02.124] [WARN] [Cache] Cache size exceeded, cleaning up
```

### 调试日志
```
[2024-01-01 10:00:03.123] [DEBUG] [Network] Request payload: {"userId":"123"}
[2024-01-01 10:00:03.124] [DEBUG] [UI] View layout: width=1080, height=1920
```

## 注意事项

1. **加密问题**: Xlog文件可能经过加密，需要先使用QXLog等工具解密
2. **编码问题**: 日志文件可能包含非UTF-8字符，解析时需要错误处理
3. **格式变化**: 不同版本的微信可能使用不同的日志格式
4. **时间精度**: 时间戳精度可能不同（毫秒、微秒等）
5. **模块名称**: 模块名称可能包含空格或特殊字符
6. **多行日志**: 某些错误信息可能跨多行，需要特殊处理

## 分析要点

- 关注ERROR和FATAL级别的日志
- 检查网络请求的失败率
- 观察模块日志的分布
- 分析时间密集的日志点
- 识别重复出现的错误模式
