# 📚 AutoClip Pro 傻瓜式教程

> 从零开始，一步一步教你使用 AutoClip Pro

---

## 🎯 第一步：准备工作

### 1.1 检查你的电脑

确保你有：
- [ ] Windows 10 或更高版本（Windows 11 也行）
- [ ] 至少 4GB 内存
- [ ] 至少 5GB 硬盘空间

### 1.2 安装 Node.js（如果没有）

1. 打开浏览器，访问 https://nodejs.org
2. 下载 LTS（长期支持）版本
3. 双击安装包，一路点"下一步"
4. 打开命令提示符，输入 `node -v`，看到版本号就成功了

### 1.3 安装 FFmpeg（如果没有）

**最简单的方法：**

1. 访问 https://www.gyan.dev/ffmpeg/builds/
2. 下载 "ffmpeg-release-essentials.zip"
3. 解压到一个文件夹（比如 `C:\ffmpeg`）
4. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
5. 在"系统变量"里找到 Path，点击编辑，添加 `C:\ffmpeg\bin`
6. 重启命令提示符，输入 `ffmpeg -version`，看到版本信息就成功了

---

## 🚀 第二步：安装 AutoClip Pro

### 方法一：一键安装（推荐）

1. 找到 `video-batch-skill` 文件夹
2. 双击 `install.bat`
3. 等待黑色窗口显示 "安装完成！"
4. 按任意键关闭窗口

### 方法二：手动安装

1. 打开命令提示符
2. 输入 `cd video-batch-skill文件夹路径`
3. 输入 `npm install`
4. 等待安装完成

---

## 🎬 第三步：准备你的视频

### 3.1 创建输入文件夹

在 `video-batch-skill` 文件夹里：
1. 新建一个文件夹，命名为 `input`
2. 把你要处理的视频放进去

**支持的视频格式：**
- MP4（推荐）
- MOV
- AVI
- MKV
- WebM

### 3.2 选择模板

打开 `config.json`，找到 `"template"` 这一行：

```json
"template": "knowledge"
```

可选值：
- `knowledge` - 知识科普风格，适合教育视频
- `emotional` - 情感故事风格，适合 Vlog
- `funny` - 搞笑段子风格，适合短视频

---

## ⚡ 第四步：开始处理

### 一键运行

双击 `run.bat`，等待处理完成！

处理好的视频在 `output` 文件夹里。

### 查看进度

黑色窗口会显示：
```
[1/5] 正在处理: video1.mp4
[2/5] 正在处理: video2.mp4
...
✅ 全部完成！共处理 5 个视频
```

---

## ❓ 常见问题

### Q: 提示"ffmpeg 不是内部或外部命令"

**A:** FFmpeg 没安装好或没有加到环境变量。看 [1.3 安装 FFmpeg](#13-安装-ffmpeg如果没有)

### Q: 提示"node 不是内部或外部命令"

**A:** Node.js 没安装。看 [1.2 安装 Node.js](#12-安装-nodejs如果没有)

### Q: 处理很慢怎么办？

**A:** 视频处理需要时间，耐心等待。可以在 `config.json` 里降低分辨率：

```json
"resolution": "720p"  // 从 1080p 改为 720p
```

### Q: 输出文件夹是空的？

**A:** 检查：
1. `input` 文件夹里有没有视频文件
2. 视频格式是否支持
3. 看黑色窗口有没有错误信息

### Q: 想修改水印怎么办？

**A:** 编辑 `config.json`：

```json
"addWatermark": true,
"watermark": {
  "text": "你的名字",
  "position": "bottom-right",
  "opacity": 0.5
}
```

---

## 🎨 进阶技巧

### 批量重命名

处理前给视频命名，输出的视频会保持原名：

```
input/
├── 01_开场.mp4
├── 02_正文.mp4
└── 03_结尾.mp4
```

### 自定义模板

复制 `templates/knowledge.json`，改名并修改参数：

```json
{
  "name": "我的自定义模板",
  "introDuration": 3,
  "outroDuration": 2,
  "transitions": true,
  "backgroundMusic": true
}
```

然后在 `config.json` 里引用你的模板：

```json
"template": "my-template"
```

---

## 🆘 还是不会？

1. 仔细检查每一步
2. 看看错误信息，复制到搜索引擎
3. 联系技术支持，发送错误截图

---

**记住：实践出真知，多试几次就熟练了！** 💪