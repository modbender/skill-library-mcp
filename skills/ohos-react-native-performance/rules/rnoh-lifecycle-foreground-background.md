---
title: Call onForeground / onBackground in page lifecycle
impact: HIGH
source: ohos_react_native performance optimization - Page lifecycle
---

# rnoh-lifecycle-foreground-background

RNAbility provides `onForeground()` and `onBackground()` so the React Native layer knows when the page is in foreground or background. Both **router** and **Navigation** must call these in the right lifecycle; otherwise React Native may not handle visibility correctly (timers, animations, resource cleanup).

## Router

In the `@Entry` page, wire RNAbility and call in lifecycle:

```typescript
import { RNAbility } from '@rnoh/react-native-openharmony';

@Entry
@Component
export struct ComponentName {
  @StorageLink('RNAbility') rnAbility: RNAbility | undefined = undefined;

  onPageShow() {
    this.rnAbility?.onForeground();
  }
  onPageHide() {
    this.rnAbility?.onBackground();
  }
}
```

## Navigation

Call in the NavDestination `onShown` / `onHidden`:

```typescript
NavDestination() { ... }
  .onShown(() => { this.rnAbility?.onForeground(); })
  .onHidden(() => { this.rnAbility?.onBackground(); })
```

## Static check

- Review every ArkTS page that hosts React Native: with router, ensure onPageShow/onPageHide call the above; with Navigation, ensure onShown/onHidden do.
- When adding a new React Native container page, add "wire onForeground/onBackground" to the checklist.
