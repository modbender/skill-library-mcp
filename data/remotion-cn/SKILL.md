---
name: remotion-cn
description: Remotion 视频创建框架 - React 编程创建视频（中文版）
metadata:
  openclaw:
    emoji: "🎥"
    category: "video"
    tags: ["remotion", "react", "video", "ffmpeg", "animation"]
    requires:
      bins: ["node", "npm", "python3"]
---

# Remotion CN - React 视频创建框架

Remotion 是一个用 React 创建视频的强大框架。支持多种输出格式（MP4、WebM、GIF），可以在服务器端渲染视频。

## 功能

### 视频创建
- **多输出格式** - MP4、WebM、GIF、PNG 序列
- **React 编程** - 用 JSX 创建动画
- **高性能** - 服务器端渲染，比 Canvas 更快
- **代码重用** - 组件化开发，可复用

### 动画类型
- **变换** - 缩放、旋转、透明度
- **时间轴** - 多轨同时播放
- **音频** - 音轨支持
- **3D** - 基础 3D 变换（CSS 3D）

---

## 安装

### 创建新项目
```bash
# 使用 create-video
npx create-video@latest my-video
cd my-video

# 或使用 Vite
npx create-vite@latest my-video
cd my-video
npm install remotion
```

### 手动安装
```bash
npm install remotion @remotion/cli --save-dev
```

---

## 快速开始

### 示例 1：Hello World 视频
```tsx
// src/App.tsx
import { Composition } from 'remotion';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition>
      <HelloWorld />
    </Composition>
  );
};

export default RemotionRoot;
```

```tsx
// src/HelloWorld.tsx
import { AbsoluteFill } from 'remotion';

export const HelloWorld: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: 'white' }}>
      <div style={{ fontSize: 120, color: 'black', fontFamily: 'sans-serif' }}>
        你好，Remotion！
      </div>
    </AbsoluteFill>
  );
};
```

### 渲染视频
```bash
# 渲染为 MP4
npx remotion render src/App.tsx out/video.mp4

# 在浏览器中预览
npx remotion studio src/App.tsx
```

### 示例 2：动画文本
```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, Video } from 'remotion';

export const TextSlide: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a2a' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%'
      }}>
        <h1 style={{
          fontSize: 80,
          color: 'white',
          opacity: frame % 60, // 闪烁效果
          transform: `translateY(${Math.sin(frame * 0.1) * 20}px)`
        }}>
          薅羊毛自动化
        </h1>
      </div>
    </AbsoluteFill>
  );
};

export default Video(TextSlide);
```

---

## 高级功能

### 1. 媒体导入
```tsx
import { useVideo } from '@remotion/use-video';
import { staticFile } from 'remotion';

export const MyVideo: React.FC = () => {
  const video = useVideo(staticFile('video.mp4'));

  return (
    <Video src={video} />
  );
};
```

### 2. 音频
```tsx
import { AbsoluteFill, useCurrentFrame, Audio, Sequence } from 'remotion';

export const AudioExample: React.FC = () => {
  return (
    <AbsoluteFill>
      <Sequence>
        <Audio src={staticFile('music.mp3')} />
      </Sequence>
    </AbsoluteFill>
  );
};
```

### 3. GIF 输出
```tsx
import { GIF, useCurrentFrame, staticFile } from 'remotion';

export const AnimatedGif: React.FC = () => {
  const frame = useCurrentFrame();
  
  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      <GIF width={400} height={400} src={staticFile('image.png')} />
    </AbsoluteFill>
  );
};
```

### 4. 时间轴（多轨）
```tsx
import { AbsoluteFill, Sequence, useCurrentFrame } from 'remotion';

export const Multitrack: React.FC = () => {
  const frame = useCurrentFrame();
  
  return (
    <AbsoluteFill style={{ backgroundColor: 'white' }}>
      <Sequence from={0} durationInFrames={60}>
        <Text>第一轨</Text>
      </Sequence>
      <Sequence from={60} durationInFrames={60}>
        <Text>第二轨</Text>
      </Sequence>
    </AbsoluteFill>
  );
};
```

---

## 配置文件

### remotion.config.ts
```typescript
import { Config } from '@remotion/cli/config';

export default {
  concurrency: 1, // 并发数量
  chromiumPath: null, // 使用默认 Chromium
  ffmpegExecutable: null, // 使用默认 FFmpeg
  log: 'verbose', // 日志级别
  overwrite: true, // 覆盖已存在的文件
  ignore: [
    'node_modules',
    '.git'
  ]
} as Config;
```

