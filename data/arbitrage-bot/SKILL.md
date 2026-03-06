---
name: arbitrage-bot
description: Cross-exchange crypto arbitrage detection and execution. Find price differences, calculate profits, execute trades automatically.
auto_trigger: false
---

# Arbitrage Bot

取引所間の仮想通貨アービトラージ検出・実行。

## 概要

異なる取引所間の価格差を検出し、利益を得るトレーディング戦略。

## アービトラージタイプ

### 単純アービトラージ
```
取引所A: BTC = $50,000
取引所B: BTC = $50,200
差額: $200 (0.4%)

操作:
1. Aで購入
2. Bに転送
3. Bで売却
4. 利益確定
```

### 三角アービトラージ
```
同一取引所内:
BTC → ETH → USDT → BTC

価格差から利益を得る
```

### DEXアービトラージ
```
DEX間の価格差を利用:
Uniswap vs SushiSwap
1inch で最適ルート探索
```

## 使用方法

### 機会検出
```
「アービトラージ機会をスキャン」
「BTC/USDTの取引所間価格差を確認」
```

### 自動実行
```
「0.5%以上の差があれば自動実行」
「最大$1000までのアービトラージ実行」
```

### 分析
```
「過去24時間のアービトラージ機会を分析」
「最も頻繁な機会のペアを表示」
```

## 対応取引所

### CEX
- Binance
- Coinbase
- Kraken
- Bybit
- OKX

### DEX
- Uniswap (Ethereum)
- PancakeSwap (BSC)
- SushiSwap (Multi-chain)
- Raydium (Solana)

## 利益計算

### コスト要因
```
- 取引手数料（0.1-0.3%）
- 送金手数料
- スリッページ
- ガス代（DEX）
```

### 最小利益閾値
```
CEX間: 0.5%以上（送金時間考慮）
DEX間: 0.3%以上（同一ブロック可能）
三角: 0.1%以上（手数料3回分考慮）
```

### 計算例
```
購入: 1 BTC @ $50,000
売却: 1 BTC @ $50,300

粗利益: $300 (0.6%)
手数料: -$100 (0.2%)
送金費: -$30
純利益: $170 (0.34%)
```

## リスク管理

### 主要リスク
```
- 価格変動リスク（送金中に逆転）
- 流動性リスク（注文が通らない）
- 送金遅延リスク
- 取引所リスク（出金停止等）
```

### 対策
```
✅ 小額から開始
✅ 流動性の高いペアのみ
✅ 送金時間の短いチェーン選択
✅ 複数取引所に資金分散
✅ 自動損切り設定
```

## 技術実装

### 価格監視
```javascript
// 複数取引所の価格を同時取得
const prices = await Promise.all([
  binance.getPrice('BTCUSDT'),
  coinbase.getPrice('BTC-USD'),
  kraken.getPrice('XBTUSD')
]);
```

### 機会検出
```javascript
// スプレッド計算
const spread = (maxPrice - minPrice) / minPrice * 100;
if (spread > MIN_SPREAD) {
  alert('Arbitrage opportunity detected!');
}
```

## セキュリティ

### 承認レベル
| 操作 | 承認 |
|------|------|
| 価格監視 | 不要 |
| 機会アラート | 不要 |
| $100未満の実行 | 通知 |
| $100以上の実行 | 承認必須 |

### API キー管理
```
- 読み取り専用キーを基本に
- 取引キーは最小権限
- 出金権限は付与しない
- IPホワイトリスト設定
```

## 収益ポテンシャル

**変動大 - 保証なし**

| 資金規模 | 期待月利 | リスク |
|---------|---------|--------|
| $1,000 | 1-5% | 中 |
| $10,000 | 2-8% | 中 |
| $100,000 | 3-10% | 中-高 |

## 注意事項

### 現実的な期待
```
- 機会は減少傾向（競争激化）
- 大手ボットが優位
- 手数料で利益が消える場合多い
- 24時間監視が必要
```

### 法的考慮
```
- 各取引所の利用規約確認
- 税務申告の必要性
- 居住国の規制確認
```
