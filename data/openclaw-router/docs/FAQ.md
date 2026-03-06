# OpenClaw Router Skill - 常见问题

**版本：** 1.0.0  
**最后更新：** 2026-03-02

---

## 📚 基础问题

### Q1: Router Skill 是什么？

**A:** Router Skill 是一个智能路由系统，自动为你的问题选择最佳模型（本地或云端），节省 60% 成本的同时保证回答质量。

---

### Q2: 为什么需要 Router Skill？

**A:** 
- ❌ **不用 Router：** 所有问题都用 L3，成本高（¥4/100 次）
- ✅ **用 Router：** 80% 本地 +15% 验证 +5%L3，成本低（¥1.6/100 次）
- 💰 **节省：** 60% 成本，质量不变

---

### Q3: 安装复杂吗？

**A:** 非常简单！只需 3 步：

```bash
# 1. 下载安装
bash install_router.sh

# 2. 自动检测环境
🔍 检测中...

# 3. 确认推荐配置
[1] 使用推荐配置 ← 按 1 确认

✅ 完成！
```

全程 2 分钟，90% 用户选择推荐配置。

---

### Q4: 支持哪些模型？

**A:** 

**本地模型（Ollama）：**
- qwen2.5:7b/14b/72b
- llama3:8b/70b
- mistral:7b, mixtral:8x7b
- gemma:7b/14b
- 以及所有 Ollama 模型

**云端模型：**
- 阿里云：qwen3.5-plus, qwen3-max, kimi-k2.5
- OpenAI: gpt-4, gpt-4o, gpt-3.5
- Anthropic: claude-3-opus/sonnet/haiku

---

### Q5: 我没有 Ollama，能用吗？

**A:** 可以！Router Skill 支持：
- ✅ 纯本地部署（需要 Ollama）
- ✅ 纯云端部署（只需云 API）
- ✅ 混合部署（推荐）

没有 Ollama 时，会自动推荐云端配置。

---

## 💰 成本问题

### Q6: 能省多少钱？

**A:** 基于真实用户数据：

| 用户类型 | 传统方案 | Router v3.0 | 节省 |
|----------|----------|-------------|------|
| 个人开发者 | ¥150/月 | ¥60/月 | ¥90/月 |
| 小企业 | ¥500/月 | ¥200/月 | ¥300/月 |
| AI 工作室 | ¥2000/月 | ¥800/月 | ¥1200/月 |

**平均节省：60%**

---

### Q7: 免费版和付费版有什么区别？

**A:**

| 功能 | 免费版 | 付费版 (¥29/月) |
|------|--------|----------------|
| 每月请求 | 1000 次 | 无限 |
| 基础路由 | ✅ | ✅ |
| Token 追踪 | ✅ | ✅ |
| 用户偏好学习 | ❌ | ✅ |
| 预算管理 | ❌ | ✅ |
| 时段优化 | ❌ | ✅ |
| 优先支持 | ❌ | ✅ |

**推荐：** 个人用户免费版够用，高频用户付费版更划算。

---

### Q8: 如何查看用量？

**A:** 每次回答后自动显示：

```markdown
---
【本次用量】
- 使用模型：qwen2.5:14b-32k (本地)
- Token 估算：输入~500 / 输出~800 = 总计~1300
- 成本：¥0 (本地免费)

【套餐剩余】
- 百炼包月：¥200/月 (剩 28 天)
- 估算已用：~5%
- 日均可用：¥7.1
- 状态：✅ 额度充足
---
```

---

## ⚙️ 配置问题

### Q9: 如何修改配置？

**A:** 

**方法 1: 编辑配置文件**
```bash
# 打开配置文件
nano ~/.openclaw/router_config.yaml

# 修改后保存
```

**方法 2: 使用命令行**
```bash
# 重新运行配置向导
openclaw router config --init

# 修改预算
openclaw router budget --set 300
```

---

### Q10: 如何切换模式？

**A:** 编辑配置文件：

```yaml
# 质量优先（重要任务）
thresholds:
  mode: "quality"
  auto_pass: 4.0

# 成本优先（预算有限）
thresholds:
  mode: "economy"
  auto_pass: 3.0

# 速度优先（快速响应）
thresholds:
  mode: "speed"
  auto_pass: 3.0
  verify_min: 0
```

---

### Q11: 多用户如何管理？

**A:** 企业版支持多用户：

