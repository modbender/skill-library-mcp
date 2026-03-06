import { parseArgs } from 'node:util';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { loadConfig } from './config/index.js';
import { setLogLevel, createLogger } from './utils/logger.js';
import { ModelRegistry, loadRoutingTable } from './router/model-registry.js';
import { LogWriter } from './logging/writer.js';
import { LogReader } from './logging/reader.js';
import { loadWeights } from './classifier/engine.js';
import { registerTools } from './server/tools.js';
import { registerResources } from './server/resources.js';
import { registerPrompts } from './server/prompts.js';

const log = createLogger('main');

const { values: flags } = parseArgs({
  options: {
    http: { type: 'boolean', default: false },
    'http-only': { type: 'boolean', default: false },
  },
  strict: false,
});

async function main(): Promise<void> {
  log.info('Clawd Throttle starting...');

  // 1. Load configuration
  const config = loadConfig();
  setLogLevel(config.logging.level);
  log.info(`Configuration loaded. Mode: ${config.mode}`);

  // 2. Initialize model registry
  const registry = new ModelRegistry(config.modelCatalogPath);

  // 3. Validate at least one provider is configured
  const configured = registry.getConfiguredProviders(config);
  if (configured.length === 0) {
    log.error(
      'No provider API keys configured. Set at least one: ' +
      'ANTHROPIC_API_KEY, GOOGLE_AI_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, ' +
      'XAI_API_KEY, MOONSHOT_API_KEY, MISTRAL_API_KEY, or configure Ollama.',
    );
    process.exit(1);
  }
  log.info(`Configured providers: ${configured.join(', ')}`);

  // 4. Load routing table
  const routingTable = loadRoutingTable(config.routingTablePath);

  // 5. Initialize classifier weights
  const weights = loadWeights(config.classifier.weightsPath);

  // 6. Initialize logging
  const logWriter = new LogWriter(config.logging.logFilePath);
  const logReader = new LogReader(config.logging.logFilePath);
  log.info(`Routing log: ${config.logging.logFilePath}`);

  // 7. Start HTTP proxy if enabled
  const httpEnabled = config.http.enabled || flags.http || flags['http-only'];
  if (httpEnabled) {
    const { createHttpProxy } = await import('./server/http-proxy.js');
    const httpServer = createHttpProxy({ config, registry, weights, logWriter, logReader, routingTable });
    httpServer.listen(config.http.port, () => {
      log.info(`HTTP proxy listening on http://localhost:${config.http.port}`);
    });
  }

  // 8. Start MCP stdio server (unless --http-only)
  if (!flags['http-only']) {
    const server = new McpServer({
      name: 'clawd-throttle',
      version: '1.0.0',
    });

    registerTools(server, config, registry, weights, logWriter, logReader, routingTable);
    registerResources(server, config, logReader);
    registerPrompts(server);
    log.info('MCP tools, resources, and prompts registered');

    const transport = new StdioServerTransport();
    await server.connect(transport);
    log.info('Clawd Throttle is running on stdio transport');
  }
}

main().catch((err) => {
  const log = createLogger('main');
  log.error('Fatal error during startup', err);
  process.exit(1);
});
