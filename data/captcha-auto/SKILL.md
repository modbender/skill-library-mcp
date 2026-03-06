---
name: captcha-auto
description: 智能验证码自动识别 Skill - 混合模式（本地 Tesseract OCR + 阿里云千问 3 VL Plus）。支持两阶段输入框查找、安全隐私警告。用于网页自动化中的验证码识别、填写和提交。
---

# Captcha Auto Skill - 混合模式 v1.0.7

利用 **本地 OCR + 视觉大模型降级** 智能识别网页验证码，平衡成本与准确率。

**实测成功率：6/6 (100%)** - 已在多个真实网站验证（国家统计局、Telerik、Digivarsity 等）

---

## ⚠️ 重要：安装路径说明

** Clawhub 默认安装到当前工作目录的 `./skills` 子目录！**

### ✅ 正确的安装方式

```bash
# 方式 1：进入 workspace 目录安装（推荐）
cd ~/.openclaw/workspace
clawhub install captcha-auto

# 方式 2：使用 --workdir 参数（任何目录都可以）
clawhub install captcha-auto --workdir ~/.openclaw/workspace

# 方式 3：设置环境变量（永久生效）
export CLAWHUB_WORKDIR=~/.openclaw/workspace
clawhub install captcha-auto
```

### ❌ 错误的安装方式

```bash
# 不要在 home 目录直接运行！
cd ~
clawhub install captcha-auto  # 会安装到 ~/skills/captcha-auto ❌
```

### 验证安装位置

```bash
# 正确位置
ls -la ~/.openclaw/workspace/skills/captcha-auto/

# 如果装错了（在 ~/skills/），删除并重新安装
rm -rf ~/skills/captcha-auto
cd ~/.openclaw/workspace
clawhub install captcha-auto
```

---

---

## ⚠️ 安全与隐私警告

**安装前请仔细阅读：**

### 🔒 1. 截图会发送到第三方 API
- 本技能会截取**网页全屏截图**并发送到阿里云 DashScope API
- ❌ **不要**在包含密码、银行卡、个人信息的页面使用
- ✅ **仅**在验证码页面使用
- 📸 截图仅用于 API 识别，不会存储或上传到其他服务

### 🔑 2. 必需配置 API Key
- 环境变量：`VISION_API_KEY`
- 或配置文件：`~/.openclaw/openclaw.json`
- 或命令行参数：`--api-key`
- ✅ **无硬编码凭证** - API Key 完全由用户控制

### 🌐 3. 需要 Chrome 浏览器
- 系统必须安装 Google Chrome 或 Chromium
- 支持 macOS、Linux、Windows

---

## ⚠️ 必需配置

### 视觉模型 API（降级方案必需）

**本 Skill 需要阿里云千问 3 VL Plus API Key**，用于当本地 OCR 失败时的降级识别。

**推荐配置（阿里云千问 3 VL Plus）：**

```bash
export VISION_API_KEY="sk-your-api-key"
export VISION_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export VISION_MODEL="qwen3-vl-plus"
```

**说明**：
- `qwen3-vl-plus` 是阿里云千问 3 视觉模型，国产性价比最高的视觉模型
- Base URL 使用阿里云 DashScope 兼容模式
- API Key 需在阿里云 DashScope 控制台申请

### 其他配置方式

