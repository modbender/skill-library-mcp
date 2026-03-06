---
name: feishu-task-integration
description: 飞书任务对接集成技能，实现待办事项与飞书任务的双向同步。自动创建飞书任务、智能解析时间表达式、设置任务负责人，支持任务状态同步和完成管理。使用场景：需要将本地待办事项同步到飞书任务、设置任务截止时间、指派任务负责人、跟踪任务完成状态。
---

# 飞书任务对接集成

## 功能概述

飞书任务对接集成技能实现了本地待办事项系统与飞书任务平台的无缝对接，提供智能化的任务管理和同步功能。

## 核心能力

### 1. 自动任务创建
- 使用 `todo任务内容` 命令自动创建飞书任务
- 自动设置任务负责人和关注人
- 生成任务唯一标识符和访问链接

### 2. 智能时间解析
- 支持自然语言时间表达："今天"、"明天"、"本周"、"下周"、"本月"
- 支持具体时间："下午3点"、"晚上11点"
- 自动转换为标准时间戳格式

### 3. 任务负责人管理
- 自动指派任务给配置的用户
- 支持多人协作（关注人和负责人分离）
- 符合飞书任务API规范

### 4. 状态同步
- 本地完成任务自动同步到飞书
- 实时获取任务完成状态
- 双向数据一致性保证

## 快速开始

### 基本使用
```bash
# 创建任务（自动同步到飞书）
todo完成项目报告

# 查看任务列表
todo

# 完成任务（同步到飞书）
done0
```

### 时间表达式示例
```bash
# 今天截止
todo今天完成文档整理

# 明天截止  
todo明天提交周报

# 本周截止
todo本周完成项目总结

# 具体时间
todo今天晚上8点之前完成演示准备
```

## 配置说明

### 必要配置
在 `feishu_config.json` 中配置以下信息：

```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret", 
  "assignee_user_id": "ou_your_user_id"
}
```

### 获取配置信息
1. **App ID & Secret**: 在飞书开发者后台创建应用获取
2. **User ID**: 用户的open_id，格式为 `ou_xxxxxxxx`

## 技术实现

### 文件结构
- `todo_handler.py` - 主处理器，处理todo命令
- `feishu_task_integration.py` - 飞书任务API集成
- `feishu_config.json` - 配置文件

### API集成
- 使用飞书任务v2 API
- 正确的字段命名：`members`、`assignee_list`
- 符合飞书API规范和权限要求

## 故障排除

### 常见问题
1. **任务创建失败**: 检查API密钥和用户ID配置
2. **负责人设置无效**: 确认用户ID格式正确（ou_开头）
3. **时间解析错误**: 使用标准时间表达格式

### 调试信息
查看详细日志输出：
```bash
python3 todo_handler.py "todo测试任务" 2>&1
```

## 资源文件

### scripts/
包含核心功能脚本：
- `todo_handler.py` - 待办事项处理器
- `feishu_task_integration.py` - 飞书API集成

### references/
包含参考文档：
- `api_guide.md` - 飞书任务API使用指南
- `configuration.md` - 详细配置说明

### assets/
包含配置文件模板：
- `feishu_config_template.json` - 配置文件模板
