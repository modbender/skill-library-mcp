---
name: dingtalk-api
description: 调用钉钉开放平台API，支持用户搜索/详情/查询、部门管理（搜索/详情/子部门/用户列表/父部门）、机器人单聊消息发送、群聊消息发送、群内机器人列表查询、Stream模式事件推送、多会话隔离管理等核心功能。Use when needing to search DingTalk users or departments, get user/department details, send robot messages, list group bots, handle Stream mode events, or manage multi-session conversations.
---

# DingTalk API Skill

用于调用钉钉开放平台 API 的技能，提供完整的钉钉企业级集成功能，包括传统API调用和Stream模式事件推送。

## 核心功能模块

### 用户与组织管理
- 用户搜索、详情查询、手机号/unionid查询
- 部门管理（搜索、详情、子部门、用户列表、父部门）
- 企业员工统计、组织架构映射
- 离职记录查询、未登录用户列表

### 消息与机器人
- 机器人单聊消息发送
- 机器人群聊消息发送  
- 群内机器人列表查询
- 消息内容格式化与发送

### Stream模式事件推送（推荐）
- **实时消息接收**：通过WebSocket长连接接收钉钉事件
- **多会话隔离**：为每个用户/群聊成员创建独立的AI会话
- **上下文保持**：每个会话保持完整的对话历史和个性化记忆
- **自动回复路由**：AI生成的回复直接通过钉钉API发送，避免多通道冲突

### OA审批管理
- 审批实例查询、详情获取
- 发起、终止、执行、转交审批任务
- 审批评论管理、待办数量统计

## API版本支持

### 传统服务端API (兼容)
- **用户管理**：用户查询、部门管理
- **消息发送**：机器人消息
- **特点**：稳定可靠、广泛使用、向后兼容

### Stream模式API (推荐)
- **事件推送**：实时接收钉钉消息和事件
- **长连接**：基于WebSocket的持久连接
- **高并发**：支持大量用户同时对话
- **低延迟**：消息处理延迟毫秒级

## 权限说明

### 企业内部应用
- **支持所有功能**：用户管理、消息、Stream模式、OA审批
- **权限配置**：在钉钉开发者后台申请相应权限
- **认证方式**：使用AppKey/AppSecret获取access_token
- **Stream配置**：需在开发者后台配置事件订阅和回调URL

### 第三方企业应用  
- **部分功能支持**：用户管理、消息
- **认证方式**：OAuth2.0授权流程
- **Stream模式**：不支持

### 第三方个人应用
- **功能受限**：仅支持基础用户查询
- **不支持**：消息发送、Stream模式

## 前置要求

### 传统API模式
- 已设置环境变量 `DINGTALK_APP_KEY` 和 `DINGTALK_APP_SECRET`
- 钉钉应用已创建并拥有相应 API 权限
- 对于企业内部应用，确保在钉钉管理后台已授权所需权限

### Stream模式（推荐）
- 企业内部应用（必须）
- 公网可访问的HTTPS服务器（用于事件回调）
- 钉钉开发者后台已配置Stream模式事件订阅
- Python 3.8+ 环境（用于运行Stream Bridge）

## 环境变量配置

```bash
# 传统API和Stream模式都需要
export DINGTALK_APP_KEY="<your-app-key>"
export DINGTALK_APP_SECRET="<your-app-secret>"

# Stream模式额外配置（可选）
export DINGTALK_STREAM_LOG_LEVEL="INFO"
export DINGTALK_SESSION_MEMORY_DIR="./memory"
```

## 使用示例

### 1. 传统API调用

#### 查询用户详情
```bash
npx ts-node scripts/get-user.ts "<userId>" [--debug]
```

#### 发送单聊消息
```bash
npx ts-node scripts/send-user-message.ts "<userId>" "<robotCode>" "<消息内容>" [--debug]
```

#### 获取部门用户列表
```bash
npx ts-node scripts/list-department-users.ts "<deptId>" [--debug]
```

#### 搜索用户
```bash
npx ts-node scripts/search-user.ts "<keyword>" [--debug]
```

### 2. Stream模式部署（推荐）

#### 启动Stream Bridge
```bash
# 创建虚拟环境
python3 -m venv dingtalk_venv
source dingtalk_venv/bin/activate
pip install dingtalk-stream

# 启动Stream服务
./start_dingtalk_stream.sh
```

#### 会话管理特性
- **私聊会话**：`dingtalk_private_{user_id}` - 每个用户独立会话
- **群聊会话**：`dingtalk_group_{group_id}_{user_id}` - 群聊中每个用户独立会话
- **记忆持久化**：会话记忆保存在 `memory/` 目录下
- **自动清理**：24小时无活动的会话自动清理

## 错误处理

所有脚本在错误时返回统一格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

常见错误码：
- `MISSING_CREDENTIALS` - 未设置环境变量
- `INVALID_ARGUMENTS` - 参数不足
- `AUTH_FAILED` - access_token 获取失败
- `PERMISSION_DENIED` - 权限不足
- `UNKNOWN_ERROR` - API 调用异常
- `STREAM_CONNECTION_FAILED` - Stream连接失败

## 最佳实践

1. **权限最小化**：只申请必要的API权限
2. **错误处理**：始终检查API响应的errcode
3. **调试模式**：使用`--debug`参数查看详细请求/响应
4. **批量操作**：对于大量数据，使用批量API接口
5. **Stream模式优先**：实时交互场景优先使用Stream模式
6. **会话隔离**：确保不同用户的对话上下文完全隔离
7. **频率控制**：遵守钉钉API调用频率限制

## 安全注意事项

- 不要在代码中硬编码AppKey/AppSecret
- 使用环境变量或安全的配置管理
- 敏感操作（如删除、修改）需要二次确认
- 遵循钉钉的安全最佳实践指南
- **Stream模式安全**：确保回调URL使用HTTPS，验证事件签名
- **数据隔离**：不同用户的会话数据完全隔离，符合企业安全要求

## 架构优势

### 多会话隔离架构
- **用户识别**：准确识别私聊和群聊中的不同用户
- **上下文保持**：每个会话保持完整的对话历史
- **个性化记忆**：支持用户偏好和历史记录的持久化
- **资源管理**：自动清理过期会话，避免资源泄露

### 回复路由优化
- **通道隔离**：钉钉回复只通过钉钉API，避免触发其他通道
- **性能优化**：异步处理，支持高并发
- **可靠性**：结果文件机制确保消息不丢失
- **错误恢复**：网络错误自动重试，保证消息送达

## 项目结构

```
dingtalk-api/
├── scripts/                    # 传统API脚本
│   ├── *.ts                   # 各类API调用脚本
├── stream/                    # Stream模式相关文件
│   ├── dingtalk_stream_bridge.py    # Stream Bridge主程序
│   ├── dingtalk_session_manager.py  # 会话管理器
│   ├── dingtalk_reply_tool.py       # 钉钉回复工具
│   └── *.sh                   # 启动/停止脚本
├── memory/                    # 会话记忆文件（运行时生成）
├── types/                     # TypeScript类型定义
├── SKILL.md                   # 技能文档
├── README.md                  # 详细使用说明
└── package.json               # 依赖配置
```