#### OpenClaw 配置

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "models": {
    "providers": {
      "bailian": {
        "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "apiKey": "sk-your-api-key"
      }
    }
  }
}
```

#### 命令行参数

```bash
node scripts/run.mjs --url="https://example.com" --api-key="sk-xxx" --model="qwen3-vl-plus"
```

---

## 功能特性

- 🎯 **混合识别** - 本地 Tesseract OCR 优先，失败自动降级视觉模型
- 💰 **成本优化** - 简单验证码本地解决（零成本），复杂情况用视觉模型
- 🔍 **自动定位** - 智能查找验证码输入框和提交按钮（支持 iframe）
- ✍️ **自动填写** - 识别后自动填写并提交
- 📸 **全程记录** - 截图保存每一步操作
- 🌐 **通用适配** - 支持任何包含验证码的网页
- ✅ **实测验证** - 已在 6 个真实网站测试，成功率 100%

### 🧪 测试成功案例

| 网站 | 验证码类型 | 结果 |
|------|-----------|------|
| captcha.com/demos | 标准文本 | ✅ |
| captcha-generator-basiakedz.netlify.app | 随机文本 | ✅ |
| tjy.stats.gov.cn (国家统计局) | 数字验证码 | ✅ |
| solvecaptcha.com/demo | 字母数字混合 | ✅ |
| demos.telerik.com/aspnet-ajax/captcha | ASP.NET 验证码 | ✅ |
| aibe.digivarsity.online | 用户认证验证码 | ✅ |

---

## 快速开始

### 1. 从 Clawhub 安装

**重要：必须在 `~/.openclaw/workspace` 目录下运行安装命令！**

```bash
# ✅ 正确：在 workspace 目录安装
cd ~/.openclaw/workspace
clawhub install captcha-auto

# ❌ 错误：在 home 目录安装（会装到 ~/skills/）
cd ~
clawhub install captcha-auto  # 不要这样！
```

**验证安装位置：**
```bash
ls -la ~/.openclaw/workspace/skills/captcha-auto/
```

### 2. 安装依赖

```bash
cd ~/.openclaw/workspace
npm install
```

### 3. 配置视觉模型 API Key

```bash
export VISION_API_KEY="sk-your-api-key"
export VISION_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export VISION_MODEL="qwen3-vl-plus"
```

### 3. 运行

```bash
node skills/captcha-auto/scripts/run.mjs --url="https://example.com/login"
```

### 4. 查看结果

运行后生成截图文件（保存在 `~/.openclaw/workspace/`）：

- `smart_captcha_page.png` - 原始页面截图
- `smart_captcha_filled.png` - 填写验证码后的截图
- `smart_captcha_result.png` - 提交后的结果截图

---

## 使用方法

### 从 Clawhub 安装（再次强调安装位置）

```bash
# ⚠️ 必须在 ~/.openclaw/workspace 目录下运行！
cd ~/.openclaw/workspace
clawhub install captcha-auto
```

### 基本用法

```bash
# 混合模式（本地 OCR 优先，失败降级视觉模型）
node skills/captcha-auto/scripts/run.mjs --url="https://example.com/login"
```

### 自定义配置

```bash
# 指定输出前缀
node scripts/run.mjs --url="https://example.com" --prefix="my_login"

# 直接使用视觉模型（跳过本地 OCR）
node scripts/run.mjs --url="https://example.com" --skip-local

# 命令行覆盖配置
node scripts/run.mjs --url="https://example.com" --api-key="sk-xxx" --model="gpt-4o"

# JSON 输出（方便程序解析）
node scripts/run.mjs --url="https://example.com" --json
```

### 在其他脚本中使用

```javascript
import { recognizeCaptcha } from './skills/captcha-auto/index.mjs';

const result = await recognizeCaptcha({
  url: 'https://example.com/login',
  outputPrefix: 'my_test',
  apiKey: 'sk-xxx',
  baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  model: 'qwen3-vl-plus'
});

if (result.success) {
  console.log(`✅ 验证码：${result.text}`);
  console.log(`识别方式：${result.method}`);
} else {
  console.error(`❌ 失败：${result.error}`);
}
```

---

## 输出格式

### 人类可读模式（默认）

```
🤖 Captcha Auto Skill v1.0.2 (混合模式)
============================================================
目标：https://example.com/login
视觉模型：qwen3-vl-plus
============================================================

🔍 尝试本地 Tesseract OCR 识别...
   识别进度：45%
   识别结果："ABC123" (置信度：52.3%)
   ⚠️ 本地 OCR 置信度过低，需要降级到视觉模型
⚠️ 本地 OCR 不可靠，降级到视觉模型...
🧠 降级到视觉模型识别...
✅ 视觉模型识别成功：ABC123

