/**
 * OTE (Operational Test Environment) integration tests for openclaw-inwx.
 *
 * These tests run against the INWX OTE sandbox at ote.inwx.com.
 * OTE is safe - no real billing, no production impact.
 *
 * Required environment variables:
 *   INWX_OTE_USERNAME  - OTE account username
 *   INWX_OTE_PASSWORD  - OTE account password
 *   INWX_OTE_OTP       - (optional) OTE 2FA shared secret
 *
 * Run with:  npm run test:ote
 * Skip with: leave env vars unset (the suite is a no-op)
 */

import { InwxClient, InwxApiError } from "../src/client";
import { createTools } from "../src/tools";
import { buildToolset, BoundTool } from "../src/index";
import { PluginConfig, ToolContext, JsonMap } from "../src/types";

/* ------------------------------------------------------------------ */
/*  Credentials & skip logic                                          */
/* ------------------------------------------------------------------ */

const OTE_USER = process.env.INWX_OTE_USERNAME ?? "";
const OTE_PASS = process.env.INWX_OTE_PASSWORD ?? "";
const OTE_OTP = process.env.INWX_OTE_OTP ?? undefined;

const HAS_CREDS = OTE_USER.length > 0 && OTE_PASS.length > 0;

const describeOTE = HAS_CREDS ? describe : describe.skip;

function oteConfig(overrides: Partial<PluginConfig> = {}): PluginConfig {
  return {
    username: OTE_USER,
    password: OTE_PASS,
    otpSecret: OTE_OTP,
    environment: "ote",
    readOnly: false,
    allowedOperations: [],
    ...overrides,
  };
}

