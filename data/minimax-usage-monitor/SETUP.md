# MiniMax Coding Plan 用量监控 - 环境配置指南

本工具用于监控 MiniMax Coding Plan 的用量情况。

## 前置要求

1. MiniMax Coding Plan 订阅
2. Windows 10/11 系统

---

## 步骤 1: 获取 API Key

1. 访问 [MiniMax 控制台](https://platform.minimaxi.com/user-center/payment/coding-plan)
2. 登录您的账户
3. 点击 **创建 Coding Plan Key** (或 "创建新的 API Key")
4. 复制生成的 Key

---

## 步骤 2: 设置环境变量

### 方法 A: PowerShell (推荐)

**临时生效 (当前终端)：**
```powershell
$env:MINIMAX_CODING_KEY = "您的API Key"
```

**永久生效 (用户级)：**
```powershell
[System.Environment]::SetEnvironmentVariable("MINIMAX_CODING_KEY", "您的API Key", "User")
```

### 方法 B: 图形界面

1. 按 `Win + R`，输入 `sysdm.cpl`，回车
2. 切换到 **高级** 选项卡
3. 点击 **环境变量**
4. 在 **用户变量** 区点击 **新建**
5. 填写：
   - 变量名：`MINIMAX_CODING_KEY`
   - 变量值：您的 API Key
6. 点击确定保存

---

## 步骤 3: 验证配置

打开 PowerShell，运行：

```powershell
python scripts/check_minimax.py
```

如果配置正确，将显示类似：

```
=== MiniMax Coding Plan Usage ===
Model: MiniMax-M2
Total Available: 1500 prompts
Used (all windows): 500 (33.3%)
Remaining: 1000 prompts (66.7%)
Reset in: 4h 30m
Status: [OK]
```

---

## 故障排除

### "API Key not found"

确保：
1. 环境变量已正确设置
2. 已重新打开 PowerShell 窗口（环境变量更新后需要）

### "API error: 401"

API Key 可能已过期或无效，请到后台重新生成。

---

## 安全说明

- API Key 存储在您的本地环境变量中，不会写入任何配置文件
- 请勿将 API Key 分享给他人
- 定期更换 API Key 以确保安全