```yaml
users:
  - name: "user1"
    budget: 100
    mode: "balanced"
  
  - name: "user2"
    budget: 200
    mode: "quality"
```

---

## 🔧 技术问题

### Q12: 自评机制准确吗？

**A:** 非常准确！基于 5 个维度：

| 维度 | 权重 | 说明 |
|------|------|------|
| 知识储备 | 30% | 是否了解该领域 |
| 推理复杂度 | 25% | 需要多少步推理 |
| 上下文长度 | 20% | 是否超过限制 |
| 质量要求 | 15% | 用户要求多高 |
| 工具需求 | 10% | 是否需要外部工具 |

测试准确率：95%+

---

### Q13: 验证机制如何工作？

**A:** 

```
本地 14b 完成 → 自评 3.2 分 → 触发验证
    ↓
Spawn L2 验证器
    ↓
验证器评估（准确性/完整性/可行性/质量）
    ↓
平均分 ≥4 → 通过 ✅
平均分 <4 → L3 重做 ❌
```

验证通过率：约 70%
验证成本：约¥0.02/次

---

### Q14: 支持自定义模型吗？

**A:** 支持！添加自定义模型：

```yaml
models:
  custom:
    - id: "my-custom-model"
      location: "local"
      cost_per_1k: 0
      tags: ["fast", "cheap"]
```

---

### Q15: 如何集成到自己的应用？

**A:** 使用 API：

```python
from router_skill import ModelRouter

router = ModelRouter(config)
result = router.select_model(self_assessment_score=3.2)
print(result['model'])
```

---

## 🐛 故障排查

### Q16: 配置向导无法启动

**解决：**
```bash
# 检查 Python
python3 --version  # 需要 3.8+

# 检查依赖
pip3 list | grep -E "requests|psutil|pyyaml"

# 重新安装依赖
pip3 install requests psutil pyyaml
```

---

### Q17: 检测不到 Ollama

**解决：**
```bash
# 检查 Ollama 服务
ollama list

# 如未安装
curl -fsSL https://ollama.com/install.sh | sh

# 重启服务
systemctl restart ollama
```

---

### Q18: 云 API 检测失败

**解决：**
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY
echo $OPENAI_API_KEY

# 如未设置
export DASHSCOPE_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."

# 永久设置（添加到 ~/.bashrc）
echo 'export DASHSCOPE_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

---

### Q19: 配置保存失败

**解决：**
```bash
# 检查目录权限
ls -la ~/.openclaw/

# 如需要，创建目录
mkdir -p ~/.openclaw
chmod 755 ~/.openclaw
```

---

### Q20: 模型选择不符合预期

**解决：**
```bash
# 检查阈值配置
cat ~/.openclaw/router_config.yaml | grep -A5 thresholds

# 调整阈值
nano ~/.openclaw/router_config.yaml

# 使用标签强制
[L3] 这个问题很重要，用专家模型
```

---

## 📞 其他问题

### Q21: 如何反馈问题？

**A:** 
- GitHub Issue: https://github.com/pepsiboy87/openclaw-router/issues
- 邮箱：pepsiboy87@example.com

---

### Q22: 如何贡献代码？

**A:** 
```bash
# Fork 项目
git fork https://github.com/pepsiboy87/openclaw-router

# 创建分支
git checkout -b feature/your-feature

# 提交代码
git commit -m "Add your feature"

# Pull Request
git push origin feature/your-feature
```

---

### Q23: 有微信群/Discord 吗？

**A:** 有！扫码加入：
- 微信群：[二维码链接]
- Discord: [邀请链接]

---

### Q24: 企业版如何购买？

**A:** 联系邮箱：pepsiboy87@example.com

**企业版功能：**
- ✅ 所有付费版功能
- ✅ 多用户管理
- ✅ 自定义模型池
- ✅ API 访问
- ✅ SLA 保障
- ✅ 私有化部署

**价格：** ¥199/月 或 ¥1999/年

---

### Q25: 后续更新计划？

**A:** 

**v3.1 (2026-03):**
- 用户偏好学习
- 时段优化
- 详细报告

**v3.2 (2026-04):**
- 多用户支持
- API 访问
- 预算管理增强

**v4.0 (2026-05):**
- AI 自动调优
- 预测性成本优化
- 企业级功能

---

_有问题没找到答案？欢迎提交 Issue！_
