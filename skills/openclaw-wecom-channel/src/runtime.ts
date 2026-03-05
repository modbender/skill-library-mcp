/**
 * 企业微信插件运行时引用
 * 保存 PluginRuntime 实例，供各模块使用
 */

import type { PluginRuntime } from "openclaw/plugin-sdk";

let runtime: PluginRuntime | null = null;

export function setWecomRuntime(next: PluginRuntime) {
  runtime = next;
}

export function getWecomRuntime(): PluginRuntime {
  if (!runtime) {
    throw new Error("WeCom runtime not initialized");
  }
  return runtime;
}
