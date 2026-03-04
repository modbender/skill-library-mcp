---
name: xiaomi-home-assistant-skill
description: 小米智能家居与 Home Assistant 集成技能，提供设备监控和即时智能建议。所有数据处理在内存中完成，不持久化敏感信息。支持小米灯具、加湿器、传感器、小爱音箱等设备的状态查询和异常告警。
---

# 小米 Home Assistant 集成技能

## 核心功能

本技能提供安全的智能家居集成，专注于实时设备监控和即时建议：

- **实时设备监控**: 查询小米设备当前状态
- **异常检测**: 识别设备异常状态并告警  
- **即时建议**: 基于当前状态提供操作建议
- **安全设计**: 所有数据处理在内存中完成，不持久化敏感信息

## 安全特性

### 隐私保护
- ❌ 不记录设备历史状态到磁盘
- ❌ 不创建持久化的家庭活动日志
- ✅ 所有数据处理在内存中完成
- ✅ 仅在需要时提供即时建议

### 最小权限
- 仅请求必要的 `read:files` 和 `network:http` 权限
- 移除了不必要的 `exec:commands` 和 `write:files` 权限

## 配置要求

### 必需配置文件
- `config.json`: Home Assistant 连接配置和自然语言命令映射
- `homeassistant_auth.json`: Home Assistant 认证令牌

### 配置步骤
1. 复制模板配置文件到工作目录
2. 替换占位符为实际的 Home Assistant URL 和长寿命访问令牌
3. 根据你的设备实体ID更新自然语言命令映射

## 功能模块

### 设备监控
- 灯具/开关状态查询
- 加湿器状态监控  
- 传感器数据查询（温湿度等）
- 宠物设备状态检查
- 小爱音箱语音控制

### 异常告警
- **宠物设备**: 滤芯寿命低、电池电量低告警
- **环境设备**: 湿度过高/过低告警
- **设备离线**: 设备连接状态异常告警

### 即时建议
- 基于当前设备状态提供操作建议
- 不依赖历史数据学习，确保隐私安全

## 使用场景

用户可以询问：
- "检查加湿器状态"
- "宠物饮水机需要维护吗？"  
- "卧室湿度正常吗？"
- "打开客厅灯"

## 文件结构

```
xiaomi-home-assistant-skill/
├── SKILL.md (本文件)
├── manifest.json
├── config.json (配置模板)
├── homeassistant_auth.json (认证模板)
├── README.md
└── handlers/
    ├── monitoring.py
    ├── natural_commands.py
    └── environment.py
```

## 依赖要求

- Home Assistant API 访问权限
- Python requests 库
- 网络连接（用于 API 调用）