# 农历生日提醒系统 v0.9.0 安装指南

## 📦 安装方法

### 方法一：快速安装（推荐）
```bash
# 1. 下载发布包
wget https://github.com/xiamuciqing/lunar-birthday-reminder/releases/download/v0.9.0/lunar-birthday-reminder-v0.9.0.tar.gz

# 2. 解压
tar -xzf lunar-birthday-reminder-v0.9.0.tar.gz
cd lunar-birthday-reminder

# 3. 运行安装脚本
./install.sh
```

### 方法二：手动安装
```bash
# 1. 克隆仓库
git clone https://github.com/xiamuciqing/lunar-birthday-reminder.git
cd lunar-birthday-reminder

# 2. 安装Python依赖
pip install lunardate cnlunar

# 3. 复制到OpenClaw技能目录
cp -r . /root/.openclaw/workspace/skills/lunar-calendar

# 4. 验证安装
cd /root/.openclaw/workspace/skills/lunar-calendar
python scripts/demo_lunar.py
```

### 方法三：OpenClaw技能市场安装
```bash
# 等待v1.0.0正式版发布后
openclaw skills install lunar-calendar
```

## 🔧 系统要求

### 最低要求
- **操作系统**: Linux, macOS, Windows (WSL)
- **Python**: 3.6 或更高版本
- **内存**: 至少100MB可用空间
- **磁盘空间**: 至少10MB

### 推荐配置
- **Python**: 3.8+
- **内存**: 256MB+
- **网络**: 用于安装依赖和更新

## 📋 安装验证

### 验证步骤
1. **检查Python版本**
   ```bash
   python3 --version
   ```

2. **验证依赖安装**
   ```bash
   python3 -c "import lunardate; print('✅ lunardate 已安装')"
   python3 -c "import cnlunar; print('✅ cnlunar 已安装')"
   ```

3. **运行演示程序**
   ```bash
   python3 scripts/demo_lunar.py
   ```

4. **测试计算功能**
   ```bash
   python3 scripts/lunar_calculator.py --solar 2026-02-17
   python3 scripts/lunar_calculator.py --lunar "2037-09-05"
   ```

### 预期输出
如果安装成功，你应该看到：
```
🌙 农历生日提醒系统演示 - 夏暮辞青
==================================================
📅 公历转农历演示:
------------------------------
2026-02-17 (2026年春节) → 正月初一
...
🎉 演示完成！
```

## 🐛 故障排除

### 常见问题

#### 1. Python版本问题
**症状**: `python3: command not found`
**解决**:
```bash
# 检查Python是否安装
which python3

# 如果未安装，安装Python3
# Ubuntu/Debian:
sudo apt update && sudo apt install python3 python3-pip

# CentOS/RHEL:
sudo yum install python3 python3-pip
```

#### 2. pip安装失败
**症状**: `pip: command not found`
**解决**:
```bash
# 安装pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

#### 3. 依赖库安装失败
**症状**: `ModuleNotFoundError: No module named 'lunardate'`
**解决**:
```bash
# 使用国内镜像加速
pip install lunardate cnlunar -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者使用conda
conda install -c conda-forge lunardate
```

#### 4. 权限问题
**症状**: `Permission denied`
**解决**:
```bash
# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install lunardate cnlunar
```

### 高级问题

#### 1. 库版本冲突
```bash
# 查看已安装版本
pip list | grep -E "lunardate|cnlunar"

# 升级到最新版本
pip install --upgrade lunardate cnlunar
```

#### 2. 系统兼容性问题
如果遇到系统兼容性问题，可以：
1. 使用Docker容器
2. 使用Python虚拟环境
3. 联系作者获取帮助

## 🔄 更新与升级

### 检查更新
```bash
# 查看当前版本
cd /root/.openclaw/workspace/skills/lunar-calendar
cat package.json | grep version

# 检查GitHub最新版本
curl -s https://api.github.com/repos/xiamuciqing/lunar-birthday-reminder/releases/latest | grep tag_name
```

### 升级到新版本
```bash
# 备份当前版本
cp -r /root/.openclaw/workspace/skills/lunar-calendar /root/.openclaw/workspace/skills/lunar-calendar.backup

# 下载新版本
cd /tmp
wget https://github.com/xiamuciqing/lunar-birthday-reminder/releases/download/v1.0.0/lunar-birthday-reminder-v1.0.0.tar.gz
tar -xzf lunar-birthday-reminder-v1.0.0.tar.gz

# 安装新版本
cd lunar-birthday-reminder
./install.sh
```

## 🗑️ 卸载

### 完全卸载
```bash
# 1. 删除技能目录
rm -rf /root/.openclaw/workspace/skills/lunar-calendar

# 2. 卸载Python包（可选）
pip uninstall lunardate cnlunar -y

# 3. 清理缓存
pip cache purge
```

### 部分卸载
```bash
# 只删除技能，保留Python包
rm -rf /root/.openclaw/workspace/skills/lunar-calendar
```

## 📞 获取帮助

### 官方支持
- **GitHub Issues**: [问题报告](https://github.com/xiamuciqing/lunar-birthday-reminder/issues)
- **文档**: [README.md](README.md)
- **示例**: [scripts/demo_lunar.py](scripts/demo_lunar.py)

### 社区支持
- **小龙虾社区**: 搜索"农历生日提醒系统"
- **OpenClaw社区**: 技能讨论区
- **技术论坛**: Python相关论坛

### 紧急联系
如果遇到紧急问题，可以通过以下方式联系：
1. GitHub Issues (最快响应)
2. 项目文档中的联系方式
3. 社区@作者

## 📝 安装后步骤

### 1. 验证安装
```bash
cd /root/.openclaw/workspace/skills/lunar-calendar
./verify_installation.sh
```

### 2. 学习使用
```bash
# 查看所有示例
ls scripts/*.py

# 运行交互式演示
python scripts/interactive_demo.py
```

### 3. 参与测试
```bash
# 运行完整测试套件
python scripts/run_all_tests.py

# 提交测试结果
python scripts/submit_test_results.py
```

## 🎉 安装完成！

恭喜！农历生日提醒系统 v0.9.0 已成功安装。现在你可以：

1. **开始使用**: 运行演示程序了解功能
2. **测试验证**: 验证重要日期计算结果
3. **提供反馈**: 报告问题或提出建议
4. **参与开发**: 贡献代码或数据

**感谢安装农历生日提醒系统系统！** 🌙

---
*最后更新: 2026-02-13*
*版本: v0.9.0*
*作者: 夏暮辞青*