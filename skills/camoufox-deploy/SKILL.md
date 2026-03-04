---
name: camoufox-deploy
description: One-click deployment of camoufox anti-detection browser with modified agent-browser. Patches agent-browser to auto-detect camoufox/firefox from executable path instead of defaulting to chromium.
---

# camoufox-deploy

🚀 一键部署 camoufox + agent-browser 反检测浏览器工具链。

## 解决的问题

agent-browser 默认只支持 Chromium，但我们需要：
1. **反检测能力**: camoufox 能绕过 Bilibili、Cloudflare 等风控
2. **Firefox 支持**: 修改 agent-browser 自动识别 camoufox/firefox 路径
3. **一键部署**: 自动化繁琐的安装、修改、编译流程

## 概述

这个 skill 帮助用户快速部署：
- **camoufox**: 基于 Firefox 的反检测浏览器
- **agent-browser**: 浏览器自动化工具（修改后支持 camoufox）

## 关键修改点

agent-browser 默认使用 Chromium，需要修改以支持 camoufox/firefox：

1. **修改 browser.ts**: 自动检测 executablePath 中的 camoufox/firefox 关键字
2. **正确的 camoufox 路径**: `~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox` (macOS)
3. **重新编译**: 需要重新编译 Rust CLI 并替换 npm 包中的二进制

## 使用方法

### 一键安装

运行安装脚本：

```bash
bash ~/.openclaw/workspace/skills/camoufox-deploy/scripts/install.sh
```

这个脚本会自动完成：
1. 安装 uv (Python 包管理器)
2. 用 uv 安装 camoufox Python 包
3. 下载 camoufox 浏览器二进制
4. 安装 agent-browser npm 包
5. 修改 agent-browser 源码（自动检测 firefox/camoufox）
6. 重新编译 Rust CLI
7. 替换系统版本

### 手动步骤（如果需要）

#### 1. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 安装 camoufox

```bash
uv pip install camoufox --system
```

#### 3. 下载 camoufox 浏览器

```bash
python3 -c "from camoufox.sync_api import Camoufox; Camoufox()"
```

或手动下载：
```bash
# macOS 路径
~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox
```

#### 4. 安装 agent-browser

```bash
npm install -g agent-browser
```

#### 5. 找到并修改 browser.ts

找到 agent-browser 的源码目录：

```bash
# 全局安装位置
npm root -g
cd $(npm root -g)/agent-browser

# 或克隆源码
git clone https://github.com/browser-use/agent-browser.git
cd agent-browser
```

修改 `src/browser.ts` 中的 `getBrowserType` 函数：

```typescript
private getBrowserType(executablePath: string): 'chromium' | 'firefox' {
  const lowerPath = executablePath.toLowerCase();
  if (lowerPath.includes('firefox') || lowerPath.includes('camoufox')) {
    return 'firefox';
  }
  return 'chromium';
}
```

#### 6. 重新编译

```bash
npm install
npm run build
```

#### 7. 替换系统版本

```bash
# 找到全局安装位置
GLOBAL_PATH=$(npm root -g)/agent-browser

# 备份原版本
cp -r "$GLOBAL_PATH" "${GLOBAL_PATH}.backup"

# 替换为修改版本
cp -r ./ "$GLOBAL_PATH/"
```

## 验证安装

```bash
# 检查 camoufox
camoufox --version

# 检查 agent-browser
agent-browser --version

# 运行测试
agent-browser --executable-path ~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox
```

## 故障排除

### 问题: camoufox 找不到

**解决**: 确认路径正确
```bash
ls ~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox
```

### 问题: agent-browser 仍使用 chromium

**解决**: 确认修改生效
```bash
cat $(npm root -g)/agent-browser/dist/browser.js | grep -A5 "getBrowserType"
```

### 问题: Rust 编译失败

**解决**: 安装 Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

## 文件位置

| 文件 | 位置 |
|------|------|
| camoufox 可执行文件 | `~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox` |
| agent-browser 全局安装 | `$(npm root -g)/agent-browser` |
| 安装脚本 | `~/.openclaw/workspace/skills/camoufox-deploy/scripts/install.sh` |

## 参考

- [camoufox 文档](https://github.com/daijro/camoufox)
- [agent-browser 仓库](https://github.com/browser-use/agent-browser)
