---
name: xiaoai-bridge
description: 小米小爱音箱语音指令桥接。截取小爱音箱的语音消息，转换为 AI 助手指令，并通过 TTS 回复。支持触发词过滤、自动去重、后台监听。适用于通过小爱音箱语音控制 OpenClaw 助手、智能家居联动、语音任务执行等场景。
version: 1.0.0
author: OpenClaw Community
tags: [xiaomi, xiaoai, voice, tts, iot, smart-home]
---

# 小爱音箱语音桥接 Skill

通过小米小爱音箱实现 OpenClaw 的语音交互能力。

## 功能特性

✅ **语音指令监听** - 实时轮询小爱音箱的语音消息（小米云端语音识别）  
✅ **智能触发过滤** - 支持触发词前缀（默认"请"），避免误触发  
✅ **TTS 语音回复** - 将 AI 处理结果通过小爱音箱播报  
✅ **消息去重机制** - 自动跟踪时间戳，避免重复处理  
✅ **后台持续运行** - 支持长期监听，稳定可靠  
✅ **多设备支持** - 支持所有小米 IoT 生态的小爱音箱设备

## 工作原理

1. **监听** - 轮询小爱音箱获取语音消息（小米云端语音转文字）
2. **处理** - 将语音消息转换为 AI 助手指令
3. **回复** - 通过小爱音箱 TTS 播报处理结果

## 快速开始

### 1. 安装依赖

```bash
cd skills/xiaoai-bridge/scripts
npm install
```

### 2. 配置环境变量

复制 `.env.example` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
MI_USER_ID=1234567890              # 小米账号 ID（纯数字）
MI_PASS_TOKEN=your_pass_token      # 推荐：使用 passToken
# MI_PASSWORD=your_password        # 备选：密码（可能触发安全验证）
MI_DEVICE_ID=小爱音箱Pro            # 设备名称、miotDID 或 MAC 地址
TRIGGER_PREFIX=请                   # 触发词前缀（默认"请"）
POLL_INTERVAL=1000                 # 轮询间隔（毫秒，默认 1000）
```

**获取 passToken**：参考 https://github.com/idootop/migpt-next/issues/4

**查找设备 ID**：运行 `DEBUG=true node scripts/xiaoai-listen.js test` 查看所有设备列表。

### 3. 测试连接

```bash
node scripts/xiaoai-listen.js test
```

预期输出：
```
🔌 正在连接小爱音箱...
✅ 连接成功
```

### 4. 启动监听

后台运行监听服务：

```bash
node scripts/xiaoai-listen.js > xiaoai.log 2>&1 &
```

或���用 OpenClaw 进程管理（推荐）。

## 使用示例

### 示例 1：后台监听 + 消息处理

启动监听进程并解析 JSON 输出：

```javascript
const { exec } = require('child_process');
const listener = exec('node skills/xiaoai-bridge/scripts/xiaoai-listen.js');

listener.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (!line.trim()) continue;
    
    try {
      const msg = JSON.parse(line);
      if (msg.type === 'message') {
        // 处理语音指令
        handleVoiceCommand(msg.text);
      }
    } catch (e) {
      // 非 JSON 的状态日志
      console.log(line);
    }
  }
});

async function handleVoiceCommand(text) {
  // 你的指令处理逻辑
  const response = await processCommand(text);
  
  // 通过 TTS 回复
  await exec(`node skills/xiaoai-bridge/scripts/xiaoai-listen.js speak "${response}"`);
}
```

### 示例 2：直接 TTS 播报

发送文本到小爱音箱：

```bash
node scripts/xiaoai-listen.js speak "任务已完成"
```

代码调用：

```javascript
const { exec } = require('child_process');

function speakViaXiaoAi(text) {
  return new Promise((resolve, reject) => {
    exec(`node skills/xiaoai-bridge/scripts/xiaoai-listen.js speak "${text}"`, 
      (error, stdout, stderr) => {
        if (error) reject(error);
        else resolve();
      }
    );
  });
}

// 使用
await speakViaXiaoAi("你好，任务已完成");
```

### 示例 3：触发词过滤

Skill 自动过滤触发词前缀（默认"请"），只处理符合条件的消息：

```javascript
// 用户说："请帮我查天气" → 处理，text = "帮我查天气"
// 用户说："今天天气怎么样" → 忽略（无触发词）

