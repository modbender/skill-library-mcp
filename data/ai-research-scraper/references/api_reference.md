## API参考文档

### 翻译API

目前使用的翻译API是Google Cloud Translation API。

#### 配置要求

Google Cloud Translation API需要以下配置：
- API密钥：需要创建并配置Google Cloud API密钥
- 项目ID：需要创建Google Cloud项目

#### 使用方法

```python
from googletrans import Translator

translator = Translator()
translated_text = translator.translate(text, dest='zh-CN')
```

#### 错误处理

如果翻译API出现错误，系统会返回原始文本。

#### 替代方案

如果Google Cloud Translation API不可用，可以尝试使用其他翻译API：

- 百度翻译API
- 有道翻译API
- Microsoft Translator API

#### 测试

```bash
python3 scripts/test_pygoogletrans.py
```

### Tavily Search API

Tavily Search API用于替代网络抓取，避免网络超时问题。

#### 配置要求

Tavily Search API需要以下配置：
- API密钥：需要创建并配置Tavily API密钥

#### 使用方法

```python
import requests

response = requests.get('https://api.tavily.com/search', params={
    'query': 'AI product development news',
    'api_key': 'TAVILY_API_KEY',
    'max_results': 10,
    'search_depth': 'basic'
}, timeout=30)
```

#### 错误处理

如果Tavily Search API出现错误，系统会使用网络抓取作为备用方法。

#### 测试

```bash
python3 scripts/test_tavily_search.py
```