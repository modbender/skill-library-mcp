# taobao-image-search-skill

淘宝以图搜同款与加购技能（脚本优先，browser 兜底）。

## 功能

- 基于图片在淘宝搜索同款/相似商品
- 自动进入候选商品详情页并尝试加入购物车
- 自动校验登录状态，未登录时提示先登录
- 产出结构化结果与截图，便于回归验证

## 快速开始

### 1. 安装依赖（如未安装）

```bash
npx playwright install chromium
```

### 2. 准备测试图片

默认使用仓库内 `test.png`。也可以在执行时传入任意本地图片路径：

```bash
node verify-taobao-runner.js --image /absolute/path/to/your-image.png
```

### 3. 首次登录并保存状态

```bash
node save-taobao-cookie.js
```

脚本会打开浏览器。登录淘宝后回到终端按回车，保存登录态到：

- `verification-artifacts/taobao-storage-state.json`

### 4. 执行完整验证流程

```bash
node verify-taobao-runner.js
```

传入指定图片：

```bash
node verify-taobao-runner.js --image ./test.png
```

默认是有界面模式；如需 headless：

```bash
node verify-taobao-runner.js --image ./test.png --headless
```

可选参数：

- `--image, -i`：图片路径（默认 `test.png`）
- `--headless` / `--headed`：是否无头运行（默认 `--headed`，除非设置 `PW_HEADLESS=1`）
- `--out-dir`：输出目录（默认 `verification-artifacts`）
- `--state`：登录态文件路径（默认 `verification-artifacts/taobao-storage-state.json`）
- `--engine`：当前仅支持 `playwright`（OpenClaw 的 `browser` 工具由技能运行时调用，不通过该本地脚本）

## 输出结果

- `verification-artifacts/result.json`：结构化执行结果
- `verification-artifacts/run-log.txt`：执行日志
- `verification-artifacts/*.png`：关键步骤截图

关键字段：

- `success`：流程是否整体执行成功
- `loginCheck.isLoggedIn`：登录状态
- `addToCart.success`：是否检测到加购成功提示
- `addToCart.reason`：失败原因（如有）

## 与 SKILL 的关系

- `SKILL.md`：给 OpenClaw/Codex 的技能说明（脚本优先）
- `verify-taobao-runner.js`：本地自动化验证主脚本
- `save-taobao-cookie.js`：登录态保存脚本

## 常见问题

- 未登录报错：重新执行 `node save-taobao-cookie.js`
- 找不到弹窗搜索按钮：淘宝页面结构变更，优先按 `SKILL.md` 的 browser 回退流程手动验证
- 加购失败：通常是规格选择、风控或登录态过期导致
