# Qiniu KODO 技能

七牛云对象存储技能 - 通过 MCP 工具 + Node.js SDK + qshell 管理七牛云存储

## 🚀 快速开始

### 1. 检查环境

```bash
bash scripts/setup.sh --check-only
```

### 2. 配置凭证

如果环境检查未通过，运行：

```bash
bash scripts/setup.sh \
  --access-key "<你的AccessKey>" \
  --secret-key "<你的SecretKey>" \
  --region "z0" \
  --bucket "<你的存储桶名称>" \
  --domain "http://你的域名.com"
```

**获取凭证：**
- 密钥管理：https://portal.qiniu.com/user/key
- 存储桶列表：https://portal.qiniu.com/kodo/bucket

### 3. 开始使用

**命令行：**

```bash
# 上传文件
node scripts/qiniu_node.mjs upload --local /path/to/file.txt --key uploads/file.txt

# 下载文件
node scripts/qiniu_node.mjs download --key uploads/file.txt --local /path/to/file.txt

# 列出文件
node scripts/qiniu_node.mjs list --prefix uploads/

# 获取 URL
node scripts/qiniu_node.mjs url --key uploads/file.txt
```

**在 OpenClaw 中：**

```
帮我上传 /backups/daily.tar.gz 到七牛云
```

## 📚 完整文档

查看 [SKILL.md](./SKILL.md) 获取完整文档。

## 🔗 相关链接

- [七牛云官网](https://www.qiniu.com/)
- [七牛云 Node.js SDK](https://developer.qiniu.com/kodo/sdk/1289/nodejs)
- [qiniu-mcp-server](https://github.com/qiniu/qiniu-mcp-server)
- [qshell 工具](https://developer.qiniu.com/kodo/tools/1302/qshell)
