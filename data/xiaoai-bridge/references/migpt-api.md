# MiGPT-Next API 参考

## 核心配置

### 使用 passToken 登录（推荐）

```typescript
const config = {
  speaker: {
    userId: "你的小米账号ID",
    passToken: "你的passToken",
    did: "小爱音箱设备ID",
  }
};
```

### 使用密码登录（可能触发风控）

```typescript
const config = {
  speaker: {
    userId: "你的小米账号ID", 
    password: "你的密码",
    did: "小爱音箱设备ID",
  }
};
```

## 底层 API

### 获取消息

```typescript
import { getMiNA } from "@mi-gpt/miot";

const mina = await getMiNA(config);

// 获取对话历史
const conversations = await mina.getConversations({
  limit: 10,
  timestamp: Date.now()
});

// 返回结构
interface MiConversations {
  records: Array<{
    time: number;        // 时间戳
    query: string;       // 用户说的话
    answers: Array<{
      tts?: { text: string }; // 小爱的回复
    }>;
  }>;
}
```

### TTS 播放

```typescript
// 播放文字
await mina.play({ text: "你好" });

// 播放音频链接
await mina.play({ url: "https://example.com/audio.mp3" });
```

### 音量控制

```typescript
// 获取音量
const volume = await mina.getVolume();

// 设置音量（0-100）
await mina.setVolume(50);
```

### 播放控制

```typescript
await mina.pause();   // 暂停
await mina.resume();  // 继续
await mina.stop();    // 停止
```

## 轮询模式

```typescript
let lastTimestamp = Date.now();

while (true) {
  const conversations = await mina.getConversations({
    limit: 10,
    timestamp: lastTimestamp,
  });

  if (conversations?.records) {
    for (const record of conversations.records) {
      if (record.time > lastTimestamp) {
        console.log(`新消息：${record.query}`);
        lastTimestamp = record.time;
      }
    }
  }

  await new Promise(resolve => setTimeout(resolve, 1000));
}
```

## 环境变量配置

```bash
MI_USER_ID=1234567890
MI_PASS_TOKEN=your_pass_token_here
MI_DEVICE_ID=小爱音箱Pro
```

## 常见问题

### 获取 passToken
访问：https://github.com/idootop/migpt-next/issues/4

### 获取设备 ID
```typescript
const miot = await getMIoT({
  userId: "...",
  passToken: "...",
  did: "任意设备名",
  debug: true  // 会打印所有设备列表
});
```

### 登录失败
- 触发风控：改用 passToken
- 账号错误：userId 是数字，不是手机号
- 设备错误：开启 debug 查看设备列表
