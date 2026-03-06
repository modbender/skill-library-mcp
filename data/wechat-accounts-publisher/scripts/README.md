# 微信公众号文章发布脚本

支持 Python 和 Node.js 两种版本，支持封面图和正文图片自动上传。

## 功能

- 自动获取和缓存 Access Token
- 创建图文草稿到微信公众号
- 上传封面图片到素材库
- **自动上传正文图片并替换 URL**
- 智能检测本地图片和外部 URL
- 支持多账号配置
- 自动生成文章摘要
- 图片格式和大小验证

## 安装依赖

### Python 版
```bash
pip install httpx
```

### Node.js 版
```bash
npm install axios form-data
```

## 配置

1. 复制配置模板：
```bash
cp config.example.json config.json
```

2. 编辑 `config.json`，填写你的公众号信息：
```json
{
  "wechat": {
    "defaultAccount": "default",
    "accounts": {
      "default": {
        "name": "我的公众号",
        "appId": "your_app_id_here",
        "appSecret": "your_app_secret_here",
        "type": "subscription",
        "enabled": true
      }
    },
    "apiBaseUrl": "https://api.weixin.qq.com",
    "tokenCacheDir": "./.tokens"
  }
}
```

**获取 AppID 和 AppSecret：**
- 登录 https://mp.weixin.qq.com
- 开发 → 基本配置 → 开发者ID

## 正文图片自动上传

### 工作原理

脚本会自动扫描 HTML 内容中的 `<img src="...">` 标签：

1. **检测类型**：判断是本地路径还是外部 URL
2. **自动上传**：本地图片上传到微信素材库
3. **URL 替换**：将本地路径替换为微信素材 URL
4. **保留原样**：外部 URL 不处理，直接使用

### 使用示例

**原始 HTML (article.html)：**
```html
<section class="article-content">
  <h1>我的文章</h1>
  <p>段落内容...</p>
  <img src="./images/cover.jpg" />      <!-- ✅ 自动上传 -->
  <p>更多内容...</p>
  <img src="diagram.png" />               <!-- ✅ 自动上传 -->
  <img src="https://example.com/pic.png" />  <!-- ⏭️ 保持原样 -->
</section>
```

**执行命令：**
```bash
python publish_article.py "我的文章" article.html \
  --from-file \
  --content-dir ./images \
  --thumb cover.jpg
```

**处理后的 HTML：**
```html
<section class="article-content">
  <h1>我的文章</h1>
  <p>段落内容...</p>
  <img src="https://mmbiz.qpic.cn/mmbiz_jpg/xxx1/..." />
  <p>更多内容...</p>
  <img src="https://mmbiz.qpic.cn/mmbiz_jpg/xxx2/..." />
  <img src="https://example.com/pic.png" />
</section>
```

### 图片路径说明

**相对路径**（推荐）：
```html
<img src="photo.jpg" />              <!-- 当前目录 -->
<img src="./images/pic.png" />       <!-- 相对于当前目录 -->
```

**使用 `--content-dir` 指定基础目录：**
```bash
python publish_article.py "标题" content.html \
  --from-file \
  --content-dir /path/to/images
```

**绝对路径：**
```html
<img src="/Users/name/Pictures/photo.jpg" />
```

**外部 URL（不会上传）：**
```html
<img src="https://example.com/img.jpg" />
```

## 使用方法

### Python 版

**简单方式（当前目录图片）：**
```bash
python publish_article.py "文章标题" "<HTML内容>"
```

**带封面图（当前目录图片）：**
```bash
python publish_article.py "文章标题" "<HTML内容>" --thumb cover.jpg
```

**从文件读取（推荐）：**
```bash
python publish_article.py "文章标题" article.html --from-file
```

**完整示例（封面图 + 正文图）：**
```bash
python publish_article.py "我的文章" article.html \
  --from-file \
  --thumb cover.jpg \
  --content-dir ./images
```

**查看帮助：**
```bash
python publish_article.py --help
```

### Node.js 版

**简单方式（当前目录图片）：**
```bash
node publish_article.js "文章标题" "<HTML内容>"
```

**带封面图（当前目录图片）：**
```bash
node publish_article.js "文章标题" "<HTML内容>" --thumb cover.jpg
```

**从文件读取（推荐）：**
```bash
node publish_article.js "文章标题" article.html --from-file
```

**完整示例（封面图 + 正文图）：**
```bash
node publish_article.js "我的文章" article.html \
  --from-file \
  --thumb cover.jpg \
  --content-dir ./images
```

**查看帮助：**
```bash
node publish_article.js --help
```

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `标题` | 文章标题 | ✅ |
| `HTML内容\|文件` | HTML内容字符串或文件路径 | ✅ |
| `--from-file` | 从文件读取内容 | ❌ |
| `--config` | 配置文件路径（默认 config.json） | ❌ |
| `--thumb` | 封面图片路径 | ❌ |
| `--content-dir` | 正文图片的基础目录（默认当前目录） | ❌ |

