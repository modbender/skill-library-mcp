# Terminal Killer - 集成指南

**Version:** 1.2.0  
**Last Updated:** 2026-03-02

## 🔒 安全说明

> **⚠️ VirusTotal 警告说明**
> 
> 本技能可能被 VirusTotal 标记为"可疑"，原因是使用了 `execSync` 执行 shell 命令。**这是误报**。
> 
> - ✅ **这是核心功能**：本技能的设计目的就是智能检测并执行用户输入的 shell 命令
> - ✅ **无外部 API 调用**：所有操作都在本地完成，不向任何外部服务器发送数据
> - ✅ **无数据外传**：不收集、不上传任何用户信息
> - ✅ **透明开源**：所有源码可见，作者 Cosper (cosperypf@163.com)
> 
> VirusTotal 的自动检测将 `execSync`、读取配置文件等行为标记为风险模式，但这些对于本技能的功能是必需的。

## 快速开始

Terminal Killer 是一个智能命令路由器，自动判断用户输入是 shell 命令还是 AI 任务。

## 📝 更新日志

### v1.2.0 (2026-03-02)

**安全说明更新：**
- 在 `clawhub.json` 中添加 `securityNote` 字段，说明 VirusTotal 误报原因
- 在 `README.md` 中添加详细安全说明
- 明确声明：无外部 API 调用、无数据外传、本地执行

### v1.1.0 (2026-02-28)

**核心改进：**

1. **✅ 忠实执行原命令**
   - 命令原样执行，不做任何修改
   - 不添加参数、不优化、不截断
   - 保留原始输出（包括进度条、特殊字符等）

2. **🪟 交互式命令检测**
   - 自动识别交互式命令（`adb shell`、`ssh`、`docker exec -it` 等）
   - 自动打开新 Terminal 窗口执行
   - 主会话保持空闲
   - 加载完整 shell 环境（~/.zshrc 等）

3. **📜 长输出处理**
   - 检测超过 2000 字节的输出
   - 显示 200 字符预览
   - 提示用户是否在新 Terminal 窗口查看
   - 避免界面渲染问题

### v1.0.0 (2026-02-28)

**初始版本：**
- 智能命令检测
- 跨平台支持
- 环境变量加载
- 危险命令检测

## 工作原理

```
用户输入 → detectCommand() → 决策
                              ↓
            ┌─────────────────┼─────────────────┐
            ↓                 ↓                 ↓
        EXECUTE            ASK              LLM
        (直接执行)      (询问确认)      (交给 AI)
```

## 检测规则

| 规则 | 说明 | 分值 |
|------|------|------|
| 系统内置命令 | 匹配平台内置命令列表 | +3 |
| 常见开发工具 | adb, git, docker, kubectl 等 | +2 |
| PATH 可执行文件 | 检查 `$PATH` 中是否存在 | +3 |
| History 匹配 | 匹配 shell 历史记录 | +2 |
| Shell 操作符 | 包含 `\|`, `>`, `&&` 等 | +2 |
| 路径引用 | 包含 `/`, `~/`, `$VAR` 等 | +2 |
| 短命令 | 少于 10 个单词 | +1 |
| 包含标志 | 如 `-la`, `--help` | +1 |
| 自然语言问题 | 包含 what/how/why 等 | -3 |
| 礼貌用语 | 包含 please/can you 等 | -2 |
| 长输入 | 超过 200 字符 | -2 |

**决策阈值：**
- **≥5 分** → EXECUTE（直接执行）
- **3-4 分** → ASK（询问用户）
- **<3 分** → LLM（交给 AI）

## 环境变量加载

Terminal Killer 自动加载用户的 shell 环境：

1. 检测用户的 shell（zsh/bash）
2. 自动加载对应的配置文件：
   - `~/.zshrc` (zsh)
   - `~/.bash_profile` (bash)
   - `~/.bashrc` (bash)
   - `~/.profile` (通用)
3. 继承完整的 PATH 和环境变量

这确保了 `adb`, `kubectl`, `docker` 等自定义路径的命令都能正常工作。

## 使用方法

### 作为独立脚本

```bash
cd /Users/cosper/MyFolder/git/31.openclaw/terminal-killer

# 测试命令检测
node scripts/index.js "ls -la"
node scripts/index.js "adb devices"
node scripts/index.js "help me write code"

# 只检测不执行
node scripts/detect-command.js "git status"

# 执行命令（带环境变量）
node scripts/exec-command.js "adb devices"
```

### 集成到 OpenClaw

在 OpenClaw agent 中添加路由逻辑：

