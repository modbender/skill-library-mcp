# Browser Ops（浏览器操作）

## 启动 AdsPower 浏览器（必须最先执行）

> **在使用任何 browser 工具之前，必须先运行此脚本启动 AdsPower 浏览器实例。** 未启动就调用 browser 工具会因无可用 CDP 端点而失败。

```bash
python {baseDir}/scripts/adspower_browser.py open \
  --user-id <USER_ID> --cdp-port <CDP_PORT>
```

- 确认输出中 `debug_port` 与预期端口一致
- 若返回 error，停止并报告

## 连接并导航

- **确认 AdsPower 浏览器已启动后**，用 browser 工具连接到 `profile=<USER_ID>`（CDP）
- 导航到 `https://www.linkedin.com/feed/`

## 登录检测

- **已登录**：URL 包含 `/feed/` 且可见 Feed 内容 → 继续执行
- **未登录**：URL 含 `/login` 或 `/checkpoint` → 尝试点击已保存账号登录
  - 若出现验证码/二次验证 → 立即停止（按风控流程处理）

## 关闭 AdsPower 浏览器

```bash
python {baseDir}/scripts/adspower_browser.py close \
  --user-id <USER_ID>
```

## 交互确认原则

点击任何交互按钮（Like、Connect、Follow 等）后：

1. 等待 2-3 秒
2. 检查按钮状态是否变化（pressed/active/数量变化）
3. **已生效** → 继续
4. **未生效** → 放弃该操作，继续后续 plan，不要连续重试（避免触发风控）

在日志中如实记录即可（如"点了 Like 但未确认生效"），不需要分析原因。

## 超时重试

任何 browser 操作（导航、点击、快照等）如果超时或返回网络错误：

1. 等待 3-5 秒后重试同一操作
2. 最多重试 **2 次**
3. 连续 2 次仍失败 → 视为异常，停止当前 plan、关闭浏览器，并在日志中记录失败原因

> 注意：重试仅针对超时/网络类错误。如果是风控信号（验证码、异常活动等），不要重试，直接走停止流程。

## 常见问题

- **browser start 报 attachOnly**：直接用 `profile=<USER_ID>` 连接 CDP，不要启动新的 profile
- **固定 targetId**：LinkedIn iframe/tab 多，尽量在同一个 targetId 连续操作
