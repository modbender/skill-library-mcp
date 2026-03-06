---
name: yahoo-auction-estimator
description: 日本雅虎拍卖商品估价工具 - 自动获取商品信息、查询历史成交价、计算建议出价
homepage: https://github.com/openclaw/skills/tree/main/yahoo-auction-estimator
metadata: {"clawdbot":{"emoji":"🏷️","requires":{"bins":["node","curl"],"env":["PROXY_SOCKS5"]},"primaryEnv":"PROXY_SOCKS5"}}
---

# Yahoo Auction Estimator

日本雅虎拍卖商品自动估价工具。输入商品ID，自动完成：
1. 获取商品信息（名称、价格、结束时间）
2. 提取精确搜索关键词
3. 查询aucfree历史成交价
4. 计算平均价和建议出价
5. 时区换算（日本→中国）

## 使用方法

### 单商品估价
```bash
node {baseDir}/scripts/estimate.mjs <商品ID>
```

### 批量估价
```bash
node {baseDir}/scripts/estimate.mjs <ID1> <ID2> <ID3> ...
```

### 示例
```bash
node {baseDir}/scripts/estimate.mjs b1220553804
node {baseDir}/scripts/estimate.mjs n1220557199 o1220500433 w1220506728
```

## 输出格式

```
┌─ 商品ID ─────────────────────────────┐
│ 商品: <名称>
│ 当前: <价格> | 结束: <中国时间>
│ 历史均价: <均价>
│ 建议出价: <建议价> (均价×85%)
│ 状态: <评估>
└────────────────────────────────────────┘
```

## 关键词提取规则

### 镜头类
```
品牌 + 系列 + 焦段 + 光圈（必须完整）
例: LEICA SUMMICRON-M 35mm F2 ASPH
```

### 机身类
```
品牌 + 系列型号
例: FUJIFILM GS645W
例: HASSELBLAD 500C/M
```

### 排除词
- SEO营销词（美品、希少、 etc.）
- 日文假名注音
- 店铺前缀
- 编号代码

## 时区换算

| 日本 (JST) | 中国 (CST) |
|:---|:---|
| UTC+9 | UTC+8 |
| 日本时间 - 1小时 = 中国时间 |

## 计算公式

```
建议出价 = 历史平均成交价 × 0.85
```

## 代理配置

需配置日本代理访问aucfree.com：
```bash
export PROXY_SOCKS5=socks5://127.0.0.1:1080
```

## 数据来源

- 商品信息: Yahoo!オークション
- 历史价格: aucfree.com

## License

MIT
