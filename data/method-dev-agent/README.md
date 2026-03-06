# 方法开发助手Agent - MVP版本

> 专为药品分析实验室设计的AI助手
> 作者：Teagee Li
> 版本：v0.1.0 MVP

## 🎯 核心功能

- 📝 实验记录管理
- 🔍 方法检索
- 📊 基础数据可视化
- 💾 本地SQLite数据库

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run src/app.py
```

## 📁 项目结构

```
method-dev-agent/
├── src/
│   ├── app.py              # Streamlit主界面
│   ├── database.py         # 数据库操作
│   ├── models.py           # 数据模型
│   └── utils.py            # 工具函数
├── data/
│   └── method_dev.db       # SQLite数据库
├── tests/
│   └── test_basic.py       # 基础测试
├── requirements.txt
└── README.md
```

## 🛣️ 开发路线图

- [x] Day 1: 项目结构、数据库设计
- [ ] Day 2: 实验记录功能
- [ ] Day 3: 方法检索功能
- [ ] Day 4: 数据可视化
- [ ] Day 5: 测试和优化
- [ ] Day 6-7: 实验室部署测试

## 💡 使用说明

1. 启动应用后，先创建新的实验记录
2. 输入色谱条件、样品信息、结果数据
3. 保存后可以在"查看记录"页面检索
4. 支持按化合物、日期、方法类型筛选

## 📧 反馈

有问题或建议？请联系 Teagee Li
