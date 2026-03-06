/**
 * UI Plugin Registry
 * 
 * Client-side registry for plugin UI registrations.
 * Loaded from gateway on connect.
 * 
 * Place this file at: ui/src/ui/plugins/registry.ts
 */

export interface PluginViewInfo {
  id: string;
  label: string;
  subtitle?: string;
  icon: string;
  group: string;
  position: number;
  pluginId?: string;
}

export interface PluginNavGroupInfo {
  id: string;
  label: string;
  icon?: string;
  position: number;
  pluginId?: string;
}

export interface PluginSettingsPanelInfo {
  id: string;
  label: string;
  icon?: string;
  position: number;
  pluginId?: string;
}

class UIPluginRegistry {
  private views: Map<string, PluginViewInfo> = new Map();
  private navGroups: Map<string, PluginNavGroupInfo> = new Map();
  private settingsPanels: Map<string, PluginSettingsPanelInfo> = new Map();
  private viewRenderers: Map<string, () => unknown> = new Map();

  registerView(view: PluginViewInfo): void {
    this.views.set(view.id, view);
  }

  registerNavGroup(group: PluginNavGroupInfo): void {
    this.navGroups.set(group.id, group);
  }

  registerSettingsPanel(panel: PluginSettingsPanelInfo): void {
    this.settingsPanels.set(panel.id, panel);
  }

  registerViewRenderer(viewId: string, renderer: () => unknown): void {
    this.viewRenderers.set(viewId, renderer);
  }

  getView(id: string): PluginViewInfo | undefined {
    return this.views.get(id);
  }

  getAllViews(): PluginViewInfo[] {
    return Array.from(this.views.values());
  }

  getNavGroup(id: string): PluginNavGroupInfo | undefined {
    return this.navGroups.get(id);
  }

  getAllNavGroups(): PluginNavGroupInfo[] {
    return Array.from(this.navGroups.values());
  }

  getSettingsPanel(id: string): PluginSettingsPanelInfo | undefined {
    return this.settingsPanels.get(id);
  }

  getAllSettingsPanels(): PluginSettingsPanelInfo[] {
    return Array.from(this.settingsPanels.values());
  }

  getViewRenderer(viewId: string): (() => unknown) | undefined {
    return this.viewRenderers.get(viewId);
  }

  hasView(id: string): boolean {
    return this.views.has(id);
  }

  getTabsForGroup(groupId: string): string[] {
    return this.getAllViews()
      .filter(v => v.group === groupId)
      .sort((a, b) => a.position - b.position)
      .map(v => v.id);
  }

  getPluginTabIds(): string[] {
    return Array.from(this.views.keys());
  }

  clear(): void {
    this.views.clear();
    this.navGroups.clear();
    this.settingsPanels.clear();
    this.viewRenderers.clear();
  }

  loadFromGateway(data: {
    views: PluginViewInfo[];
    navGroups: PluginNavGroupInfo[];
    settingsPanels: PluginSettingsPanelInfo[];
  }): void {
    this.clear();
    for (const view of data.views) {
      this.registerView(view);
    }
    for (const group of data.navGroups) {
      this.registerNavGroup(group);
    }
    for (const panel of data.settingsPanels) {
      this.registerSettingsPanel(panel);
    }
  }
}

export const uiPluginRegistry = new UIPluginRegistry();

export function isPluginTab(tab: string): boolean {
  return uiPluginRegistry.hasView(tab);
}

export function getPluginViewInfo(tab: string): PluginViewInfo | null {
  return uiPluginRegistry.getView(tab) ?? null;
}
