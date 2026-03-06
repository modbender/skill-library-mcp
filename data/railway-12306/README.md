# Railway 12306 Skill

🚄 中国铁路12306火车票智能查询助手

## 功能特性

- ✅ 实时余票查询
- ✅ 智能推荐车次（最快/最便宜/直达）
- ✅ 多日期价格对比
- ✅ 车站代码自动转换
- ✅ 农历日期智能识别
- ✅ 零依赖（仅需Node.js内置模块）

## 快速开始

### 基础查询

```bash
# 查询明天的票
node scripts/query_tickets.js --from "丽水" --to "上海" --date "tomorrow"

# 查询指定日期
node scripts/query_tickets.js --from "北京" --to "上海" --date "2026-02-27"
```

### 智能推荐

```bash
# 推荐最快车次
node scripts/query_tickets.js --from "丽水" --to "上海" --date "2026-02-27" --recommend --prefer "fastest"

# 推荐最便宜车次
node scripts/query_tickets.js --from "丽水" --to "上海" --date "2026-02-27" --recommend --prefer "cheapest"
```

### 多日期对比

```bash
node scripts/query_tickets.js \
  --from "丽水" \
  --to "上海" \
  --dates "2026-02-25,2026-02-27,2026-02-28" \
  --compare-dates
```

## 输出示例

```
🚄 丽水 → 上海 (2026-02-27)

【推荐车次】⭐
G7344  07:20-09:56  02:36  有票
├─ 出发：丽水
├─ 到达：上海虹桥
└─ 余票：二等座:99、一等座:20

【所有车次】
G7368  09:28-12:00  02:32  有票
├─ 出发：丽水
├─ 到达：上海南
└─ 余票：二等座:充足

💡 共查询到 16 个车次
```

## 支持的车站

主要覆盖：
- 直辖市：北京、上海、天津、重庆
- 省会城市：广州、深圳、杭州、南京、武汉等
- 浙江省：杭州、宁波、温州、金华、丽水等

详见 `references/station_codes.json`

## 注意事项

- ⚠️ 仅供查询，不支持购票
- ⚠️ 建议查询间隔≥3秒
- ⚠️ 购票请前往12306官网/APP
- ⚠️ 数据仅供参考，以12306实际为准

## 作者

- **Author**: 玉斧 (wangyuqin2@xiaohongshu.com)
- **Created**: 2026-02-21
- **License**: MIT

## 更新日志

### v1.0.0 (2026-02-21)
- ✨ 初始版本
- ✅ 支持基础查询
- ✅ 支持智能推荐
- ✅ 支持多日期对比
- ✅ 内置常用车站代码

## 待办事项

- [ ] 价格查询集成
- [ ] 中转方案推荐
- [ ] 候补监控
- [ ] 历史价格追踪
