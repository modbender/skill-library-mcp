# literature-report

自动科研文献汇报系统

## 功能特点

- 双重数据源（RSS + PubMed API）
- AI辅助检索
- 双语输出
- 自动推送
- 定时任务

## 安装

```bash
bash install.sh
```

## 配置

1. 复制配置文件模板：
```bash
cp config.yaml.example config.yaml
```

2. 编辑 `config.yaml`，填入你的配置：
   - LLM API Key
   - 飞书用户ID（可选）
   - 研究主题

## 使用

```bash
python3 scripts/fetch_papers.py
python3 scripts/generate_summary.py
python3 scripts/send_to_feishu.py
```

## 许可证

MIT License