## 图片上传支持

### 封面图
- **格式**：JPG、JPEG、PNG
- **大小限制**：不超过 64MB
- **建议尺寸**：900 × 383 像素（2.35:1 比例）
- **用途**：文章列表显示的封面

### 正文图片
- **格式**：JPG、JPEG、PNG、BMP、GIF
- **大小限制**：不超过 2MB（单张）
- **用途**：嵌入在文章内容中
- **处理方式**：自动上传并替换 URL

### 图片要求对照表

| 类型 | 格式 | 大小限制 | 用途 |
|------|------|----------|------|
| 封面图 | JPG, PNG | 64MB | 文章封面 |
| 正文图 | JPG, PNG, BMP, GIF | 2MB | 文章内嵌 |

## 程序化使用

### Python

**上传封面图：**
```python
import asyncio
from publish_article import WeChatAPI

async def upload_thumb():
    api = WeChatAPI("config.json")
    result = await api.upload_image("cover.jpg", is_thumb=True)
    # result: { 'media_id': 'xxx', 'url': '...' }
    print(f"media_id: {result['media_id']}")

asyncio.run(upload_thumb())
```

**上传正文图：**
```python
async def upload_content_image():
    api = WeChatAPI("config.json")
    result = await api.upload_image("photo.jpg", is_thumb=False)
    # result: { 'media_id': 'xxx', 'url': 'https://...' }
    print(f"URL: {result['url']}")

asyncio.run(upload_content_image())
```

**处理内容中所有图片：**
```python
async def process_content():
    api = WeChatAPI("config.json")
    html = '<p>内容</p><img src="photo1.jpg" /><img src="photo2.jpg" />'

    processed_content, uploaded = await api.process_content_images(
        html,
        base_dir='./images'
    )

    print(f"上传了 {len(uploaded)} 张图片")
    return processed_content

asyncio.run(process_content())
```

**完整发布流程：**
```python
async def publish_with_images():
    api = WeChatAPI("config.json")

    # 1. 上传封面
    thumb_result = await api.upload_image("cover.jpg", is_thumb=True)

    # 2. 处理内容
    content = '<img src="photo1.jpg" /><p>正文</p>'
    processed_content, _ = await api.process_content_images(content, base_dir='./images')

    # 3. 创建草稿
    media_id = await api.create_draft("标题", processed_content, thumb_result['media_id'])
    print(f"草稿 ID: {media_id}")

asyncio.run(publish_with_images())
```

### Node.js

**上传封面图：**
```javascript
const { WeChatAPI } = require('./publish_article.js');

async function uploadThumb() {
  const api = new WeChatAPI('config.json');
  const result = await api.uploadImage('cover.jpg', true);
  // result: { media_id: 'xxx', url: '...' }
  console.log(`media_id: ${result.media_id}`);
}

uploadThumb();
```

**上传正文图：**
```javascript
async function uploadContentImage() {
  const api = new WeChatAPI('config.json');
  const result = await api.uploadImage('photo.jpg', false);
  // result: { media_id: 'xxx', url: 'https://...' }
  console.log(`URL: ${result.url}`);
}

uploadContentImage();
```

**处理内容中所有图片：**
```javascript
async function processContent() {
  const api = new WeChatAPI('config.json');
  const html = '<p>内容</p><img src="photo1.jpg" /><img src="photo2.jpg" />';

  const { content: processedContent, uploadedImages } = await api.processContentImages(
    html,
    './images'
  );

  console.log(`上传了 ${Object.keys(uploadedImages).length} 张图片`);
  return processedContent;
}

processContent();
```

**完整发布流程：**
```javascript
async function publishWithImages() {
  const api = new WeChatAPI('config.json');

  // 1. 上传封面
  const thumbResult = await api.uploadImage('cover.jpg', true);

  // 2. 处理内容
  const content = '<img src="photo1.jpg" /><p>正文</p>';
  const { content: processedContent } = await api.processContentImages(content, './images');

  // 3. 创建草稿
  const mediaId = await api.createDraft('标题', processedContent, thumbResult.media_id);
  console.log(`草稿 ID: ${mediaId}`);
}

publishWithImages();
```

## 文章格式

文章内容应为微信支持的 HTML 格式，例如：

```html
<section class="article-content">
  <p>这是段落内容。</p>
  <h2>二级标题</h2>
  <p>更多内容...</p>
  <img src="本地图片.jpg" />           <!-- 会自动上传 -->
  <img src="https://example.com/img.jpg" />  <!-- 保持原样 -->
</section>
```

**重要提示：**
- 使用 `<section class="article-content">` 包裹全文
- 只使用闭合标签，避免自闭合标签如 `<br/>`
- 推荐使用 HTTPS 图片链接
- 避免复杂 CSS（微信有限制）
- 本地图片路径会自动处理

## 注意事项

