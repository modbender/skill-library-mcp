# a-share-metrics-card

生成 A 股单只股票的关键指标“体检卡”（学习用途），输出为统一 Markdown，便于对比与持续跟踪。

## 使用

```bash
cd /home/joig/.openclaw/workspace
source .venv/bin/activate
python skills/a-share-metrics-card/scripts/metrics_card.py --symbol 600406 --name 国电南瑞
```

输出文件默认：
- `notes/stocks/cards/<symbol>.md`

也可以指定输出：

```bash
python skills/a-share-metrics-card/scripts/metrics_card.py --symbol 600406 --out notes/stocks/cards/600406.md
```

## 常见问题

### 1) 为什么卡片里显示“行情拉取失败/超时”？

在云主机（Azure/阿里云/腾讯云）上，部分公开数据源会对机房 IP 限流或直接断开连接。
本脚本会：
- 尽量生成卡片（失败会写备注，不让整个流程崩）
- 后续可加“多数据源 fallback / 重试退避 / 本地缓存”来提高稳定性

### 2) 这张卡片怎么用？

- 当作单股研究主页：每次更新覆盖同一文件
- 用 `git diff` 看指标变化
- 看到不懂的字段，把概念丢给 `a-share-glossary-tutor` 写进词典

> 不提供买卖建议，仅用于学习与信息整理。
