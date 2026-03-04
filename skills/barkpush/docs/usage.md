# Bark Push Skill 使用说明

## 快速开始
### 基本推送
```bash
bark-push --user alice --content "会议将在10分钟后开始"
```

### 指定标题与副标题
```bash
bark-push --user alice --title "会议提醒" --subtitle "10分钟后" --content "请准时参加"
```

## 内容类型示例
### 纯文本
```bash
bark-push --user alice --content "今天18:00例会"
```

### 纯链接
```bash
bark-push --user alice --content "https://example.com"
```

### 纯图片
```bash
bark-push --user alice --content "https://example.com/image.png"
```

### 混合内容
```bash
bark-push --user alice --content "进度说明 https://example.com/docs 这是截图 https://example.com/image.png"
```

## 多用户与全员推送
### 多用户推送
```bash
bark-push --user alice,bob --content "双人通知"
```

### 全员推送
```bash
bark-push --user all --title "系统通知" --content "今晚维护"
```

## 分组与参数配置
### 指定分组
```bash
bark-push --user alice --group work --content "工作提醒"
```

### 级别与音量
```bash
bark-push --user alice --level critical --volume 10 --content "紧急告警"
```

### 角标与铃声
```bash
bark-push --user alice --badge 3 --sound alarm --content "新消息"
```

### 图标与复制内容
```bash
bark-push --user alice --icon "https://example.com/icon.png" --copy "验证码:123456" --content "请查收验证码"
```

### 自动复制与呼叫
```bash
bark-push --user alice --autoCopy 1 --call 1 --content "请尽快处理"
```

### 归档与自定义动作
```bash
bark-push --user alice --isArchive 1 --action '{"action":"confirm","text":"确认"}' --content "是否确认?"
```

## 更新与删除
### 更新已推送消息
```bash
bark-push --update <push_id> --user alice --content "会议时间改为15分钟后"
```

### 删除已推送消息
```bash
bark-push --delete <push_id> --user alice --content "删除该条消息"
```

## 查询与帮助
### 查看用户列表
```bash
bark-push --list-users
```

### 查看分组列表
```bash
bark-push --list-groups
```

### 查看历史记录
```bash
bark-push --list-history --history-limit 20
```

### 查看帮助
```bash
bark-push --help-skill
```

## 配置说明
### 配置文件位置
优先级如下：
1. 命令行 `--config` 指定路径
2. 当前目录 `config.json`
3. `config/config.json`
4. `~/.bark-push/config.json`

### 最小可用配置示例
```json
{
  "default_push_url": "https://api.day.app",
  "ciphertext": "",
  "users": {
    "alice": "device_key_alice_abc123"
  },
  "defaults": {
    "level": "active",
    "volume": 10,
    "badge": 1,
    "sound": "bell",
    "icon": "",
    "group": "default",
    "call": false,
    "autoCopy": false,
    "copy": "",
    "isArchive": true,
    "action": ""
  },
  "groups": ["default"],
  "history_limit": 100,
  "enable_update": true
}
```

## 说明要点
- 用户输入的参数优先于默认配置
- 未输入的参数使用 defaults 中的默认值
- 配置错误会返回明确提示信息
