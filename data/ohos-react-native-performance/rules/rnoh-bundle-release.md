---
title: Use release bundle and HBC for performance
impact: HIGH
source: ohos_react_native performance optimization - JS release config, HBC
---

# rnoh-bundle-release

For performance tuning or production, use production bundle options and prefer Hermes bytecode (HBC) to reduce startup time and memory.

## Development / debug (not for perf tuning)

```cmd
npm run codegen && react-native bundle-harmony --dev --minify=false
```

## Performance / production (recommended)

```cmd
npm run codegen && react-native bundle-harmony --dev=false --minify=true
```

- `--dev=false`: production mode, optimizations on.
- `--minify=true`: minify output, smaller bundle.

## Hermes bytecode (HBC)

Compiling the JS bundle to Hermes bytecode further improves startup, memory, and avoids runtime compile:

```cmd
npm run codegen && react-native bundle-harmony --dev=false --minify=true --bundle-output /tmp/bundle.harmony.js && hermesc --emit-binary /tmp/bundle.harmony.js -out ./harmony/entry/src/main/resources/rawfile/hermes_bundle.hbc
```

## Static check

- In CI or scripts, ensure perf/release pipeline uses `--dev=false --minify=true`.
- If using HBC, confirm the app loads the `.hbc` file, not the `.js` bundle.
