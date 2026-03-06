# 七牛云 KODO 技能 - 使用示例

本文档包含七牛云 KODO 技能的各种使用示例。

---

## 📤 示例1：上传文件

### 在 OpenClaw 中

**用户说：**
```
帮我上传 /backups/daily-20260301.tar.gz 到七牛云
```

**AI 执行：**
```
优先级 1：尝试使用 qiniu-mcp MCP 工具
优先级 2：如果 MCP 不可用，使用 Python SDK
优先级 3：如果 SDK 也不可用，使用 qshell
```

**返回：**
```
✅ 上传成功！

文件：daily-20260301.tar.gz
大小：15.2 MB
URL：http://your-domain.com/backups/daily-20260301.tar.gz
```

### 命令行方式

```bash
node scripts/qiniu_node.mjs upload \
  --local /backups/daily-20260301.tar.gz \
  --key backups/daily-20260301.tar.gz
```

---

## 📋 示例2：列出文件

### 在 OpenClaw 中

**用户说：**
```
列出七牛云 backups 目录下的所有文件
```

**返回：**
```
📋 共找到 15 个文件：

backups/backup-20260301.tar.gz  - 15.2 MB  - 2026-03-01 20:00
backups/backup-20260228.tar.gz  - 14.8 MB  - 2026-02-28 20:00
backups/backup-20260227.tar.gz  - 16.1 MB  - 2026-02-27 20:00
...
```

### 命令行方式

```bash
# 列出所有文件
node scripts/qiniu_node.mjs list

# 列出指定前缀的文件
node scripts/qiniu_node.mjs list --prefix backups/ --limit 50

# JSON 格式输出
node scripts/qiniu_node.mjs list --prefix backups/ --format json
```

---

## 🔗 示例3：获取文件 URL

### 在 OpenClaw 中

**用户说：**
```
给我 images/photo.jpg 的访问链接，1小时有效
```

**返回：**
```
🔗 临时访问链接（1小时有效）：

http://your-domain.com/images/photo.jpg?e=1583097600&token=...
```

### 命令行方式

```bash
# 公开空间 URL
node scripts/qiniu_node.mjs url --key images/photo.jpg

# 私有空间 URL（1小时有效）
node scripts/qiniu_node.mjs url --key documents/report.pdf --private --expires 3600
```

---

## 🗑️ 示例4：删除文件

### 在 OpenClaw 中

**用户说：**
```
删除七牛云上的 old-backup.tar.gz
```

**AI 执行：**
```
1. 先确认：是否真的要删除？
2. 用户确认后执行删除
```

**返回：**
```
✅ 删除成功！

文件：old-backup.tar.gz
```

### 命令行方式

```bash
# 删除单个文件（需要确认）
node scripts/qiniu_node.mjs delete --key backups/old-backup.tar.gz

# 强制删除（不需要确认）
node scripts/qiniu_node.mjs delete --key backups/old-backup.tar.gz --force

# 批量删除
cat > delete-list.txt << EOF
backups/backup-20260101.tar.gz
backups/backup-20260102.tar.gz
EOF

node scripts/qiniu_node.mjs batch-delete --file delete-list.txt
```

---

## 📊 示例5：获取文件信息

### 在 OpenClaw 中

**用户说：**
```
查看 documents/report.pdf 的详细信息
```

**返回：**
```
📊 文件信息：

文件名：documents/report.pdf
大小：2.5 MB
类型：application/pdf
Hash：FhGxK...（文件哈希值）
修改时间：2026-03-01 15:30:00
```

### 命令行方式

```bash
node scripts/qiniu_node.mjs stat --key documents/report.pdf
```

---

## 📥 示例6：下载文件

### 在 OpenClaw 中

**用户说：**
```
从七牛云下载 documents/report.pdf 到本地
```

**返回：**
```
✅ 下载成功！

文件：documents/report.pdf
大小：2.5 MB
保存到：/downloads/report.pdf
```

### 命令行方式

