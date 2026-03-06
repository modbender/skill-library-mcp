# 安全记忆系统栈安装指南

## 📦 安装方式

### 方式1: 通过ClawdHub安装 (推荐)

```bash
# 安装skill
clawdhub install secure-memory-stack

# 验证安装
secure-memory help
```

### 方式2: 手动安装

#### 步骤1: 下载skill
```bash
# 将下载的secure-memory-stack文件夹放入
# /root/clawd/skills/ 目录下
```

#### 步骤2: 设置权限
```bash
# 进入skills目录
cd /root/clawd/skills

# 设置执行权限
chmod +x secure-memory-stack/secure-memory
chmod +x secure-memory-stack/scripts/*.sh
```

#### 步骤3: 验证安装
```bash
# 测试命令
./secure-memory-stack/secure-memory help
```

## 🚀 首次使用

### 初始化系统
```bash
# 首次运行需要初始化
secure-memory setup
```

### 检查系统状态
```bash
# 验证系统是否正常
secure-memory status
```

## 🔧 配置选项

### 百度Embedding API (可选)
如果需要语义搜索功能，可以配置百度API：

```bash
# 配置百度API
secure-memory configure baidu
```

然后按照提示设置环境变量：
```bash
export BAIDU_API_KEY='your_api_key'
export BAIDU_SECRET_KEY='your_secret_key'
```

## ✅ 验证安装

安装完成后，运行以下命令验证：

```bash
# 检查帮助信息
secure-memory help

# 检查系统状态
secure-memory status

# 添加测试记忆
secure-memory remember "安装测试成功" --tags installation --importance normal

# 搜索测试
secure-memory search "安装"
```

## 🔍 故障排除

### 如果命令找不到
确保路径正确，或者使用完整路径：
```bash
/root/clawd/skills/secure-memory-stack/secure-memory status
```

### 如果权限错误
确保脚本具有执行权限：
```bash
chmod +x /root/clawd/skills/secure-memory-stack/secure-memory
chmod +x /root/clawd/skills/secure-memory-stack/scripts/*.sh
```

### 如果Git相关错误
修复Git配置：
```bash
secure-memory fix git
```

## 📝 使用示例

### 基本使用
```bash
# 添加记忆
secure-memory remember "重要的项目截止日期是周五" --tags project,deadline --importance high

# 搜索记忆
secure-memory search "项目截止日期"

# 查看统计
secure-memory stats
```

### 高级用法
```bash
# 系统诊断
secure-memory diagnose

# 修复组件
secure-memory fix all
```

## 🔄 更新

如果需要更新到新版本：

```bash
# 通过ClawdHub更新
clawdhub update secure-memory-stack

# 或者手动替换文件夹内容
```

## 🗑️ 卸载

如果需要卸载：

```bash
# 删除skill目录
rm -rf /root/clawd/skills/secure-memory-stack

# 如果通过ClawdHub安装
clawdhub uninstall secure-memory-stack
```

## 🆘 支持

如果遇到问题，运行：
```bash
secure-memory diagnose
```

这将生成系统诊断报告，有助于排查问题。