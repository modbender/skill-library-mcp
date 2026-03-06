# Behavior Scripts（剧本库）

> 目标：不是"随机 sleep"，而是长期行为分布更像真人。
> 规则：每次 session 只选 1 个剧本；允许中途走神/退出；允许 0 产出。
> 选择方式：根据记忆中的近期行为分布、距上次 connect 天数、风险状态自主选择。

## Script 1: PureFeed（纯刷动态）

- **适用**：默认首选；近期 connect 偏多时必选；想降风险
- **允许**：滚动、停留阅读、打开/关闭评论区、偶发点赞 0-1
- **禁止**：connect
- **最小链路**：停留 → 滚动 →（可选 hover）→ 再滚动 → 退出

## Script 2: ExploreTrail（内容驱动探索链）

- **适用**：想建立"内容/互动 → 社交"的因果；但不一定要 connect
- **允许**：从 feed 的作者/评论者进入 profile；浏览后返回；可点赞 0-1
- **禁止**：除非记忆明确允许且本次计划中有完整证据链，否则不 connect
- **最小链路**：Feed 选一条内容 → 打开评论区 → 点作者/评论者 → profile 停留/滚动两屏 → 返回 feed → 退出

## Script 3: DistractedWander（走神乱逛）

- **适用**：增加"人类不确定性"；降低动机一致性
- **允许**：随意点 1-2 个页面（Notifications / Jobs / My Network），停留后退出
- **禁止**：connect
- **最小链路**：进入一个非 feed 页面 → 停留 → 返回 → 退出

## Script 4: WeakSocial（弱社交，偶发 connect 2-3）

- **适用**：当最近多次 session 均 0 connect 且无风险事件
- **允许**：connect 1-2（无 note）；点赞可有可无
- **禁止**：为了凑数去搜索人
- **前置证据链（必须）**：
  1) 有触发源（feed 作者/评论者/People you may know）
  2) 进入 profile
  3) 停留 + 滚动（至少两屏）
  4) 决策 connect（或放弃）

## Script 5: StrongSocial（强社交）

- **慎用**。只有当从记忆中判断：账号长期稳定（连续 7+ 天无风控事件）、近期多次 session 均 0 connect、且有明确内容触发链路时，才可偶发启用。
- **允许**：最多 3-5 个 connect；可写 note 但不强制
- **注意**：如果出现 Premium/配额限制弹窗，立刻停止并记录到记忆，后续禁用 note。
