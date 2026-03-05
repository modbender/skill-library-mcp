#!/usr/bin/env node

/**
 * 小爱音箱消息监听服务
 * 轮询获取小爱音箱的语音消息，转换为用户指令
 */

import { getMiNA } from "@mi-gpt/miot";
import dotenv from "dotenv";

// 加载 .env 文件
dotenv.config();

// 配置
const config = {
  userId: process.env.MI_USER_ID,
  passToken: process.env.MI_PASS_TOKEN,
  password: process.env.MI_PASSWORD,
  did: process.env.MI_DEVICE_ID,
  debug: process.env.DEBUG === "true",
};

// 触发条件
const TRIGGER_PREFIX = process.env.TRIGGER_PREFIX || "请";

// 验证配置
if (!config.userId || !config.did) {
  console.error("❌ 缺少必要配置：MI_USER_ID 和 MI_DEVICE_ID");
  process.exit(1);
}

if (!config.passToken && !config.password) {
  console.error("❌ 需要提供 MI_PASS_TOKEN 或 MI_PASSWORD");
  process.exit(1);
}

// 初始化
let mina;
let lastTimestamp = Date.now();
let isRunning = false;

async function init() {
  try {
    console.log("🔌 正在连接小爱音箱...");
    mina = await getMiNA(config);
    
    if (!mina) {
      throw new Error("登录失败");
    }
    
    console.log("✅ 连接成功");
    return true;
  } catch (error) {
    console.error("❌ 连接失败:", error.message);
    return false;
  }
}

async function fetchMessages() {
  try {
    const conversations = await mina.getConversations({
      limit: 10,
      timestamp: lastTimestamp,
    });

    if (!conversations?.records) {
      return [];
    }

    const newMessages = [];
    
    for (const record of conversations.records) {
      if (record.time > lastTimestamp) {
        // 检查是否以触发前缀开头
        if (record.query.startsWith(TRIGGER_PREFIX)) {
          // 移除触发前缀
          const text = record.query.substring(TRIGGER_PREFIX.length).trim();
          
          newMessages.push({
            text: text,
            originalText: record.query,
            timestamp: record.time,
          });
        }
        lastTimestamp = record.time;
      }
    }

    return newMessages;
  } catch (error) {
    console.error("❌ 获取消息失败:", error.message);
    return [];
  }
}

async function speak(text) {
  try {
    await mina.play({ text });
    return true;
  } catch (error) {
    console.error("❌ 播放失败:", error.message);
    return false;
  }
}

async function poll() {
  const messages = await fetchMessages();
  
  for (const msg of messages) {
    // 输出为 JSON 格式，便于 OpenClaw 解析
    console.log(JSON.stringify({
      type: "message",
      text: msg.text,
      originalText: msg.originalText,
      timestamp: msg.timestamp,
    }));
  }
}

async function start() {
  if (isRunning) {
    console.error("❌ 服务已在运行");
    return;
  }

  const connected = await init();
  if (!connected) {
    process.exit(1);
  }

  isRunning = true;
  console.log("🎤 开始监听消息...");

  // 轮询间隔（毫秒）
  const POLL_INTERVAL = parseInt(process.env.POLL_INTERVAL || "1000");

  while (isRunning) {
    await poll();
    await new Promise(resolve => setTimeout(resolve, POLL_INTERVAL));
  }
}

// 处理命令行参数
const command = process.argv[2];

if (command === "speak") {
  // 播放模式：node xiaoai-listen.js speak "要说的话"
  const text = process.argv[3];
  if (!text) {
    console.error("❌ 缺少文本参数");
    process.exit(1);
  }
  
  init().then(async (connected) => {
    if (connected) {
      const success = await speak(text);
      process.exit(success ? 0 : 1);
    } else {
      process.exit(1);
    }
  });
} else if (command === "test") {
  // 测试模式：检查连接
  init().then((connected) => {
    process.exit(connected ? 0 : 1);
  });
} else {
  // 默认：监听模式
  start().catch((error) => {
    console.error("❌ 服务异常:", error);
    process.exit(1);
  });
}

// 优雅退出
process.on("SIGINT", () => {
  console.log("\n👋 停止监听");
  isRunning = false;
  process.exit(0);
});

process.on("SIGTERM", () => {
  isRunning = false;
  process.exit(0);
});
