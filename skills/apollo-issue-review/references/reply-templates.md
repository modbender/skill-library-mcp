# Reply Templates

Use these as skeletons. Replace placeholders with issue-specific facts.

## Template A: environment or dependency bottleneck

**初步判断**  
从 `<old_version>` 到 `<new_version>`，`<endpoint_or_code_path>` 的核心实现没有明显变化，当前更像是链路或依赖（`<adminservice/db/sso/network>`）导致的性能差异，不是明确的版本回归。

**建议排查路径（优先级从高到低）**  
1. 浏览器 Network 里确认 `GET <slow_endpoint>` 的 TTFB 和响应大小。  
2. 在 portal 侧执行 `<arthas_cmd_1>`、`<arthas_cmd_2>`。  
3. 在 adminservice 侧执行 `<arthas_cmd_3>`。  
4. 检查 `<db_or_auth_or_network_focus>`。  

## Template B: known unoptimized path in target version

**初步判断**  
当前现象更接近 `<path>` 的已知性能瓶颈，`<target_version>` 尚未包含后续优化（例如 `<pr_or_commit>`），因此更像是优化差异而非功能回归。

**建议排查路径**  
1. 先确认慢点是否集中在 `<endpoint>`。  
2. 对 `<method_or_controller>` 做方法级 trace。  
3. 结合 `<pr_or_commit>` 判断是否需要升级或 backport。  

## Template C: likely regression with evidence

**初步判断**  
在相同数据和拓扑下，从 `<old_version>` 升级到 `<new_version>` 后，`<endpoint_or_feature>` 明显变慢，且对应热路径在版本间有变化，当前倾向于版本回归。

**下一步建议**  
1. 锁定最慢的 `<endpoint>`，给出每次调用耗时分布。  
2. 对 `<changed_method>` 做 trace 并对比旧版本。  
3. 若确认回归，补充最小复现条件并关联 `<issue_or_pr_link>`。  

## Template D: roadmap or test-asset request

**初步判断**  
这个问题核心是 `<roadmap_or_validation_goal>`，不是单点性能回归。当前更需要明确支持边界（是否有升级计划）和可执行验证资产（现有测试/文档/附件）以支持用户自助迁移验证。

**当前状态（直接回答用户诉求）**  
1. 升级计划：`<has_or_no_explicit_timeline>`。  
2. 验证资产：`<existing_tests_docs_or_attachments>`。  

**建议落地路径（优先级从高到低）**  
1. 先定义最小回归范围：`<core_read_publish_notify_portal_endpoints>`。  
2. 在现有仓库测试基础上执行并补齐定制点验证：`<mvn_or_module_tests>`。  
3. 做非代码验证：`<db_sso_network_focus>`。  
4. 如希望社区协同推进，提供 `<minimal_boot3_branch_or_repro_scope>` 以便评审兼容性风险。  

## Template E: community user claims implementation

**结论（先鼓励，再判断）**  
感谢 @<contributor> 认领这个需求并给出方案，方向整体 `<可行/部分可行>`。  

**可复用部分**  
1. `<existing_controller_or_service_logic>` 可复用，建议沉到 service 层复用。  
2. `<existing_validation_or_permission_logic>` 可沿用，减少行为偏差。  

**不建议直接复用的部分**  
1. `<existing_notifier_or_event_pipeline>` 语义是 `<current_semantics>`，不建议直接用于 `<new_semantics>`。  

**建议落地拆分**  
1. 先交付最小可用能力：`<single_api_or_small_scope>`。  
2. 再扩展：`<batch_or_notification_or_extra_capability>`。  
3. 补齐：鉴权、重复数据处理、失败语义、测试与文档。  

**后续路径**  
欢迎继续推进 PR，maintainer 会按以上边界优先协助 review。  

## Tone Rules

- 先给判断，再给步骤，最后给边界。  
- 用“可能/倾向/初步判断”表达不确定性，避免绝对化结论。  
- 开源社区语境下优先给自助排查方案，避免承诺 maintainer 代排障。  

## Publish Confirmation Gate (mandatory)

Before posting to GitHub, always send this question after showing the draft:

`这是一版可直接发布的回复。是否直接发布到 issue #<id>？回复“发布”或“先不发”。`

Only run `gh api .../comments` or `curl .../comments` after explicit confirmation.
