# ✈️ Variflight Aviation Skill

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

飞常准(Variflight)航班信息查询 Skill for OpenClaw。支持实时航班动态、航线搜索、舒适度评估、机场天气等功能。

## 🌟 特性

- 🔍 **航线搜索** - 按出发地/目的地搜索航班
- 🛫 **航班号查询** - 精确查询指定航班信息
- 🔄 **中转方案** - 获取最优转机路线
- 😊 **舒适度指数** - 航班准点率、机型舒适度评估
- 📍 **实时位置** - 飞机实时位置追踪
- 🌤️ **机场天气** - 3天机场天气预报
- 💰 **票价查询** - 可购买航班及最低价格
- 🔒 **安全设计** - API Key 本地管理，不上传云端

## 🔧 配置

### 方式一：环境变量（推荐）

**重要提示**：Variflight MCP 服务器使用特殊的环境变量名 `X_VARIFLIGHT_KEY`

```bash
# 添加到 ~/.zshrc 或 ~/.bash_profile
export X_VARIFLIGHT_KEY="your_api_key_here"
```

### 方式二：本地配置文件
创建 config.local.json（已加入 .gitignore，不会提交）：
``` json
{
  "apiKey": "your_api_key_here"
}
```
## 📦 安装

### 通过 OpenClaw 安装

```bash
clawhub install variflight-aviation