# iFlow CLI 认证指南 - Linux 服务器版

> **适用场景**: 在无浏览器的 Linux 服务器上使用 iFlow CLI

---

## 📋 认证方式对比

| 方式 | 适用场景 | 难度 | 推荐度 |
|------|----------|------|--------|
| **环境变量** | 服务器/无浏览器 | ⭐ 简单 | ⭐⭐⭐ |
| OAuth 网页 | 本地电脑/有浏览器 | ⭐⭐ 中等 | ⭐⭐ |
| ACP 模式 | 高级用户/程序调用 | ⭐⭐⭐ 复杂 | ⭐ |

---

## 🔧 方式一：环境变量认证（推荐）⭐

### **优势**
- ✅ 无需浏览器
- ✅ 配置简单
- ✅ 适合服务器
- ✅ 长期稳定

### **步骤**

#### **1. 获取 API Key**

在**有浏览器的设备**上（电脑/手机）：

1. 访问 https://iflow.cn/
2. 登录/注册账号
3. 进入 **用户设置** 页面
4. 点击 **生成 API Key**
5. 复制生成的 API Key（格式：`sk-xxxxxxxx`）

#### **2. 配置到服务器**

在服务器上执行：

```bash
# 编辑环境变量文件
nano ~/.bashrc

# 添加到文件末尾
export IFLOW_API_KEY="sk-你的 API Key"
export IFLOW_BASE_URL="https://apis.iflow.cn/v1"
export IFLOW_MODEL_NAME="glm-5"

# 保存后加载
source ~/.bashrc
```

#### **3. 验证配置**

```bash
# 检查环境变量
echo $IFLOW_API_KEY

# 测试 iflow
iflow -p "hello"
```

---

## 🌐 方式二：OAuth 网页认证（本地电脑）

### **适用场景**
- 本地电脑（有浏览器）
- 首次使用
- 交互式环境

### **完整步骤**

#### **步骤 1：启动 iflow**

```bash
iflow
```

#### **步骤 2：选择登录方式**

iflow 会显示菜单：

```
How would you like to authenticate for this project?

● 1. Login with iFlow(recommend)
  2. Login with iFlow ApiKey
  3. OpenAI Compatible API
```

**操作**：输入 `1` 然后按 `Enter`

#### **步骤 3：复制 OAuth 链接**

iflow 会显示：

```
iFlow OAuth Login

1. Please copy the following link and open it in your browser:

   https://iflow.cn/oauth?loginMethod=phone&type=phone&redirect=...&state=xxx&client_id=xxx

2. Login to your iFlow account and authorize

3. Copy the authorization code and paste it below:

Authorization Code: [等待输入...]
```

**操作**：
1. 复制上面的长链接
2. 在浏览器打开

#### **步骤 4：登录并授权**

1. 在浏览器打开链接
2. 使用手机号登录 iFlow
3. 点击 **授权** 按钮
4. 页面会显示 **授权码**（Authorization Code）
5. 复制授权码

#### **步骤 5：粘贴授权码**

回到终端，粘贴授权码到输入框：

```
Authorization Code: 04753be03f08418e8e380bb395c9d87b
```

按 `Enter` 确认。

#### **步骤 6：完成**

认证成功后，iflow 会保存认证信息到 `~/.iflow/settings.json`

后续使用无需再次认证！

---

## 🤖 方式三：ACP 模式（高级）

### **适用场景**
- 程序化调用
- 与其他工具集成
- WebSocket 通信

### **步骤**

```bash
# 启动 iflow ACP 服务
iflow --experimental-acp --port 8090

# 通过 WebSocket 连接
# ws://localhost:8090/acp
```

---

## 📁 配置文件位置

### **Linux/Mac**
```
~/.iflow/settings.json
```

### **配置示例**
```json
{
  "apiKey": "sk-xxxxxxxx",
  "baseUrl": "https://apis.iflow.cn/v1",
  "modelName": "glm-5",
  "selectedAuthType": "api_key"
}
```

---

## ⚠️ 常见问题

### **1. API Key 有效期多久？**

- **7 天**
- 过期后需要重新生成
- 建议设置每周提醒

### **2. 如何更新过期的 API Key？**

```bash
# 重新生成 API Key（在浏览器）
https://iflow.cn/

# 更新环境变量
export IFLOW_API_KEY="sk-新密钥"
```

### **3. 如何检查认证状态？**

```bash
# 检查配置文件
cat ~/.iflow/settings.json

# 检查环境变量
echo $IFLOW_API_KEY

# 测试连接
iflow -p "test"
```

### **4. 认证失败怎么办？**

```bash
# 1. 检查 API Key 是否正确
cat ~/.iflow/settings.json

# 2. 检查网络连接
curl -I https://apis.iflow.cn/v1

# 3. 重新生成 API Key
# 访问 https://iflow.cn/ 生成新的 Key

# 4. 清除配置重新认证
rm -rf ~/.iflow
iflow
```

---

## 📝 最佳实践

### **1. 使用环境变量**

在服务器上，使用环境变量更安全：

```bash
# ~/.bashrc 或 ~/.zshrc
export IFLOW_API_KEY="sk-xxx"
export IFLOW_BASE_URL="https://apis.iflow.cn/v1"
export IFLOW_MODEL_NAME="glm-5"
```

### **2. 设置权限**

保护配置文件：

```bash
chmod 600 ~/.iflow/settings.json
```

### **3. 定期更新**

设置每周提醒更新 API Key：

```bash
# 在日历中设置每周一提醒
# 或使用 cron 任务
```

### **4. 备份配置**

```bash
# 备份配置
cp ~/.iflow/settings.json ~/.iflow/settings.json.bak

# 恢复配置
cp ~/.iflow/settings.json.bak ~/.iflow/settings.json
```

---

## 🔗 相关链接

- **iFlow 官网**: https://iflow.cn/
- **iFlow CLI GitHub**: https://github.com/iflow-ai/iflow-cli
- **开发者论坛**: https://vibex.iflow.cn/t/topic/1057
- **完整文档**: https://platform.iflow.cn/cli/

---

## 📞 获取帮助

遇到问题？

1. 查看日志：`~/.iflow/log/`
2. 运行调试模式：`iflow -d`
3. 访问开发者论坛
4. 提交 GitHub Issue

---

**最后更新**: 2026-02-28  
**适用版本**: iFlow CLI 0.5.14+