1. 确保公众号类型支持草稿接口（认证订阅号/服务号）
2. AppSecret 要保密，不要提交到代码仓库
3. Access Token 会自动缓存到 `.tokens/` 目录（可配置）
4. 草稿创建后需要登录公众号后台进行编辑和群发
5. 上传的图片会保存到公众号素材库，可在素材管理中查看
6. 正文图片单张不超过 2MB，封面图不超过 64MB
7. 相对路径默认从当前目录查找，使用 `--content-dir` 指定其他目录

## 错误处理

常见错误：

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| 40001 | AppID 或 AppSecret 错误 | 检查配置文件中的凭证 |
| 40004 | 不支持的媒体类型 | 检查图片格式 |
| 40164 | IP 不在白名单中 | 在公众号后台添加服务器 IP |
| 41005 | 媒体文件为空 | 检查图片文件是否损坏 |
| 45009 | 接口调用超过限制 | 等待或降低频率 |
| 图片太大 | 超过大小限制 | 压缩图片（正文<2MB，封面<64MB） |
| 图片找不到 | 路径错误 | 检查路径或使用 `--content-dir` 指定目录 |

## 多账号支持

配置文件支持多个账号：

```json
{
  "wechat": {
    "defaultAccount": "account1",
    "accounts": {
      "account1": { ... },
      "account2": { ... }
    }
  }
}
```

通过修改 `defaultAccount` 切换使用的账号。

## 技术说明

### API 端点
- **获取 Token**: `GET /cgi-bin/token`
- **上传素材**: `POST /cgi-bin/material/add_material`
  - `type=thumb`: 封面图
  - `type=image`: 正文图片
- **创建草稿**: `POST /cgi-bin/draft/add`

### 图片上传流程
1. 扫描 HTML 中的 `<img>` 标签
2. 检测 src 属性是否为本地路径
3. 上传到微信素材库（获得 media_id 和 url）
4. 替换原 src 为新的 URL
5. 外部 URL 保持不变

### Token 缓存
- **机制**：Token 有效期内缓存，提前 5 分钟自动刷新
- **位置**：`.tokens/token_cache.json`
- **作用**：减少 API 调用次数，避免频率限制

## 示例流程

### 完整的发布示例

```bash
# 1. 准备文件结构
# .
# ├── article.html      # 文章内容
# ├── cover.jpg         # 封面图
# └── images/
#     ├── photo1.jpg    # 正文图片1
#     ├── photo2.jpg    # 正文图片2
#     └── diagram.png   # 正文图片3

# 2. 执行发布命令
python publish_article.py \
  "我的第一篇微信公众号文章" \
  article.html \
  --from-file \
  --thumb cover.jpg \
  --content-dir ./images

# 3. 查看结果
# 显示成功后，登录 https://mp.weixin.qq.com 查看草稿
```

### 文章示例 HTML (article.html)

```html
<section class="article-content">
  <h1>Python 自动化发布</h1>
  <p>这是一篇关于自动化发布的文章。</p>

  <h2>第一章：简介</h2>
  <p>这里介绍自动化发布的基本概念。</p>
  <img src="images/diagram.png" />

  <h2>第二章：实践</h2>
  <p>让我们看看实际操作。</p>
  <img src="images/screenshot1.jpg" />
  <p>更多细节...</p>
  <img src="images/screenshot2.jpg" />

  <h2>总结</h2>
  <p>自动化发布大大提高了效率。</p>
</section>
```

### 输出示例

```
🚀 开始发布公众号文章...

✅ 找到配置文件: config.json
📱 使用账号: 我的公众号

📝 文章标题: 我的第一篇微信公众号文章
📊 文章长度: 456 字符

📷 处理封面图片...
📤 正在上传封面图: cover.jpg (156.23KB)
✅ 封面图上传成功
   URL: https://mmbiz.qpic.cn/mmbiz_jpg/xxx/...

📷 检测到 3 张图片，开始处理...

📤 正在上传正文图片: diagram.png (89.45KB)
✅ 正文图片上传成功
   URL: https://mmbiz.qpic.cn/mmbiz_png/yyy/...
  [1] diagram.png - 已替换为微信 URL

📤 正在上传正文图片: screenshot1.jpg (234.12KB)
✅ 正文图片上传成功
   URL: https://mmbiz.qpic.cn/mmbiz_jpg/zzz/...
  [2] screenshot1.jpg - 已替换为微信 URL

📤 正在上传正文图片: screenshot2.jpg (198.67KB)
✅ 正文图片上传成功
   URL: https://mmbiz.qpic.cn/mmbiz_jpg/www/...
  [3] screenshot2.jpg - 已替换为微信 URL

✓ 图片处理完成，成功上传 3 张

✅ Access Token 获取成功
✅ 草稿创建成功！
   草稿 ID: MediaId_xxx
   上传封面: 是
   上传正文图: 3 张
   请登录微信公众号后台查看: https://mp.weixin.qq.com/
```