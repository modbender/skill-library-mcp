# 小红书内容发布与校验

本文档说明如何使用 `xhs-kit` 进行内容发布前的校验（debug）和正式发布。

## 安装

```
# 使用 pip 安装
pip install -U xhs-kit

# 安装 Playwright 浏览器（必需）
playwright install chromium
```

## Debug 模式：发布前校验

在正式发布前，使用 `debug-publish` 命令验证内容是否符合小红书规范，**无需登录，不会实际发布**。

### 命令格式

```bash
xhs-kit debug-publish \
  --title "标题" \
  --content "正文内容" \
  --image /path/to/image1.png \
  --image /path/to/image2.png \
  --tag "标签1" \
  --tag "标签2" \
  [--verbose]
```

### 参数说明

| 参数 | 简写 | 必填 | 说明 |
| --- | --- | --- | --- |
| `--title` | `-t` | ✅ | 文章标题（最多 20 字符） |
| `--content` | `-c` | ✅ | 正文内容（建议 900 字符内） |
| `--image` | `-i` | ✅ | 图片路径（可多次指定，最多 16 张） |
| `--tag` | 无 | ❌ | 话题标签（可多次指定） |
| `--verbose` | `-v` | ❌ | 显示详细信息（错误、警告、图片详情） |

### 输出模式

**简洁模式（默认）：**
```
✅ 验证通过
```
或
```
❌ 验证失败
```

**Verbose 模式（`--verbose`）：**
```
✅ 验证通过

详细信息:
{
  "title_length": 8,
  "content_length": 120,
  "total_images": 2,
  "valid_images": 2,
  "image_details": [
    {
      "index": 1,
      "path": "/path/to/image1.png",
      "exists": true,
      "format_valid": true,
      "format": ".png",
      "size_mb": 2.5,
      "width": 1024,
      "height": 1024,
      "mode": "RGB"
    }
  ]
}
```

### 校验规则

**必须通过的验证（errors）：**
- ❌ 标题为空
- ❌ 标题长度超过 20 字符
- ❌ 图片文件不存在
- ❌ 图片格式不支持（仅支持 jpg/png/webp/heic）
- ❌ 图片数量超过 16 张

**建议性警告（warnings）：**
- ⚠️ 标题接近长度限制（17-20 字符）
- ⚠️ 正文为空
- ⚠️ 正文过长（超过 1000 字符）
- ⚠️ 正文接近上限（900-1000 字符）
- ⚠️ 图片分辨率较低（小于 480x480）
- ⚠️ 图片文件较大（超过 20MB）
- ⚠️ 标签数量过多（超过 10 个）
- ⚠️ 单个标签过长（超过 20 字符）

### 在自动化流程中使用

```bash
# 在脚本中调用 debug-publish
xhs-kit debug-publish \
  --title "$TITLE" \
  --content "$CONTENT" \
  --image "$IMAGE_PATH" \
  --verbose > validation.log

# 检查退出码
if [ $? -eq 0 ]; then
  echo "验证通过，可以继续发布"
else
  echo "验证失败，请检查 validation.log"
  exit 1
fi
```

## 正式发布

**⚠️ 重要：正式发布需要先登录小红书账号。**

### 登录步骤

1. 检查登录状态：
```bash
xhs-kit status
```

2. 如果未登录，执行登录（推荐终端二维码方式）：
```bash
xhs-kit login-qrcode --terminal
```

或保存二维码图片：
```bash
xhs-kit login-qrcode --save /tmp/qrcode.png
```

3. 扫码后按回车完成登录

### 发布图文内容

```bash
xhs-kit publish \
  --title "标题" \
  --content "正文内容" \
  --image /path/to/image1.png \
  --image /path/to/image2.png \
  --tag "标签1" \
  --tag "标签2"
```

### 参数说明

| 参数 | 简写 | 必填 | 说明 |
| --- | --- | --- | --- |
| `--title` | `-t` | ✅ | 文章标题（最多 20 字符） |
| `--content` | `-c` | ✅ | 正文内容 |
| `--image` | `-i` | ✅ | 图片路径（可多次指定，最多 16 张） |
| `--tag` | 无 | ❌ | 话题标签（可多次指定） |
| `--schedule-at` | 无 | ❌ | 定时发布时间（ISO8601 格式） |

### 发布成功输出

```
🎉 发布成功
标题: 标题
笔记 ID: 6789abcdef123456
笔记链接: https://www.xiaohongshu.com/explore/6789abcdef123456
```

## 完整工作流示例

```bash
#!/bin/bash
set -e

TITLE="我的小红书分享"
CONTENT="今天分享一些生活小技巧..."
IMAGE="/path/to/image.png"

# 步骤 1: Debug 校验
echo "正在校验内容..."
xhs-kit debug-publish \
  --title "$TITLE" \
  --content "$CONTENT" \
  --image "$IMAGE" \
  --verbose

# 步骤 2: 检查登录状态
echo "检查登录状态..."
if ! xhs-kit status; then
  echo "未登录，请先登录"
  xhs-kit login-qrcode --terminal
fi

# 步骤 3: 正式发布
echo "正在发布..."
xhs-kit publish \
  --title "$TITLE" \
  --content "$CONTENT" \
  --image "$IMAGE"

echo "发布完成！"
```

## 常见问题

1. **debug-publish 报错"图片不存在"**：确认图片路径是绝对路径且文件存在。
2. **publish 报错"未登录"**：先执行 `xhs-kit status` 检查，如未登录则执行 `xhs-kit login-qrcode`。
3. **发布后内容不可见**：可能触发平台审核，等待 1-2 小时后查看。
4. **Cookies 过期**：执行 `xhs-kit status --verify` 真实校验，如失败则重新登录。
