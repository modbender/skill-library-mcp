# GitHub Upstream Synchronization

## 1. 目标

持续追踪源仓库变更（commit / PR / release），并把变化映射为 Rust 重写任务，避免重写分支与原仓库长期漂移。

## 2. 推荐协作方式

1. 用 `github-helper` skill 管理本地仓库、问题单、PR 语义上下文。
2. 用本技能的 `scripts/upstream_sync_report.py` 计算 upstream 与 origin 的 commit 差异。
3. 将新增变更标注为三类任务：
   - 行为一致性修复；
   - API/协议兼容调整；
   - 性能或工程治理优化。

## 3. 标准同步流程

### 3.1 建立远程关系

在重写仓库中确保存在两个 remote：

- `upstream`：原始项目仓库；
- `origin`：重写分支仓库（你自己的 fork 或镜像仓库）。

### 3.2 获取差异报告

```bash
python3 scripts/upstream_sync_report.py --repo /path/to/rewrite-repo --branch main
```

输出应包含：

- upstream 独有 commit 数；
- origin 独有 commit 数；
- 上游最近新增 commit 列表（用于进入 backlog）。

### 3.3 映射到重写 backlog

每条 upstream commit 至少记录：

- 影响模块；
- 风险等级（高/中/低）；
- 是否影响协议/持久化/对外 API；
- 对应 Rust 任务编号与预计批次。

## 4. PR 与发布追踪

若本地环境具备 `gh`，补充执行：

```bash
gh pr list --repo <owner>/<repo> --state open --limit 30
gh release list --repo <owner>/<repo> --limit 10
```

将“已合并但未同步”的 PR 标记为高优先级输入。

## 5. 节奏建议

- 高频活跃仓库：每日同步一次；
- 常规仓库：每周同步两次；
- 重大版本窗口：在 release 前后增加同步频次。

## 6. 失败处理原则

- 获取失败时明确报错，不伪造“同步成功”；
- 同步数据不完整时，暂停生成重写结论并标记阻塞原因；
- 任何自动化结果都要带上执行时间和分支名。