```javascript
const terminalKiller = require('./terminal-killer/scripts/index');

// 在 agent 处理用户输入时
function handleUserInput(input) {
  const result = terminalKiller.handleInput(input);
  
  switch (result.action) {
    case 'execute':
      // 直接返回命令输出
      return result.execution.output;
    
    case 'ask':
      // 向用户确认
      return result.message;
    
    case 'llm':
      // 交给 LLM 处理
      return callLLM(input);
  }
}
```

### 在 OpenClaw 技能系统中

1. **复制技能文件夹**
   ```bash
   cp -r terminal-killer ~/.openclaw/skills/
   ```

2. **验证安装**
   ```bash
   openclaw skills list
   ```

3. **在 agent 中触发**
   
   Terminal Killer 会在以下情况自动激活：
   - 用户输入简短（< 20 词）
   - 以动词/命令开头
   - 不含问题词（what, how, why 等）

## 测试

### 运行测试套件

```bash
cd terminal-killer
node scripts/test-detector.js
```

### 测试用例

**应该直接执行的命令：**
```bash
ls -la
git status
npm install
adb devices
kubectl get pods
docker ps
curl https://example.com
python3 script.py
```

**应该交给 LLM 的任务：**
```bash
help me write a script
what does git reset do
explain this code
can you help me fix this bug
I need to create a new project
```

**应该询问确认的命令：**
```bash
rm -rf /tmp/test
sudo apt update
deploy
run tests
```

## 配置

在 `scripts/detect-command.js` 中调整：

```javascript
const CONFIG = {
  CONFIDENCE_EXECUTE: 5,    // 执行阈值
  CONFIDENCE_ASK: 3,        // 询问阈值
  MAX_HISTORY_CHECK: 100,   // 检查多少条历史记录
  DANGEROUS_PATTERNS: [     // 危险命令模式
    'rm -rf',
    'sudo',
    'dd if=',
    // ...
  ]
};
```

添加开发工具识别：

```javascript
const DEV_TOOLS = [
  'adb', 'fastboot',
  'git', 'svn',
  'docker', 'kubectl',
  // 添加你的工具...
];
```

## 输出格式

### 成功执行（短输出）
```
命令输出内容...
（完整、原样输出，不截断）
```

### 成功执行（长输出）
当输出超过 3000 字节时：

```
📝 命令执行完成，但输出较长（15234 字节）

预览：
```
第一行内容...
```

要在新 Terminal 窗口中查看完整输出吗？回复 **是** 或 **yes**
```

用户回复后：
- **是/yes** → 打开新 Terminal 窗口显示完整输出
- **否/no** → 取消，可手动输出到文件

### 执行失败
```
zsh:1: command not found: adb
(Command exited with code 127)
```

### 询问确认
```
这看起来像是一个命令：`rm -rf /tmp/test`

⚠️ **危险命令！** 确认要执行吗？
```

## 安全特性

### 危险命令检测

自动识别并提示确认：
- `rm -rf /` - 递归删除
- `sudo` - 提权命令
- `dd if=` - 磁盘操作
- `mkfs` - 格式化
- `chmod 777` - 权限修改
- `curl | sh` - 网络执行

### 环境变量隔离

- 只加载用户的 shell 配置文件
- 不修改系统环境变量
- 执行超时限制（30 秒）

## 故障排除

### 命令找不到

**问题：** `adb: command not found`

**解决：**
1. 确认 `~/.zshrc` 中包含 adb 路径
2. 测试：`source ~/.zshrc && adb devices`
3. 检查 `scripts/index.js` 是否正确加载环境变量

### 检测不准确

**问题：** 命令被误判为 LLM 任务

**解决：**
1. 运行 `node scripts/detect-command.js "你的命令"` 查看分数
2. 如果分数低，添加命令到 `DEV_TOOLS` 列表
3. 或降低 `CONFIDENCE_EXECUTE` 阈值

### 输出不显示

**问题：** 命令执行了但看不到输出

**解决：**
1. 检查输出是否包含特殊字符
2. 尝试输出到文件：`command > /tmp/output.txt`
3. 查看文件：`cat /tmp/output.txt`

## 性能

- **检测时间：** < 10ms
- **执行时间：** 取决于命令本身
- **内存占用：** < 50MB

## 贡献

欢迎提交 Issue 和 Pull Request！

### 添加新命令支持

1. 编辑 `scripts/detect-command.js`
2. 添加命令到 `DEV_TOOLS` 列表
3. 运行测试：`node scripts/test-detector.js`
4. 提交 PR

### 添加平台支持

1. 在 `references/builtins/` 添加平台命令列表
2. 更新 `getBuiltinCommands()` 函数
3. 测试并提


# 联系我
cosperypf@163.com
