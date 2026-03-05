# Agent Vision Scraper 🤖👁️

Docker 化的智能网页自动化与抓取工具，利用 LLM 视觉能力破解图形验证码。

## 特性

- 🖥️ **虚拟屏幕** - 内置 Xvfb，无头服务器也能运行有头浏览器
- 🔍 **VNC 远程查看** - 端口 5900 可连接查看实时操作
- 🕵️ **隐身模式** - Playwright Stealth 插件绕过反爬检测
- 👁️ **视觉验证码识别** - 利用 LLM Vision 能力破解图形验证码
- 📦 **最新 Playwright** - 基于 v1.58.2-jammy 镜像

## 快速开始

### 1. 构建镜像

```bash
docker build -t agent-scraper-image .
```

### 2. 运行

```bash
docker run --rm --env-file .env -p 5900:5900 agent-scraper-image node agent-scraper.js "<URL>" "<INSTRUCTION>"
```

### 示例

```bash
# 登录带验证码的网站
docker run --rm --env-file .env -p 5900:5900 agent-scraper-image node agent-scraper.js \
  "https://example.com/login" \
  "查看页面，如果发现图形验证码，读出图片上的字母，并与账号 admin 和密码 123456 一起填入表单，点击登录。"

# 抓取数据
docker run --rm --env-file .env -p 5900:5900 agent-scraper-image node agent-scraper.js \
  "https://example.com/products" \
  "抓取所有产品的名称、价格和图片链接，返回 JSON 格式。"
```

## 环境变量

创建 `.env` 文件：

```env
# 可选：LLM API 配置（如果需要调用外部视觉模型）
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# 可选：代理配置
HTTP_PROXY=http://proxy:8080
HTTPS_PROXY=http://proxy:8080
```

## VNC 查看

运行时映射了 5900 端口，可用 VNC 客户端连接查看浏览器操作过程：

- **地址**: `localhost:5900`
- **密码**: 无（免密）

## 文件结构

```
agent-vision-scraper/
├── Dockerfile           # Docker 镜像定义
├── package.json         # Node.js 依赖
├── agent-scraper.js     # 主程序
├── skill.md             # ClawHub skill 描述
└── README.md            # 本文档
```

## 工作原理

1. **启动虚拟桌面** - Xvfb 创建虚拟显示器 :99
2. **启动浏览器** - Playwright Chromium 有头模式运行
3. **导航页面** - 访问目标 URL
4. **视觉分析** - 截图发送给 LLM 分析
5. **执行操作** - 根据 LLM 返回的指令点击/输入
6. **循环执行** - 直到任务完成

## 适用场景

- ✅ 带图形验证码的网站登录
- ✅ 复杂网页自动化操作
- ✅ 反爬网站数据抓取
- ✅ 需要视觉判断的网页任务

## 注意事项

- 首次运行需要下载浏览器（约 200MB）
- VNC 端口 5900 需要开放
- 建议在有足够内存的机器上运行（2GB+）

## License

MIT

---

**Author**: Tedtalk  
**Version**: 1.0.0  
**Last Updated**: 2026-03-03
