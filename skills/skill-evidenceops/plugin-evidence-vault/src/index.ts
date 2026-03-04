export * from './types';
export * from './drivers/interface';
export * from './drivers/filesystem';
export * from './drivers/s3';
export * from './tools/index';

import { EvidenceVaultPlugin, EvidenceVaultTools, createTools, toolDefinitions, PluginContext } from './tools/index';
import { VaultConfig, DEFAULT_CONFIG } from './types';

export { EvidenceVaultPlugin, EvidenceVaultTools, createTools, toolDefinitions, PluginContext, VaultConfig, DEFAULT_CONFIG };

export async function initializeVault(config?: Partial<VaultConfig>): Promise<EvidenceVaultTools> {
  const plugin = new EvidenceVaultPlugin({ config });
  await plugin.initialize();
  return plugin;
}
