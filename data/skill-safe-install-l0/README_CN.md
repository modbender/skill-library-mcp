# Skill Safe Install（L0 级）

这是一个用于 OpenClaw 的**严格安全安装流程**技能。

## 解决的问题
当用户说“安装技能”时，不能只执行 `clawhub install`，必须走完整安全流程：

1. 查重检查
2. 搜索候选
3. 安全审查（`clawhub inspect`）
4. 沙箱安装（隔离 workdir）
5. 正式安装
6. 白名单写入（必须用户授权）

## 为什么重要
- 防止盲装技能
- 形成可审计的安全检查链路
- 修改 JSON 配置前强制授权

## 沙箱替代方案
由于 `clawhub install` 当前没有 `--sandbox` 参数，使用隔离目录代替：

```bash
TMP=$(mktemp -d)
clawhub --workdir "$TMP" --dir skills install <slug>
```

## 版本
- v2.1.0：强化 L0 触发规则，统一输出模板，修正沙箱说明。
