# SRE Agent 新功能使用指南

本文档详细说明如何配置和使用 SRE Agent 的新功能。

---

## 目录

1. [学习引擎 (Learning Engine)](#1-学习引擎-learning-engine)
2. [K8s 集群执行器](#2-k8s-集群执行器)
3. [Ansible 执行器](#3-ansible-执行器)
4. [Lark 飞书审批](#4-lark-飞书审批)

---

## 1. 学习引擎 (Learning Engine)

学习引擎会自动从每次执行结果中学习，持续优化风险评估和决策。

### 1.1 工作原理

```
执行 Playbook
     ↓
记录执行结果 (成功/失败/耗时)
     ↓
更新 Playbook 统计
     ↓
计算风险调整建议
     ↓
存储执行案例到知识库
     ↓
下次执行时应用学习结果
```

### 1.2 配置

**config/config.yaml**:
```yaml
learning:
  enabled: true                      # 启用学习引擎
  min_executions_for_learning: 3     # 最少执行3次后才开始学习
  success_rate_threshold: 0.8        # 成功率阈值
  auto_risk_adjustment: true         # 自动调整风险分数
  max_risk_reduction: 0.2            # 最大风险降低幅度
```

### 1.3 学习引擎如何影响决策

**场景示例**：

假设有一个 "restart-pod" Playbook：
- 初始风险分数: 0.5 (需要审批)
- 执行 10 次后，成功率 95%
- 学习引擎建议风险调整: -0.15
- 调整后风险分数: 0.35 (自动执行)

```python
# 风险调整逻辑
if success_rate >= 0.95:
    risk_adjustment = -0.15  # 降低风险
elif success_rate >= 0.90:
    risk_adjustment = -0.10
elif success_rate >= 0.80:
    risk_adjustment = -0.05
elif success_rate < 0.50:
    risk_adjustment = +0.15  # 提高风险
```

### 1.4 查询学习统计

**查看学习引擎状态**:
```bash
curl http://localhost:8000/api/v1/learning/stats
```

响应:
```json
{
  "enabled": true,
  "auto_risk_adjustment": true,
  "min_executions_for_learning": 5,
  "playbooks_with_adjustments": 3,
  "total_playbooks": 5,
  "total_executions": 47,
  "successful_executions": 42,
  "overall_success_rate": 0.89
}
```

**查看所有 Playbook 统计**:
```bash
curl http://localhost:8000/api/v1/playbooks/stats
```

响应:
```json
{
  "count": 3,
  "playbooks": [
    {
      "playbook_id": "restart-pod",
      "playbook_name": "Restart Pod",
      "total_executions": 25,
      "success_rate": "92.0%",
      "avg_duration": "15.3s",
      "confidence": "0.92",
      "risk_adjustment": "-0.10",
      "last_execution": "2026-02-25T10:30:00Z"
    },
    {
      "playbook_id": "scale-hpa",
      "playbook_name": "Scale HPA",
      "total_executions": 12,
      "success_rate": "83.3%",
      "avg_duration": "8.2s",
      "confidence": "0.50",
      "risk_adjustment": "-0.05",
      "last_execution": "2026-02-25T09:15:00Z"
    }
  ]
}
```

**查看单个 Playbook 详情**:
```bash
curl http://localhost:8000/api/v1/playbooks/stats/restart-pod
```

**查看执行历史**:
```bash
curl http://localhost:8000/api/v1/playbooks/executions/restart-pod?limit=10
```

响应:
```json
{
  "playbook_id": "restart-pod",
  "count": 10,
  "executions": [
    {
      "id": "exec-a1b2c3d4",
      "plan_id": "plan-xyz",
      "success": true,
      "duration_seconds": 12,
      "executed_at": "2026-02-25T10:30:00Z",
      "error_message": null,
      "rolled_back": false
    },
    {
      "id": "exec-e5f6g7h8",
      "plan_id": "plan-abc",
      "success": false,
      "duration_seconds": 45,
      "executed_at": "2026-02-25T09:00:00Z",
      "error_message": "Connection timeout",
      "rolled_back": true
    }
  ]
}
```

### 1.5 在代码中使用学习引擎

```python
from src.cognition.learning_engine import LearningEngine
from src.cognition.knowledge_base import KnowledgeBase

# 初始化
kb = KnowledgeBase()
await kb.initialize()

learning_engine = LearningEngine(knowledge_base=kb)

# 检查是否应该自动批准
should_auto = learning_engine.should_auto_approve(
    playbook_id="restart-pod",
    base_risk_score=0.5
)
# 如果历史成功率高，可能返回 True

# 获取调整后的风险分数
adjusted_risk = learning_engine.get_adjusted_risk_score(
    playbook_id="restart-pod",
    base_risk_score=0.5
)
# 可能返回 0.35 (降低了 0.15)

# 记录执行结果 (通常由 AutoRemediation 自动调用)
await learning_engine.record_execution(
    plan=completed_plan,
    anomaly=anomaly,
    playbook_id="restart-pod",
    playbook_name="Restart Pod"
)
```

---

## 2. K8s 集群执行器

K8s 集群执行器用于节点级别和集群级别的操作。

### 2.1 配置

**config/config.yaml**:
```yaml
k8s_cluster:
  drain_timeout_seconds: 300    # Drain 操作超时时间
  drain_grace_period: 30        # Pod 优雅终止时间
  ignore_daemonsets: true       # Drain 时忽略 DaemonSet Pod
  delete_emptydir_data: false   # 是否删除 emptyDir 数据
  force_drain: false            # 强制 Drain (即使有 PDB 阻止)
```

### 2.2 支持的操作

| ActionType | 说明 | Target 格式 |
|------------|------|-------------|
| `NODE_CORDON` | 标记节点不可调度 | `node/<name>` |
| `NODE_DRAIN` | 驱逐所有 Pod 并 Cordon | `node/<name>` |
| `NODE_UNCORDON` | 标记节点可调度 | `node/<name>` |
| `PVC_EXPAND` | 扩容 PVC | `pvc/<namespace>/<name>` |
| `PVC_SNAPSHOT` | 创建 VolumeSnapshot | `pvc/<namespace>/<name>` |
| `NETWORK_POLICY_APPLY` | 应用 NetworkPolicy | `netpol/<namespace>/<name>` |
| `NETWORK_POLICY_REMOVE` | 删除 NetworkPolicy | `netpol/<namespace>/<name>` |

### 2.3 使用示例

#### 节点 Cordon (隔离节点)

```python
from src.action.executors.k8s_cluster_executor import K8sClusterExecutor

executor = K8sClusterExecutor()
await executor.connect()

# Cordon 节点 - 阻止新 Pod 调度到该节点
result = await executor.cordon_node(
    target="node/worker-node-1",
    namespace="",  # 节点操作不需要 namespace
    parameters={}
)

print(result)
# {
#   "success": True,
#   "state_before": {"name": "worker-node-1", "unschedulable": False},
#   "state_after": {"unschedulable": True},
#   "rollback_data": {"name": "worker-node-1", "unschedulable": False}
# }
```

#### 节点 Drain (排空节点)

```python
# Drain 节点 - 驱逐所有 Pod
result = await executor.drain_node(
    target="node/worker-node-1",
    namespace="",
    parameters={
        "grace_period": 30,           # Pod 优雅终止时间
        "timeout": 300,               # 超时时间
        "ignore_daemonsets": True,    # 忽略 DaemonSet
        "delete_emptydir_data": False,# 不删除 emptyDir 数据
        "force": False,               # 不强制
        "dry_run": False              # 设为 True 只预览
    }
)

print(result)
# {
#   "success": True,
#   "evicted_pods": [
#     {"name": "nginx-abc123", "namespace": "default"},
#     {"name": "app-xyz789", "namespace": "production"}
#   ],
#   "failed_pods": [],
#   "skipped_pods": [
#     {"name": "node-exporter-xxx", "namespace": "monitoring", "reason": "DaemonSet"}
#   ],
#   "rollback_data": {"node": "worker-node-1", "was_cordoned": False}
# }
```

#### 节点 Uncordon (恢复节点)

```python
# Uncordon 节点 - 恢复调度
result = await executor.uncordon_node(
    target="node/worker-node-1",
    namespace="",
    parameters={}
)
```

#### PVC 扩容

```python
# 扩容 PVC (需要 StorageClass 支持 allowVolumeExpansion)
result = await executor.expand_pvc(
    target="pvc/default/my-data-pvc",  # pvc/<namespace>/<name>
    namespace="default",
    parameters={
        "new_size": "20Gi"  # 新大小 (必需)
    }
)

print(result)
# {
#   "success": True,
#   "state_before": {"name": "my-data-pvc", "namespace": "default", "size": "10Gi"},
#   "state_after": {"size": "20Gi"},
#   "rollback_data": {...}  # 注意: PVC 不支持缩容
# }
```

#### PVC 快照

```python
# 创建 VolumeSnapshot (需要 VolumeSnapshot CRD)
result = await executor.create_pvc_snapshot(
    target="pvc/default/my-data-pvc",
    namespace="default",
    parameters={
        "snapshot_class": "csi-snapclass",  # 可选
        "snapshot_name": "my-backup"        # 可选，不填自动生成
    }
)

print(result)
# {
#   "success": True,
#   "snapshot_name": "my-backup",
#   "pvc_name": "my-data-pvc",
#   "namespace": "default"
# }
```

#### NetworkPolicy 管理

```python
# 应用 NetworkPolicy
result = await executor.apply_network_policy(
    target="netpol/default/deny-all",
    namespace="default",
    parameters={
        "policy_spec": {
            "podSelector": {"matchLabels": {"app": "web"}},
            "policyTypes": ["Ingress", "Egress"],
            "ingress": [],  # 拒绝所有入站
            "egress": []    # 拒绝所有出站
        }
    }
)

# 删除 NetworkPolicy
result = await executor.remove_network_policy(
    target="netpol/default/deny-all",
    namespace="default",
    parameters={}
)
```

### 2.4 在 Playbook 中使用

创建一个 Playbook 使用 K8s 集群执行器：

```yaml
# playbooks/node-maintenance.yaml
id: node-maintenance
name: Node Maintenance
description: Safely drain and cordon a node for maintenance
triggers:
  - metric_pattern: "node_.*"
    anomaly_types: ["threshold"]

steps:
  - action: NODE_CORDON
    target: "node/${NODE_NAME}"
    description: "Cordon the node"

  - action: NODE_DRAIN
    target: "node/${NODE_NAME}"
    parameters:
      grace_period: 60
      ignore_daemonsets: true
      timeout: 600
    description: "Drain all pods from node"

rollback:
  - action: NODE_UNCORDON
    target: "node/${NODE_NAME}"
```

---

## 3. Ansible 执行器

Ansible 执行器允许运行 Ansible Playbook 和 Role 进行复杂的自动化操作。

### 3.1 配置

**环境变量**:
```bash
ANSIBLE_ENABLED=true
ANSIBLE_PLAYBOOKS_DIR=/etc/sre-agent/ansible/playbooks
ANSIBLE_ROLES_DIR=/etc/sre-agent/ansible/roles
ANSIBLE_INVENTORY=/etc/sre-agent/ansible/inventory
```

**config/config.yaml**:
```yaml
ansible:
  enabled: true
  playbooks_dir: /etc/sre-agent/ansible/playbooks
  roles_dir: /etc/sre-agent/ansible/roles
  inventory_file: /etc/sre-agent/ansible/inventory
  timeout_seconds: 600      # 执行超时
  forks: 5                  # 并行执行数
  become: false             # 默认不使用 sudo
  become_user: root         # sudo 用户
  extra_vars: {}            # 全局额外变量
```

### 3.2 目录结构

```
/etc/sre-agent/ansible/
├── inventory                    # Ansible Inventory 文件
├── playbooks/
│   ├── restart-service.yml
│   ├── deploy-hotfix.yml
│   └── cleanup-disk.yml
└── roles/
    ├── common/
    ├── web-server/
    └── database/
```

### 3.3 Inventory 示例

```ini
# /etc/sre-agent/ansible/inventory

[web_servers]
web-1.example.com
web-2.example.com
web-3.example.com

[db_servers]
db-master.example.com
db-slave.example.com

[all:vars]
ansible_user=deploy
ansible_ssh_private_key_file=/etc/sre-agent/ssh/id_rsa
```

### 3.4 使用示例

#### 执行 Playbook

```python
from src.action.executors.ansible_executor import AnsibleExecutor

executor = AnsibleExecutor()

# 执行 playbook
result = await executor.run_playbook(
    target="playbook/restart-service",  # 或 "restart-service.yml"
    namespace="",  # Ansible 不使用 namespace
    parameters={
        "hosts": "web_servers",       # 目标主机组
        "extra_vars": {               # 额外变量
            "service_name": "nginx",
            "restart_delay": 5
        },
        "tags": ["restart"],          # 只运行这些 tag
        "skip_tags": ["cleanup"],     # 跳过这些 tag
        "check": False,               # 检查模式 (dry-run)
        "diff": True,                 # 显示差异
        "verbosity": 1,               # 详细程度 (0-4)
        "limit": "web-1.example.com", # 限制主机
        "become": True,               # 使用 sudo
        "timeout": 300                # 超时时间
    }
)

print(result)
# {
#   "success": True,
#   "rc": 0,
#   "duration_seconds": 45,
#   "stats": {
#     "web-1.example.com": {"ok": 5, "changed": 2, "failures": 0},
#     "web-2.example.com": {"ok": 5, "changed": 2, "failures": 0}
#   },
#   "stdout": "...",
#   "stderr": "",
#   "error": null
# }
```

#### 执行 Role

```python
# 执行单个 role
result = await executor.run_role(
    target="role/web-server",  # 或 "web-server"
    namespace="",
    parameters={
        "hosts": "web_servers",  # 必需
        "extra_vars": {
            "nginx_port": 8080,
            "ssl_enabled": True
        },
        "become": True
    }
)
```

#### Playbook 示例文件

```yaml
# /etc/sre-agent/ansible/playbooks/restart-service.yml
---
- name: Restart Service
  hosts: "{{ target_hosts | default('all') }}"
  become: yes

  vars:
    service_name: "{{ service | default('nginx') }}"
    restart_delay: "{{ delay | default(5) }}"

  tasks:
    - name: Stop service
      service:
        name: "{{ service_name }}"
        state: stopped
      tags: [restart, stop]

    - name: Wait before restart
      pause:
        seconds: "{{ restart_delay }}"
      tags: [restart]

    - name: Start service
      service:
        name: "{{ service_name }}"
        state: started
      tags: [restart, start]

    - name: Verify service is running
      service:
        name: "{{ service_name }}"
        state: started
      register: service_status
      failed_when: service_status.state != "started"
      tags: [restart, verify]
```

### 3.5 在 SRE Playbook 中使用 Ansible

```yaml
# SRE Agent Playbook 配置
id: ansible-restart-nginx
name: Restart Nginx via Ansible
description: Use Ansible to restart nginx on web servers
triggers:
  - metric_pattern: "nginx_.*_errors"
    anomaly_types: ["threshold"]
    severity: ["high", "critical"]

steps:
  - action: ANSIBLE_PLAYBOOK
    target: "playbook/restart-service"
    parameters:
      hosts: "web_servers"
      extra_vars:
        service_name: nginx
        restart_delay: 10
      tags: ["restart"]
      become: true
    description: "Restart nginx on all web servers"

risk_override: 0.5  # 中等风险，需要审批
```

### 3.6 查询可用 Playbook

```python
# 列出所有可用 playbook
playbooks = await executor.list_playbooks()
# [
#   {"name": "restart-service", "path": "restart-service.yml", "full_path": "/etc/.../restart-service.yml"},
#   {"name": "deploy-hotfix", "path": "deploy-hotfix.yml", "full_path": "/etc/.../deploy-hotfix.yml"}
# ]

# 列出所有可用 role
roles = await executor.list_roles()
# [
#   {"name": "web-server", "path": "/etc/sre-agent/ansible/roles/web-server"},
#   {"name": "database", "path": "/etc/sre-agent/ansible/roles/database"}
# ]

# 验证 playbook 语法
validation = await executor.validate_playbook("restart-service")
# {"valid": True, "error": None}
```

---

## 4. Lark 飞书审批

### 4.1 配置

**环境变量**:
```bash
LARK_ENABLED=true
LARK_APP_ID=cli_xxxxx
LARK_APP_SECRET=xxxxx
LARK_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
LARK_VERIFICATION_TOKEN=xxxxx
```

### 4.2 飞书开放平台配置

1. 创建企业自建应用
2. 获取 App ID 和 App Secret
3. 创建机器人，获取 Webhook URL
4. 配置事件订阅，回调地址设为: `https://your-domain/api/v1/callbacks/lark`
5. 订阅 "卡片回调" 事件

### 4.3 审批流程

```
异常检测 → 生成 Action Plan → 风险评估
                                    ↓
                            风险 >= 阈值?
                                    ↓
                        发送审批卡片到飞书
                                    ↓
                        用户点击 批准/拒绝
                                    ↓
                        回调到 /api/v1/callbacks/lark
                                    ↓
                        更新卡片状态 + 执行/取消
```

### 4.4 使用示例

```python
from src.action.notifiers.lark_notifier import LarkNotifier

notifier = LarkNotifier()
await notifier.start()

# 发送异常告警
result = await notifier.send_anomaly(anomaly)

# 发送审批请求 (带交互按钮)
result = await notifier.send_approval_request(
    plan_id="plan-abc123",
    action_type="DEPLOYMENT_ROLLBACK",
    target="deployment/web-app",
    risk_score=0.65,
    summary="Rollback web-app to previous version due to high error rate"
)

# 发送执行状态
result = await notifier.send_remediation_status(
    action_type="DEPLOYMENT_ROLLBACK",
    target="deployment/web-app",
    status="success",
    duration_seconds=45
)
```

---

## 5. 完整使用流程示例

### 场景: 节点内存不足，自动化处理

1. **异常检测**: 检测到 `node_memory_available` 低于阈值

2. **创建 Action Plan**:
```python
plan = action_planner.create_plan(
    anomaly=memory_anomaly,
    playbook_id="node-memory-relief"
)
```

3. **学习引擎检查**:
```python
# 检查是否可以自动批准
adjusted_risk = learning_engine.get_adjusted_risk_score(
    playbook_id="node-memory-relief",
    base_risk_score=plan.risk_score
)
# 如果历史成功率高，风险会降低
```

4. **发送审批 (如需要)**:
```python
if plan.requires_approval:
    await lark_notifier.send_approval_request(
        plan_id=plan.id,
        action_type="NODE_DRAIN",
        target=f"node/{node_name}",
        risk_score=adjusted_risk,
        summary="Drain node to relieve memory pressure"
    )
```

5. **执行 (用户批准后或自动)**:
```python
# 执行步骤 1: Cordon 节点
await k8s_cluster_executor.cordon_node(target, namespace, {})

# 执行步骤 2: Drain 节点
await k8s_cluster_executor.drain_node(target, namespace, {
    "ignore_daemonsets": True,
    "grace_period": 60
})

# 执行步骤 3: Ansible 清理
await ansible_executor.run_playbook(
    target="playbook/cleanup-memory",
    namespace="",
    parameters={"hosts": node_name}
)

# 执行步骤 4: Uncordon 节点
await k8s_cluster_executor.uncordon_node(target, namespace, {})
```

6. **记录学习**:
```python
# 自动记录执行结果
await learning_engine.record_execution(
    plan=completed_plan,
    anomaly=memory_anomaly,
    playbook_id="node-memory-relief"
)
# 下次类似情况，风险评估会更准确
```

7. **通知结果**:
```python
await lark_notifier.send_remediation_status(
    action_type="NODE_MEMORY_RELIEF",
    target=f"node/{node_name}",
    status="success",
    duration_seconds=total_duration
)
```

---

## 常见问题

### Q: 学习引擎数据存储在哪里?
A: 默认存储在内存中。生产环境建议通过 KnowledgeBase 持久化到 Qdrant。

### Q: Ansible 执行需要 SSH 密钥吗?
A: 是的，需要配置 SSH 密钥或密码。建议在 inventory 中配置 `ansible_ssh_private_key_file`。

### Q: K8s 集群操作需要什么权限?
A: 需要 ClusterRole 权限，包括:
- nodes: get, list, patch, update
- pods: get, list, delete, create (eviction)
- persistentvolumeclaims: get, patch
- volumesnapshots: create
- networkpolicies: get, create, update, delete

### Q: 飞书回调地址必须是 HTTPS 吗?
A: 生产环境必须是 HTTPS。开发环境可以使用 ngrok 等工具。

---

**文档结束**
