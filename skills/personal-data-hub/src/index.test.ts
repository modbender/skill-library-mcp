import { describe, it, expect, vi, afterEach } from 'vitest';

// Mock readCredentials so tests don't depend on real ~/.pdh/credentials.json
vi.mock('./setup.js', async (importOriginal) => {
  const actual = await importOriginal() as Record<string, unknown>;
  return {
    ...actual,
    readCredentials: vi.fn(() => null),
  };
});

import plugin from './index.js';

describe('PersonalDataHub Plugin', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('has correct plugin metadata', () => {
    expect(plugin.id).toBe('personal-data-hub');
    expect(plugin.name).toBe('Personal Data Hub');
    expect(plugin.description).toContain('PersonalDataHub');
  });

  it('config schema validates correct config', () => {
    const result = plugin.configSchema.safeParse({
      hubUrl: 'http://localhost:7007',
      apiKey: 'pk_test_123',
    });
    expect(result.success).toBe(true);
  });

  it('config schema rejects missing hubUrl', () => {
    const result = plugin.configSchema.safeParse({
      apiKey: 'pk_test_123',
    });
    expect(result.success).toBe(false);
  });

  it('config schema rejects missing apiKey', () => {
    const result = plugin.configSchema.safeParse({
      hubUrl: 'http://localhost:7007',
    });
    expect(result.success).toBe(false);
  });

  it('config schema rejects non-object', () => {
    const result = plugin.configSchema.safeParse('not an object');
    expect(result.success).toBe(false);
  });

  it('registers tools when config is valid', async () => {
    const registerTool = vi.fn();
    const on = vi.fn();
    const api = {
      pluginConfig: {
        hubUrl: 'http://localhost:7007',
        apiKey: 'pk_test_123',
      },
      logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
      registerTool,
      on,
    };

    await plugin.register(api);

    expect(registerTool).toHaveBeenCalledTimes(2);

    // Verify pull tool
    const pullTool = registerTool.mock.calls[0][0];
    expect(pullTool.name).toBe('personal_data_pull');

    // Verify propose tool
    const proposeTool = registerTool.mock.calls[1][0];
    expect(proposeTool.name).toBe('personal_data_propose');

    // Verify hook registration
    expect(on).toHaveBeenCalledWith('before_agent_start', expect.any(Function));
  });

  it('before_agent_start hook returns system prompt', async () => {
    const on = vi.fn();
    const api = {
      pluginConfig: {
        hubUrl: 'http://localhost:7007',
        apiKey: 'pk_test_123',
      },
      logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
      registerTool: vi.fn(),
      on,
    };

    await plugin.register(api);

    // Get the registered hook handler
    const hookCall = on.mock.calls.find((c: unknown[]) => c[0] === 'before_agent_start');
    expect(hookCall).toBeDefined();

    const handler = hookCall![1] as (event: unknown) => Promise<{ systemPromptAppend: string }>;
    const result = await handler({});
    expect(result.systemPromptAppend).toContain('PersonalDataHub');
    expect(result.systemPromptAppend).toContain('personal_data_pull');
    expect(result.systemPromptAppend).toContain('personal_data_propose');
  });

  describe('auto-setup', () => {
    it('auto-discovers hub and creates API key when config is empty', async () => {
      const registerTool = vi.fn();
      const on = vi.fn();
      const mockFetch = vi.fn();
      vi.stubGlobal('fetch', mockFetch);

      // discoverHub probes localhost:3000 — succeeds
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true, version: '0.1.0' }),
        })
        // checkHub called again during auto-setup
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true, version: '0.1.0' }),
        })
        // createApiKey
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true, id: 'openclaw-agent', key: 'pk_auto123' }),
        });

      const api = {
        pluginConfig: undefined,
        logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
        registerTool,
        on,
      };

      await plugin.register(api);

      expect(registerTool).toHaveBeenCalledTimes(2);
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining('Auto-created API key'),
      );
    });

    it('falls back to warning when no hub is running', async () => {
      const registerTool = vi.fn();
      const on = vi.fn();
      const mockFetch = vi.fn();
      vi.stubGlobal('fetch', mockFetch);

      // All discovery attempts fail
      mockFetch.mockRejectedValue(new Error('ECONNREFUSED'));

      const api = {
        pluginConfig: undefined,
        logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
        registerTool,
        on,
      };

      await plugin.register(api);

      expect(registerTool).not.toHaveBeenCalled();
      expect(api.logger.warn).toHaveBeenCalledWith(
        expect.stringContaining('npx pdh init'),
      );
    });

    it('creates API key when hubUrl provided but apiKey missing', async () => {
      const registerTool = vi.fn();
      const on = vi.fn();
      const mockFetch = vi.fn();
      vi.stubGlobal('fetch', mockFetch);

      // checkHub
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true }),
        })
        // createApiKey
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true, id: 'openclaw', key: 'pk_new456' }),
        });

      const api = {
        pluginConfig: { hubUrl: 'http://localhost:3000' },
        logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
        registerTool,
        on,
      };

      await plugin.register(api);

      expect(registerTool).toHaveBeenCalledTimes(2);
    });

    it('uses credentials file when pluginConfig and env vars are missing', async () => {
      const { readCredentials } = await import('./setup.js');
      const mockedReadCredentials = vi.mocked(readCredentials);
      mockedReadCredentials.mockReturnValueOnce({
        hubUrl: 'http://localhost:5555',
        apiKey: 'pk_creds_file_key',
      });

      const registerTool = vi.fn();
      const on = vi.fn();
      const api = {
        pluginConfig: undefined,
        logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
        registerTool,
        on,
      };

      await plugin.register(api);

      expect(registerTool).toHaveBeenCalledTimes(2);
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining('Configured from credentials file'),
      );
    });

    it('uses environment variables when pluginConfig is missing (ClawHub pattern)', async () => {
      process.env.PDH_HUB_URL = 'http://localhost:9999';
      process.env.PDH_API_KEY = 'pk_env_test_key';

      const registerTool = vi.fn();
      const on = vi.fn();
      const api = {
        pluginConfig: undefined,
        logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
        registerTool,
        on,
      };

      await plugin.register(api);

      expect(registerTool).toHaveBeenCalledTimes(2);
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining('Configured from environment variables'),
      );

      delete process.env.PDH_HUB_URL;
      delete process.env.PDH_API_KEY;
    });

    it('warns with missing config when no config is passed (legacy behavior)', async () => {
      // Stub fetch so discoverHub fails
      const mockFetch = vi.fn();
      vi.stubGlobal('fetch', mockFetch);
      mockFetch.mockRejectedValue(new Error('ECONNREFUSED'));

      const registerTool = vi.fn();
      const on = vi.fn();
      const api = {
        pluginConfig: undefined,
        logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
        registerTool,
        on,
      };

      await plugin.register(api);

      expect(registerTool).not.toHaveBeenCalled();
      expect(api.logger.warn).toHaveBeenCalledWith(
        expect.stringContaining('Missing hubUrl or apiKey'),
      );
    });
  });
});
