# Changelog

All notable changes to AIOps Agent will be documented in this file.

## [1.1.0] - 2026-02-25

### Added
- 🎉 **Lark (飞书) 审批对接**
  - 交互式审批卡片 (带批准/拒绝按钮)
  - 回调 API 处理用户操作
  - 卡片状态自动更新
  - 签名验证和消息加密支持

- 🧠 **学习引擎 (Learning Engine)**
  - Playbook 执行统计 (成功率、耗时)
  - 基于历史表现的风险分数自动调整
  - 执行案例存储到知识库
  - 失败经验自动提取

- 🔧 **Ansible 执行器**
  - 支持执行 Ansible Playbook
  - 支持执行 Ansible Role
  - 变量注入、标签过滤
  - Check 模式 (dry-run)

- ☸️ **K8s 集群级执行器**
  - NODE_CORDON: 节点隔离
  - NODE_DRAIN: 节点排空
  - NODE_UNCORDON: 节点恢复
  - PVC_EXPAND: PVC 扩容
  - PVC_SNAPSHOT: PVC 快照
  - NETWORK_POLICY_APPLY/REMOVE: 网络策略管理

- 📢 **通知器重构**
  - BaseNotifier 抽象基类
  - WebhookNotifier (重构)
  - LarkNotifier (新增)

### API Endpoints
- `GET /api/v1/learning/stats` - 学习引擎统计
- `GET /api/v1/playbooks/stats` - Playbook 统计
- `GET /api/v1/playbooks/stats/{id}` - 单个 Playbook 统计
- `GET /api/v1/playbooks/executions/{id}` - 执行历史
- `POST /api/v1/callbacks/lark` - Lark 回调

### Configuration
- 新增 `lark` 配置段
- 新增 `ansible` 配置段
- 新增 `k8s_cluster` 配置段
- 新增 `learning` 配置段

---

## [1.0.1] - 2026-02-25

### Fixed
- 🐛 修复核心模块语法错误
- ✅ 所有测试通过 (18/18)
- 📝 完善依赖文档说明

### Added
- 📦 补充缺失的依赖说明:
  - pytest, pytest-asyncio, pytest-cov
  - scikit-learn
  - fastapi
  - kubernetes
  - anthropic

### Improved
- 📖 改进SKILL.md文档
- 🧪 提升测试覆盖率
- 📝 添加详细的依赖安装说明

### Testing
- ✅ 18/18 tests passing
- ✅ All syntax errors resolved
- ✅ Dependencies validated

## [1.0.0] - 2026-02-25

### Added
- 🎉 Initial release
- 🤖 AIOps架构及产品初始化
- 📊 Multi-dimensional monitoring
- 🔍 Anomaly detection
- 🧠 Prediction engine
- 💡 Root cause analysis
- 🚀 Self-healing automation

### Features
- ⚡ Proactive alerting (1-3 hours ahead)
- 🔍 Automated root cause analysis
- 🤖 Self-healing automation
- 📊 Multi-dimensional data collection
- 🧠 LLM-powered insights

### Architecture
- **Perception Layer**: Metrics, logs, events collection
- **Cognition Layer**: Anomaly detection, prediction, RCA
- **Decision Layer**: Risk assessment, action planning
- **Action Layer**: Automated remediation

---

## Version Format

[Major.Minor.Patch]

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes and improvements
