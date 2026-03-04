# ohos-react-native-performance

OpenHarmony React Native performance static-check agent skill for the **static analysis** tool. For use by any agent that supports skills.

## Source

- **Official repo (this skill):** <https://gitcode.com/openharmony-sig/homecheck> — path `skills/ohos-react-native-performance/`.
- **Content source (performance docs):** [performance-optimization (en)](https://gitcode.com/openharmony-sig/ohos_react_native/blob/master/docs/en/performance-optimization.md) · [性能调优 (zh)](https://gitcode.com/openharmony-sig/ohos_react_native/blob/master/docs/zh-cn/性能调优.md)


## Usage

### npx skills add

If your agent supports [skills.sh](https://skills.sh/), install from the homecheck repo:

```bash
# From homecheck repo (GitCode)
npx skills add https://gitcode.com/openharmony-sig/homecheck --skill ohos-react-native-performance

# Or if shorthand is supported for your git host
# npx skills add openharmony-sig/homecheck --skill ohos-react-native-performance
```

### Common agent installation

| Agent | Command / Path |
|-------|----------------|
| **skills.sh** | `npx skills add <source> --skill ohos-react-native-performance` |
| **Claude Code** | Copy to agent skills dir, or use `npx skills add` |
| **VS Code / Copilot** | Copy to configured skills path, or use `npx ai-agent-skills install` |
| **Manual** | Copy this folder into your agent's skills directory |

## Structure

```
ohos-react-native-performance/
├── README.md
├── SKILL.md
└── rules/
    ├── rnoh-render-avoid-same-state.md
    ├── rnoh-render-pure-memo.md
    ├── rnoh-render-props-once.md
    ├── rnoh-render-merge-setstate.md
    ├── rnoh-list-key.md
    ├── rnoh-bundle-release.md
    ├── rnoh-lifecycle-foreground-background.md
    └── rnoh-turbo-worker.md
```
