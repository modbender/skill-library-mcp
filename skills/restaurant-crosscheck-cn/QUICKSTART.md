# 🚀 快速开始指南

## 自动化版本（使用真实数据）

### 一键安装

```bash
cd skills/restaurant-review-crosscheck
bash setup.sh
```

安装脚本会自动：
1. ✅ 安装所有 Python 依赖
2. ✅ 下载 Playwright 浏览器
3. ✅ 引导配置登录会话

### 配置登录（首次使用）

运行安装脚本时，会自动提示配置：

1. **大众点评登录**
   - 浏览器自动打开 https://www.dianping.com
   - 使用手机号或微信扫码登录
   - 登录后关闭浏览器
   - 脚本自动保存登录状态

2. **小红书登录**
   - 浏览器自动打开 https://www.xiaohongshu.com
   - 使用手机号或微信扫码登录
   - 登录后关闭浏览器
   - 脚本自动保存登录状态

**注意**：登录状态会保存 1-2 周，过期后重新运行配置即可。

### 开始使用

```bash
# 查询餐厅推荐（自动使用真实数据）
./crosscheck-auto "深圳市南山区" "美食"

# 或使用完整路径
python3 scripts/crosscheck_real.py "深圳市南山区" "火锅"
```

### 管理登录会话

```bash
# 查看会话状态
python3 scripts/session_manager.py

# 重置所有会话（需要重新登录）
python3 scripts/session_manager.py --reset

# 只配置大众点评
python3 scripts/session_manager.py --dianping

# 只配置小红书
python3 scripts/session_manager.py --xiaohongshu
```

---

## 测试版本（使用模拟数据）

如果不想配置登录，可以使用模拟数据测试：

```bash
# 使用模拟数据
python3 scripts/crosscheck.py "上海静安区" "日式料理"
```

---

## 工作流程

```
用户输入查询
    ↓
检查登录会话
    ↓
会话有效？ → 是 → 使用保存的会话抓取数据
    ↓ 否
自动打开浏览器
    ↓
用户手动登录
    ↓
保存会话
    ↓
抓取真实数据
    ↓
交叉验证分析
    ↓
生成推荐报告
```

---

## 常见问题

### Q: 会话过期怎么办？
```bash
# 重新运行配置脚本
python3 scripts/session_manager.py
```

### Q: 如何查看会话状态？
```bash
python3 scripts/session_manager.py
```

### Q: 抓取失败怎么办？
1. 检查网络连接
2. 尝试重新登录：`python3 scripts/session_manager.py --reset`
3. 检查搜索关键词是否合理

### Q: 可以跳过登录直接使用吗？
可以，使用模拟数据版本：
```bash
python3 scripts/crosscheck.py "地区" "菜系"
```

---

## 对比：模拟数据 vs 真实数据

| 特性 | 模拟数据 | 真实数据 |
|------|---------|---------|
| 数据来源 | 固定测试数据 | 大众点评 + 小红书 |
| 配置难度 | 无需配置 | 需要登录一次 |
| 数据准确性 | 仅测试用 | 真实数据 |
| 使用场景 | 测试功能 | 实际使用 |
| 命令 | `crosscheck.py` | `crosscheck_real.py` |

---

## 下一步

安装完成后：

1. ✅ 测试基本功能
2. 📖 阅读 [完整文档](README.md)
3. 🔧 自定义配置（`scripts/config.py`）
4. 📊 查看数据结构（`references/data_schema.md`）
