# Camoufox Deploy

一键部署 camoufox + agent-browser 反检测浏览器工具链。

## 快速开始

### 一键安装

```bash
bash ~/.openclaw/workspace/skills/camoufox-deploy/scripts/install.sh
```

### 手动安装

如果一键安装遇到问题，可以按以下步骤手动安装：

#### 1. 安装依赖

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 camoufox
uv pip install camoufox --system

# 下载 camoufox 浏览器
python3 -c "from camoufox.sync_api import Camoufox; Camoufox()"
```

#### 2. 安装并修改 agent-browser

```bash
# 安装 agent-browser
npm install -g agent-browser

# 找到安装位置
AGENT_BROWSER_PATH=$(npm root -g)/agent-browser
echo $AGENT_BROWSER_PATH
```

#### 3. 修改源码

编辑 `$AGENT_BROWSER_PATH/src/browser.ts`，找到 `getBrowserType` 函数并修改为：

```typescript
private getBrowserType(executablePath: string): 'chromium' | 'firefox' {
  const lowerPath = executablePath.toLowerCase();
  if (lowerPath.includes('firefox') || lowerPath.includes('camoufox')) {
    return 'firefox';
  }
  return 'chromium';
}
```

#### 4. 重新编译

```bash
cd $AGENT_BROWSER_PATH
npm install
npm run build
```

## 使用方法

### 使用 camoufox 路径运行

```bash
# macOS
agent-browser --executable-path ~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox

# Linux
agent-browser --executable-path ~/.cache/camoufox/camoufox
```

### 在代码中使用

```typescript
import { AgentBrowser } from 'agent-browser';

const browser = new AgentBrowser({
  executablePath: '/Users/YOUR_USERNAME/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox',
  headless: false
});

await browser.goto('https://example.com');
```

## 关键路径

| 组件 | macOS 路径 |
|------|-----------|
| camoufox | `~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox` |
| agent-browser | `$(npm root -g)/agent-browser` |

## 故障排除

### camoufox 未找到

```bash
# 确认路径
ls -la ~/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox

# 手动下载
python3 -c "from camoufox.sync_api import Camoufox; Camoufox()"
```

### agent-browser 仍使用 chromium

```bash
# 检查修改是否生效
cat $(npm root -g)/agent-browser/dist/browser.js | grep -i camoufox

# 如果没有输出，需要重新执行修改步骤
```

### Rust 编译错误

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

## 参考

- [camoufox GitHub](https://github.com/daijro/camoufox)
- [agent-browser GitHub](https://github.com/browser-use/agent-browser)
