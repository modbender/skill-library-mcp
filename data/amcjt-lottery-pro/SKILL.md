---
name: amcjt-lottery-pro
description: 专业彩票助手 - 支持双色球开奖查询、彩票OCR识别、中奖核对、开奖提醒。触发词：彩票、双色球、开奖、中奖、lottery。
license: MIT
allowed-tools:
  - get_lottery_result
  - ocr_lottery_ticket
  - check_lottery_win
  - get_lottery_countdown
  - get_lottery_calendar
  - Bash(node:*)
  - Bash(npx:*)
metadata:
  openclaw:
    icon: "🏆"
    category: "lifestyle"
    author: "amcjt"
    bins: ["node"]
    os: ["darwin", "linux", "win32"]
    user-invocable: true
---

# 专业彩票助手

> ⚠️ **重要前提**：本技能依赖 **OpenClaw 内置的 mcporter 技能** 来调用 MCP 工具。使用前请确保：
> 1. 已启用 mcporter 技能
> 2. mcporter 已配置并注册 **amcjt-mcp-server**

集成 amcjt-mcp-server 提供的彩票服务，支持双色球相关操作。

## 环境要求

### 必需依赖
- **OpenClaw mcporter 技能**: 用于调用 MCP 工具（请确保已启用并配置 amcjt-mcp-server）
- **Node.js**: 用于图片压缩脚本

### 支持系统
- macOS, Linux, Windows

## 触发条件

当用户提到以下关键词时触发：
- "彩票"、"双色球"、"开奖"、"中奖"、"lottery"
- 用户上传图片文件（彩票照片）
- "我中了没"、"查一下开奖"、"看看中奖号码"

## 核心功能

> 💡 **工具调用方式**：以下所有 MCP 工具均通过 **mcporter 技能** 调用，确保 mcporter 已正确配置 amcjt-mcp-server。

### 1. 查询开奖结果

用户询问某期开奖号码时：

1. 提取期号（格式：YYYY + 3位序号，如 2026020）
2. 如未提供期号，查询最新一期
3. 通过 mcporter 调用 `get_lottery_result` MCP 工具获取结果
4. 展示：开奖日期、红球号码（6个）、蓝球号码（1个）、奖池金额、中奖注数

### 2. 彩票OCR识别

用户上传彩票图片时：

1. 读取图片文件
2. 如图片 > 200KB，先用脚本压缩
3. 转为 base64 格式
4. 通过 mcporter 调用 `ocr_lottery_ticket` MCP 工具识别号码
5. 展示识别的红球和蓝球号码

### 3. 中奖核对

用户提供投注号码时：

1. 获取期号（用户输入或查询最新）
2. 获取投注号码（6个红球 01-33，1个蓝球 01-16）
3. 通过 mcporter 调用 `check_lottery_win` MCP 工具核对
4. 展示中奖等级和奖金

## 工作流程

### 流程1：查询指定期号开奖

```
用户：查一下2026020期双色球开奖
↓
提取期号：2026020
↓
通过 mcporter 调用 MCP 工具：get_lottery_result
  参数：{"issueNo": "2026020", "lottoType": "101"}
↓
解析返回，格式化展示
```

### 流程2：识别彩票图片

```
用户上传 lottery.jpg
↓
读取图片 → 检查大小 → 必要时压缩
↓
转为 base64
↓
通过 mcporter 调用 MCP 工具：ocr_lottery_ticket
  参数：{"imageBase64": "...", "lottoType": "101"}
↓
展示识别结果，询问是否核对中奖
```

### 流程3：核对中奖

```
用户：我买的 01 13 14 21 24 30 + 02，中了没？
↓ 
提取红球：[01,13,14,21,24,30]，蓝球：[02]
↓
获取期号（最新或指定）
↓
通过 mcporter 调用 MCP 工具：check_lottery_win
  参数：{"issueNo": "...", "lottoType": "101", "bets": [{"redNumbers": [...], "blueNumbers": [...]}]}
↓
展示中奖等级和奖金
```

### 流程4：获取最新开奖信息

```
用户：最新一期双色球开奖号码是什么？
↓
通过 mcporter 调用 MCP 工具：get_lottery_result
  参数：{"lottoType": "101"}（不指定 issueNo 获取最新）
↓
展示最新开奖结果
```

### 流程5：开奖倒计时查询

```
用户：下次双色球什么时候开奖？
↓
通过 mcporter 调用 MCP 工具：get_lottery_countdown
↓
展示倒计时信息
```

## 数据格式

### 投注号码格式
```json
{
  "redNumbers": ["01","13","14","21","24","30"],
  "blueNumbers": ["02"]
}
```

### 红球范围：01-33（选6个）
### 蓝球范围：01-16（选1个）

## 辅助脚本

### scripts/compress_image.js
用于压缩过大的彩票图片（>200KB），配合 OCR 识别使用。

使用方法：
```bash
# node amcjt-lottery-pro/scripts/compress_image.js <输入路径> [输出路径]
node amcjt-lottery-pro/scripts/compress_image.js ./lottery.jpg ./lottery-small.jpg
```

## 注意事项

1. **mcporter 配置**: 使用前请确保 OpenClaw 的 mcporter 技能已启用，且已注册 amcjt-mcp-server
2. 图片建议 < 2MB，太大时先压缩
3. 双色球 lottoType = "101"
4. 期号格式：年份 + 3位序号（如2026020）
5. 使用图片压缩需要安装 `npm install sharp`
