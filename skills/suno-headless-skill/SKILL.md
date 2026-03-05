---
name: suno-headless
description: Suno AI 音乐创作助手（无头 Linux 服务器专用版）— 自动登录、创建歌曲、下载音频。通过 Xvfb 虚拟显示在无 GUI 的 Linux 云服务器上运行。当用户要求生成音乐、写歌、创作歌曲、用 Suno 生成 AI 音乐时使用。
metadata: {"openclaw": {"emoji": "🎵", "requires": {"bins": ["google-chrome", "Xvfb"]}}}
---

# 🎵 Suno AI 音乐创作助手（Headless Linux 专用版）

专为 **无图形界面的 Linux 云服务器** 设计，通过 **Xvfb 虚拟显示** 在没有显示器的环境下运行 Chrome GUI 模式，绕过 Google 反自动化检测。

两大核心能力：**账号登录**（通过 Google OAuth）和 **歌曲创作**（自定义歌词+风格+下载）。

---

## 零、前置检查

每次操作前必须先执行环境检查：

```bash
bash {baseDir}/suno-headless/check_env.sh
```

返回码：`0` = 正常已登录 → 可直接创建歌曲；`1` = 缺少依赖 → 安装依赖；`2` = 未登录 → 登录流程。

---

## 一、安装依赖（仅首次）

### 1.1 系统依赖

```bash
# Xvfb 虚拟显示（核心依赖，无 GUI 环境必装）
sudo apt update && sudo apt install -y xvfb

# Google Chrome 浏览器
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable

# 中文字体支持（歌词含中文时需要）
sudo apt install -y fonts-noto-cjk
```

### 1.2 Python 依赖

```bash
cd {baseDir}/suno-headless
pip3 install -r requirements.txt
playwright install
```

---

## 二、登录流程

**⚠️ 重要：不要在 skill 代码中硬编码账号密码！必须先询问用户的凭据。**

提供两种登录方式：
- **方式 A: Cookie 导入（🌟 推荐！完美绕过 Google 安全验证）**
- **方式 B: 邮箱密码直接登录（可能触发 Google 安全验证）**

### 2.1 方式 A: Cookie 导入（推荐）

这是云服务器上最稳定的登录方式，完全绕过 Google 的安全验证。

**操作步骤：**

当需要登录时，向用户说明：

> 🍪 推荐使用 Cookie 导入方式登录（绕过 Google 安全验证）：
>
> **步骤 1**: 在你的本地电脑（有浏览器的）上运行：
> ```bash
> pip install playwright && playwright install
> python3 export_cookies.py
> ```
> 这会打开浏览器，你手动登录 Suno，登录成功后自动导出 Cookie 文件。
>
> **步骤 2**: 把导出的 Cookie 文件上传到服务器固定路径：
> ```bash
> scp <本地导出的Cookie文件> user@your-server:/root/suno_cookie/suno_cookies.json
> ```
>
> **步骤 3**: 上传完成后告诉我，我来导入。

用户上传文件后，执行导入。脚本会自动检测 `/root/suno_cookie/suno_cookies.json` 是否存在，存在则自动导入，无需额外指定参数：

```bash
cd {baseDir}/suno-headless
python3 suno_login.py
```

也可以显式指定 Cookie 文件路径：

```bash
python3 suno_login.py --import-cookies /path/to/cookies.json
```

### 2.2 方式 B: 邮箱密码登录

**⚠️ 注意：云服务器上可能触发 Google 安全验证，推荐优先使用方式 A。**

当需要登录时，**必须先向用户询问**：

> 需要登录 Suno.com（通过 Google 账号）。请提供：
> 1. **Gmail 邮箱地址**
> 2. **Gmail 密码**
>
> ⚠️ 你的凭据仅用于本次登录，不会被存储或传输到任何第三方。

用户提供邮箱和密码后：

```bash
cd {baseDir}/suno-headless
python3 suno_login.py --email "<用户邮箱>" --password "<用户密码>"
```

**Headless Linux 模式说明**：
- 脚本会自动检测无 GUI 环境（无 `$DISPLAY` 变量）
- 自动启动 Xvfb 虚拟显示，在内存中模拟一个假显示器
- Chrome 以 GUI 模式运行（`headless=False`），但屏幕上不显示任何东西
- 这样可以绕过 Google 对 headless 浏览器的检测拦截

### 2.3 检查登录状态

```bash
cd {baseDir}/suno-headless
python3 suno_login.py --check-only
```

退出码 `0` = 已登录，`2` = 未登录。

### 2.4 强制重新登录

```bash
# 方式 A: 重新导入 Cookie
cd {baseDir}/suno-headless
python3 suno_login.py --import-cookies "<新的Cookie文件>"

# 方式 B: 邮箱密码重新登录
cd {baseDir}/suno-headless
python3 suno_login.py --email "<邮箱>" --password "<密码>" --force-login
```

---

## 三、创建歌曲

### 3.1 前置条件

1. 已完成登录（`suno_login.py --check-only` 返回 0）
2. 需要 **Gemini API Key**（用于自动解决 hCaptcha 验证码）