function oteContext(overrides: Partial<PluginConfig> = {}): ToolContext {
  return { config: oteConfig(overrides) };
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

function findTool(tools: BoundTool[], name: string): BoundTool {
  const tool = tools.find((t) => t.name === name);
  if (!tool) throw new Error(`Tool ${name} not found in toolset`);
  return tool;
}

const TEST_TIMEOUT = 30_000; // 30s per test - real HTTP calls

/* ------------------------------------------------------------------ */
/*  1. Client-level tests                                             */
/* ------------------------------------------------------------------ */

describeOTE("OTE integration - InwxClient", () => {
  it(
    "authenticates and retrieves account info",
    async () => {
      const client = new InwxClient(oteConfig());
      try {
        const info = await client.call<JsonMap>("account.info", {});
        // OTE accounts always return some account data
        expect(info).toBeDefined();
        expect(typeof info).toBe("object");
      } finally {
        await client.logout();
      }
    },
    TEST_TIMEOUT,
  );

  it(
    "supports sequential calls on the same session",
    async () => {
      const client = new InwxClient(oteConfig());
      try {
        // First call triggers login
        const info = await client.call<JsonMap>("account.info", {});
        expect(info).toBeDefined();

        // Second call reuses session
        const check = await client.call<JsonMap>("domain.check", {
          domain: "ote-integration-test-1234567890.de",
        });
        expect(check).toBeDefined();
      } finally {
        await client.logout();
      }
    },
    TEST_TIMEOUT,
  );

  it(
    "logout is idempotent",
    async () => {
      const client = new InwxClient(oteConfig());
      await client.call<JsonMap>("account.info", {});
      await client.logout();
      // Second logout should not throw
      await client.logout();
    },
    TEST_TIMEOUT,
  );
});

/* ------------------------------------------------------------------ */
/*  2. Read tool tests                                                */
/* ------------------------------------------------------------------ */

describeOTE("OTE integration - read tools", () => {
  let tools: BoundTool[];

  beforeAll(() => {
    tools = buildToolset(oteConfig());
  });

  it(
    "inwx_account_info returns account data",
    async () => {
      const result = (await findTool(tools, "inwx_account_info").run({})) as JsonMap;
      expect(result).toBeDefined();
      expect(typeof result).toBe("object");
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_domain_check returns availability",
    async () => {
      const result = (await findTool(tools, "inwx_domain_check").run({
        domain: "ote-integration-unique-test-domain-9876.de",
      })) as Array<{ domain: string; avail: boolean }>;
      expect(result).toBeDefined();
      // Response is an array of check results or a single result mapped
      const items = Array.isArray(result) ? result : [result];
      expect(items.length).toBeGreaterThan(0);
      expect(items[0]).toHaveProperty("domain");
      expect(items[0]).toHaveProperty("avail");
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_domain_list returns a list (may be empty)",
    async () => {
      const result = (await findTool(tools, "inwx_domain_list").run({})) as {
        total: number;
        domains: unknown[];
      };
      expect(result).toBeDefined();
      expect(typeof result.total).toBe("number");
      expect(Array.isArray(result.domains)).toBe(true);
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_domain_pricing returns pricing data",
    async () => {
      const result = (await findTool(tools, "inwx_domain_pricing").run({
        domain: "example.de",
      })) as { total: number; pricing: unknown[] };
      expect(result).toBeDefined();
      expect(typeof result.total).toBe("number");
      expect(Array.isArray(result.pricing)).toBe(true);
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_contact_list returns contacts",
    async () => {
      const result = await findTool(tools, "inwx_contact_list").run({});
      expect(result).toBeDefined();
    },
    TEST_TIMEOUT,
  );
});

/* ------------------------------------------------------------------ */
/*  3. Guard enforcement on live connection                           */
/* ------------------------------------------------------------------ */

describeOTE("OTE integration - guard enforcement", () => {
  it(
    "readOnly config blocks write tools even on OTE",
    async () => {
      const tools = buildToolset(oteConfig({ readOnly: true }));
      const registerTool = findTool(tools, "inwx_domain_register");

      await expect(
        registerTool.run({ domain: "should-be-blocked.de" }),
      ).rejects.toThrow("readOnly");
    },
    TEST_TIMEOUT,
  );

  it(
    "allowedOperations whitelist blocks unlisted tools",
    async () => {
      const tools = buildToolset(
        oteConfig({ allowedOperations: ["inwx_account_info"] }),
      );
      const checkTool = findTool(tools, "inwx_domain_check");

      await expect(
        checkTool.run({ domain: "should-be-blocked.de" }),
      ).rejects.toThrow("allowedOperations");
    },
    TEST_TIMEOUT,
  );

  it(
    "allowedOperations still allows whitelisted tool to make real API call",
    async () => {
      const tools = buildToolset(
        oteConfig({ allowedOperations: ["inwx_account_info"] }),
      );
      const infoTool = findTool(tools, "inwx_account_info");

      const result = await infoTool.run({});
      expect(result).toBeDefined();
    },
    TEST_TIMEOUT,
  );
});

/* ------------------------------------------------------------------ */
/*  4. Input validation on live connection                            */
/* ------------------------------------------------------------------ */

describeOTE("OTE integration - input validation", () => {
  let tools: BoundTool[];

  beforeAll(() => {
    tools = buildToolset(oteConfig());
  });

  it(
    "inwx_domain_check rejects empty domain",
    async () => {
      await expect(
        findTool(tools, "inwx_domain_check").run({ domain: "" }),
      ).rejects.toThrow("domain is required");
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_domain_info rejects empty domain",
    async () => {
      await expect(
        findTool(tools, "inwx_domain_info").run({ domain: "" }),
      ).rejects.toThrow("domain is required");
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_dns_record_list rejects empty domain",
    async () => {
      await expect(
        findTool(tools, "inwx_dns_record_list").run({ domain: "" }),
      ).rejects.toThrow("domain is required");
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_nameserver_set rejects missing ns array",
    async () => {
      await expect(
        findTool(tools, "inwx_nameserver_set").run({ domain: "test.de" }),
      ).rejects.toThrow("domain and ns[] are required");
    },
    TEST_TIMEOUT,
  );

  it(
    "inwx_domain_pricing rejects empty domain list",
    async () => {
      await expect(
        findTool(tools, "inwx_domain_pricing").run({}),
      ).rejects.toThrow("domain or domains[] is required");
    },
    TEST_TIMEOUT,
  );
});

/* ------------------------------------------------------------------ */
/*  5. Error handling with live API                                   */
/* ------------------------------------------------------------------ */

describeOTE("OTE integration - API error handling", () => {
  it(
    "rejects invalid credentials with auth error",
    async () => {
      const client = new InwxClient({
        username: "definitely-not-a-real-user-xyz",
        password: "wrong-password",
        environment: "ote",
      });
      try {
        await expect(
          client.call<JsonMap>("account.info", {}),
        ).rejects.toThrow();
      } finally {
        await client.logout();
      }
    },
    TEST_TIMEOUT,
  );
});

/* ------------------------------------------------------------------ */
/*  6. buildToolset integration                                       */
/* ------------------------------------------------------------------ */

describeOTE("OTE integration - buildToolset", () => {
  it(
    "all 23 tools are present and callable",
    async () => {
      const tools = buildToolset(oteConfig());
      expect(tools).toHaveLength(23);

      // Verify every tool has the expected shape
      for (const tool of tools) {
        expect(typeof tool.name).toBe("string");
        expect(tool.name.startsWith("inwx_")).toBe(true);
        expect(typeof tool.description).toBe("string");
        expect(typeof tool.run).toBe("function");
      }
    },
    TEST_TIMEOUT,
  );

  it(
    "round-trip: buildToolset tools work end-to-end against OTE",
    async () => {
      const tools = buildToolset(oteConfig());
      const accountInfo = findTool(tools, "inwx_account_info");
      const domainCheck = findTool(tools, "inwx_domain_check");

      // Each tool call creates its own client + session
      const info = await accountInfo.run({});
      expect(info).toBeDefined();

      const check = (await domainCheck.run({
        domain: "roundtrip-ote-test-99999.de",
      })) as Array<{ domain: string }>;
      expect(check).toBeDefined();
    },
    TEST_TIMEOUT,
  );
});

/* ------------------------------------------------------------------ */
/*  Skip message when credentials are absent                          */
/* ------------------------------------------------------------------ */

if (!HAS_CREDS) {
  describe("OTE integration tests", () => {
    it("skipped - set INWX_OTE_USERNAME and INWX_OTE_PASSWORD to enable", () => {
      // Intentional no-op so the test runner shows why OTE tests were skipped
      expect(true).toBe(true);
    });
  });
}