listener.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    try {
      const msg = JSON.parse(line);
      if (msg.type === 'message') {
        // msg.text 已自动去除触发词前缀
        console.log(`处理指令: ${msg.text}`);
        handleVoiceCommand(msg.text);
      }
    } catch (e) {}
  }
});
```

自定义触发词（在 `.env` 中配置）：

```bash
TRIGGER_PREFIX=请      # 默认
# TRIGGER_PREFIX=小助手  # 自定义唤醒词
# TRIGGER_PREFIX=       # 空值 = 处理所有消息
```

## 消息格式

监听器输出 JSON 格式消息（仅处理符合触发词的消息）：

```json
{
  "type": "message",
  "text": "查一下天气",
  "originalText": "请查一下天气",
  "timestamp": 1708070400000
}
```

**注意**：`text` 字段已自动去除触发词前缀。如需完整消息，使用 `originalText`。

## API 参考

完整 MiGPT-Next API 文档见 [references/migpt-api.md](references/migpt-api.md)。

### 脚本命令

```bash
# 启动监听（默认）
node scripts/xiaoai-listen.js

# TTS 播报文本
node scripts/xiaoai-listen.js speak "要说的话"

# 测试连接
node scripts/xiaoai-listen.js test
```

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `MI_USER_ID` | 是 | 小米账号 ID（纯数字） |
| `MI_PASS_TOKEN` | 是* | passToken（推荐） |
| `MI_PASSWORD` | 是* | 密码（可能触发安全验证） |
| `MI_DEVICE_ID` | 是 | 设备名称、miotDID 或 MAC |
| `TRIGGER_PREFIX` | 否 | 触发词前缀（默认"请"） |
| `POLL_INTERVAL` | 否 | 轮询间隔（毫秒，默认 1000） |
| `DEBUG` | 否 | 调试模式（true/false） |

*`MI_PASS_TOKEN` 或 `MI_PASSWORD` 二选一。

## 故障排查

### 登录失败

**症状**：`❌ 连接失败: 登录失败`

**解决方案**：
1. 使用 `passToken` 替代密码（推荐）
2. 检查 `MI_USER_ID` 是否为纯数字（不是手机号或邮箱）
3. 开启 `DEBUG=true` 查看详细错误信息

### 找不到设备

**症状**：`❌ 找不到设备`

**解决方案**：运行以下命令查看所有设备：

```bash
DEBUG=true node scripts/xiaoai-listen.js test
```

使用设备的 `name`、`miotDID` 或 `mac` 作为 `MI_DEVICE_ID`。

### 收不到消息

**可能原因**：
1. 消息同步延迟（1-2 秒正常）
2. 设备离线或无响应
3. 自上次轮询后无新消息

### 需要验证码

**症状**：`❌ 本次登录需要验证码`

**解决方案**：必须使用 `passToken` 登录。参考 https://github.com/idootop/migpt-next/issues/4

## 最佳实践

1. **使用 passToken** - 比密码更稳定，避免安全验证
2. **轮询间隔** - 1-2 秒最佳（平衡响应速度和 API 负载）
3. **消息去重** - 跟踪已处理的时间戳，避免重复处理
4. **错误处理** - 实现重试逻辑应对网络故障
5. **长文本分段** - 将长回复分句播报，提升 TTS 体验

## 完整集成示例

与 OpenClaw 助手的完整集成：

```javascript
const { exec } = require('child_process');
const path = require('path');

class XiaoAiBridge {
  constructor() {
    this.listener = null;
    this.lastTimestamp = Date.now();
  }

  start(onMessage) {
    const scriptPath = path.join(__dirname, 'skills/xiaoai-bridge/scripts/xiaoai-listen.js');
    this.listener = exec(`node ${scriptPath}`);

    this.listener.stdout.on('data', (data) => {
      const lines = data.toString().split('\n');
      for (const line of lines) {
        if (!line.trim()) continue;
        
        try {
          const msg = JSON.parse(line);
          if (msg.type === 'message' && msg.timestamp > this.lastTimestamp) {
            this.lastTimestamp = msg.timestamp;
            onMessage(msg.text);
          }
        } catch (e) {
          console.log(line); // 状态日志
        }
      }
    });

    this.listener.stderr.on('data', (data) => {
      console.error('XiaoAi Error:', data.toString());
    });
  }

  async speak(text) {
    const scriptPath = path.join(__dirname, 'skills/xiaoai-bridge/scripts/xiaoai-listen.js');
    return new Promise((resolve, reject) => {
      exec(`node ${scriptPath} speak "${text}"`, (error) => {
        if (error) reject(error);
        else resolve();
      });
    });
  }

  stop() {
    if (this.listener) {
      this.listener.kill();
    }
  }
}

// 使用示例
const bridge = new XiaoAiBridge();

bridge.start(async (voiceCommand) => {
  console.log(`收到语音指令: ${voiceCommand}`);
  
  // 用你的 AI 助手处理指令
  const response = await yourAgentProcess(voiceCommand);
  
  // 通过小爱音箱回复
  await bridge.speak(response);
});
```

## 相关资源

- MiGPT-Next 项目：https://github.com/idootop/migpt-next
- passToken 获取教程：https://github.com/idootop/migpt-next/issues/4
- API 完整文档：[references/migpt-api.md](references/migpt-api.md)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
