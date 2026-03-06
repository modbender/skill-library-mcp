---
name: 百度网盘 Skill
description: 用于 OpenClaw 的百度网盘操作 Skill，支持完整的文件管理功能：文件列表查看、搜索、分享链接提取、转存、目录创建、文件增删改查等。
---

# 百度网盘 Skill

## 简介

用于 OpenClaw 的百度网盘操作 Skill，支持完整的文件管理功能：文件列表查看、搜索、分享链接提取、转存、目录创建、文件增删改查等。

## ⚠️ 安全警告

**重要提示**：
- 本 Skill 需要您的百度网盘登录凭证（BDUSS 和 STOKEN），这些凭证具有完全访问您网盘账户的权限
- 请仅在受信任的环境中使用，不要在公共设备或共享环境中配置
- 建议创建专门的测试账号使用本 Skill，避免使用主账号
- 凭证存储在本地 `config.json` 文件中，请确保文件权限安全
- **删除操作不可恢复**，请谨慎使用

## 功能特性

### 查询操作（稳定）
- 📁 **文件列表** - 查看网盘指定目录的文件列表
- 🔍 **文件搜索** - 在网盘中搜索文件
- 🔗 **分享提取** - 提取百度网盘分享链接的文件列表

### 文件操作（稳定）
- 💾 **一键转存** - 将分享的文件转存到自己的网盘
- 📂 **创建目录** - 在网盘中创建新目录

### 文件管理（需要 bdstoken）
- ✏️ **重命名** - 重命名文件或目录
- 🔄 **移动** - 移动文件到不同目录
- 🗑️ **删除** - 删除文件或目录（谨慎使用）

## 技术说明

### API 实现
- **查询和转存功能**：使用百度网盘 REST API（`rest/2.0/xpan`）
- **文件管理功能**：使用百度网盘 filemanager API（`/api/filemanager`）
- **bdstoken**：文件管理操作需要额外的 bdstoken，Skill 会自动获取

### 认证流程
1. 使用 BDUSS 和 STOKEN 进行身份认证
2. 自动获取 bdstoken 用于文件管理操作
3. 所有 API 调用使用 HTTPS 加密

## 安装

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 Skill

在 `config.json` 中配置百度网盘登录凭证：

```json
{
  "bduss": "your_bduss_here",
  "stoken": "your_stoken_here",
  "default_save_path": "~/Downloads/BaiduNetdisk"
}
```

**或者使用环境变量**（更安全）：
```bash
export BAIDU_BDUSS="your_bduss_here"
export BAIDU_STOKEN="your_stoken_here"
```

### 3. 获取 BDUSS 和 STOKEN

1. 登录百度网盘网页版 (https://pan.baidu.com)
2. 按 F12 打开开发者工具
3. 切换到 Application/应用 标签
4. 找到 Cookies -> https://pan.baidu.com
5. 复制 `BDUSS` 和 `STOKEN` 的值

**注意**：BDUSS 和 STOKEN 是敏感信息，请妥善保管，不要泄露给他人。

## 使用方法

### 列出文件

```bash
# 列出根目录文件
python scripts/main.py list

# 列出指定目录
python scripts/main.py list path=/我的资源

# 按文件名排序
python scripts/main.py list path=/我的资源 order=name
```

### 搜索文件

```bash
# 搜索文件名包含"电影"的文件
python scripts/main.py search keyword=电影

# 在指定路径下搜索
python scripts/main.py search keyword=电影 path=/我的资源
```

### 提取分享链接

```bash
# 提取无密码的分享链接
python scripts/main.py extract share_url=https://pan.baidu.com/s/1xxxxx

# 提取有密码的分享链接
python scripts/main.py extract share_url=https://pan.baidu.com/s/1xxxxx extract_code=abcd
```

### 转存分享文件

```bash
# 转存到默认路径
python scripts/main.py transfer share_url=https://pan.baidu.com/s/1xxxxx

# 转存到指定路径
python scripts/main.py transfer share_url=https://pan.baidu.com/s/1xxxxx save_path=/我的资源/电影

# 带提取码转存
python scripts/main.py transfer share_url=https://pan.baidu.com/s/1xxxxx extract_code=abcd save_path=/我的资源
```

### 创建目录

```bash
# 创建新目录
python scripts/main.py mkdir path=/新目录名
```

### 文件管理

```bash
# 重命名文件/目录
python scripts/main.py rename path=/原文件名 new_name=新文件名

# 移动文件
python scripts/main.py move path=/原路径 dest=/目标路径

# 删除文件/目录（不可恢复，请谨慎使用）
python scripts/main.py delete path=/要删除的路径
```

## 在 OpenClaw 中使用

### 配置 Agent 使用该 Skill

在 Agent 配置中添加：

```json
{
  "skills": ["baidunetdisk"]
}
```

### 使用示例

```bash
# 让 Agent 列出网盘文件
openclaw agent --message "查看我的百度网盘根目录有什么文件"

# 搜索文件
openclaw agent --message "在我的百度网盘搜索所有PDF文件"

# 转存分享链接
openclaw agent --message "把这个百度网盘分享链接转存到我的网盘: https://pan.baidu.com/s/1xxxxx 提取码: abcd"

# 创建目录
openclaw agent --message "在百度网盘创建一个名为'工作文档'的目录"

# 重命名文件
openclaw agent --message "把百度网盘里的'旧文件名.txt'重命名为'新文件名.txt'"

# 删除文件（谨慎）
openclaw agent --message "删除百度网盘里的'/测试/临时文件.txt'"
```

## 注意事项

1. **登录状态**：BDUSS 和 STOKEN 有过期时间，如遇到权限错误请重新获取
2. **频率限制**：百度网盘 API 有访问频率限制，请合理使用
3. **隐私安全**：不要在公共场合或共享环境中使用，避免凭证泄露
4. **bdstoken**：文件管理操作（重命名/移动/删除）需要 bdstoken，Skill 会自动获取
5. **数据安全**：删除操作不可恢复，请谨慎使用

## 故障排除

### 错误码 -6
表示登录凭证无效或过期，请重新获取 BDUSS 和 STOKEN

### 错误码 2
参数错误或权限不足，请检查：
- 文件路径是否正确
- 是否有操作该文件的权限
- bdstoken 是否成功获取

### 错误码 9019
API 调用受限，请检查网络连接或稍后再试

### 无法获取 bdstoken
- 检查 BDUSS 和 STOKEN 是否有效
- 尝试重新登录百度网盘获取新的凭证
- 检查网络连接是否正常

## 版本信息

- **版本**: 1.0.2
- **作者**: MaxStorm Team
- **许可证**: MIT
- **源码**: https://github.com/maxstorm/baidunetdisk-skill
