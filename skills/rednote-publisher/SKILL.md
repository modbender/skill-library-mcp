# 小红书长图文发布 Skill

**功能**：自动化完成小红书长图文笔记的完整发布流程  
**适用场景**：需要通过网页版发布纯文字/长图文笔记  
**预期效果**：使用 Skill 后，发布耗时从 15 分钟降至 2-3 分钟

---

## 前置条件

### 1. 浏览器配置检查

执行前确认 `~/.openclaw/openclaw.json` 包含：
```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "browser": {
          "allowHostControl": true
        }
      }
    }
  },
  "browser": {
    "enabled": true,
    "defaultProfile": "openclaw",
    "headless": false
  }
}
```

### 2. 账号状态
- 小红书账号已登录（在 openclaw 浏览器中）
- 已开通创作服务平台权限

---

## 标准发布流程

### Step 1: 启动浏览器并导航（约 30 秒）

```javascript
// 检查浏览器状态
browser status

// 启动 openclaw 浏览器
browser start --profile openclaw

// 打开创作平台
browser open https://creator.xiaohongshu.com/publish/publish?source=official --profile openclaw
```

**检查点**：页面显示"创作服务平台"左侧导航栏

---

### Step 2: 进入长文编辑器（约 20 秒）

1. 点击左侧导航 **"发布笔记"**
2. 点击 **"写长文"**
3. 点击 **"新的创作"**

**检查点**：进入编辑器，显示标题输入框 + 正文区域

---

### Step 3: 填写内容（约 30 秒）

```javascript
// 填写标题（点击标题输入框）
browser act click "输入标题" textbox
browser act type "你的标题"

// 填写正文（点击正文区域）
browser act click paragraph
browser act type "你的正文内容..."
```

**注意事项**：
- 标题限制 64 字
- 正文支持 Markdown 格式
- 建议字数 300-800 字

---

### Step 4: 一键排版（约 1 分钟）

1. 点击 **"一键排版"** 按钮
2. **选择版式**（推荐第一个版式或根据内容风格选择）
3. 点击 **"下一步"**

**检查点**：进入发布预览页面，显示封面、标题、正文预览

---

### Step 5: 发布设置（约 20 秒）

**可选操作**：
- 添加话题标签（点击"话题"按钮）
- 添加地点（点击"添加地点"）
- 勾选"原创声明"

**检查点**：标题已显示，预览正常

---

### Step 6: 发布（约 10 秒）

1. 点击 **"发布"** 按钮
2. 等待 3-5 秒
3. 点击左侧 **"笔记管理"** 验证

**检查点**：笔记管理显示新笔记，状态为"审核中"

---

## 完整命令序列

```bash
# 1. 启动并导航
openclaw browser start --profile openclaw
openclaw browser open https://creator.xiaohongshu.com/publish/publish?source=official --profile openclaw

# 2. 进入编辑器（需根据实际 snapshot 调整 ref）
# - 点击"写长文"
# - 点击"新的创作"

# 3. 填写内容
# - 点击标题 textbox，输入标题
# - 点击正文 paragraph，输入内容

# 4. 排版
# - 点击"一键排版"
# - 选择版式（如 e237）
# - 点击"下一步"

# 5. 发布
# - 点击"发布"按钮
# - 验证：笔记管理中查看
```

---

## 常见问题处理

### Q1: 浏览器无法连接
**现象**：`Error: Chrome extension relay is running, but no tab is connected`
**解决**：
1. 确保配置中 `browser.defaultProfile: "openclaw"`
2. 重启 gateway: `openclaw gateway restart`
3. 重新启动浏览器

### Q2: 标签页丢失
**现象**：targetId 失效，需要重新打开页面
**预防**：
- 使用稳定的 targetId 跟踪
- 重要操作前保存草稿

### Q3: 找不到"发布"按钮
**原因**：长图文必须先排版才能发布
**解决**：确保已完成"一键排版"→"选择版式"→"下一步"

### Q4: 发布后在哪里查看
**路径**：笔记管理 → 全部笔记 → 审核中/已发布

---

## 优化建议

1. **批量发布**：如有多篇笔记，可保持在创作平台页面，重复 Step 2-6
2. **草稿利用**：长文支持自动保存，意外中断可从草稿箱恢复
3. **版式选择**：
   - 情感/故事类：文艺清新、黄昏手稿
   - 职场/干货类：理性现代、清晰明朗
   - 生活/日常类：轻感明快、手帐书写

---

## 💰 经济性优化（Token 降本）

### 优化前 vs 优化后

| 操作 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| 浏览器操作 | 每次操作后 snapshot | 关键节点 snapshot | ~30% Token |
| 上下文管理 | 累积到 150K+ | 每任务后清理 | ~20% Token |
| 工具调用 | 多次独立调用 | 批量执行 | ~10% Token |

### 推荐操作模式

```
❌ 低效模式（浪费 Token）：
browser act click → snapshot → browser act type → snapshot → browser act click → snapshot
总 Token：~8K

✅ 高效模式（节省 Token）：
browser act click → browser act type → browser act click → wait 2s → snapshot
总 Token：~3K
```

### 关键检查点（只在这几处 snapshot）
1. 页面首次加载完成
2. 内容填写完成（标题+正文）
3. 排版完成、进入预览
4. 发布完成、验证结果

### Token 预算
- 单次发布目标：< 5K Token（不含内容创作）
- 对比：无 Skill 时 25K，节省 80%

---

## 版本记录

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2026-02-28 | 初始版本，基于 2 次实操经验 |

---

**使用本 Skill 后，预计单次发布耗时：2-3 分钟**
