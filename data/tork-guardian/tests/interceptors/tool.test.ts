import { describe, it, expect } from 'vitest';
import { governToolCall } from '../../dist/interceptors/tool';
import { TorkConfigSchema } from '../../dist/config';

function makeConfig(overrides: Record<string, unknown> = {}) {
  return TorkConfigSchema.parse({ apiKey: 'test-key', ...overrides });
}

describe('governToolCall', () => {
  describe('shell command governance', () => {
    it('blocks rm -rf command', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'shell_execute', args: { command: 'rm -rf /' } },
        config,
      );
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('rm -rf');
    });

    it('blocks mkfs command', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'bash', args: { command: 'mkfs.ext4 /dev/sda' } },
        config,
      );
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('mkfs');
    });

    it('blocks chmod 777', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'terminal', args: { command: 'chmod 777 /etc/passwd' } },
        config,
      );
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('chmod 777');
    });

    it('blocks shutdown command', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'shell_execute', args: { command: 'shutdown -h now' } },
        config,
      );
      expect(result.allowed).toBe(false);
    });

    it('strict policy blocks all shell commands', () => {
      const config = makeConfig({ policy: 'strict' });
      const result = governToolCall(
        { name: 'shell_execute', args: { command: 'ls -la' } },
        config,
      );
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Strict policy');
    });

    it('allows safe shell commands under standard policy', () => {
      const config = makeConfig({ policy: 'standard' });
      const result = governToolCall(
        { name: 'shell_execute', args: { command: 'ls -la /tmp' } },
        config,
      );
      expect(result.allowed).toBe(true);
    });
  });

  describe('file access governance', () => {
    it('blocks access to .env files', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'file_write', args: { path: '.env' } },
        config,
      );
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('.env');
    });

    it('blocks access to SSH keys', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'file_delete', args: { path: '~/.ssh/id_rsa' } },
        config,
      );
      expect(result.allowed).toBe(false);
    });

    it('blocks access to /etc/passwd', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'file_read', args: { path: '/etc/passwd' } },
        config,
      );
      expect(result.allowed).toBe(false);
    });

    it('allows access to normal paths', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'file_read', args: { path: '/tmp/output.txt' } },
        config,
      );
      expect(result.allowed).toBe(true);
    });

    it('enforces allowedPaths whitelist', () => {
      const config = makeConfig({ allowedPaths: ['/app/data/'] });
      const result = governToolCall(
        { name: 'file_write', args: { path: '/tmp/hack.txt' } },
        config,
      );
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('not in the allowed paths');
    });
  });

  describe('network tool governance', () => {
    it('strict policy blocks network_request', () => {
      const config = makeConfig({ policy: 'strict' });
      const result = governToolCall(
        { name: 'network_request', args: { url: 'https://api.openai.com' } },
        config,
      );
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Strict policy');
    });

    it('standard policy allows network_request', () => {
      const config = makeConfig({ policy: 'standard' });
      const result = governToolCall(
        { name: 'http_request', args: { url: 'https://api.openai.com' } },
        config,
      );
      expect(result.allowed).toBe(true);
    });
  });

  describe('minimal policy', () => {
    it('allows everything under minimal policy', () => {
      const config = makeConfig({ policy: 'minimal' });

      expect(governToolCall({ name: 'shell_execute', args: { command: 'rm -rf /' } }, config).allowed).toBe(true);
      expect(governToolCall({ name: 'file_delete', args: { path: '.env' } }, config).allowed).toBe(true);
      expect(governToolCall({ name: 'network_request', args: {} }, config).allowed).toBe(true);
    });
  });

  describe('unknown tools', () => {
    it('allows unknown tool names by default', () => {
      const config = makeConfig();
      const result = governToolCall(
        { name: 'custom_tool', args: { foo: 'bar' } },
        config,
      );
      expect(result.allowed).toBe(true);
    });
  });
});
