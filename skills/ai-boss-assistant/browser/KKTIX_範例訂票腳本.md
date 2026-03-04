# KKTIX 活動頁自動化腳本模板

> 活動頁：https://kklivetw.kktix.cc/events/rgt6hi7y
> 目的：示範如何用 agent-browser 幫老闆「看票況／整理資訊／準備填單」，
>      此腳本為設計範本，執行前需由老闆確認。

---

## 1. 開啟活動頁並等待載入完成

```bash
cd /Users/user/clawd

# 開啟活動頁
agent-browser open https://kklivetw.kktix.cc/events/rgt6hi7y

# 等待網路穩定（避免半載入狀態）
agent-browser wait --load networkidle

# 抓目前畫面的互動元素與 refs
agent-browser snapshot -i --json
```

> 執行到這裡後，由 AI 解析 snapshot JSON，找出：
> - 場次選擇區塊
> - 票價／票種資訊
> - 下一步按鈕（例如「我要購票」）

---

## 2. 抓取票價與場次資訊（邏輯示意）

> 以下命令中的 `@eX`, `@eY` 只是示意，實際要根據 snapshot 中的 refs 調整。

```bash
# 假設票價列表區塊是 @e10
agent-browser get text @e10 --json

# 假設場次列表是 @e11
agent-browser get text @e11 --json
```

AI 拿到這些文字後，要整理成對老闆有用的格式，例如：

- 場次 A：日期／時間／票價範圍／是否還有票
- 場次 B：...

並用人話回報給老闆，請老闆決定要看哪一場、哪一種票種。

---

## 3. 半自動填單（只做到確認頁，不代按最後送出）

假設老闆選擇了某場次與票種：

```bash
# 點選「我要購票」之類的按鈕
agent-browser click @e20
agent-browser wait --load networkidle
agent-browser snapshot -i --json

# 在新頁面中：
# - 選擇場次（假設是 @e21）
# - 選擇票種／張數（假設是 @e22, @e23）
agent-browser click @e21             # 選擇指定場次
agent-browser click @e22             # 選擇票種
agent-browser click @e23             # 選擇張數

# 再 snapshot 一次，確認已填好
agent-browser snapshot -i --json
```

最後，AI 應該停在「確認頁」之前，並用人話對老闆說明：

> 「我已經幫你在 KKTIX 活動頁把場次、票種、張數都選好了，
>   現在畫面停在確認頁，建議你自己確認資訊無誤後再按『確認』或『下一步』。」

不應該自動按下最後的確定／付款按鈕，除非老闆特別要求且風險已說明清楚。

---

## 4. 注意事項

- 此腳本為 **模板**，實際執行前需：
  - 由 AI 重新跑一次 `snapshot -i --json`，
  - 確認真實頁面上的 refs（@eX）與這裡的示意一致，必要時調整。
- 若 KKTIX 啟用了防機器人機制（例如 ReCAPTCHA），可能需要老闆親自完成驗證步驟後，再讓 agent-browser 接手後續流程。
- 老闆有權決定：
  - AI 只讀取資訊（看場次／票價）
  - AI 讀取資訊＋幫忙填到確認頁
