# GitLab OAuth

通过 OAuth 授权访问私有 GitLab 仓库。

## 功能

- OAuth 授权认证
- 列出用户仓库
-

## 配置 读取仓库文件

### 1. 创建 GitLab OAuth 应用

访问 `http://gitlab.dmall.com/-/profile/applications` 创建应用：
- **Name**: OpenClaw
- **Redirect URI**: `http://localhost/callback`
- **Scopes**: `api`

### 2. 授权

```bash
node index.js auth <Application ID> <Secret>
```

然后用返回的 code 换取 token：
```bash
node index.js token <ID> <Secret> <code>
```

## 使用

```bash
# 列出仓库
node index.js list

# 读取文件
node index.js read <项目ID> <文件路径>
```
