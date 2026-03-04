# Quick Start Guide

## 🚀 3步开始使用

### 1. 克隆项目

```bash
git clone https://github.com/kk43994/claw-desktop-pet.git
cd claw-desktop-pet
```

### 2. 安装依赖

```bash
npm install
pip install edge-tts
```

### 3. 启动应用

```bash
npm start
```

## 🔧 配置

### OpenClaw集成

编辑 `desktop-bridge.js`:

```javascript
const OPENCLAW_PORT = 18788;  // OpenClaw端口
const VOICE_ENABLED = true;    // 启用语音
```

### 语音设置

编辑 `voice-player.js`:

```javascript
const DEFAULT_VOICE = 'zh-CN-XiaoxiaoNeural';  // Edge TTS语音
const DEFAULT_RATE = '+0%';                     // 语速
const DEFAULT_VOLUME = '+0%';                   // 音量
```

## 📝 使用示例

### 发送通知

```javascript
// 从OpenClaw发送
await exec('node C:\\path\\to\\desktop-bridge.js agent-response "你好,我是桌面龙虾!"');
```

### 检查状态

```javascript
// 查看健康分数
const health = await fetch('http://localhost:18788/health');
console.log(await health.json());
```

### 查看日志

```bash
# 主日志
tail -f logs/desktop-pet.log

# 语音日志
tail -f logs/voice.log

# 性能日志
tail -f logs/performance.log
```

## 🛠️ 开发

### 调试模式

```bash
npm run dev
```

### 运行测试

```bash
node tests/test-error-handling.js
node tests/test-auto-restart.js
node tests/test-performance-monitor.js
node tests/test-voice-system.js
node tests/test-log-management.js
```

## ❓ 常见问题

### Q: 如何修改窗口大小?
A: 编辑 `main.js` 中的 `width` 和 `height` 参数

### Q: 如何更换语音?
A: 修改 `voice-player.js` 中的 `DEFAULT_VOICE` 配置

### Q: 如何查看性能指标?
A: 访问 http://localhost:18788/health 或查看 `logs/performance.log`

### Q: 如何禁用自动重启?
A: 编辑 `auto-restart.js` 中的 `RESTART_ENABLED = false`

## 📚 更多文档

- [完整README](https://github.com/kk43994/claw-desktop-pet#readme)
- [技术文档](https://github.com/kk43994/claw-desktop-pet/tree/master/docs)
- [发布说明](https://github.com/kk43994/claw-desktop-pet/blob/master/RELEASE-v1.3.0.md)

---

需要帮助? [提交Issue](https://github.com/kk43994/claw-desktop-pet/issues)