### 3.2 获取 Gemini API Key

如果用户没有 Gemini API Key，引导用户获取：

> 创建歌曲时 Suno 会弹出验证码，需要 Gemini API Key 来自动解决。
> 1. 访问 https://aistudio.google.com/app/apikey
> 2. 点击 "Create API key"
> 3. 复制生成的 Key

获取后保存到环境文件：

```bash
mkdir -p ~/.suno
echo "GEMINI_API_KEY=<用户的key>" > ~/.suno/.env
```

或通过环境变量：

```bash
export GEMINI_API_KEY="<用户的key>"
```

### 3.3 hCaptcha 兼容补丁

首次使用前需运行一次（Suno 使用自定义 hCaptcha 域名，需打补丁）：

```bash
cd {baseDir}/suno-headless
python3 patch_hcaptcha.py
```

### 3.4 创建歌曲命令

```bash
cd {baseDir}/suno-headless
python3 suno_create_song.py \
  --lyrics "<歌词内容>" \
  --style "<音乐风格标签>" \
  --title "<歌曲标题>" \
  --output-dir "<下载目录>"
```

也可以从文件读取歌词：

```bash
cd {baseDir}/suno-headless
python3 suno_create_song.py \
  --lyrics-file "<歌词文件路径>" \
  --style "<音乐风格标签>" \
  --title "<歌曲标题>"
```

**Headless 模式说明**：
- `suno_create_song.py` 会自动检测无 GUI 环境
- 自动启动 Xvfb 虚拟显示，Chrome 以 GUI 模式在虚拟显示中运行
- 脚本结束后自动关闭虚拟显示，无需手动操作

### 3.5 参数说明

| 参数 | 说明 | 必填 | 默认值 |
|------|------|:---:|--------|
| `--lyrics` | 歌词内容（与 `--lyrics-file` 二选一） | ✅ | - |
| `--lyrics-file` | 歌词文件路径（与 `--lyrics` 二选一） | ✅ | - |
| `--style` | 音乐风格标签（英文，逗号分隔） | ❌ | `rock, electric guitar, energetic, male vocals` |
| `--title` | 歌曲标题 | ❌ | `My Song` |
| `--output-dir` | MP3 下载目录 | ❌ | `{baseDir}/output_mp3` |
| `--gemini-key` | Gemini API Key（也可通过环境变量或 ~/.suno/.env） | ❌ | 自动读取 |
| `--verbose` / `-v` | 详细输出模式（实时打印所有中间步骤） | ❌ | 关闭（默认只输出最终摘要） |

> **📋 输出行为说明**：默认情况下，所有脚本（`suno_create_song.py`、`suno_login.py`、`export_cookies.py`）只在完成时输出一条简洁的摘要，中间步骤的详细日志写入 `{baseDir}/suno-headless/logs/` 目录。如需实时查看所有中间步骤，请添加 `--verbose` 或 `-v` 参数。

### 3.6 音乐风格标签参考

常用风格标签（英文，可自由组合）：

- **流派**: rock, pop, jazz, blues, electronic, hip-hop, R&B, classical, folk, metal, country, reggae, latin, indie
- **乐器**: electric guitar, acoustic guitar, piano, synthesizer, drums, bass, violin, saxophone, trumpet
- **情绪**: energetic, emotional, melancholic, upbeat, dark, dreamy, aggressive, peaceful, romantic
- **人声**: male vocals, female vocals, choir, rap, whisper, powerful vocals, falsetto
- **语言**: chinese, japanese, korean, english, spanish
- **其他**: fast tempo, slow tempo, instrumental, lo-fi, cinematic, epic

**示例**：
- 摇滚: `rock, electric guitar, energetic, male vocals, chinese`
- 抒情: `pop, piano, emotional, female vocals, slow tempo, chinese`
- 电子: `electronic, synthesizer, upbeat, fast tempo, dance`
- 说唱: `hip-hop, rap, bass, drums, energetic, chinese`

---

## 四、完整使用示例

### 示例：在 Linux 云服务器上创建中文摇滚歌曲

```bash
# 1. 检查环境（会自动检测 Xvfb、Chrome 等）
bash {baseDir}/suno-headless/check_env.sh

# 2. 如果未登录，使用 Cookie 导入方式登录（推荐）
#    步骤 1: 在本地电脑运行 export_cookies.py 导出 Cookie
#    步骤 2: scp <Cookie文件> user@server:/root/suno_cookie/suno_cookies.json
#    步骤 3: 服务器上运行登录脚本（自动检测默认路径并导入）
cd {baseDir}/suno-headless
python3 suno_login.py

# 或者使用邮箱密码方式（可能触发 Google 安全验证）
# python3 suno_login.py --email "user@gmail.com" --password "password123"

# 3. 确保 hCaptcha 补丁已应用
python3 patch_hcaptcha.py

# 4. 创建歌曲（自动使用 Xvfb 虚拟显示）
python3 suno_create_song.py \
  --lyrics "窗外的麻雀 在电线杆上多嘴
你说这一句 很有夏天的感觉
手中的铅笔 在纸上来来回回
我用几行字形容你是我的谁" \
  --style "rock, electric guitar, energetic, male vocals, chinese" \
  --title "七里香摇滚版"
```

