---
name: taobao-image-search
description: 使用淘宝进行以图搜同款、候选比对和加购物车操作。用户提供商品图片并要求“搜同款/找类似款/比价/加入购物车”时使用。优先执行本地脚本（save-taobao-cookie.js、verify-taobao-runner.js）完成全流程；当脚本失败或页面结构变化时回退 browser 工具手动执行。
---

# 淘宝图片搜索技能

## 执行策略

- 优先执行脚本：`save-taobao-cookie.js`、`verify-taobao-runner.js`。
- 脚本失败或页面结构变化时，回退 `browser` 工具。
- 默认不下单、不支付；仅搜索与加购。

## 输入要求

- 必需：本地图片路径或会话中的图片。
- 可选：预算、偏好（品牌/颜色/尺码）、仅搜索或加购。

若缺少关键输入，先补充最少问题（例如“是否直接加购？”、“预算上限是多少？”）。

## 主流程（脚本优先）

### 1. 准备登录态

先检查是否已存在登录态文件：

```bash
ls -la verification-artifacts/taobao-storage-state.json
```

若不存在或登录态过期，执行：

```bash
node save-taobao-cookie.js
```

执行后让用户在打开的淘宝页面完成登录，再在终端回车保存登录态。

### 2. 执行完整链路

```bash
node verify-taobao-runner.js --image /absolute/path/to/image.png
```

该脚本覆盖：

1. 打开淘宝首页。
2. 验证登录状态（未登录即中止并提示先登录）。
3. 打开图搜弹窗并上传图片。
4. 点击弹窗内搜索按钮（优先 `#image-search-upload-button.upload-button.upload-button-active`）。
5. 采样候选商品并进入详情页。
6. 点击加入购物车并检测成功提示。

脚本参数约定：

- `--image, -i`：图片路径（默认 `test.png`）。
- `--headless` / `--headed`：本地调试运行模式。
- `--delay-ms`：为关键步骤追加等待时长（默认 `2000`，慢网可增大到 `4000-8000`）。
- `--engine`：当前本地脚本仅支持 `playwright`。
- `browser` 工具在 OpenClaw 运行时由技能流程调用，不由该本地脚本直接调用。

### 3. 读取验证结果

脚本运行后读取：

- `verification-artifacts/result.json`
- `verification-artifacts/run-log.txt`
- `verification-artifacts/*.png`（流程截图）

关键判定字段：

- `success`：流程是否成功执行。
- `loginCheck.isLoggedIn`：是否登录。
- `addToCart.success`：是否加购成功。
- `addToCart.reason`：失败原因（如有）。

## 回退流程（browser 工具）

仅在脚本执行失败、页面结构变化、或需要人工交互排障时使用。

### 1. 打开淘宝并校验登录

- 打开 `https://www.taobao.com`。
- 校验昵称元素 `.site-nav-login-info-nick` 或 `.member-nick-info` 是否可见。
- 若未登录，提示用户先登录，再继续。

### 2. 上传图片并搜索

- 点击相机/搜同款入口打开上传弹窗。
- 上传图片。
- 只点击弹窗内搜索按钮，优先：
  - `#image-search-upload-button.upload-button.upload-button-active`
  - `.image-search-context-wrapper-active #image-search-upload-button.upload-button.upload-button-active`
  - `.image-search-context-wrapper-active .upload-button.upload-button-active[data-spm='image_search_button']`
- 上述失效时兜底：
  - `.image-search-context-wrapper-active .upload-button:has-text('搜索')`

### 3. 选品与加购

- 分析候选商品并优先选择最相似商品。
- 进入详情页点击“加入购物车”。
- 若强制规格选择，先选默认规格再加购。
- 用页面成功提示确认结果。

## 失败回退建议

- 登录失败：重新运行 `node save-taobao-cookie.js`。
- 上传失败：重新打开图搜弹窗再上传。
- 搜索按钮定位失败：优先使用上述弹窗按钮精确选择器。
- 加购失败：检查规格选择、风控拦截或登录失效。

## 安全边界

- 仅操作用户明确指示的商品。
- 不执行“立即购买”“提交订单”“支付”动作。
- 规格、数量、店铺偏好不明确时先确认。