```bash
node scripts/qiniu_node.mjs download \
  --key documents/report.pdf \
  --local /downloads/report.pdf
```

---

## 🔄 示例7：移动和复制文件

### 在 OpenClaw 中

**用户说：**
```
把 temp/file.txt 移动到 archive/file.txt
```

**返回：**
```
✅ 文件已移动

原路径：temp/file.txt
新路径：archive/file.txt
```

### 命令行方式（需要扩展）

```bash
# 移动文件（需要扩展 Python 脚本）
# 复制文件（需要扩展 Python 脚本）
```

---

## 🖼️ 示例8：图片处理（需要 MCP）

### 在 OpenClaw 中

**用户说：**
```
把 images/photo.jpg 缩小到 800x600，加水印
```

**AI 执行：**
```
使用 qiniu-mcp MCP 工具进行图片处理
（需要 MCP 工具支持）
```

**返回：**
```
✅ 图片处理完成！

原图：http://your-domain.com/images/photo.jpg
处理后：http://your-domain.com/images/photo.jpg?imageView2/1/w/800/h/600|watermark/...
```

---

## 🤖 示例9：自动化备份脚本

### 完整脚本

```bash
#!/bin/bash

# 每日备份脚本
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d)
BACKUP_FILE="backup-${DATE}.tar.gz"

# 1. 创建备份
echo "📦 创建备份..."
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" /data

# 2. 上传到七牛云
echo "📤 上传到七牛云..."
cd /home/node/.openclaw/workspace/skills/qiniu-kodo
node scripts/qiniu_node.mjs upload \
  --local "${BACKUP_DIR}/${BACKUP_FILE}" \
  --key "backups/${BACKUP_FILE}"

# 3. 清理本地旧备份（保留7天）
echo "🗑️  清理旧备份..."
find ${BACKUP_DIR} -name "backup-*.tar.gz" -mtime +7 -delete

# 4. 清理云端旧备份（保留30天）
echo "🗑️  清理云端旧备份..."
python -c "
from scripts.qiniu_python import QiniuKodo
from datetime import datetime, timedelta

kodo = QiniuKodo()
cutoff = datetime.now() - timedelta(days=30)

for file in kodo.list_files(prefix='backups/'):
    if datetime.fromtimestamp(file['mtime']) < cutoff:
        kodo.delete(file['key'])
        print(f'已删除: {file[\"key\"]}')
"

echo "✅ 备份完成！"
```

---

## 📝 示例10：批量操作

### 批量上传图片

```python
from scripts.qiniu_python import QiniuKodo
import os

kodo = QiniuKodo()

image_dir = "/path/to/images"
uploaded = 0

for filename in os.listdir(image_dir):
    if filename.endswith(('.jpg', '.png', '.gif')):
        local_path = os.path.join(image_dir, filename)
        key = f"images/{filename}"

        try:
            result = kodo.upload(local_path, key)
            print(f"✅ {filename} -> {result['url']}")
            uploaded += 1
        except Exception as e:
            print(f"❌ {filename} 上传失败: {e}")

print(f"\n✅ 共上传 {uploaded} 个文件")
```

---

## 🔧 高级用法

### 使用配置文件

```python
from scripts.qiniu_python import QiniuKodo

# 使用自定义配置文件
kodo = QiniuKodo(config_path='/path/to/custom-config.json')

# 上传文件
result = kodo.upload('/path/to/file.txt', 'uploads/file.txt')
```

### 错误处理

```python
from scripts.qiniu_python import QiniuKodo

kodo = QiniuKodo()

try:
    result = kodo.upload('/path/to/file.txt', 'uploads/file.txt')
    print(f"上传成功: {result['url']}")
except FileNotFoundError as e:
    print(f"文件不存在: {e}")
except Exception as e:
    print(f"上传失败: {e}")
```

---

## 🎯 更多示例

查看 [SKILL.md](../SKILL.md) 获取更多详细信息和 API 文档。
