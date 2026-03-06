# 🦞 小龙虾多平台视频发布助手

> 一键上传视频到抖音、视频号、小红书、B 站、YouTube 等平台

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 playwright
pip install playwright

# 安装浏览器
playwright install chromium
```

### 2. 配置账号

首次运行会自动创建配置文件：
```
config/accounts.json
```

编辑文件，启用要发布的平台（大部分平台使用二维码登录，无需填写密码）

### 3. 发布视频

```bash
# 基础用法
python auto_publisher.py "D:\AI-Video-Studio\outputs\video.mp4"

# 指定标题和标签
python auto_publisher.py "video.mp4" --title "AI 生成的未来城市" --tags "#AI,#科技,#未来"

# 指定平台
python auto_publisher.py "video.mp4" --platforms douyin,xiaohongshu,bilibili

# 无头模式（后台运行）
python auto_publisher.py "video.mp4" --headless
```

---

## 📱 支持的平台

| 平台 | 登录方式 | 标题限制 | 时长限制 |
|------|---------|---------|---------|
| **抖音** | 二维码 | 100 字 | 15 分钟 |
| **视频号** | 二维码 | 1000 字 | 30 分钟 |
| **小红书** | 二维码 | 20 字标题 +1000 字内容 | 15 分钟 |
| **B 站** | 二维码/密码 | 80 字 | 4 小时 |
| **YouTube** | Google 账号 | 100 字 | 12 小时 |

---

## ⚙️ 配置文件说明

### config/accounts.json

```json
{
  "douyin": {
    "enabled": true,        // 是否启用
    "qr_login": true,       // 使用二维码登录
    "notes": "首次需要扫码"
  }
}
```

---

## 📝 常用命令

### 发布到所有平台
```bash
python auto_publisher.py "video.mp4"
```

### 只发布到抖音和小红书
```bash
python auto_publisher.py "video.mp4" --platforms douyin,xiaohongshu
```

### 自定义文案风格
```bash
# 吸引互动
python auto_publisher.py "video.mp4" --style engaging

# 专业风格
python auto_publisher.py "video.mp4" --style professional

# 搞笑风格
python auto_publisher.py "video.mp4" --style funny
```

### 批量发布
```bash
# 发布整个文件夹的视频
for file in D:\AI-Video-Studio\outputs\*.mp4; do
    python auto_publisher.py "$file"
done
```

---

## 🔄 定时发布

### Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发时间
4. 操作：启动程序
   - 程序：`python`
   - 参数：`auto_publisher.py "video.mp4"`
   - 起始于：`D:\AI-Video-Studio`

### 或使用发布队列

创建 `schedule.json`:
```json
{
  "posts": [
    {
      "video": "video1.mp4",
      "time": "2026-03-02 08:00:00",
      "platforms": ["douyin", "wechat_channels"]
    },
    {
      "video": "video2.mp4",
      "time": "2026-03-02 12:00:00",
      "platforms": ["xiaohongshu", "bilibili"]
    }
  ]
}
```

---

## 📊 发布记录

发布记录保存在 `config/publish_log.json`

包含：
- 发布时间
- 视频文件
- 标题和标签
- 发布结果

---

## ⚠️ 注意事项

### 首次使用
1. 每个平台首次登录需要扫码
2. 扫码后 Cookie 会保存，下次无需重复登录
3. Cookie 有效期约 7-30 天

### 发布频率
- **抖音：** 建议日更 1-3 条
- **视频号：** 建议日更 1-2 条
- **小红书：** 建议日更 1-3 条
- **B 站：** 建议周更 2-3 条
- **YouTube：** 建议日更 1 条 Shorts

### 内容规范
- 不要发布违规内容
- 注意版权问题
- 各平台规则可能不同

---

## 🐛 故障排除

### 问题：Playwright 安装失败
```bash
# 解决方法
pip install --upgrade pip
pip install playwright
playwright install chromium
```

### 问题：登录超时
- 检查网络连接
- 手动打开平台网站，确认可以访问
- 重新运行，重新扫码

### 问题：发布失败
- 检查视频格式是否支持
- 检查视频大小是否超限
- 查看浏览器窗口中的错误信息

---

## 🦞 小龙虾提示

> "工具是辅助，内容才是王道！"

发布助手帮你节省时间，但好的内容才能吸引粉丝。

建议：
1. 用工具批量发布
2. 花时间优化内容质量
3. 积极回复评论互动
4. 分析数据，持续改进

---

_小龙虾 AI 工作室 🦞 | "小龙虾，有大钳（前）途！"_
