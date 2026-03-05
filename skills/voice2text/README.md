# voice2text

离线语音转文字技能（Python + Vosk）

## 介绍
本项目演示如何使用 **Vosk** 离线模型实现语音转文字，并在 **ClawHub** 中封装为可发布的技能。

## 快速上手
```bash
# 安装依赖
pip install -r requirements.txt
# 运行示例（确保有 sample.wav）
python main.py '{"audio": "sample.wav"}'
```

## 目录结构
```
voice2text/
├─ main.py          # 技能入口
├─ package.json     # ClawHub 元信息
├─ requirements.txt # Python 依赖
├─ model/           # 下载的 Vosk 模型（自行放置）
└─ tests/
   └─ test_main.py # 单元测试
```
