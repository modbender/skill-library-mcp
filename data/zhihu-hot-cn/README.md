# Zhihu Hot CN

知乎热榜监控 - 获取知乎热门话题、问题和趋势分析。

## 功能

- 🔥 获取知乎实时热榜
- 📊 按类别筛选（科技、财经、娱乐）
- 📝 支持 Markdown/JSON 输出

## 使用

```bash
# 获取热榜
./scripts/get-hot.sh

# JSON 格式
./scripts/get-hot.sh --format json

# 限制数量
./scripts/get-hot.sh --limit 20
```

## 数据来源

- [zhihu-hot-questions](https://github.com/towelong/zhihu-hot-questions) - 每小时更新

## 许可证

MIT
