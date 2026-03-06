---
name: feishu-bitable
description: 飞书多维表格(Bitable)API技能。用于创建、读取、更新和删除飞书多维表格的数据表、记录和字段。
metadata: {"clawdbot":{"emoji":"📊","requires":{"env":["FEISHU_APP_ID","FEISHU_APP_SECRET"]},"primaryEnv":"FEISHU_APP_ID"}}
---

# 飞书多维表格(Bitable)技能

用于操作飞书多维表格的完整技能，支持数据表、记录和字段的CRUD操作。

## 功能特性

- ✅ 数据表管理（创建、列表、获取、删除）
- ✅ 记录管理（创建、读取、更新、删除、批量操作）
- ✅ 字段管理（创建、列表、更新）
- ✅ 视图管理（列表、获取）
- ✅ 应用管理（获取应用信息）

## 环境变量配置

```bash
# 飞书应用ID
export FEISHU_APP_ID=cli_xxxxxx

# 飞书应用密钥（或密钥文件路径）
export FEISHU_APP_SECRET=your_app_secret
# 或
export FEISHU_APP_SECRET_PATH=~/.clawdbot/secrets/feishu_app_secret
```

## 快速开始

### 1. 安装依赖
```bash
cd skills/feishu-bitable
npm install
```

### 2. 设置环境变量
```bash
export FEISHU_APP_ID=cli_xxxxxx
export FEISHU_APP_SECRET=your_app_secret
```

### 3. 使用CLI工具
```bash
# 获取帮助
node bitable-cli.js --help

# 列出所有数据表
node bitable-cli.js list-tables --app-token basxxxxxx

# 创建新记录
node bitable-cli.js create-record --app-token basxxxxxx --table-id tblxxxxxx --data '{"字段1": "值1", "字段2": "值2"}'

# 查询记录
node bitable-cli.js list-records --app-token basxxxxxx --table-id tblxxxxxx
```

## API端点

### 数据表相关
- `GET /bitable/v1/apps/{app_token}/tables` - 获取数据表列表
- `POST /bitable/v1/apps/{app_token}/tables` - 创建数据表
- `GET /bitable/v1/apps/{app_token}/tables/{table_id}` - 获取数据表详情
- `DELETE /bitable/v1/apps/{app_token}/tables/{table_id}` - 删除数据表

### 记录相关
- `POST /bitable/v1/apps/{app_token}/tables/{table_id}/records` - 新增记录
- `GET /bitable/v1/apps/{app_token}/tables/{table_id}/records` - 获取记录列表
- `PUT /bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}` - 更新记录
- `DELETE /bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}` - 删除记录
- `POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create` - 批量新增记录
- `POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update` - 批量更新记录
- `POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete` - 批量删除记录

### 字段相关
- `GET /bitable/v1/apps/{app_token}/tables/{table_id}/fields` - 获取字段列表
- `POST /bitable/v1/apps/{app_token}/tables/{table_id}/fields` - 创建字段
- `PUT /bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}` - 更新字段

### 视图相关
- `GET /bitable/v1/apps/{app_token}/tables/{table_id}/views` - 获取视图列表
- `GET /bitable/v1/apps/{app_token}/tables/{table_id}/views/{view_id}` - 获取视图详情

## 使用示例

### 1. 创建数据表
```bash
node bitable-cli.js create-table \
  --app-token basxxxxxx \
  --name "任务管理" \
  --fields '[{"field_name": "任务名称", "type": "text"}, {"field_name": "状态", "type": "select", "property": {"options": [{"name": "待办"}, {"name": "进行中"}, {"name": "已完成"}]}}]'
```

### 2. 添加记录
```bash
node bitable-cli.js create-record \
  --app-token basxxxxxx \
  --table-id tblxxxxxx \
  --data '{"任务名称": "完成API开发", "状态": "进行中", "优先级": "高", "截止日期": "2024-12-31"}'
```

### 3. 查询记录
```bash
node bitable-cli.js list-records \
  --app-token basxxxxxx \
  --table-id tblxxxxxx \
  --filter '{"conjunction": "and", "conditions": [{"field_name": "状态", "operator": "is", "value": ["进行中"]}]}' \
  --sort '["-创建时间"]' \
  --page-size 50
```

### 4. 批量操作
```bash
node bitable-cli.js batch-create \
  --app-token basxxxxxx \
  --table-id tblxxxxxx \
  --data-file records.json
```

## 字段类型支持

飞书多维表格支持以下字段类型：
- `text` - 文本
- `number` - 数字
- `single_select` - 单选
- `multi_select` - 多选
- `date` - 日期
- `person` - 人员
- `checkbox` - 复选框
- `url` - 链接
- `phone` - 电话
- `email` - 邮箱
- `attachment` - 附件
- `formula` - 公式
- `created_time` - 创建时间
- `modified_time` - 修改时间
- `created_by` - 创建人
- `modified_by` - 修改人

## 错误处理

技能包含完整的错误处理机制：
- 网络错误重试
- 权限验证
- 参数验证
- 速率限制处理

## 注意事项

1. **权限要求**：应用需要具备`bitable:record:readonly`和`bitable:record:write`权限
2. **速率限制**：飞书API有速率限制，建议添加适当的延迟
3. **数据大小**：单次请求记录数量建议不超过100条
4. **字段名称**：字段名称在表中必须唯一

## Clawdbot集成

### 在Clawdbot中使用此技能

1. **确保技能已安装**：技能应该位于 `skills/feishu-bitable` 目录
2. **设置环境变量**：在Clawdbot配置中设置飞书应用凭证
3. **在对话中调用**：Clawdbot可以调用此技能来操作飞书多维表格

### 示例对话

**用户**: "帮我在飞书多维表格中添加一个任务"
**Clawdbot**: 
```bash
# 使用技能添加任务
node skills/feishu-bitable/bin/cli.js create-record \
  --app-token basxxxxxx \
  --table-id tblxxxxxx \
  --data '{"任务名称": "新任务", "状态": "待办", "优先级": "中"}'
```

### 自动化工作流

你可以创建自动化工作流，例如：
- 每天同步任务状态
- 从其他系统导入数据到飞书多维表格
- 根据条件自动更新记录
- 生成报表并发送到飞书群聊

## 开发指南

如需扩展功能，请参考：
- `src/api.js` - API客户端
- `src/cli.js` - 命令行接口
- `src/utils.js` - 工具函数

### 添加新的API端点

1. 在 `src/api.js` 的 `FeishuBitableAPI` 类中添加新方法
2. 在 `bin/cli.js` 中添加对应的命令
3. 更新文档

### 错误处理最佳实践

- 使用 `try-catch` 包装所有API调用
- 提供有意义的错误消息
- 实现重试逻辑处理网络错误
- 验证输入参数