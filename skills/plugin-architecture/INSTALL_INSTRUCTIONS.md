# Plugin Architecture - Installation Instructions

Follow these steps in order. After each step, verify the change was applied correctly.

## Prerequisites

- OpenClaw source at `~/clawdbot` (or `$CLAWDBOT_DIR`)
- pnpm installed
- Ability to restart the gateway

## Step 1: Add UI Registration Types

**File:** `src/plugins/types.ts`

Add these interfaces at the end of the file:

```typescript
// UI Plugin Registration Types
export interface PluginViewRegistration {
  id: string;
  label: string;
  subtitle?: string;
  icon: string;
  group: string;
  position?: number;
  pluginId?: string;
}

export interface PluginNavGroupRegistration {
  id: string;
  label: string;
  icon?: string;
  position: number;
  pluginId?: string;
}

export interface PluginSettingsPanelRegistration {
  id: string;
  label: string;
  icon?: string;
  position?: number;
  pluginId?: string;
}
```

Also find the `ClawdbotPluginApi` interface and add these methods before `registerCommand`:

```typescript
  registerView: (view: PluginViewRegistration) => void;
  registerNavGroup: (group: PluginNavGroupRegistration) => void;
  registerSettingsPanel: (panel: PluginSettingsPanelRegistration) => void;
```

## Step 2: Update Plugin Registry

**File:** `src/plugins/registry.ts`

1. Add imports at the top (with other type imports from "./types.js"):
```typescript
  PluginViewRegistration,
  PluginNavGroupRegistration,
  PluginSettingsPanelRegistration,
```

2. Add to the `PluginRegistry` type (after `diagnostics`):
```typescript
  uiViews: PluginViewRegistration[];
  uiNavGroups: PluginNavGroupRegistration[];
  uiSettingsPanels: PluginSettingsPanelRegistration[];
```

3. Initialize the arrays in `createPluginRegistry` (after `diagnostics: []`):
```typescript
    uiViews: [],
    uiNavGroups: [],
    uiSettingsPanels: [],
```

4. Add registration functions inside `createPluginRegistry` (before `pushDiagnostic`):
```typescript
  const registerView = (record: PluginRecord, view: PluginViewRegistration) => {
    registry.uiViews.push({ ...view, pluginId: record.id, position: view.position ?? 99 });
  };
  const registerNavGroup = (record: PluginRecord, group: PluginNavGroupRegistration) => {
    if (!registry.uiNavGroups.find(g => g.id === group.id)) {
      registry.uiNavGroups.push({ ...group, pluginId: record.id });
    }
  };
  const registerSettingsPanel = (record: PluginRecord, panel: PluginSettingsPanelRegistration) => {
    registry.uiSettingsPanels.push({ ...panel, pluginId: record.id, position: panel.position ?? 99 });
  };
```

5. Add to the API object returned by `createApi` (before `registerCommand`):
```typescript
      registerView: (view) => registerView(record, view),
      registerNavGroup: (group) => registerNavGroup(record, group),
      registerSettingsPanel: (panel) => registerSettingsPanel(record, panel),
```

## Step 3: Update Runtime Empty Registry

**File:** `src/plugins/runtime.ts`

In `createEmptyRegistry`, add after `diagnostics: []`:
```typescript
  uiViews: [],
  uiNavGroups: [],
  uiSettingsPanels: [],
```

## Step 4: Update Test Utils (if they exist)

Check these files and add the same three arrays to any empty registry objects:
- `src/test-utils/channel-plugins.ts`
- `src/gateway/server/__tests__/test-utils.ts`  
- `src/gateway/test-helpers.mocks.ts`

## Step 5: Create Gateway Method

**Create file:** `src/gateway/server-methods/plugins-ui.ts`

```typescript
import type { GatewayRequestHandlers } from "./types.js";
import { getActivePluginRegistry } from "../../plugins/runtime.js";
import type {
  PluginViewRegistration,
  PluginNavGroupRegistration,
  PluginSettingsPanelRegistration,
} from "../../plugins/types.js";

export const pluginsUiMethods: GatewayRequestHandlers = {
  "plugins.ui.registry": async ({ respond }) => {
    try {
      const registry = getActivePluginRegistry();
      respond(true, {
        views: registry?.uiViews ?? [],
        navGroups: registry?.uiNavGroups ?? [],
        settingsPanels: registry?.uiSettingsPanels ?? [],
      }, undefined);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      respond(true, { views: [], navGroups: [], settingsPanels: [], error: message }, undefined);
    }
  },
};
```

## Step 6: Register Gateway Method

**File:** `src/gateway/server-methods.ts`

1. Add import:
```typescript
import { pluginsUiMethods } from "./server-methods/plugins-ui.js";
```