---

## 渲染命令

### 开发模式
```bash
# 启动开发服务器
npx remotion studio

# 渲染预览
npx remotion preview src/App.tsx
```

### 生产渲染
```bash
# 渲染 MP4
npx remotion render src/App.tsx out/video.mp4

# 指定分辨率
npx remotion render src/App.tsx out/video.mp4 --width=1920 --height=1080

# 渲染 GIF
npx remotion render src/App.tsx out/video.gif --codec=gif

# 渲染 PNG 序列
npx remotion render src/App.tsx out/video/ --sequence

# 使用配置文件
npx remotion render src/App.tsx out/video.mp4 --config=remotion.config.ts
```

---

## 最佳实践

### 1. 性能优化
- **使用 useCallback** - 避免重复渲染
- **预计算** - 静态资源提前处理
- **代码分割** - 大视频分解为多个片段

### 2. 错误处理
- **边界检查** - 避免超出范围
- **容错机制** - 提供默认值
- **日志记录** - 记录错误信息

### 3. 文件管理
- **输出分离** - 视频文件放在单独目录
- **清理临时文件** - 渲染完成后清理
- **版本控制** - 代码和资源分离

---

## 中文资源

### 文档
- [Remotion 中文文档](https://www.remotion.dev/docs/)
- [Remotion 官方示例](https://github.com/remotion-dev/remotion/tree/main/examples)
- [Remotion API 参考](https://www.remotion.dev/api/)

### 社区
- [Remotion 中文社区](https://www.remotion.dev/docs/)
- [GitHub Discussions](https://github.com/remotion-dev/remotion/discussions)

### 视频教程
- [B站 Remotion 教程](https://www.bilibili.com/)
- [抖音 Remotion 教程](https://www.douyin.com/)
- [YouTube Remotion 教程](https://www.youtube.com/)

---

## 与其他框架对比

| 框架 | 优点 | 缺点 |
|------|------|------|
| **Remotion** | React 编程，高性能，组件化 | 需要 React 知识 |
| **Canvas** | 简单，学习曲线平 | 性能一般，功能有限 |
| **Three.js** | 强大的 3D 能力 | 学习曲线陡峭 |
| **P5.js** | 脚本化，简单 | 功能有限 |

---

## 常见问题

### 1. 渲染失败
- **原因**: 依赖未安装
- **解决**: `npm install remotion`

### 2. 内存不足
- **原因**: 大视频占用过多内存
- **解决**: 代码分割，减少并发

### 3. Chromium 错误
- **原因**: Chromium 环境问题
- **解决**: 更新依赖，使用 Docker 容器

### 4. FFmpeg 错误
- **原因**: FFmpeg 未安装或版本不兼容
- **解决**: 安装最新版 FFmpeg

---

## 示例项目

### 1. 自动化视频生成器
```bash
# 从数据生成产品宣传视频
npx create-video@latest product-video
cd product-video
# 从 API 获取产品数据
# 渲染每个产品的短视频
```

### 2. 社交媒体内容
```bash
# 自动生成抖音/快手视频
npx create-video@latest social-video
cd social-video
# 根据热点生成视频
```

### 3. 教育视频
```bash
# 自动生成教学视频
npx create-video@latest education-video
cd education-video
# 从讲义生成视频
```

---

## AI 集成

### 用 AI 生成 Remotion 代码

```python
from openai import OpenAI

def generate_remotion_code(video_description):
    """用 AI 生成 Remotion 代码"""
    client = OpenAI(api_key="your_key")
    
    prompt = f"""
    创建一个 Remotion 组件：
    {video_description}
    
    要求：
    1. 使用 TypeScript
    2. 导入 Remotion 必需组件
    3. 代码简洁可读
    4. 添加适当的样式
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# 使用
code = generate_remotion_code("一个产品展示视频，展示旋转和缩放")
print(code)
```

---

## 版本管理

| 版本 | 发布日期 | 变更 |
|------|---------|------|
| 1.0.0 | 2026-02-19 | 初始版本，基础功能 |
| 1.1.0 | 待定 | 集成 AI 代码生成 |

---

## 许可证

MIT

---

*版本: 1.0.0*
*框架: Remotion (React 视频创建）*
*适配: 中文环境和社区*
