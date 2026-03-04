# 百度电商知识技能包

百度电商知识技能，包括商品对比、全网比价、榜单、商品参数、品牌品类知识等能力。

## 功能特性

- **全维度对比决策助手**: SPU 参数/口碑/价格全方位对比评测
- **商品百科知识**: 品类选购指南、品牌科普知识、全维度参数库
- **实时品牌天梯榜单**: 基于搜索热度、全网声量及销量的品牌排行
- **全网 CPS 商品**: 获取全网 CPS 商品链接及热卖商品信息
- **全网比价**: 获取全网相关 SPU 与优质低价商品链接

## 安装要求

- Python 3.x（使用标准库，无需额外安装依赖）
- 百度电商 API Token

## 配置

1. 访问 https://openai.baidu.com 并登录百度账号
2. 点击权限申请，勾选需要的能力
3. 设置环境变量：

```bash
export BAIDU_EC_SEARCH_TOKEN="your-token"
```

## 目录结构

```
baidu-ecommerce-search/
├── _meta.json           # 元数据配置
├── SKILL.md             # 技能详细说明
├── README.md            # 本文件
└── scripts/
    ├── common.py        # 公共模块（API 请求、Token 管理）
    ├── compare.py       # 商品对比
    ├── knowledge.py     # 品牌/品类/商品参数知识
    ├── ranking.py       # 品牌榜单
    ├── cps.py           # CPS商品搜索
    └── bijia.py         # 全网比价
```

## 使用示例

```bash
# 商品对比
python3 scripts/compare.py "iphone16和iphone15对比"

# 品牌知识
python3 scripts/knowledge.py brand "华为"

# 品类选购知识
python3 scripts/knowledge.py entity "无人机怎么选"

# 商品参数
python3 scripts/knowledge.py param "iphone16"

# 品牌榜单
python3 scripts/ranking.py brand "手机品牌榜"

# CPS商品搜索
python3 scripts/cps.py "机械键盘"

# 全网比价
python3 scripts/bijia.py spu "iphone16价格"
python3 scripts/bijia.py goods "苹果手机价格"
```

## 许可证

MIT License
