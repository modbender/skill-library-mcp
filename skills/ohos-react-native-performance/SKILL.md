---
name: ohos-react-native-performance
description: OpenHarmony React Native performance static checks and optimization. Based on ohos_react_native performance doc. Use when writing or reviewing React Native for OpenHarmony code, bundle-harmony, lifecycle, or TurboModule. Applies to RNAbility, Hermes bytecode, React render optimization.
license: MIT
metadata:
  author: OpenHarmony-SIG / homecheck
  repository: https://gitcode.com/openharmony-sig/homecheck
  path_in_repo: skills/ohos-react-native-performance
  source_en: https://gitcode.com/openharmony-sig/ohos_react_native/blob/master/docs/en/performance-optimization.md
  source_zh: https://gitcode.com/openharmony-sig/ohos_react_native/blob/master/docs/zh-cn/性能调优.md
  version: '1.0.0'
---

# OpenHarmony React Native Performance Static Check Skills

Static-check rules and config for React Native for OpenHarmony, from the official [performance-optimization](https://gitcode.com/openharmony-sig/ohos_react_native/blob/master/docs/en/performance-optimization.md) doc. This skill is English-only to reduce token usage; Chinese content is available via links below.

## When to Apply

Use this skill when:

- Writing or reviewing **React Native for OpenHarmony** (RNOH) application code or OpenHarmony project configuration
- Optimizing React Native page rendering, setState, or list performance
- Configuring **bundle-harmony** build, Hermes bytecode, or Release build
- Integrating or reviewing **RNAbility** lifecycle (onForeground/onBackground)
- Designing or implementing **TurboModule** (main vs worker thread)
- Preparing for performance analysis with Trace, React Marker, FCP, etc.

## Rule Categories by Priority

| Priority | Category            | Impact   | Prefix                    |
| -------- | ------------------- | -------- | ------------------------- |
| 1        | Render optimization | CRITICAL | `rnoh-render-`              |
| 2        | Bundle & native     | HIGH     | `rnoh-bundle-`, `rnoh-native-` |
| 3        | Lifecycle & monitor | HIGH     | `rnoh-lifecycle-`           |
| 4        | TurboModule         | MEDIUM   | `rnoh-turbo-`               |
| 5        | List & key          | MEDIUM   | `rnoh-list-`                |

## Quick Reference

### 1. Render optimization (CRITICAL)

- `rnoh-render-avoid-same-state` — Avoid setState when state unchanged to prevent extra renders
- `rnoh-render-pure-memo` — Use PureComponent or React.memo to avoid unnecessary re-renders
- `rnoh-render-props-once` — Create callbacks/prop objects once (constructor or outside component)
- `rnoh-render-split-child` — Split independent UI into child components
- `rnoh-render-merge-setstate` — Merge setState to avoid multiple commits and renders
- `rnoh-render-state-not-mutate` — Use new objects in setState; do not mutate existing state
- `rnoh-render-batching` — Keep React 18 Automatic Batching enabled (RNOH default concurrentRoot: true)

### 2. Bundle & native config (HIGH)

- `rnoh-bundle-release` — Use `--dev=false --minify=true` for performance/production bundle
- `rnoh-bundle-hbc` — Prefer Hermes bytecode (hermesc) for production
- `rnoh-native-release` — Use Release build on native side; lower LOG_VERBOSITY_LEVEL when appropriate
- `rnoh-native-bisheng` — Optionally use BiSheng compiler (buildOption.nativeCompiler: "BiSheng")

### 3. Lifecycle & monitoring (HIGH)

- `rnoh-lifecycle-foreground-background` — Call onForeground/onBackground in onPageShow/onPageHide or onShown/onHidden
- `rnoh-lifecycle-fcp` — First-frame monitoring: use mount event or root onLayout to report FCP

### 4. TurboModule (MEDIUM)

- `rnoh-turbo-worker` — Run heavy TurboModules (JSON, crypto, image, network, I/O) on worker thread; avoid ImageLoader on worker

### 5. List & key (MEDIUM)

- `rnoh-list-key` — Provide stable keys for list items; avoid using index as key

## How to Use

- **Static checks:** Apply the rules above in code review or scripts (JS/TS and config).
- **Details and examples:** See the corresponding rule files under `rules/` (e.g. `rules/rnoh-render-pure-memo.md`).
- **Full doc:** [Performance optimization (en)](https://gitcode.com/openharmony-sig/ohos_react_native/blob/master/docs/en/performance-optimization.md).

## Relation to general React Native skills

- This skill focuses on **OpenHarmony**-specific React Native performance (RNAbility, bundle-harmony, HBC, TurboModule worker, Trace/React Marker).
- It complements **vercel-react-native-skills** and **react-native-best-practices**: list virtualization (FlashList), Pressable, expo-image, StyleSheet, etc. still apply; this skill adds OpenHarmony-side config and render-optimization details.
