# react-native-update integration playbook

## 1) Fast path
1. Install CLI and SDK in app root:
   - `npm i -g react-native-update-cli`
   - `npm i react-native-update`
2. iOS pod install:
   - `cd ios && pod install`
3. Generate/select app config (`update.json`) with pushy CLI.
4. Wire appKey from `update.json` by platform.
5. Initialize `Pushy` and wrap app with `UpdateProvider`.
6. Build release package and validate update flow.

## 2) App type specifics

### React Native CLI
- Standard install + iOS pods.
- For very old RN or non-standard project structure, manual link may still be needed.

### Expo
- Require modern Expo workflow; run prebuild when needed:
  - `npx expo prebuild`
- Do not co-install `expo-updates` (conflict risk for update behavior).

## 3) Minimum JS wiring
- Read appKey from `update.json` with `Platform.OS`.
- Create `new Pushy({ appKey, ...options })`.
- Wrap app root with `<UpdateProvider client={pushyClient}>`.

## 4) Strategy defaults to discuss
- `checkStrategy`: `both` / `onAppStart` / `onAppResume` / `null`
- `updateStrategy`: `alwaysAlert` / `alertUpdateAndIgnoreError` / `silentAndNow` / `silentAndLater` / `null`
- For custom UI: set `updateStrategy: null`, then use `useUpdate()`.

## 5) Native touchpoints (high level)

### iOS
- Ensure release bundle URL resolves via Pushy bundle method in app delegate flow.
- Keep DEBUG bundle behavior unchanged.

### Android
- Ensure integration point in `MainApplication` (or custom React instance manager path).

## 6) Verification checklist
- [ ] Release build succeeds on target platform.
- [ ] App can call check update and returns structured update state.
- [ ] Update package download succeeds.
- [ ] App can switch to new version (now/later behavior as expected).
- [ ] Rollback behavior understood/tested for crash scenarios.

## 7) Common pitfalls
- Missing/incorrect `update.json` appKey by platform.
- Expecting real apply-update behavior in DEBUG builds.
- Expo project still carrying `expo-updates`.
- iOS pods not installed after dependency update.
- Native file edits not followed by full rebuild.

## 8) Example: class component integration
Use this when the app root is still class-based.

```tsx
import React from 'react';
import { Platform } from 'react-native';
import { Pushy, UpdateProvider } from 'react-native-update';
import App from './App';
import _updateConfig from './update.json';

const { appKey } = _updateConfig[Platform.OS];

const pushyClient = new Pushy({
  appKey,
  checkStrategy: 'onAppStart',
  updateStrategy: 'alertUpdateAndIgnoreError',
});

export default class Root extends React.Component {
  render() {
    return (
      <UpdateProvider client={pushyClient}>
        <App />
      </UpdateProvider>
    );
  }
}
```

## 9) Example: custom whitelist (gray release)
Use `metaInfo` and your own user/device attributes to decide whether to apply update.

```tsx
import { useEffect } from 'react';
import { useUpdate } from 'react-native-update';

// example only: implement with your real uid / device tags
function useWhitelistGate(currentUserId: string) {
  const { checkUpdate, updateInfo, downloadUpdate, switchVersionLater } = useUpdate();

  useEffect(() => {
    (async () => {
      await checkUpdate();
      if (!updateInfo?.update) return;

      const allowList: string[] = updateInfo.metaInfo?.allowUsers ?? [];
      if (!allowList.includes(currentUserId)) return; // not in whitelist

      const ok = await downloadUpdate();
      if (ok) switchVersionLater();
    })();
  }, [currentUserId, checkUpdate, updateInfo, downloadUpdate, switchVersionLater]);
}
```

Notes:
- Keep server-side rollout rules as source of truth; client whitelist is an extra guard.
- Store small, explicit whitelist keys in `metaInfo` (e.g. `allowUsers`, `allowChannels`).
- Prefer phased rollout: internal users -> small percent -> full rollout.
