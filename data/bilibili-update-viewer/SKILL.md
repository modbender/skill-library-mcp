---
name: bilibili-update-viewer
description: 查看B站UP主的最新视频、动态，检查UP主今天是否更新。触发词：B站、UP主、视频更新、今天更新了吗、最新视频、最新动态、查看UP主
metadata: {"openclaw":{"emoji":"📺","requires":{"bins":["python3"]},"os":["darwin","linux","win32"]}}
---

# B站UP主查看器

查看B站UP主的最新视频和动态，支持检查UP主今天是否更新。
如果遇到访问太频繁的问题，直接和用户说访问太频繁，不要尝试别的方式。

## Setup

### 1. 安装依赖

```bash
pip install -r {baseDir}/requirements.txt
```

### 2. 设置环境变量

需要B站Cookies才能访问API。获取方法：登录 bilibili.com → F12 → Network → 复制任意请求的 Cookie 字段。

```bash
export BILIBILI_COOKIES="你的B站cookies"
```

## Usage

### 第一步：获取UP主的 mid

a. 如果用户直接给了 mid（纯数字），直接进入第二步。

b. 如果用户给的是UP主用户名，先从本地缓存查找：

```bash
python3 {baseDir}/get_mid.py "用户名"
```

- 如果输出了 mid 数字，直接使用该 mid 进入第二步。
- 如果输出 `NOT_FOUND`，则通过搜索获取：

```bash
python3 {baseDir}/update_viewer.py --search "用户名" --count 1
```

从搜索结果中提取 `mid` 数字，进入第二步。

### 第二步：根据用户意图执行对应命令

根据用户的问题选择合适的命令：

**场景A - 用户问"今天更新了吗"、"有没有新视频"等：**
```bash
python3 {baseDir}/update_viewer.py --mid {MID} --videos --count 3
```
运行后，从输出中查看每条视频的「发布」时间，判断是否有今天的日期（{今天的日期}），然后告诉用户今天是否有更新。如果有，列出今天更新的视频标题和链接。

**场景B - 用户想查看最新视频列表：**
```bash
python3 {baseDir}/update_viewer.py --mid {MID} --videos
```

**场景C - 用户想查看最新动态：**
```bash
python3 {baseDir}/update_viewer.py --mid {MID} --dynamics
```

## 命令行参数

### update_viewer.py

| 参数 | 说明 | 必需 |
|------|------|------|
| `--mid` | UP主的 mid | 与 --search 二选一 |
| `--search`, `-s` | 根据用户名搜索UP主 | 与 --mid 二选一 |
| `--videos`, `-v` | 显示最新视频 | 否 |
| `--dynamics`, `-d` | 显示最新动态 | 否 |
| `--count`, `-n` | 显示数量（默认3） | 否 |

## 注意事项

- Cookies 有效期有限，失效后需重新获取
- 请求频率不宜过高，建议间隔 1 秒以上
- 需要设置 BILIBILI_COOKIES 环境变量
