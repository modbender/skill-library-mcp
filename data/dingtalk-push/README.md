# DingTalk Push - 钉钉消息推送

发送钉钉群聊机器人消息的技能。

## 功能

- 发送 Markdown 格式消息到钉钉群
- 支持消息类型（success/warning/error/info）
- 支持 @指定人员和 @所有人
- 支持加签验证（安全）
- 可被其他 Skill 导入调用

## 使用方法

### 命令行

```bash
node skills/dingtalk-push/send.js -m "消息内容"
node skills/dingtalk-push/send.js -m "警告" --type warning
node skills/dingtalk-push/send.js -m "错误" --type error --all
```

### 编程调用

```javascript
import { dingtalkPush, dingtalkSuccess, dingtalkWarning } from './skills/dingtalk-push/tool.js';

// 发送消息
await dingtalkPush({ message: "任务完成", type: "success" });

// 快捷方法
await dingtalkSuccess("备份完成");
await dingtalkWarning("CPU使用率高");
await dingtalkError("服务异常");
```

## 配置

### 方式1: 环境变量

```bash
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=xxx"
export DINGTALK_SECRET="SEC_xxx"
```

### 方式2: 配置文件

复制配置示例并填入你的Webhook：

```bash
cp skills/dingtalk-push/config.example.json ~/.config/dingtalk-push/config.json
```

## 消息类型

| 类型 | Emoji | 适用场景 |
|------|-------|----------|
| info | ℹ️ | 普通通知 |
| success | ✅ | 成功完成任务 |
| warning | ⚠️ | 警告、需要关注 |
| error | ❌ | 错误、异常 |

## 创建钉钉机器人

1. 打开钉钉群 → 群设置 → 智能群助手 → 添加机器人
2. 选择自定义机器人，填写名称
3. 开启"加签"安全设置（推荐）
4. 复制 Webhook 地址和加签密钥

## 依赖

- Node.js 16+
