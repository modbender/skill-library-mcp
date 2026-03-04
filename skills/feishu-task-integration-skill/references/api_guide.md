# 飞书任务API使用指南

## API基础信息

### 基础URL
```
https://open.feishu.cn/open-apis/task/v2/
```

### 认证方式
- **租户访问令牌**: `Bearer {tenant_access_token}`
- **获取方式**: 通过app_id和app_secret获取

## 核心API接口

### 1. 获取租户访问令牌
```http
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Content-Type: application/json

{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret"
}
```

### 2. 创建任务
```http
POST https://open.feishu.cn/open-apis/task/v2/tasks
Authorization: Bearer {tenant_access_token}
Content-Type: application/json

{
  "summary": "任务标题",
  "description": "任务描述",
  "due": {
    "timestamp": "1675454764000"
  },
  "members": [
    {
      "id": "ou_user_id",
      "type": "user",
      "role": "assignee"
    }
  ]
}
```

### 3. 获取任务详情
```http
GET https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}
Authorization: Bearer {tenant_access_token}
```

### 4. 更新任务状态
```http
PATCH https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}
Authorization: Bearer {tenant_access_token}
Content-Type: application/json

{
  "task": {
    "completed_at": "1675454764000"
  },
  "update_fields": ["completed_at"]
}
```

## 字段说明

### 任务字段
- **summary**: 任务标题（必填）
- **description**: 任务描述（可选）
- **due**: 截止时间对象
  - `timestamp`: 时间戳（毫秒）
  - `is_all_day`: 是否全天任务
- **members**: 成员列表
  - `id`: 用户open_id
  - `type`: 类型（user）
  - `role`: 角色（assignee/follower）

### 响应字段
- **task_id**: 任务ID（t开头）
- **guid**: 任务唯一标识（UUID格式）
- **status**: 任务状态（todo/done）
- **created_at**: 创建时间
- **updated_at**: 更新时间
- **completed_at**: 完成时间

## 错误处理

### 常见错误码
- **99991663**: 无效的访问令牌
- **1470400**: 参数验证失败
- **99992402**: 字段验证失败

### 错误响应格式
```json
{
  "code": 1470400,
  "msg": "Invalid Param",
  "error": {
    "log_id": "error_log_id",
    "field_violations": [
      {
        "field": "field_name",
        "description": "错误描述"
      }
    ]
  }
}
```

## 最佳实践

### 1. 令牌管理
- 缓存tenant_access_token，避免频繁获取
- token有效期2小时，需要定期刷新

### 2. 错误重试
- API调用失败时实现重试机制
- 指数退避策略避免频繁请求

### 3. 数据同步
- 本地和飞书任务状态保持一致
- 定期同步确保数据准确性

### 4. 用户ID格式
- 必须使用open_id格式（ou_开头）
- 避免使用其他ID格式

## 调试技巧

### 1. 日志记录
- 记录完整的API请求和响应
- 便于问题排查和分析

### 2. 参数验证
- 在发送请求前验证参数格式
- 避免不必要的API调用

### 3. 状态检查
- 定期检查任务状态同步情况
- 及时发现和修复数据不一致问题