# read_wechat_article - 微信公众号文章阅读Skill

> 🎯 符合Claw Hub发布标准的生产级微信公众号文章抓取和解析工具

## 🌟 主要特性

- 🚀 **高性能**：直接HTTP请求HTML，无需浏览器渲染
- 🎯 **精准解析**：智能提取标题、作者、发布时间等核心信息
- 🧹 **智能清洗**：自动去除广告、赞赏等无关内容
- 📝 **多格式输出**：支持HTML、Markdown、纯文本
- 🖼️ **图片提取**：自动提取文章中的所有图片
- 📊 **数据分析**：自动计算字数和阅读时间
- 🔒 **安全合规**：严格遵循微信平台使用条款
- 🛡️ **健壮可靠**：完善的异常处理和重试机制

## 📦 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/claw-community/read_wechat_article.git
cd read_wechat_article

# 安装依赖
pip install -r requirements.txt
```

### 2. 命令行使用

```bash
# 基本使用
python read_wechat_article.py "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"

# 详细日志模式
python read_wechat_article.py "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw" -v

# 保存结果到文件
python read_wechat_article.py "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw" -o output.json
```

### 3. Python模块集成

```python
from read_wechat_article import read_wechat_article

# 公众号文章URL
url = "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"

# 抓取并解析
result = read_wechat_article(url)

# 打印结果
print(f"📖 标题: {result['title']}")
print(f"✍️ 作者: {result['author']}")
print(f"🗓️ 时间: {result['publish_time']}")
print(f"📝 字数: {result['word_count']:,}")
print(f"⏱️ 阅读时间: {result['read_time_minutes']}分钟")
```

### 4. Claw Skill调用

```python
from claw import skill

# 调用Skill
response = skill.run(
    "read_wechat_article",
    url="https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"
)

if response["success"]:
    data = response["data"]
    print(f"✅ 处理成功")
    print(f"📄 标题: {data['title']}")
else:
    print(f"❌ 处理失败: {response['error']}")
```

## 📊 输出结果

### 成功响应

```json
{
  "title": "未来1500天，影视行业的钱会被这1%的人赚走？",
  "author": "郑林",
  "publish_time": "2024-03-18 18:06",
  "content_markdown": "# 未来1500天，影视行业的钱会被这1%的人赚走？\n\n...",
  "content_text": "未来1500天，影视行业的钱会被这1%的人赚走？\n\n...",
  "images": [
    "https://mmbiz.qpic.cn/mmbiz_jpg/.../640",
    "https://mmbiz.qpic.cn/mmbiz_jpg/.../640"
  ],
  "original_url": "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw",
  "word_count": 25306,
  "read_time_minutes": 51
}
```

### 失败响应

```json
{
  "success": false,
  "error": "需要登录微信账号才能访问该文章"
}
```

## 🔧 配置选项

### 请求配置

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://mp.weixin.qq.com/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7"
}

TIMEOUT = 15  # 超时时间（秒）
RETRY_TIMES = 3  # 重试次数
RETRY_DELAY = 2  # 重试间隔（秒）
```

### 内容提取规则

支持自定义内容提取规则，只需修改以下方法：
- `extract_author()`: 作者提取规则
- `extract_publish_time()`: 发布时间提取规则
- `clean_content_html()`: 内容清洗规则

## ⚠️ 合规使用

### 核心原则

1. **用户主动触发**：仅在用户明确授权下进行抓取
2. **非商用用途**：仅供个人学习研究使用
3. **不批量爬取**：禁止大规模自动化抓取
4. **合理频率**：限制请求频率（建议≤10次/分钟）
5. **版权尊重**：不得侵犯原作者和平台的权益

### 法律责任

本工具仅提供技术实现，使用者需自行承担以下责任：
- 遵守微信公众平台的使用条款
- 符合国家相关法律法规
- 尊重原作者的知识产权

## 📈 性能优化

### 1. 网络优化

- 启用HTTP持久连接
- 支持gzip压缩
- 配置合理的超时和重试策略
- 模拟真实浏览器请求

### 2. 解析优化

- 使用高效的HTML解析器
- 避免重复DOM遍历
- 批量处理内容清洗
- 异步IO支持

### 3. 存储优化

- 流式处理大文本
- 增量更新机制
- 缓存已处理的文章

## 🎨 功能扩展

### 1. 图片处理

```python
def download_images(images: list, save_dir: str = "images"):
    """批量下载文章中的图片"""
    os.makedirs(save_dir, exist_ok=True)
    for i, img_url in enumerate(images):
        try:
            response = requests.get(img_url, headers=HEADERS)
            filename = f"image_{i+1}.jpg"
            with open(os.path.join(save_dir, filename), 'wb') as f:
                f.write(response.content)
            print(f"已下载: {filename}")
        except Exception as e:
            print(f"下载失败: {img_url}, {str(e)}")
```

### 2. 内容增强

```python
from transformers import pipeline

def summarize_article(text: str, max_length: int = 150) -> str:
    """使用大模型生成文章摘要"""
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
    return summary[0]['summary_text']
```

### 3. 知识库集成

```python
def save_to_vector_db(article: dict, db_client):
    """保存文章到向量数据库"""
    # 向量化
    embedding = generate_embedding(article['content_text'])
    
    # 存储
    db_client.insert({
        "title": article['title'],
        "content": article['content_text'],
        "embedding": embedding,
        "metadata": article
    })
```

## 🐛 故障排除

### Q: 需要登录微信账号？

A: 部分文章需要微信登录权限才能访问。解决方法：
- 尝试在微信客户端中打开文章
- 更换其他不需要登录的文章测试
- 检查IP是否被限制

### Q: 网络请求失败？

A: 可能是网络问题或服务器限制。解决方法：
- 检查网络连接
- 增加重试次数
- 更换User-Agent
- 使用代理服务器

### Q: 解析结果不准确？

A: 可能是微信页面结构更新。解决方法：
- 更新解析规则
- 提交Issue反馈
- 参与项目贡献

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request
5. 代码审查
6. 合并分支

### 贡献方向

- 新功能开发
- Bug修复
- 文档完善
- 性能优化
- 测试用例

## 📄 许可证

MIT License - 详见LICENSE文件

## 📞 联系方式

- **项目地址**: https://github.com/claw-community/read_wechat_article
- **问题反馈**: https://github.com/claw-community/read_wechat_article/issues
- **社区讨论**: https://discord.gg/claw
- **电子邮件**: support@claw.ai

## 🙏 致谢

感谢以下开源项目和库：
- requests: HTTP请求
- beautifulsoup4: HTML解析
- markdownify: HTML转Markdown
- claw framework: 技能框架
