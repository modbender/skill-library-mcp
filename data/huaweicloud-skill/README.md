# 华为云架构设计 Skill

OpenClaw skill，用于华为云架构设计、资源配置、成本预估和 Terraform 模板生成。

## 功能

- **需求分析**：从业务描述提取关键要素
- **架构推荐**：匹配 Web/微服务/大数据/AI 等架构模式
- **资源清单**：生成详细资源配置
- **成本预估**：计算月度费用
- **Terraform 模板**：输出可执行的 TF 代码

## 安装

```bash
git clone https://github.com/jiachenz/huaweicloud-skill.git ~/.openclaw/skills/huaweicloud
```

重启 OpenClaw 或开始新会话即可使用。

## 使用

向 OpenClaw 描述你的需求，例如：

> "帮我设计一个日活 5 万的电商网站架构，部署在华为云"

## 目录结构

```
huaweicloud/
├── SKILL.md                 # 工作流程
├── references/              # 参考文档
│   ├── services.md          # 产品目录
│   ├── architectures.md     # 架构模式
│   ├── terraform-providers.md
│   └── pricing-api.md
├── scripts/                 # 工具脚本
│   └── hwc-pricing.py
└── assets/terraform/        # TF 模板
```

## License

MIT
