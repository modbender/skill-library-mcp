# skill-feishu-manager

飞书 (Feishu) 综合管理 Toolkit

## Features

- 📄 Document management
- 📚 Knowledge base (Wiki)
- 📊 Bitable tables
- ☁️ Cloud drive

## Install

```bash
clawhub install skill-feishu-manager
```

## Setup

1. Create Feishu app: https://open.feishu.cn
2. Enable permissions: docx:document, wiki:wiki, drive:drive, bitable:data
3. Configure:
```yaml
channels:
  feishu:
    app_id: "cli_xxx"
    app_secret: "xxx"
```

## License

MIT