✅ 完成！验证码：ABC123
识别方式：视觉模型
```

### JSON 模式（`--json`）

```json
{
  "success": true,
  "text": "ABC123",
  "method": "vision",
  "analysis": {
    "captchaText": "ABC123",
    "captchaLocation": "登录框右侧",
    "inputLocation": "验证码图片左侧",
    "buttonLocation": "输入框下方",
    "buttonText": "登录"
  },
  "screenshots": {
    "page": "/Users/xxx/.openclaw/workspace/smart_captcha_page.png",
    "filled": "/Users/xxx/.openclaw/workspace/smart_captcha_filled.png",
    "result": "/Users/xxx/.openclaw/workspace/smart_captcha_result.png"
  },
  "metadata": {
    "url": "https://example.com/login",
    "model": "qwen3-vl-plus",
    "timestamp": "2026-02-24T12:00:00Z"
  }
}
```

---

## 工作原理

```
1. 打开目标网页并截图
2. 第一层：本地 Tesseract OCR 识别
   - 置信度 >= 60% → 使用结果
   - 置信度 < 60% → 降级
3. 第二层：视觉模型分析截图
   - 调用阿里云千问 3 VL Plus
   - 返回验证码文字和位置信息
4. 自动查找输入框并填写
5. 自动点击提交按钮
6. 截图记录结果
```

---

## 优势与局限

### 优势
- ✅ **成本优化** - 简单验证码本地解决（零 token 消耗）
- ✅ **高成功率** - 视觉模型兜底，复杂验证码也能处理
- ✅ **通用性强** - 无需分析网页结构，自动适配
- ✅ **高性价比** - 使用阿里云千问 3 VL Plus（国产性价比最高）

### 局限
- ⚠️ **需要 API Key** - 视觉模型降级需要配置第三方 API
- ⚠️ **本地 OCR 限制** - 严重扭曲/干扰线的验证码本地识别率低
- ⚠️ **Canvas 验证码** - 某些动态绘制的验证码可能不支持
- ⚠️ **Token 成本** - 视觉模型调用消耗 token（约 0.01-0.05 元/次）

---

## 故障排除

### 本地 OCR 总是失败

**原因**：验证码过于复杂（扭曲、干扰线、背景噪声）

**解决**：使用 `--skip-local` 直接用视觉模型

```bash
node scripts/run.mjs --url="https://example.com" --skip-local
```

### API 401 错误

**检查**：`VISION_API_KEY` 是否正确

```bash
echo $VISION_API_KEY
```

### API 404 错误

**检查**：`VISION_BASE_URL` 是否正确

```bash
echo $VISION_BASE_URL
# 应为：https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 找不到 Chrome 浏览器

**macOS**：安装 Google Chrome
```bash
# 下载地址：https://www.google.com/chrome/
```

**Linux**：安装 Chromium
```bash
sudo apt install chromium-browser
```

---

## 版本历史

- **v1.0.7** - 统一版本号、完善安全警告（强调无硬编码凭证）、添加跨平台支持说明
- **v1.0.6** - 更新文档：添加测试成功案例表、增强安全警告说明、修复路径引用
- **v1.0.5** - 优化输入框查找逻辑、改进按钮点击策略
- **v1.0.4** - 添加 iframe 支持、优化 accessibility 分析
- **v1.0.3** - 修复元数据匹配（env: VISION_API_KEY, bins: node + google-chrome）；添加安全与隐私警告（截图会发送到第三方 API）；运行时显示安全提示
- **v1.0.2** - 混合模式（本地 Tesseract OCR + 阿里云千问 3 VL Plus 视觉模型降级）；两阶段输入框查找策略；支持无 placeholder 的验证码输入框

---

## 依赖

### 必需

- **Node.js >= 18** - 运行环境
- **playwright-core** - 浏览器自动化
- **tesseract.js** - 本地 OCR 引擎
- **Chrome/Chromium** - 系统需安装浏览器
- **视觉模型 API Key** - Qwen/GPT-4V/Claude 等（降级必需）

### 环境检查

```bash
# 检查 Node.js
node --version  # 需 >= 18

# 检查 Chrome（macOS）
ls /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome

# 检查 API Key
echo $VISION_API_KEY
```

---

## 授权

MIT