---

## 五、与原版 suno skill 的区别

| 特性 | suno（原版） | suno-headless（本版） |
|------|-------------|---------------------|
| 目标环境 | macOS / 有 GUI 的 Linux | **无 GUI 的 Linux 云服务器** |
| 显示方式 | 弹出真实 Chrome 窗口 | **Xvfb 虚拟显示（内存模拟）** |
| 额外依赖 | 无 | `xvfb` + `PyVirtualDisplay` |
| 登录 Xvfb | ✅ 已支持 | ✅ 已支持 |
| 创建歌曲 Xvfb | ❌ 不支持 | ✅ **已支持** |
| 环境检查 | 基础检查 | **增加 Xvfb/Chrome/字体检查** |

---

## 六、技术原理

### Xvfb 虚拟显示方案

```
┌─────────────────────────────────────────┐
│          Linux 云服务器（无显示器）         │
│                                         │
│  ┌─────────────┐    ┌────────────────┐  │
│  │   Xvfb      │    │  Chrome        │  │
│  │ (虚拟显示器) │◄───│ (GUI 模式)     │  │
│  │ :99 1280x800│    │ headless=False │  │
│  └─────────────┘    └────────────────┘  │
│        ▲                    │           │
│        │              自动操作 Suno.com   │
│   PyVirtualDisplay          │           │
│   自动管理生命周期           ▼           │
│                     ┌────────────────┐  │
│                     │ 歌曲生成+下载   │  │
│                     └────────────────┘  │
└─────────────────────────────────────────┘
```

- **为什么不用 headless=True？** Google OAuth 会检测到 headless 浏览器并拒绝登录
- **Xvfb 方案**：在内存中创建虚拟 X11 显示，Chrome 以为自己有真实 GUI，Google 无法检测到自动化
- **自动检测**：脚本检查 `$DISPLAY` 环境变量，无 GUI 时自动启用 Xvfb
- **资源占用**：Xvfb 仅占用极少内存，脚本结束后自动释放

### 登录方案
- 使用 Playwright + 真实 Chrome 浏览器 (`channel='chrome'`)
- `persistent context` 保持浏览器状态（cookies、localStorage）
- `headless=False` + Xvfb 虚拟显示绕过 Google 反自动化
- 首次登录后 persistent context 自动保持会话

### 歌曲创建方案
- 浏览器自动化操作 suno.com/create 页面
- hcaptcha-challenger + Gemini API 自动解决 hCaptcha 验证码
- 通过拦截浏览器网络响应捕获新生成的 clip ID
- 通过 Suno 内部 API (`studio-api.prod.suno.com`) 轮询歌曲生成状态
- 生成完成后自动下载 MP3 文件

### 文件结构

```
suno-headless/
├── suno_login.py          # 登录工具（Google OAuth / Cookie 导入 + Xvfb）
├── suno_create_song.py    # 歌曲创建+下载工具（Xvfb 支持）
├── export_cookies.py      # Cookie 导出工具（在本地电脑上运行）
├── output_manager.py      # 输出管理器（控制日志和摘要）
├── patch_hcaptcha.py      # hCaptcha 域名兼容补丁
├── check_env.sh           # 环境检查脚本（含 Xvfb/Chrome 检查）
├── requirements.txt       # Python 依赖（含 PyVirtualDisplay）
└── SKILL.md               # 本文档
```

---

## 七、注意事项

1. **不要硬编码账号密码** — 每次都需要询问用户（推荐优先使用 Cookie 导入方式）
2. **必须安装 Xvfb** — `sudo apt install -y xvfb`，否则无法在无 GUI 环境运行
3. **必须安装真实 Chrome** — Playwright 自带的 Chromium 可能被 Google 检测
4. Suno 免费账号每天有积分限制，每首歌消耗约 100 积分
5. 歌曲生成通常需要 1-3 分钟
6. 每次创建会生成 2 首不同版本的歌曲
7. 如果遇到 Google 登录被拒（rejected），等待 10-30 分钟后重试
8. Gemini API 免费额度：每分钟 15 次请求，每天 1500 次
9. hCaptcha 可能需要多次尝试，成功率取决于 Gemini 模型的图片识别能力

## 八、故障排查

```bash
# 检查环境（含 Xvfb 状态）
bash {baseDir}/suno-headless/check_env.sh

# 手动测试 Xvfb 是否正常
Xvfb :99 -screen 0 1280x800x24 &
DISPLAY=:99 google-chrome --no-sandbox --version
kill %1

# 查看登录截图
ls -la /tmp/suno_debug_*.png

# 检查 persistent context
ls -la ~/.suno/chrome_gui_profile/

# 查看 cookies
python3 -c "import json; d=json.load(open('$HOME/.suno/cookies.json')); print(f'{len(d)} cookies')"

# 查看 Gemini API Key
cat ~/.suno/.env

# 查看下载的歌曲
ls -la {baseDir}/output_mp3/
```
