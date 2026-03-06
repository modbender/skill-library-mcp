# 飞书任务对接配置指南

## 配置文件结构

### feishu_config.json
```json
{
  "app_id": "cli_your_app_id",
  "app_secret": "your_app_secret",
  "assignee_user_id": "ou_your_user_id"
}
```

## 配置获取步骤

### 1. 获取App ID和App Secret

#### 步骤1: 登录飞书开发者后台
- 访问: https://open.feishu.cn/app
- 使用企业管理员账号登录

#### 步骤2: 创建或选择应用
- 点击"创建应用"或选择现有应用
- 填写应用基本信息

#### 步骤3: 获取应用凭证
- 在应用详情页面找到"应用凭证"
- 复制App ID和App Secret

#### 步骤4: 配置应用权限
- 进入"权限管理"页面
- 添加以下权限:
  - `task:task` (任务读写权限)
  - `task:task.assignee` (任务负责人管理)
  - `task:task.follower` (任务关注人管理)

### 2. 获取用户Open ID

#### 方法1: 通过飞书API获取
```bash
# 获取用户信息API
GET https://open.feishu.cn/open-apis/contact/v3/users/{user_id}
Authorization: Bearer {tenant_access_token}
```

#### 方法2: 通过飞书客户端查看
- 在飞书客户端右键点击用户头像
- 选择"复制用户ID"
- 格式应为: `ou_xxxxxxxxxxxxxxxx`

#### 方法3: 通过管理后台查看
- 登录企业管理后台
- 进入"组织架构"页面
- 查找对应用户的open_id

## 配置验证

### 1. 验证App凭证
```python
from feishu_task_integration import FeishuTaskManager

manager = FeishuTaskManager()
success = manager.get_tenant_access_token()
print(f"认证结果: {success}")
```

### 2. 验证用户ID
```python
# 创建测试任务验证用户ID
task_id = manager.create_task(
    title="测试任务",
    description="验证用户ID配置"
)
print(f"任务创建结果: {task_id}")
```

## 环境变量配置（可选）

### 方法1: 环境变量
```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_ASSIGNEE_USER_ID="ou_your_user_id"
```

### 方法2: 配置文件优先级
1. 环境变量（最高优先级）
2. feishu_config.json文件
3. 代码中硬编码值（最低优先级）

## 安全建议

### 1. 保护敏感信息
- 不要将配置文件提交到版本控制系统
- 使用.gitignore忽略配置文件
- 定期轮换App Secret

### 2. 最小权限原则
- 只授予必要的API权限
- 定期审查权限使用情况
- 及时撤销不需要的权限

### 3. 配置备份
- 备份配置文件到安全位置
- 记录配置变更历史
- 准备应急恢复方案

## 故障排除

### 问题1: 认证失败
```
错误: Invalid access token
解决方案:
1. 检查App ID和App Secret是否正确
2. 确认应用权限配置完整
3. 重新获取tenant_access_token
```

### 问题2: 用户ID无效
```
错误: member id is not a valid open id
解决方案:
1. 确认用户ID格式正确（ou_开头）
2. 验证用户是否存在且活跃
3. 检查应用是否有访问该用户的权限
```

### 问题3: 权限不足
```
错误: Insufficient permissions
解决方案:
1. 检查应用权限配置
2. 联系管理员授予必要权限
3. 重新安装应用授权
```

## 配置示例

### 基础配置
```json
{
  "app_id": "cli_a1b2c3d4e5f6g7h8",
  "app_secret": "abcdef1234567890abcdef1234567890",
  "assignee_user_id": "ou_1234567890abcdef"
}
```

### 多用户配置（高级）
```json
{
  "app_id": "cli_a1b2c3d4e5f6g7h8",
  "app_secret": "abcdef1234567890abcdef1234567890",
  "assignee_user_id": "ou_1234567890abcdef",
  "follower_user_ids": [
    "ou_abcdef1234567890",
    "ou_fedcba0987654321"
  ]
}
```

## 版本兼容性

### API版本
- 当前版本: v2
- 兼容性: 向后兼容v1主要功能
- 升级计划: 关注官方文档更新

### SDK版本
- 推荐使用最新版本
- 定期检查更新
- 测试环境验证后再上线