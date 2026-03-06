# 百度网盘 Skill

用于 OpenClaw 的百度网盘操作 Skill，支持文件列表查看、搜索、分享链接提取和转存等功能。

## 功能特性

- 📁 **文件列表** - 查看网盘指定目录的文件列表
- 🔍 **文件搜索** - 在网盘中搜索文件
- 🔗 **分享提取** - 提取百度网盘分享链接的文件列表
- 💾 **一键转存** - 将分享的文件转存到自己的网盘
- 📊 **文件信息** - 显示文件名、大小、修改时间等详细信息

## 安装

### 1. 安装依赖

```bash
pip install requests tqdm
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
```

## API 说明

### BaiduNetdiskAPI 类

#### list_files(path, order)
- **path**: 网盘路径，默认为根目录 "/"
- **order**: 排序方式，可选 "time"(时间)、"name"(名称)、"size"(大小)
- **返回**: 文件列表，包含文件名、路径、大小、是否为目录等信息

#### search_files(keyword, path)
- **keyword**: 搜索关键词
- **path**: 搜索路径，默认为根目录
- **返回**: 匹配的文件列表

#### extract_share(share_url, extract_code)
- **share_url**: 分享链接 URL
- **extract_code**: 提取码，可选
- **返回**: 分享中的文件列表、shareid、uk 等信息

#### transfer_share(share_url, extract_code, save_path)
- **share_url**: 分享链接 URL
- **extract_code**: 提取码，可选
- **save_path**: 保存到网盘的路径，默认为 "/我的资源"
- **返回**: 转存结果

## 注意事项

1. **登录状态**：BDUSS 和 STOKEN 有过期时间，如遇到权限错误请重新获取
2. **频率限制**：百度网盘 API 有访问频率限制，请合理使用
3. **文件大小**：转存大文件可能需要较长时间，请耐心等待
4. **隐私安全**：不要在公共场合或共享环境中使用，避免凭证泄露

## 常见问题

### Q: 提示 "缺少 BDUSS 或 STOKEN 配置"
A: 请确保 config.json 文件中正确配置了 bduss 和 stoken，或设置了环境变量 BAIDU_BDUSS 和 BAIDU_STOKEN

### Q: 提示 "API错误: -6"
A: 通常是登录凭证过期或无效，请重新获取 BDUSS 和 STOKEN

### Q: 转存失败
A: 可能是分享链接失效、提取码错误或网盘空间不足，请检查分享链接和网盘空间

## 技术说明

- 基于百度网盘开放平台 API (xpan)
- 使用 BDUSS + STOKEN 方式进行身份验证
- 支持 HTTP/HTTPS 代理（通过环境变量 HTTP_PROXY/HTTPS_PROXY 设置）

## 更新日志

### v1.0.0 (2025-02-16)
- 初始版本发布
- 支持文件列表、搜索、分享提取、转存功能

## License

MIT License

## 作者

MaxStorm Team