2. Add to `coreGatewayHandlers` object:
```typescript
  ...pluginsUiMethods,
```

## Step 7: Create UI Plugin Registry

**Create file:** `ui/src/ui/plugins/registry.ts`

See reference file: `reference/ui-plugin-registry.ts`

## Step 8: Update Navigation

**File:** `ui/src/ui/navigation.ts`

1. Add import at top:
```typescript
import { uiPluginRegistry, isPluginTab, getPluginViewInfo } from "./plugins/registry.js";
```

2. Add these functions at end of file:
```typescript
export function getDynamicTabGroups(): Array<{ label: string; tabs: string[] }> {
  const coreGroups = TAB_GROUPS.map(g => ({ label: g.label, tabs: [...g.tabs] as string[] }));
  for (const view of uiPluginRegistry.getAllViews()) {
    let group = coreGroups.find(g => g.label.toLowerCase() === view.group.toLowerCase());
    if (!group) {
      const pg = uiPluginRegistry.getNavGroup(view.group);
      if (pg) { group = { label: pg.label, tabs: [] }; coreGroups.push(group); }
    }
    if (group && !group.tabs.includes(view.id)) group.tabs.push(view.id);
  }
  return coreGroups;
}

export function getDynamicIconForTab(tab: string): IconName {
  if (tab in TAB_PATHS) return iconForTab(tab as Tab);
  return (getPluginViewInfo(tab)?.icon as IconName) || "folder";
}

export function getDynamicTitleForTab(tab: string): string {
  if (tab in TAB_PATHS) return titleForTab(tab as Tab);
  return getPluginViewInfo(tab)?.label || tab;
}

export function getDynamicSubtitleForTab(tab: string): string {
  if (tab in TAB_PATHS) return subtitleForTab(tab as Tab);
  return getPluginViewInfo(tab)?.subtitle || "";
}

export { isPluginTab, getPluginViewInfo };
```

## Step 9: Update App Render

**File:** `ui/src/ui/app-render.ts`

1. Update navigation imports to include:
```typescript
  getDynamicTabGroups,
  getDynamicTitleForTab,
  getDynamicSubtitleForTab,
  isPluginTab,
```

2. Replace `TAB_GROUPS.map` with `getDynamicTabGroups().map`

3. Replace `titleForTab(state.tab)` with `getDynamicTitleForTab(state.tab)` in the page header

4. Replace `subtitleForTab(state.tab)` with `getDynamicSubtitleForTab(state.tab)` in the page header

5. Add plugin view rendering before the debug view section:
```typescript
${isPluginTab(state.tab)
  ? html`<div class="plugin-view" data-plugin-tab="${state.tab}">
      <p>Plugin view: ${state.tab}</p>
    </div>`
  : nothing}
```

## Step 10: Update App Render Helpers

**File:** `ui/src/ui/app-render.helpers.ts`

1. Update imports to include `getDynamicIconForTab`, `getDynamicTitleForTab`, `isPluginTab`

2. Update `renderTab` function signature to accept `Tab | string`

3. Handle plugin tabs in `renderTab` by checking `isPluginTab(tab)` and using dynamic functions

## Step 11: Load Plugin Registry on Connect

**File:** `ui/src/ui/app-gateway.ts`

1. Add import:
```typescript
import { uiPluginRegistry } from "./plugins/registry.js";
```

2. In the `onHello` handler, add:
```typescript
void loadPluginUIRegistry(host.client);
```

3. Add the loading function:
```typescript
async function loadPluginUIRegistry(client: GatewayBrowserClient): Promise<void> {
  try {
    const result = await client.call("plugins.ui.registry") as {
      views?: Array<{ id: string; label: string; icon: string; group: string; position?: number; pluginId?: string; subtitle?: string }>;
      navGroups?: Array<{ id: string; label: string; position: number; icon?: string; pluginId?: string }>;
      settingsPanels?: Array<{ id: string; label: string; position?: number; icon?: string; pluginId?: string }>;
    };
    uiPluginRegistry.loadFromGateway({
      views: result.views ?? [],
      navGroups: result.navGroups ?? [],
      settingsPanels: result.settingsPanels ?? [],
    });
    console.log(`[plugin-ui] Loaded ${result.views?.length ?? 0} plugin views`);
  } catch (err) {
    console.warn("[plugin-ui] Failed to load plugin UI registry:", err);
  }
}
```

## Step 12: Build and Test

1. Run `pnpm build` - fix any TypeScript errors
2. Run `pnpm ui:build`
3. Restart gateway: `clawdbot gateway restart`
4. Refresh browser and check for plugin tabs

## Verification

After installation, run:
```bash
clawdbot plugins list 2>&1 | grep -i "view"
```

You should see plugins logging "Registered ... UI view" if they use `registerView()`.
