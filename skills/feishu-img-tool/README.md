# Feishu Image Skill - 飞书图片发送技能

这个技能允许你在飞书中发送图片消息。

## 安装

```bash
clawhub install feishu-image-send
```

技能将安装到 ClawHub 技能目录。

## 使用方法

### 方法 1：直接使用 Node.js 脚本

```bash
# 发送图片给用户（带文字说明）
node feishu-image-tool.js send \
  --target ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --file /tmp/stock-report.png \
  --message "📊 今日股票报告"

# 仅上传图片，获取 image_key
node feishu-image-tool.js upload \
  --file /tmp/image.png

# 使用已有的 image_key 发送消息
node feishu-image-tool.js send-with-key \
  --target ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --image-key img_v3_xxx
```

### 方法 2：在 OpenClaw 中调用

```javascript
const { exec } = require('child_process');

exec(`node feishu-image-tool.js send --target ${userId} --file ${filePath}`, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error}`);
    return;
  }
  const result = JSON.parse(stdout);
  console.log('Image sent:', result.message_id);
});
```

## 配置

### 方法 1：环境变量（推荐）

```bash
export FEISHU_APP_ID="cli_xxxxxxxxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 方法 2：配置文件

创建 `~/.feishu-image/config.json`：

```json
{
  "appId": "cli_xxxxxxxxxxxxxxxx",
  "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

可从示例配置复制：
```bash
cp config.example.json ~/.feishu-image/config.json
# 然后编辑 ~/.feishu-image/config.json 填入你的凭证
```

### 获取飞书应用凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 确保应用有以下权限：
   - `im:message` - 发送消息
   - `im:image` - 上传图片

## 限制

- 图片大小：最大 10 MB
- 支持格式：JPG, JPEG, PNG, WEBP, GIF, BMP, ICO
- 分辨率限制：
  - GIF: 最大 2000 x 2000 像素
  - 其他格式：最大 12000 x 12000 像素

## 输出示例

成功响应：
```json
{
  "success": true,
  "image_key": "img_v3_02vd_xxx",
  "message_id": "om_x100b5560xxx"
}
```

## 故障排除

### 错误：Cannot find module '@larksuiteoapi/node-sdk'

确保 SDK 路径正确。默认路径：
```
/root/.local/share/pnpm/global/5/.pnpm/@larksuiteoapi+node-sdk@1.59.0/node_modules/@larksuiteoapi/node-sdk
```

如果路径变化，请更新脚本中的 `LARK_SDK_PATH`。

### 错误：Upload failed

检查：
1. 文件是否存在
2. 图片格式是否支持
3. 图片大小是否超过 10MB
4. 飞书应用配置是否正确

## 开发者

此技能由 ivan lee 开发，用于扩展飞书机器人的图片发送功能。
