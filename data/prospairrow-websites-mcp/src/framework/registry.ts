import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { z } from "zod";
import { resolveEnabledCapabilities } from "./policy.js";
import { Capability, type RegistrySummary, type SiteConfigFile, type SiteDefinition, type TaskDefinition } from "./types.js";

const registrySchema = z.object({
  policy: z.object({
    enabledCapabilities: z.array(z.nativeEnum(Capability)).default([Capability.READ_ONLY])
  }),
  sites: z.array(
    z.object({
      siteId: z.string(),
      moduleDir: z.string(),
      tasks: z.array(z.string())
    })
  )
});

const siteConfigSchema = z.object({
  baseUrl: z.string().url(),
  allowedHosts: z.array(z.string()).min(1),
  capabilities: z.array(z.nativeEnum(Capability)).default([Capability.READ_ONLY])
});

async function loadTask(modulePath: string): Promise<TaskDefinition> {
  const mod = await import(pathToFileURL(modulePath).href);
  if (!mod.task) {
    throw new Error(`Task module missing exported 'task': ${modulePath}`);
  }
  return mod.task as TaskDefinition;
}

export async function loadRegistry(rootDir: string): Promise<RegistrySummary> {
  const raw = await fs.readFile(path.join(rootDir, "site-registry.json"), "utf-8");
  const parsed = registrySchema.parse(JSON.parse(raw));
  const enabledCapabilities = resolveEnabledCapabilities(parsed.policy.enabledCapabilities);

  const sites: SiteDefinition[] = [];

  for (const entry of parsed.sites) {
    const moduleDir = path.join(rootDir, entry.moduleDir);
    const siteConfigRaw = await fs.readFile(path.join(moduleDir, "site.json"), "utf-8");
    const siteConfig = siteConfigSchema.parse(JSON.parse(siteConfigRaw)) as SiteConfigFile;

    const tasks: TaskDefinition[] = [];
    for (const taskId of entry.tasks) {
      const taskModulePath = path.join(moduleDir, "tasks", `${taskId}.ts`);
      const taskDef = await loadTask(taskModulePath);

      // list_sites should only show currently runnable tasks.
      if (enabledCapabilities.includes(taskDef.capability)) {
        tasks.push(taskDef);
      }
    }

    sites.push({
      siteId: entry.siteId,
      baseUrl: siteConfig.baseUrl,
      allowedHosts: siteConfig.allowedHosts,
      capabilities: siteConfig.capabilities,
      tasks
    });
  }

  return {
    policy: {
      enabledCapabilities
    },
    sites
  };
}

export async function loadSiteAndTask(rootDir: string, siteId: string, taskId: string): Promise<{
  registry: RegistrySummary;
  site: SiteDefinition;
  task: TaskDefinition;
}> {
  const raw = await fs.readFile(path.join(rootDir, "site-registry.json"), "utf-8");
  const parsed = registrySchema.parse(JSON.parse(raw));
  const enabledCapabilities = resolveEnabledCapabilities(parsed.policy.enabledCapabilities);

  const entry = parsed.sites.find((s) => s.siteId === siteId);
  if (!entry) {
    throw new Error(`Unknown siteId: ${siteId}`);
  }

  const moduleDir = path.join(rootDir, entry.moduleDir);
  const siteConfigRaw = await fs.readFile(path.join(moduleDir, "site.json"), "utf-8");
  const siteConfig = siteConfigSchema.parse(JSON.parse(siteConfigRaw)) as SiteConfigFile;

  if (!entry.tasks.includes(taskId)) {
    throw new Error(`Unknown taskId '${taskId}' for site '${siteId}'`);
  }

  const taskModulePath = path.join(moduleDir, "tasks", `${taskId}.ts`);
  const task = await loadTask(taskModulePath);

  const site: SiteDefinition = {
    siteId,
    baseUrl: siteConfig.baseUrl,
    allowedHosts: siteConfig.allowedHosts,
    capabilities: siteConfig.capabilities,
    tasks: [task]
  };

  const registry: RegistrySummary = {
    policy: {
      enabledCapabilities
    },
    sites: [site]
  };

  return { registry, site, task };
}
