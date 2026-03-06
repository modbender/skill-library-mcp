---
name: python-script-generator
description: 生成专业的 Python 脚本和应用模板，支持 CLI 工具、Flask API、FastAPI、Django Command、Scraper 等，一键生成完整项目代码。
metadata: {"clawdbot":{"emoji":"🐍","requires":{},"primaryEnv":""}}
---

# Python Script Generator

快速生成专业的 Python 脚本和应用代码。

## 功能

- ⚡ 一键生成项目
- 📝 支持多种类型
- 🔧 完整的项目结构
- 📖 最佳实践

## 支持的类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| cli | 命令行工具 | 自动化脚本 |
| flask | Flask API | 轻量级 Web 服务 |
| fastapi | FastAPI | 高性能 API |
| django-cmd | Django Command | Django 管理命令 |
| scraper | 网页爬虫 | 数据采集 |
| bot | Telegram/Discord Bot | 机器人开发 |

## 使用方法

### CLI 工具

```bash
toolpython-script-generator my --type cli
python-script-generator backup-script --type cli --description "Backup important files"
```

### FastAPI

```bash
python-script-generator myapi --type fastapi
python-script-generator rest-api --type fastapi --crud
```

### 爬虫

```bash
python-script-generator scraper --type scraper
python-script-generator news-collector --type scraper --selector ".article"
```

### Bot

```bash
python-script-generator mybot --type bot --platform telegram
```

## 生成的项目结构

```
mytool/
├── mytool/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_main.py
├── requirements.txt
├── setup.py
└── README.md
```

## CLI 模板

```python
#!/usr/bin/env python3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Your CLI tool description'
    )
    parser.add_argument(
        '--name', 
        default='World',
        help='Name to greet'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f'[DEBUG] Greeting {args.name}')
    
    print(f'Hello, {args.name}!')

if __name__ == '__main__':
    main()
```

## FastAPI 模板

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="My API",
    description="API description",
    version="1.0.0"
)

class Item(BaseModel):
    name: str
    description: str = None
    price: float

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## 安装依赖

```bash
# CLI
pip install argparse

# FastAPI
pip install fastapi uvicorn

# Flask
pip install flask

# Scraper
pip install requests beautifulsoup4
```

## 变现思路

1. **脚本模板销售** - 专业脚本模板
2. **定制开发** - Python 开发服务
3. **培训课程** - Python 编程培训
4. **SaaS 工具** - 在线工具平台

## 安装

```bash
# 无需额外依赖
```
