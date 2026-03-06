# ARCH_SPLIT.md

## Architecture Decision
GuavaGuard は OSS の汎用セキュリティエンジンとして公開し、Soul/Hash/Memory統合は GuavaSuite として private 管理する。

## Product Boundary

### GuavaGuard (OSS)
含む:
- 静的スキャン（汎用ルール）
- Runtime Guard（汎用）
- CLI / JSON / SARIF 出力
- Extension Host（plugin API）

含まない:
- Soul Lock
- Identity hash ledger
- Memory v4 integration
- Dee/Guava 固有ポリシー

### GuavaSuite (Private)
含む:
- Soul Lock
- Hash integration and recovery
- GuavaMemory v4 orchestration
- EAE integration policies

## Integration Model
- Guard → Suite は plugin API 経由のみ
- 直接 import 禁止
- Suite 未接続時は fail-closed（guard-only安全動作）

## Compatibility Contract
- API versioning: `x.y`
- Backward compatible: minor
- Breaking changes: major

## Directory Sketch
- `skills/guava-guard/` (OSS)
- `private/guava-suite/` (Private)
- `skills/guava-guard/plugin-api/` (shared contract only)

## Non-goals
- OSS側にSuite実装断片を残さない
- 「隠しフラグ」で実質統合しない
