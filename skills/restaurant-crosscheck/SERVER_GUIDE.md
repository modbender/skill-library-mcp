# 🖥️ 服务器使用指南

## 快速开始

### 作为 OpenClaw 技能使用

这个 skill 已经集成到 OpenClaw 技能系统中。你可以直接通过对话使用：

```
你：查询深圳南山区推荐餐厅
AI：[自动调用 restaurant-crosscheck skill]
```

### 命令行使用

在服务器上直接使用命令：

```bash
# 基本用法
restaurant-crosscheck "深圳市南山区" "美食"
restaurant-crosscheck "上海静安区" "日式料理"
restaurant-crosscheck "北京朝阳区" "火锅"
```

## 📍 命令位置

- **本地命令**：`skills/restaurant-review-crosscheck/restaurant-crosscheck`
- **全局链接**：`~/workspace/bin/restaurant-crosscheck`（可选）

## 🎯 使用场景

### 1. 通过对话使用（推荐）

```
你：帮我查一下深圳南山区有什么好吃的餐厅
AI：[调用 skill，返回推荐列表]
```

```
你：上海静安区日式料理推荐
AI：[调用 skill，返回 3 家推荐餐厅]
```

### 2. 通过脚本使用

```bash
#!/bin/bash
# 查询多个地区的餐厅

locations=("深圳市南山区" "上海静安区" "北京朝阳区")
cuisines=("美食" "火锅" "日式料理")

for loc in "${locations[@]}"; do
    for food in "${cuisines[@]}"; do
        echo "查询: $loc - $food"
        restaurant-crosscheck "$loc" "$food"
        echo "---"
    done
done
```

### 3. 集成到其他工具

```python
# Python 脚本调用
import subprocess

def get_restaurant_recommendations(location, cuisine):
    result = subprocess.run(
        ['restaurant-crosscheck', location, cuisine],
        capture_output=True,
        text=True
    )
    return result.stdout

recommendations = get_restaurant_recommendations("深圳市南山区", "美食")
print(recommendations)
```

## ⚠️ 重要说明

### 当前版本特点

1. **使用模拟数据**
   - 不需要登录账号
   - 不需要浏览器
   - 适合无头服务器环境
   - 数据为模拟生成（用于测试）

2. **功能完整**
   - ✅ 交叉验证算法
   - ✅ 推荐评分系统
   - ✅ 一致性分析
   - ✅ 格式化输出

3. **数据限制**
   - ⚠️ 非真实数据
   - ⚠️ 仅用于功能演示
   - ⚠️ 不能用于实际决策

### 真实数据版本

如需真实数据，在有图形界面的环境中：

```bash
# 使用 Playwright 版本（需要浏览器）
bash setup.sh  # 配置登录
./crosscheck-auto "深圳市南山区" "美食"
```

## 📊 输出格式

```
📍 深圳市南山区 美食 餐厅推荐

1. 餐厅名称
   🏆 推荐指数: 6.4/10
   ⭐ 大众点评: 4.7⭐ (2028评价)
   💬 小红书: 2.7⭐ (309赞/80收藏)
   📍 地址: 深圳市南山区某某路88号
   💰 人均: ¥180-250
   ✅ 一致性: 低
```

## 🔧 配置选项

编辑 `scripts/config.py` 自定义：

```python
DEFAULT_THRESHOLDS = {
    "min_rating": 4.0,              # 最低评分
    "min_dianping_reviews": 50,     # 最少评价数
    "min_xhs_notes": 20,            # 最少笔记数
    "max_results": 10,              # 最多显示结果
    "similarity_threshold": 0.7     # 匹配相似度
}
```

## 🎮 完整示例

### 查询深圳美食

```bash
$ restaurant-crosscheck "深圳市南山区" "美食"

🔍 搜索: 深圳市南山区 - 美食
⚠️ 使用模拟数据（服务器版本）

📍 深圳市南山区 美食 餐厅推荐

============================================================

1. 美食推荐店A
   🏆 推荐指数: 6.4/10
   ⭐ 大众点评: 4.7⭐ (2028评价)
   💬 小红书: 2.7⭐ (309赞/80收藏)
   📍 地址: 深圳市南山区某某路88号
   💰 人均: ¥180-250
   ✅ 一致性: 低
...
```

### 在 Python 脚本中使用

```python
import subprocess
import json

# 查询餐厅
result = subprocess.run(
    ['restaurant-crosscheck', '深圳市南山区', '火锅'],
    capture_output=True,
    text=True
)

# 解析输出
recommendations = result.stdout
print(recommendations)
```

### 在 Node.js 脚本中使用

```javascript
const { exec } = require('child_process');

exec('restaurant-crosscheck "深圳市南山区" "美食"', (error, stdout, stderr) => {
    if (error) {
        console.error(`Error: ${error}`);
        return;
    }
    console.log(stdout);
});
```

## 📚 相关文档

- **[完整文档](README.md)** - 详细功能说明
- **[快速开始](QUICKSTART.md)** - 5分钟上手
- **[实现说明](IMPLEMENTATION.md)** - 技术细节
- **[数据结构](references/data_schema.md)** - 数据格式

## 🚀 下一步

1. **测试功能**
   ```bash
   restaurant-crosscheck "深圳市南山区" "美食"
   ```

2. **集成到对话**
   - 直接通过对话查询餐厅
   - AI 会自动调用 skill

3. **自定义配置**
   - 编辑 `scripts/config.py`
   - 调整评分权重和阈值

4. **查看更多文档**
   ```bash
   cat README.md
   cat QUICKSTART.md
   ```

---

**状态**：✅ 已集成到 OpenClaw，可以立即使用！
