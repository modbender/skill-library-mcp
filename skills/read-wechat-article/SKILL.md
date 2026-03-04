# 微信公众号文章阅读 Skill

> 🎯 生产级微信公众号文章抓取和解析工具，符合Claw Hub发布标准

## 🌟 功能特性

- 🚀 **高性能抓取**：服务端直接请求HTML，无需浏览器渲染，响应速度快
- 🎯 **精准解析**：智能提取标题、作者、发布时间、正文等核心信息
- 🧹 **内容清洗**：自动去除广告、赞赏、阅读数、分享按钮等无关内容
- 📝 **多格式输出**：支持HTML、Markdown、纯文本三种格式
- 🖼️ **图片处理**：自动提取文章中的所有图片URL
- 📊 **数据分析**：自动计算字数和预计阅读时间
- 🔒 **安全合规**：遵循微信公众平台使用条款，确保合法使用
- 🛡️ **健壮性**：完善的异常处理和重试机制，应对网络波动
- 🧰 **可扩展**：模块化设计，易于扩展新功能

## 📦 安装使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或直接安装：

```bash
pip install requests beautifulsoup4 markdownify
```

### 2. 命令行使用

```bash
# 基本使用
python read_wechat_article.py "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"

# 输出详细日志
python read_wechat_article.py "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw" -v

# 保存结果到文件
python read_wechat_article.py "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw" -o output.json
```

### 3. 作为Python模块使用

```python
from read_wechat_article import read_wechat_article

# 公众号文章URL
url = "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"

# 抓取并解析文章
result = read_wechat_article(url)

# 输出结果
print(f"标题: {result['title']}")
print(f"作者: {result['author']}")
print(f"发布时间: {result['publish_time']}")
print(f"字数: {result['word_count']:,}")
print(f"阅读时间: {result['read_time_minutes']}分钟")
print(f"图片数量: {len(result['images'])}")
print(f"Markdown内容: {result['content_markdown'][:500]}...")
```

### 4. 作为Claw Skill使用

```python
from claw import skill

# 调用Skill
result = skill.run(
    "read_wechat_article",
    url="https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"
)

if result["success"]:
    data = result["data"]
    print(f"文章标题: {data['title']}")
else:
    print(f"处理失败: {result['error']}")
```

## 📊 输出结果结构

```python
{
    "title": "未来1500天，影视行业的钱会被这1%的人赚走？",
    "author": "郑林",
    "publish_time": "2024-03-18 18:06",
    "content_markdown": "# 未来1500天，影视行业的钱会被这1%的人赚走？\n\n在过去的三年里，影视行业经历了前所未有的挑战...",
    "content_text": "未来1500天，影视行业的钱会被这1%的人赚走？\n\n在过去的三年里，影视行业经历了前所未有的挑战...",
    "images": [
        "https://mmbiz.qpic.cn/mmbiz_jpg/.../640",
        "https://mmbiz.qpic.cn/mmbiz_jpg/.../640"
    ],
    "original_url": "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw",
    "word_count": 25306,
    "read_time_minutes": 51
}
```

## ⚙️ 配置参数

### 全局配置

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://mp.weixin.qq.com/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7"
}

TIMEOUT = 15  # 超时时间（秒）
RETRY_TIMES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试间隔时间（秒）
```

### 正则表达式

```python
PUB_TIME_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})')  # 匹配发布时间
URL_CLEAN_PATTERN = re.compile(r'https://mp\.weixin\.qq\.com/s/[A-Za-z0-9_-]+')  # 清理URL
```

## 🔧 技术原理

### 1. URL清理

自动去除URL中的多余参数，只保留核心部分：

```
原始URL: https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw?from=groupmessage&isappinstalled=0
清理后: https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw
```

### 2. 内容解析流程

```
HTTP请求 → HTML响应 → 标题提取 → 作者提取 → 时间提取 → 正文提取 → 内容清洗 → 格式转换 → 结果输出
```

### 3. 内容清洗策略

- **去除无关标签**：script、style、iframe、video、audio等
- **去除广告区块**：包含ad-wrap、reward_area、like_area等class的元素
- **去除社交元素**：分享按钮、点赞、评论、阅读数等
- **清理空标签**：去除没有内容的空div、p、span标签
- **优化格式**：统一换行、空格，提高可读性

## ⚠️ 合规使用指南

### 合法使用原则

1. **用户主动触发**：仅在用户主动提供URL时进行抓取
2. **非商用用途**：不得将抓取的内容用于商业目的
3. **不批量爬取**：不进行大规模批量爬取操作
4. **遵守平台规则**：尊重微信公众平台的使用条款
5. **合理频率**：避免高频抓取触发平台限制（建议不超过10次/分钟）
6. **标明来源**：如引用文章内容，需标明原文来源和作者

### 风险提示

- **登录限制**：部分文章需要登录微信账号才能访问
- **权限限制**：部分文章可能设置了访问权限
- **反爬机制**：微信可能会更新反爬机制，导致抓取失败
- **法律风险**：非法抓取和使用可能会导致法律责任

### 免责声明

本工具仅用于学习和研究目的，请勿用于非法用途。用户需自行承担因使用本工具而产生的法律责任。

## 📈 性能优化

### 1. 网络优化

- 使用持久化HTTP连接（keep-alive）
- 启用gzip压缩，减少传输数据量
- 设置合理的超时时间和重试策略
- 配置合适的User-Agent，提高兼容性

### 2. 解析优化

- 使用lxml解析器（需要安装lxml库）
- 避免重复解析HTML文档
- 批量处理DOM操作，减少遍历次数
- 使用CSS选择器替代XPath，提高效率

### 3. 内存优化

- 流式处理大文件，避免一次性加载过多内容
- 及时清理不再使用的对象，释放内存
- 分块处理大文本内容，减少内存占用

## 🎨 扩展功能

### 1. 图片下载

```python
def download_image(url: str, save_path: str):
    """下载图片到本地"""
    response = requests.get(url, headers=HEADERS)
    with open(save_path, 'wb') as f:
        f.write(response.content)
```

### 2. 内容增强

```python
def summarize_content(text: str, max_length: int = 500) -> str:
    """内容摘要"""
    # 这里可以接入大模型实现智能摘要
    return text[:max_length] + "..."
```

### 3. 数据存储

```python
def save_to_database(result: Dict, db_conn):
    """保存到数据库"""
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO articles (title, author, content_text) VALUES (?, ?, ?)",
        (result['title'], result['author'], result['content_text'])
    )
    db_conn.commit()
```

## 🐛 常见问题

### Q: 出现"需要登录微信账号才能访问该文章"错误？

A: 这篇文章需要登录微信账号才能访问。可以尝试：
- 使用已登录的微信客户端打开链接
- 检查网络环境是否正常
- 换一个不需要登录的文章测试

### Q: 出现"网络请求失败"错误？

A: 可能是网络问题或服务器限制。可以尝试：
- 检查网络连接
- 增加重试次数
- 更换User-Agent
- 使用代理服务器

### Q: 提取的内容不完整？

A: 可能是微信页面结构更新导致的。可以尝试：
- 更新解析规则
- 检查HTML结构
- 提交Issue反馈

### Q: 运行速度慢？

A: 可能是网络延迟或页面加载慢。可以尝试：
- 增加超时时间
- 使用更快的网络环境
- 启用多线程处理

## 📞 支持与反馈

- **GitHub Issues**: 提交问题和建议
- **Discord社区**: 与其他开发者交流
- **邮件**: support@claw.ai

## 📄 许可证

MIT License - 详见LICENSE文件
