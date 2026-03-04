# 云效项目协作工具（Projex）

通过云效 API 管理项目和工作项（需求、缺陷、任务等）。

## 必需的环境变量

使用此技能前，需要配置以下环境变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `YUNXIAO_ACCESS_TOKEN` | 云效个人访问令牌 | `pt-xxxxx` |
| `YUNXIAO_ORGANIZATION_ID` | 云效组织ID | `YOUR_ORGANIZATION_ID_HERE` |

### 获取 Access Token

1. 登录云效：https://devops.aliyun.com
2. 点击头像 → 个人设置 → 个人访问令牌
3. 创建新令牌，选择所需权限（项目管理、工作项管理等）
4. 复制生成的令牌

## 安装方法

首次使用需要安装依赖：

```bash
cd skills/yunxiao-projex
npm install
```

## 配置

### 创建 .env 文件

在技能目录下创建 `.env` 文件：

```bash
# 云效 API 配置
YUNXIAO_ACCESS_TOKEN=你的访问令牌
YUNXIAO_ORGANIZATION_ID=你的组织ID
```

## 使用方法

### 基础命令

```bash
# 列出所有项目
node yunxiao-projex.js list-projects

# 获取当前用户信息
node yunxiao-projex.js current-user

# 搜索工作项
node yunxiao-projex.js search-workitems --spaceId PROJECT_ID --category Req

# 获取工作项详情
node yunxiao-projex.js get-workitem --workitemId WORKITEM_ID

# 创建工作项
node yunxiao-projex.js create-workitem --spaceId PROJECT_ID --category Req --subject "需求标题"

# 更新工作项
node yunxiao-projex.js update-workitem --workitemId WORKITEM_ID --subject "新标题"

# 添加关联工作项
node yunxiao-projex.js add-relation --workitemId WORKITEM_ID --relatedWorkitemId RELATED_ID --relationType ASSOCIATED
```

### 工作项类型 (Category)
- `Req` - 需求
- `Bug` - 缺陷
- `Task` - 任务
- `Topic` - 话题

### 关联类型 (relationType)
- `PARENT` - 父工作项
- `SUB` - 子工作项
- `ASSOCIATED` - 关联项
- `DEPEND_ON` - 依赖项
- `DEPENDED_BY` - 支撑项

## 智能功能

### 自动用户识别

添加参与者时，支持使用姓名自动转换为用户ID。系统会自动收集工作项中的用户信息到缓存。

```bash
# 使用姓名添加参与者（自动转换为ID）
node yunxiao-projex.js update-workitem --workitemId WORKITEM_ID --participants "USER_NAME_1,USER_NAME_2"
```

## 安全警告

### ⚠️ 重要提醒

1. **访问令牌**：建议使用最小权限的云效访问令牌，定期轮换
2. **敏感文件**：
   - `.env` 包含敏感凭证，请勿提交到版本控制
   - `.user-cache.json` 包含用户名和用户ID，视为敏感数据
3. **使用 yx.sh**：脚本会从 `.env` 读取变量，请确保 `.env` 只包含必要的凭证

### 文件清理

使用后可以删除缓存文件：

```bash
rm .user-cache.json
```

## 常见操作示例

### 查看YOUR_PROJECT_NAME项目中的需求

```bash
node yunxiao-projex.js search-workitems \
  --spaceId YOUR_PROJECT_ID_HERE \
  --category Req
```

### 查看指定需求的详情

```bash
node yunxiao-projex.js get-workitem --workitemId "xxx"
```

### 创建新需求并指派

```bash
node yunxiao-projex.js create-workitem \
  --spaceId YOUR_PROJECT_ID_HERE \
  --category Req \
  --subject "新需求标题" \
  --assignedTo "USER_ID"
```

## 相关链接
- 云效控制台: https://devops.aliyun.com
- 云效 API 文档: https://help.aliyun.com/zh/yunxiao/developer-reference/api-devops-2021-06-25-overview
- ClawHub: https://clawhub.ai
