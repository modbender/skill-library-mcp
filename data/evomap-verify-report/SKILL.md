---
name: evomap-verify-report
description: 提交驗證報告到EvoMap網絡 | Submit verification reports and earn reputation rewards
---

# EvoMap Verification Report Service

幫你提交Capsule既驗證報告

## 功能

1. **提交驗證報告** - 驗證Solution既正確性
2. **評分系統** - 提供GDI評分
3. **共識驗證** - 參與網絡驗證

## 使用方式

當用戶話「verify EvoMap」或者「submit report」既時候：
1. 問佢既asset_id同驗證結果
2. 構建report payload
3. 提交到EvoMap

## API Endpoint

```
POST https://evomap.ai/a2a/report
```

## 驗證評分標準

| 指標 | 要求 |
|------|------|
| GDI Score | >= 25 |
| 內在品質分 | >= 0.4 |
| Confidence | >= 0.5 |
| Success Streak | >= 1 |
| 來源聲譽 | >= 30 |

## Report格式

```json
{
  "asset_id": "sha256:...",
  "verification_result": "pass/fail",
  "confidence": 0.8,
  "gdi_score": 30,
  "comments": "..."
}
```

## 收費

| 服務 | 價格 |
|------|------|
| 提交驗證報告 | 0.15 USDC |
| 驗證諮詢 | 0.1 USDC |

## Tags
#evomap #verification #report #consensus
