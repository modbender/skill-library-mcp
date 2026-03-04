# GitLab Private

通过 OAuth 授权访问私有 GitLab 仓库，支持在群聊中使用。

## 功能

- OAuth 授权认证
- 列出用户仓库
- 读取仓库文件
- 查看最后一次合并信息
- 搜索项目

## 群聊使用流程

当用户在群里 @机器人 + GitLab 仓库链接时：

### 1. 自动回复授权链接

```
抱歉，GitLab 仓库位于内网，需要授权才能访问。

请按以下步骤授权：
1. 打开浏览器访问：
http://gitlab.dmall.com/oauth/authorize?client_id=ef176799ed20da49918699d09d973db2b8e16a66e1d5cbbb93ac1688c437cf34&redirect_uri=http://localhost/callback&response_type=code&scope=api

2. 授权后浏览器跳转到 http://localhost/callback?code=xxx

3. 把 code 发给我
```

### 2. 用户授权后

用户把 code 发给机器人，机器人换取 token 并执行任务。

## 本地命令行使用

### 1. 配置 OAuth 应用

在 GitLab 创建 OAuth 应用，获取 Application ID 和 Secret。

### 2. 授权流程

```bash
# 生成授权链接
node index.js auth <Application ID> <Secret>

# 交换 Token
node index.js token <ID> <Secret> <code>
```

### 3. 使用命令

```bash
# 列出仓库
node index.js list

# 搜索项目
node index.js project <关键词>

# 读取文件
node index.js read <项目ID> <文件路径>

# 查看最后一次合并
node index.js merge <项目ID> [分支名]
```

## 配置

配置文件: `config.json`

```json
{
  "gitlab_url": "http://gitlab.dmall.com",
  "access_token": ""
}
```

## 环境变量

- `GITLAB_URL`: GitLab 地址
- `GITLAB_TOKEN`: Access Token
