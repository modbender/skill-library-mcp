# 測試 Agent Token 流程

## 🧪 生成測試 Token

```bash
# 在 skill repo 執行
npm run generate-token

# 或者手動執行
node generate-fresh-token.ts
```

這會生成一個有效的 JWT token 和完整的 dashboard URL。

## 🔍 測試步驟

### Step 1: 生成 Token
```bash
cd /Users/andrea.unicorn/bloom-identity-skill
npm run generate-token
```

應該會看到：
```
🌐 Dashboard URL:
https://preflight.bloomprotocol.ai/dashboard?token=eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

### Step 2: 複製 URL 到瀏覽器

打開瀏覽器，貼上完整的 URL。

### Step 3: 觀察流程

**預期行為**：
1. ✅ Middleware 允許 access（不跳轉到首頁）
2. ✅ DashboardClient 顯示 "Authenticating..."
3. ✅ Token 被驗證並儲存到 localStorage
4. ✅ URL 變成 `/dashboard`（token 被移除）
5. ✅ Carousel 顯示並自動滑到 agent card
6. ✅ Modal 自動彈出顯示完整 identity card

**如果失敗**：
- ❌ 跳回首頁 → Middleware 問題
- ❌ "Authentication Failed" → Token 驗證失敗
- ❌ "jwt malformed" → Token 格式錯誤
- ❌ 空白頁面 → Frontend 沒 deploy 或 build 失敗

## 🐛 Debug Commands

### 檢查 Frontend Deployment
```bash
# 檢查 Railway logs
railway logs -s bloom-protocol-fe
```

### 檢查 Token 內容
```javascript
// 在 browser console 執行
const token = "YOUR_TOKEN_HERE";
const payload = JSON.parse(atob(token.split('.')[1]));
console.log(payload);
```

應該看到：
```json
{
  "type": "agent",
  "address": "0x...",
  "identity": {
    "personalityType": "The Visionary",
    "tagline": "...",
    ...
  }
}
```

## ✅ Verification Checklist

- [ ] Token 成功生成
- [ ] URL 可以訪問（不跳轉首頁）
- [ ] Token 被驗證（console 有 ✅ log）
- [ ] Agent data 儲存到 localStorage
- [ ] Carousel 顯示 agent card
- [ ] Modal 自動彈出
- [ ] 看到完整的 identity card

## 🚨 已知問題

1. **Frontend build failed** - TypeScript error 已修復（commit a2631bc）
2. **SSG caching** - 已修復（commit a00226e）
3. **JWT_SECRET mismatch** - 已確認相符

## 📦 下一步

如果測試成功：
1. ✅ 整合進 OpenClaw skill
2. ✅ 加上 error handling
3. ✅ 完善 UI feedback

如果測試失敗：
1. 檢查 Railway deployment logs
2. 確認 environment variables
3. Debug frontend auth flow
