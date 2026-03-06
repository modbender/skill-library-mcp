# Web Learner 参考资料

## 常用新闻网站

| 网站 | 网址 | 特点 |
|------|------|------|
| 百度新闻 | news.baidu.com | 聚合类新闻 |
| 澎湃新闻 | www.thepaper.cn | 深度报道 |
| 今日头条 | www.toutiao.com | 个性化推荐 |
| 腾讯新闻 | news.qq.com | 综合门户 |
| 新浪新闻 | news.sina.com.cn | 综合门户 |

## 常用查询网站

### 天气
- wttr.in/Shanghai - 简洁天气
- www.weather.com.cn - 中国天气网
- www.cma.gov.cn - 中央气象局

### 学术/知识
- zh.wikipedia.org - 维基百科
- www.zhihu.com - 知乎
- www.bilibili.com - B站教程

### 技术文档
- developer.mozilla.org - MDN Web Docs
- docs.python.org - Python 文档
- github.com - GitHub

## 搜索技巧

### 中文搜索
```
country: "CN"
search_lang: "zh"
```

### 时间限定
- `freshness: "pd"` - 今天
- `freshness: "pw"` - 本周
- `freshness: "pm"` - 本月

### 高级搜索
- 使用引号精确匹配
- 使用减号排除无关结果
- 使用 site: 限定网站

## API 工具限制

| 工具 | 限制 | 解决方案 |
|------|------|----------|
| web_search | 需要 Brave API Key | 使用 web_fetch 替代 |
| web_fetch | 部分网站有反爬 | 使用 browser |
| browser | 需要服务运行 | 提示用户启动 |

## 处理失败情况

1. **web_search 失败** → 尝试 web_fetch 搜索引挚
2. **web_fetch 失败** → 尝试 browser 或告知用户
3. **browser 不可用** → 提供手动查看链接
4. **内容被墙** → 提示用户可能需要 VPN
