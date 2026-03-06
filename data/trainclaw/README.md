# TrainClaw

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/AI4MSE/TrainClaw/blob/master/LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-AI4MSE%2FTrainClaw-black.svg)](https://github.com/AI4MSE/TrainClaw)

铁路火车票 CLI 查询工具 — 查询余票、经停站、中转方案。


## 功能

- **OpenClaw** 支持成为OpenClaw技能，参考SKILL.md文件
- **余票查询** (`query`) — 查询两站之间的余票信息，支持按车次类型、出发时间筛选，按时间/历时排序，输出 text/json/csv
- **经停站查询** (`route`) — 查询指定车次的全部经停站信息，输出 text/json
- **中转查询** (`transfer`) — 查询需要换乘的中转方案，支持指定中转站，输出 text/json
- **日志系统** (`-v/--verbose`) — 可选的详细日志输出，DEBUG 级别显示 HTTP 请求细节
- **查询冷却** — API 请求间隔可设置，避免请求过于频繁
- **友好错误信息** — 中文错误提示、车站名候选建议、空结果操作建议

## 安装

```bash
# 仅需 Python 3.8+ 和 requests 库
pip install requests
```

## 使用示例

### 余票查询

```bash
# 基础查询
python trainclaw.py query -f 北京 -t 上海

# 明天的高铁，上午出发，按历时排序，取前 5 条
python trainclaw.py query -f 北京 -t 上海 -d 2026-03-04 --type G \
  --earliest 8 --latest 12 --sort duration -n 5

# JSON 输出
python trainclaw.py query -f 南京 -t 杭州 --type D -o json

# CSV 输出
python trainclaw.py query -f 广州 -t 深圳 -o csv

# 详细日志模式（DEBUG 输出到 stderr）
python trainclaw.py -v query -f 北京 -t 上海
```

### 经停站查询

```bash
python trainclaw.py route -c G1 -d 2026-03-04
python trainclaw.py route -c G1033 -o json
```

### 中转查询

```bash
# 自动推荐中转站
python trainclaw.py transfer -f 深圳 -t 拉萨 -n 5

# 指定中转站
python trainclaw.py transfer -f 深圳 -t 拉萨 -m 西安 -d 2026-03-04
```

## 车站名输入

支持三种格式，自动识别：

| 格式 | 示例 | 说明 |
|------|------|------|
| 精确站名 | `北京南`、`上海虹桥` | 直接匹配 |
| 城市名 | `北京`、`上海` | 匹配该城市代表站 |
| 三字母代码 | `BJP`、`SHH` | 直接使用 |

## 车次类型代码

| 代码 | 含义 |
|------|------|
| G | 高铁/城际（G/C 开头） |
| D | 动车 |
| Z | 直达特快 |
| T | 特快 |
| K | 快速 |
| O | 其他（非 GDZTK） |
| F | 复兴号 |
| S | 智能动车组 |

可组合使用，如 `--type GD` 表示高铁+动车。

## 版本

**当前版本**: 0.0.3

## 注意事项

1. 一般仅支持查询今天及未来 15 天内的车票
2. 首次运行需下载车站数据（~3000 站），之后使用本地缓存（7 天有效）
3. 错误信息输出到 stderr，数据输出到 stdout，支持管道操作
4. 中转查询结果取决于查询网站的推荐算法

## 免责声明

本工具仅供学习和研究技术之用，不建议任何实际使用，使用时请遵守当地法律和法规。本项目与中国铁路无任何关联。

## 许可证

[Apache License 2.0](LICENSE)
