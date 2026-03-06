import { createTools } from "../src/tools";
import { ISPConfigClient } from "../src/client";
import { ISPConfigError, normalizeError, classifyApiMessage } from "../src/errors";
import { ToolContext, ToolDefinition, JsonMap } from "../src/types";
import { validateParams, TOOL_SCHEMAS } from "../src/validate";

// ---------------------------------------------------------------------------
// Mock ISPConfigClient so no real HTTP calls are made
// ---------------------------------------------------------------------------

jest.mock("../src/client");

const MockedClient = ISPConfigClient as jest.MockedClass<typeof ISPConfigClient>;

let mockCall: jest.Mock;
let mockLogout: jest.Mock;

function resetMocks(): void {
  MockedClient.mockClear();
  mockCall = jest.fn();
  mockLogout = jest.fn().mockResolvedValue(undefined);
  MockedClient.mockImplementation(() => ({
    call: mockCall,
    logout: mockLogout,
    login: jest.fn().mockResolvedValue("mock-session"),
  } as unknown as ISPConfigClient));
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const BASE_CONFIG = {
  apiUrl: "https://panel.example.com:8080/remote/json.php",
  username: "admin",
  password: "secret",
  serverId: 1,
  defaultServerIp: "1.2.3.4",
};

function ctx(overrides: Partial<typeof BASE_CONFIG> = {}): ToolContext {
  return { config: { ...BASE_CONFIG, ...overrides } };
}

function findTool(tools: ToolDefinition[], name: string): ToolDefinition {
  const t = tools.find((td) => td.name === name);
  if (!t) throw new Error(`Tool ${name} not found`);
  return t;
}

// ---------------------------------------------------------------------------
// Test suites
// ---------------------------------------------------------------------------

describe("write tools (mock-based)", () => {
  let tools: ToolDefinition[];

  beforeEach(() => {
    resetMocks();
    tools = createTools();
  });

  // ---- isp_client_add ----
  test("isp_client_add passes params to client_add", async () => {
    mockCall.mockResolvedValueOnce(42);
    const tool = findTool(tools, "isp_client_add");
    const params = { company_name: "Acme", email: "ceo@acme.test" };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("client_add", { reseller_id: 0, params });
    expect(result).toBe(42);
    expect(mockLogout).toHaveBeenCalled();
  });

  // ---- isp_site_add ----
  test("isp_site_add forwards params to sites_web_domain_add", async () => {
    mockCall.mockResolvedValueOnce(101);
    const tool = findTool(tools, "isp_site_add");
    const params = { client_id: 1, params: { domain: "acme.test", active: "y" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("sites_web_domain_add", params);
    expect(result).toBe(101);
  });

  // ---- isp_domain_add (alias) ----
  test("isp_domain_add is alias for sites_web_domain_add", async () => {
    mockCall.mockResolvedValueOnce(102);
    const tool = findTool(tools, "isp_domain_add");
    const params = { client_id: 2, params: { domain: "alias.test" } };

    await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("sites_web_domain_add", params);
  });

  // ---- isp_dns_zone_add ----
  test("isp_dns_zone_add forwards to dns_zone_add", async () => {
    mockCall.mockResolvedValueOnce(200);
    const tool = findTool(tools, "isp_dns_zone_add");
    const params = { client_id: 1, params: { origin: "acme.test.", ns: "ns1.acme.test." } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("dns_zone_add", params);
    expect(result).toBe(200);
  });

  // ---- isp_dns_record_add - all supported types ----
  test.each([
    ["A", "dns_a_add"],
    ["AAAA", "dns_aaaa_add"],
    ["MX", "dns_mx_add"],
    ["TXT", "dns_txt_add"],
    ["CNAME", "dns_cname_add"],
  ])("isp_dns_record_add type=%s dispatches to %s", async (type, expectedMethod) => {
    mockCall.mockResolvedValueOnce(300);
    const tool = findTool(tools, "isp_dns_record_add");
    const params = { type, zone: 10, name: "test.", data: "1.2.3.4" };

    await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith(expectedMethod, params);
  });

  test("isp_dns_record_add rejects unsupported type via schema validation", async () => {
    const tool = findTool(tools, "isp_dns_record_add");

    await expect(tool.run({ type: "SRV" }, ctx())).rejects.toThrow("must be one of [A, AAAA, MX, TXT, CNAME]");
  });

  // ---- isp_dns_record_delete - type dispatch ----
  test.each([
    ["A", "dns_a_delete"],
    ["AAAA", "dns_aaaa_delete"],
    ["MX", "dns_mx_delete"],
    ["TXT", "dns_txt_delete"],
    ["CNAME", "dns_cname_delete"],
  ])("isp_dns_record_delete type=%s dispatches to %s", async (type, expectedMethod) => {
    mockCall.mockResolvedValueOnce(true);
    const tool = findTool(tools, "isp_dns_record_delete");
    const params = { type, primary_id: 55 };

    await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith(expectedMethod, params);
  });

  // ---- isp_mail_domain_add ----
  test("isp_mail_domain_add forwards to mail_domain_add", async () => {
    mockCall.mockResolvedValueOnce(400);
    const tool = findTool(tools, "isp_mail_domain_add");
    const params = { client_id: 1, params: { domain: "acme.test", active: "y" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("mail_domain_add", params);
    expect(result).toBe(400);
  });

  // ---- isp_mail_user_add ----
  test("isp_mail_user_add forwards to mail_user_add", async () => {
    mockCall.mockResolvedValueOnce(500);
    const tool = findTool(tools, "isp_mail_user_add");
    const params = { client_id: 1, params: { email: "info@acme.test" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("mail_user_add", params);
    expect(result).toBe(500);
  });

  // ---- isp_mail_user_delete ----
  test("isp_mail_user_delete forwards to mail_user_delete", async () => {
    mockCall.mockResolvedValueOnce(true);
    const tool = findTool(tools, "isp_mail_user_delete");
    const params = { primary_id: 500 };

    await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("mail_user_delete", params);
  });

  // ---- isp_db_add ----
  test("isp_db_add forwards to sites_database_add", async () => {
    mockCall.mockResolvedValueOnce(600);
    const tool = findTool(tools, "isp_db_add");
    const params = { client_id: 1, params: { database_name: "testdb" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("sites_database_add", params);
    expect(result).toBe(600);
  });

  // ---- isp_db_user_add ----
  test("isp_db_user_add forwards to sites_database_user_add", async () => {
    mockCall.mockResolvedValueOnce(700);
    const tool = findTool(tools, "isp_db_user_add");
    const params = { client_id: 1, params: { database_user: "u_test" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("sites_database_user_add", params);
    expect(result).toBe(700);
  });

  // ---- isp_shell_user_add ----
  test("isp_shell_user_add forwards to sites_shell_user_add", async () => {
    mockCall.mockResolvedValueOnce(800);
    const tool = findTool(tools, "isp_shell_user_add");
    const params = { client_id: 1, params: { username: "shell1" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("sites_shell_user_add", params);
    expect(result).toBe(800);
  });

  // ---- isp_ftp_user_add ----
  test("isp_ftp_user_add forwards to sites_ftp_user_add", async () => {
    mockCall.mockResolvedValueOnce(900);
    const tool = findTool(tools, "isp_ftp_user_add");
    const params = { client_id: 1, params: { username: "ftp1" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("sites_ftp_user_add", params);
    expect(result).toBe(900);
  });

  // ---- isp_cron_add ----
  test("isp_cron_add forwards to sites_cron_add", async () => {
    mockCall.mockResolvedValueOnce(1000);
    const tool = findTool(tools, "isp_cron_add");
    const params = { client_id: 1, params: { command: "/usr/bin/php cron.php" } };

    const result = await tool.run(params, ctx());

    expect(mockCall).toHaveBeenCalledWith("sites_cron_add", params);
    expect(result).toBe(1000);
  });

  // ---- logout always called ----
  test("logout is called even when tool throws", async () => {
    mockCall.mockRejectedValueOnce(new Error("API failure"));
    const tool = findTool(tools, "isp_client_add");

    await expect(tool.run({}, ctx())).rejects.toThrow("API failure");
    expect(mockLogout).toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// isp_methods_list dynamic discovery
// ---------------------------------------------------------------------------

describe("isp_methods_list (mock-based)", () => {
  let tools: ToolDefinition[];

  beforeEach(() => {
    resetMocks();
    tools = createTools();
  });

  test("uses dynamic discovery when get_function_list succeeds", async () => {
    const serverFunctions = [
      "server_get_all", "server_get", "client_get_all", "client_get", "client_add",
      "sites_web_domain_get", "sites_web_domain_add", "dns_zone_get_by_user",
      "extra_method_one", "extra_method_two",
    ];
    mockCall.mockResolvedValueOnce(serverFunctions);

    const tool = findTool(tools, "isp_methods_list");
    const result = await tool.run({}, ctx()) as JsonMap;

    expect(result.discovery).toBe("dynamic");
    expect(mockCall).toHaveBeenCalledWith("get_function_list", {});
    expect(mockCall).toHaveBeenCalledTimes(1);

    const available = result.available as string[];
    expect(available).toContain("server_get_all");
    expect(available).toContain("client_add");

    const unavailable = result.unavailable as Array<{ method: string; reason: string }>;
    expect(unavailable.length).toBeGreaterThan(0);
    expect(unavailable[0].reason).toBe("not in get_function_list");

    const extra = result.extra as string[];
    expect(extra).toContain("extra_method_one");
    expect(extra).toContain("extra_method_two");

    expect(result.totalServer).toBe(serverFunctions.length);
  });

  test("falls back to probe when get_function_list throws", async () => {
    // First call: get_function_list fails
    mockCall.mockRejectedValueOnce(new Error("ISPConfig API error: invalid function name"));
    // Subsequent calls: probing each known method
    mockCall.mockResolvedValue(undefined);

    const tool = findTool(tools, "isp_methods_list");
    const result = await tool.run({}, ctx()) as JsonMap;

    expect(result.discovery).toBe("probe");
    expect(mockCall.mock.calls[0][0]).toBe("get_function_list");
    // All known methods should have been probed after the failed discovery
    expect(mockCall.mock.calls.length).toBeGreaterThan(1);
  });

  test("falls back to probe when get_function_list returns empty array", async () => {
    mockCall.mockResolvedValueOnce([]);
    // Subsequent probing calls
    mockCall.mockResolvedValue(undefined);

    const tool = findTool(tools, "isp_methods_list");
    const result = await tool.run({}, ctx()) as JsonMap;

    expect(result.discovery).toBe("probe");
  });

  test("falls back to probe when get_function_list returns non-array", async () => {
    mockCall.mockResolvedValueOnce("not-an-array");
    // Subsequent probing calls
    mockCall.mockResolvedValue(undefined);

    const tool = findTool(tools, "isp_methods_list");
    const result = await tool.run({}, ctx()) as JsonMap;

    expect(result.discovery).toBe("probe");
  });

  test("probe classifies methods by error type", async () => {
    // get_function_list fails
    mockCall.mockRejectedValueOnce(new Error("invalid function"));
    // First known method succeeds
    mockCall.mockResolvedValueOnce([]);
    // Second known method fails with invalid function (unavailable)
    mockCall.mockRejectedValueOnce(new Error("invalid function name"));
    // Rest succeed
    mockCall.mockResolvedValue([]);

    const tool = findTool(tools, "isp_methods_list");
    const result = await tool.run({}, ctx()) as JsonMap;

    expect(result.discovery).toBe("probe");
    const available = result.available as string[];
    const unavailable = result.unavailable as Array<{ method: string; reason: string }>;
    expect(available.length + unavailable.length).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// Provision flow
// ---------------------------------------------------------------------------

describe("isp_provision_site (mock-based)", () => {
  let tools: ToolDefinition[];

  beforeEach(() => {
    resetMocks();
    tools = createTools();
  });

  test("full provision with mail and db", async () => {
    // Sequence of client.call responses:
    // 1. client_add -> newClientId
    // 2. sites_web_domain_add -> websiteId
    // 3. dns_zone_add -> zoneId
    // 4. dns_a_add (A record)
    // 5. dns_cname_add (CNAME www)
    // 6. dns_txt_add (SPF)
    // 7. dns_txt_add (DMARC)
    // 8. mail_domain_add -> mailDomainId
    // 9. mail_user_add (info@)
    // 10. mail_user_add (admin@)
    // 11. sites_database_user_add -> dbUserId
    // 12. sites_database_add -> dbId
    // 13. sites_web_domain_update (enable SSL)
    mockCall
      .mockResolvedValueOnce(10)   // client_add
      .mockResolvedValueOnce(20)   // sites_web_domain_add
      .mockResolvedValueOnce(30)   // dns_zone_add
      .mockResolvedValueOnce(true) // dns_a_add
      .mockResolvedValueOnce(true) // dns_cname_add
      .mockResolvedValueOnce(true) // dns_txt_add (SPF)
      .mockResolvedValueOnce(true) // dns_txt_add (DMARC)
      .mockResolvedValueOnce(40)   // mail_domain_add
      .mockResolvedValueOnce(true) // mail_user_add info@
      .mockResolvedValueOnce(true) // mail_user_add admin@
      .mockResolvedValueOnce(50)   // sites_database_user_add
      .mockResolvedValueOnce(60)   // sites_database_add
      .mockResolvedValueOnce(true); // sites_web_domain_update

    const tool = findTool(tools, "isp_provision_site");
    const result = await tool.run({
      domain: "acme.test",
      clientName: "Acme Corp",
      clientEmail: "admin@acme.test",
      createMail: true,
      createDb: true,
    }, ctx()) as JsonMap;

    expect(result.ok).toBe(true);
    expect(result.domain).toBe("acme.test");

    const created = result.created as JsonMap;
    expect(created.client_id).toBe(10);
    expect(created.site_id).toBe(20);
    expect(created.dns_zone_id).toBe(30);
    expect(created.mail_domain_id).toBe(40);
    expect(created.database_user_id).toBe(50);
    expect(created.database_id).toBe(60);

    // Verify API call sequence
    expect(mockCall).toHaveBeenCalledTimes(13);

    // 1. client_add
    expect(mockCall.mock.calls[0][0]).toBe("client_add");
    expect(mockCall.mock.calls[0][1]).toMatchObject({ reseller_id: 0, params: { company_name: "Acme Corp" } });

    // 2. sites_web_domain_add
    expect(mockCall.mock.calls[1][0]).toBe("sites_web_domain_add");
    expect(mockCall.mock.calls[1][1]).toMatchObject({ client_id: 10, params: { domain: "acme.test", ssl: "y", ssl_letsencrypt: "y" } });

    // 3. dns_zone_add
    expect(mockCall.mock.calls[2][0]).toBe("dns_zone_add");
    expect(mockCall.mock.calls[2][1]).toMatchObject({ client_id: 10, params: { origin: "acme.test." } });

    // 4. A record
    expect(mockCall.mock.calls[3][0]).toBe("dns_a_add");
    expect(mockCall.mock.calls[3][1]).toMatchObject({ params: { data: "1.2.3.4" } });

    // 5. CNAME www
    expect(mockCall.mock.calls[4][0]).toBe("dns_cname_add");
    expect(mockCall.mock.calls[4][1]).toMatchObject({ params: { name: "www.acme.test." } });

    // 6. SPF
    expect(mockCall.mock.calls[5][0]).toBe("dns_txt_add");
    expect(mockCall.mock.calls[5][1]).toMatchObject({ params: { data: "v=spf1 mx a ~all" } });

    // 7. DMARC
    expect(mockCall.mock.calls[6][0]).toBe("dns_txt_add");
    expect(mockCall.mock.calls[6][1]).toMatchObject({ params: { name: "_dmarc.acme.test." } });

    // 8. mail_domain_add
    expect(mockCall.mock.calls[7][0]).toBe("mail_domain_add");

    // 9-10. mail_user_add
    expect(mockCall.mock.calls[8][0]).toBe("mail_user_add");
    expect(mockCall.mock.calls[8][1]).toMatchObject({ params: { login: "info@acme.test" } });
    expect(mockCall.mock.calls[9][0]).toBe("mail_user_add");
    expect(mockCall.mock.calls[9][1]).toMatchObject({ params: { login: "admin@acme.test" } });

    // 11. sites_database_user_add
    expect(mockCall.mock.calls[10][0]).toBe("sites_database_user_add");

    // 12. sites_database_add
    expect(mockCall.mock.calls[11][0]).toBe("sites_database_add");
    expect(mockCall.mock.calls[11][1]).toMatchObject({ params: { database_user_id: 50 } });

    // 13. sites_web_domain_update (SSL enable)
    expect(mockCall.mock.calls[12][0]).toBe("sites_web_domain_update");
    expect(mockCall.mock.calls[12][1]).toMatchObject({ primary_id: 20, params: { ssl: "y", ssl_letsencrypt: "y" } });
  });

  test("provision without mail or db skips those steps", async () => {
    mockCall
      .mockResolvedValueOnce(10)   // client_add
      .mockResolvedValueOnce(20)   // sites_web_domain_add
      .mockResolvedValueOnce(30)   // dns_zone_add
      .mockResolvedValueOnce(true) // dns_a_add
      .mockResolvedValueOnce(true) // dns_cname_add
      .mockResolvedValueOnce(true) // dns_txt_add (SPF)
      .mockResolvedValueOnce(true) // dns_txt_add (DMARC)
      .mockResolvedValueOnce(true); // sites_web_domain_update

    const tool = findTool(tools, "isp_provision_site");
    const result = await tool.run({
      domain: "nomail.test",
      clientName: "NoMail Inc",
      clientEmail: "boss@nomail.test",
      createMail: false,
      createDb: false,
    }, ctx()) as JsonMap;

    expect(result.ok).toBe(true);

    const created = result.created as JsonMap;
    expect(created.client_id).toBe(10);
    expect(created.site_id).toBe(20);
    expect(created.dns_zone_id).toBe(30);
    // No mail or db entries
    expect(created.mail_domain_id).toBeUndefined();
    expect(created.database_id).toBeUndefined();
    expect(created.database_user_id).toBeUndefined();

    // 7 calls without mail/db + 1 final SSL update = 8
    expect(mockCall).toHaveBeenCalledTimes(8);
  });

  test("provision without serverIp skips A and CNAME records", async () => {
    mockCall
      .mockResolvedValueOnce(10)   // client_add
      .mockResolvedValueOnce(20)   // sites_web_domain_add
      .mockResolvedValueOnce(30)   // dns_zone_add
      .mockResolvedValueOnce(true) // dns_txt_add (SPF)
      .mockResolvedValueOnce(true) // dns_txt_add (DMARC)
      .mockResolvedValueOnce(true); // sites_web_domain_update

    const tool = findTool(tools, "isp_provision_site");
    const result = await tool.run({
      domain: "noip.test",
      clientName: "NoIP Ltd",
      clientEmail: "it@noip.test",
      createMail: false,
      createDb: false,
    }, ctx({ defaultServerIp: "" })) as JsonMap;

    expect(result.ok).toBe(true);

    // No dns_a_add or dns_cname_add
    const methods = mockCall.mock.calls.map((c) => c[0]);
    expect(methods).not.toContain("dns_a_add");
    expect(methods).not.toContain("dns_cname_add");
    expect(mockCall).toHaveBeenCalledTimes(6);
  });

  test("provision rejects missing required fields via schema validation", async () => {
    const tool = findTool(tools, "isp_provision_site");

    await expect(tool.run({ domain: "x.test" }, ctx())).rejects.toThrow(
      "Validation failed for isp_provision_site",
    );

    await expect(tool.run({ clientName: "Foo", clientEmail: "a@b.c" }, ctx())).rejects.toThrow(
      "Missing required parameter: domain",
    );
  });
});

// ---------------------------------------------------------------------------
// Guard enforcement on write tools
// ---------------------------------------------------------------------------

describe("guard enforcement", () => {
  let tools: ToolDefinition[];

  beforeEach(() => {
    resetMocks();
    tools = createTools();
  });

  // Valid params per tool so schema validation passes and guard check is reached
  const WRITE_TOOLS_WITH_PARAMS: Array<[string, JsonMap]> = [
    ["isp_client_add", {}],
    ["isp_site_add", {}],
    ["isp_domain_add", {}],
    ["isp_dns_zone_add", {}],
    ["isp_dns_record_add", { type: "A" }],
    ["isp_dns_record_delete", { type: "A" }],
    ["isp_mail_domain_add", {}],
    ["isp_mail_user_add", {}],
    ["isp_mail_user_delete", {}],
    ["isp_db_add", {}],
    ["isp_db_user_add", {}],
    ["isp_shell_user_add", {}],
    ["isp_ftp_user_add", {}],
    ["isp_cron_add", {}],
    ["isp_provision_site", { domain: "x.test", clientName: "X", clientEmail: "x@x.test" }],
  ];

  test.each(WRITE_TOOLS_WITH_PARAMS)("readOnly blocks %s", async (toolName, params) => {
    const tool = findTool(tools, toolName);
    const readOnlyCtx = ctx({ readOnly: true } as never);

    await expect(tool.run(params, readOnlyCtx)).rejects.toThrow("readOnly=true");
    // Client.call should never be invoked
    expect(mockCall).not.toHaveBeenCalled();
  });

  test("allowedOperations whitelist blocks unlisted tools", async () => {
    const tool = findTool(tools, "isp_client_add");
    const restrictedCtx: ToolContext = {
      config: { ...BASE_CONFIG, allowedOperations: ["isp_sites_list"] },
    };

    await expect(tool.run({}, restrictedCtx)).rejects.toThrow("blocked by allowedOperations");
    expect(mockCall).not.toHaveBeenCalled();
  });

  test("allowedOperations whitelist permits listed tools", async () => {
    mockCall.mockResolvedValueOnce(1);
    const tool = findTool(tools, "isp_client_add");
    const permittedCtx: ToolContext = {
      config: { ...BASE_CONFIG, allowedOperations: ["isp_client_add"] },
    };

    await expect(tool.run({}, permittedCtx)).resolves.toBe(1);
    expect(mockCall).toHaveBeenCalled();
  });

  test("read tools work in readOnly mode", async () => {
    mockCall.mockResolvedValueOnce([{ domain_id: 1, domain: "x.test", active: "y" }]);
    const tool = findTool(tools, "isp_sites_list");
    const readOnlyCtx = ctx({ readOnly: true } as never);

    await expect(tool.run({}, readOnlyCtx)).resolves.toBeDefined();
    expect(mockCall).toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// Schema-level runtime validation (validateParams)
// ---------------------------------------------------------------------------

describe("validateParams (unit)", () => {
  test("passes for tools without schemas", () => {
    expect(() => validateParams("isp_methods_list", {})).not.toThrow();
    expect(() => validateParams("isp_client_list", { random: "stuff" })).not.toThrow();
    expect(() => validateParams("unknown_tool", {})).not.toThrow();
  });

  // ---- isp_provision_site ----
  test("isp_provision_site rejects missing required fields", () => {
    expect(() => validateParams("isp_provision_site", {})).toThrow("Validation failed");
    expect(() => validateParams("isp_provision_site", {})).toThrow("Missing required parameter: domain");
    expect(() => validateParams("isp_provision_site", {})).toThrow("Missing required parameter: clientName");
    expect(() => validateParams("isp_provision_site", {})).toThrow("Missing required parameter: clientEmail");
  });

  test("isp_provision_site rejects empty strings for required fields", () => {
    expect(() => validateParams("isp_provision_site", {
      domain: "  ", clientName: "Test", clientEmail: "a@b.c",
    })).toThrow("must not be empty");
  });

  test("isp_provision_site accepts valid params", () => {
    expect(() => validateParams("isp_provision_site", {
      domain: "acme.test", clientName: "Acme", clientEmail: "a@acme.test",
    })).not.toThrow();
  });

  test("isp_provision_site rejects non-numeric serverId", () => {
    expect(() => validateParams("isp_provision_site", {
      domain: "x.test", clientName: "X", clientEmail: "x@x.test",
      serverId: "not-a-number",
    })).toThrow("must be a valid number");
  });

  test("isp_provision_site accepts numeric string serverId", () => {
    expect(() => validateParams("isp_provision_site", {
      domain: "x.test", clientName: "X", clientEmail: "x@x.test",
      serverId: "5",
    })).not.toThrow();
  });

  // ---- anyOf groups ----
  test("isp_client_get requires client_id or clientId", () => {
    expect(() => validateParams("isp_client_get", {})).toThrow("One of [client_id, clientId] is required");
    expect(() => validateParams("isp_client_get", { client_id: 1 })).not.toThrow();
    expect(() => validateParams("isp_client_get", { clientId: 2 })).not.toThrow();
  });

  test("isp_site_get requires primary_id, domain_id, or site_id", () => {
    expect(() => validateParams("isp_site_get", {})).toThrow("One of [primary_id, domain_id, site_id] is required");
    expect(() => validateParams("isp_site_get", { primary_id: 1 })).not.toThrow();
    expect(() => validateParams("isp_site_get", { domain_id: 2 })).not.toThrow();
    expect(() => validateParams("isp_site_get", { site_id: 3 })).not.toThrow();
  });

  test("isp_dns_record_list requires zone_id or zoneId", () => {
    expect(() => validateParams("isp_dns_record_list", {})).toThrow("One of [zone_id, zoneId] is required");
    expect(() => validateParams("isp_dns_record_list", { zone_id: 10 })).not.toThrow();
    expect(() => validateParams("isp_dns_record_list", { zoneId: 10 })).not.toThrow();
  });

  test("isp_quota_check requires client_id or clientId", () => {
    expect(() => validateParams("isp_quota_check", {})).toThrow("One of [client_id, clientId] is required");
    expect(() => validateParams("isp_quota_check", { client_id: 1 })).not.toThrow();
  });

  // ---- DNS type enum ----
  test("isp_dns_record_add rejects missing type", () => {
    expect(() => validateParams("isp_dns_record_add", {})).toThrow("Missing required parameter: type");
  });

  test("isp_dns_record_add rejects invalid type", () => {
    expect(() => validateParams("isp_dns_record_add", { type: "SRV" })).toThrow("must be one of");
  });

  test("isp_dns_record_add accepts valid types case-insensitively", () => {
    for (const t of ["A", "a", "AAAA", "aaaa", "MX", "mx", "TXT", "txt", "CNAME", "cname"]) {
      expect(() => validateParams("isp_dns_record_add", { type: t })).not.toThrow();
    }
  });

  test("isp_dns_record_delete validates type the same way", () => {
    expect(() => validateParams("isp_dns_record_delete", {})).toThrow("Missing required parameter: type");
    expect(() => validateParams("isp_dns_record_delete", { type: "INVALID" })).toThrow("must be one of");
    expect(() => validateParams("isp_dns_record_delete", { type: "A" })).not.toThrow();
  });

  // ---- null/undefined handling ----
  test("null values count as missing", () => {
    expect(() => validateParams("isp_client_get", { client_id: null })).toThrow("is required");
    expect(() => validateParams("isp_provision_site", {
      domain: null, clientName: "X", clientEmail: "x@x.test",
    })).toThrow("Missing required parameter: domain");
  });

  // ---- multiple errors ----
  test("collects multiple errors in one message", () => {
    try {
      validateParams("isp_provision_site", {});
      fail("should have thrown");
    } catch (e) {
      const msg = (e as Error).message;
      expect(msg).toContain("domain");
      expect(msg).toContain("clientName");
      expect(msg).toContain("clientEmail");
    }
  });
});

// ---------------------------------------------------------------------------
// Validation integrated into tool execution
// ---------------------------------------------------------------------------

describe("validation prevents API calls", () => {
  let tools: ToolDefinition[];

  beforeEach(() => {
    resetMocks();
    tools = createTools();
  });

  test("isp_client_get rejects without id before any API call", async () => {
    const tool = findTool(tools, "isp_client_get");

    await expect(tool.run({}, ctx())).rejects.toThrow("Validation failed");
    expect(mockCall).not.toHaveBeenCalled();
    expect(mockLogout).not.toHaveBeenCalled();
  });

  test("isp_site_get rejects without id before any API call", async () => {
    const tool = findTool(tools, "isp_site_get");

    await expect(tool.run({}, ctx())).rejects.toThrow("Validation failed");
    expect(mockCall).not.toHaveBeenCalled();
  });

  test("isp_dns_record_add rejects invalid type before any API call", async () => {
    const tool = findTool(tools, "isp_dns_record_add");

    await expect(tool.run({ type: "BOGUS" }, ctx())).rejects.toThrow("must be one of");
    expect(mockCall).not.toHaveBeenCalled();
  });

  test("isp_dns_record_list rejects missing zone_id before any API call", async () => {
    const tool = findTool(tools, "isp_dns_record_list");

    await expect(tool.run({}, ctx())).rejects.toThrow("Validation failed");
    expect(mockCall).not.toHaveBeenCalled();
  });

  test("isp_quota_check rejects missing client_id before any API call", async () => {
    const tool = findTool(tools, "isp_quota_check");

    await expect(tool.run({}, ctx())).rejects.toThrow("Validation failed");
    expect(mockCall).not.toHaveBeenCalled();
  });

  test("isp_provision_site rejects empty params before any API call", async () => {
    const tool = findTool(tools, "isp_provision_site");

    await expect(tool.run({}, ctx())).rejects.toThrow("Validation failed");
    expect(mockCall).not.toHaveBeenCalled();
  });

  test("tools without schemas still work normally", async () => {
    mockCall.mockResolvedValueOnce(42);
    const tool = findTool(tools, "isp_client_add");

    const result = await tool.run({ company_name: "Test" }, ctx());

    expect(result).toBe(42);
    expect(mockCall).toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// TOOL_SCHEMAS coverage check
// ---------------------------------------------------------------------------

describe("TOOL_SCHEMAS completeness", () => {
  test("all schema tool names correspond to real tools", () => {
    const tools = createTools();
    const toolNames = new Set(tools.map((t) => t.name));

    for (const schemaName of Object.keys(TOOL_SCHEMAS)) {
      expect(toolNames.has(schemaName)).toBe(true);
    }
  });
});

// ---------------------------------------------------------------------------
// ISPConfigError class
// ---------------------------------------------------------------------------

describe("ISPConfigError", () => {
  test("extends Error with correct name", () => {
    const err = new ISPConfigError("api_error", "something broke");
    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(ISPConfigError);
    expect(err.name).toBe("ISPConfigError");
    expect(err.message).toBe("something broke");
  });

  test("stores code, retryable, and statusCode", () => {
    const err = new ISPConfigError("network_error", "timeout", {
      retryable: true,
      statusCode: 504,
    });
    expect(err.code).toBe("network_error");
    expect(err.retryable).toBe(true);
    expect(err.statusCode).toBe(504);
  });

  test("defaults retryable to false", () => {
    const err = new ISPConfigError("validation_error", "bad input");
    expect(err.retryable).toBe(false);
  });

  test("stores cause", () => {
    const cause = new Error("original");
    const err = new ISPConfigError("api_error", "wrapped", { cause });
    expect(err.cause).toBe(cause);
  });
});

// ---------------------------------------------------------------------------
// classifyApiMessage
// ---------------------------------------------------------------------------

describe("classifyApiMessage", () => {
  test.each([
    ["ISPConfig API error: invalid function name", "invalid_method"],
    ["ISPConfig API error: Unknown method foo_bar", "invalid_method"],
    ["ISPConfig API error: method not found", "invalid_method"],
    ["ISPConfig API error: function not found", "invalid_method"],
    ["ISPConfig API error: not a valid method", "invalid_method"],
  ])("classifies '%s' as %s", (msg, expected) => {
    expect(classifyApiMessage(msg)).toBe(expected);
  });

  test.each([
    ["ISPConfig API error: permission denied for this action", "permission_denied"],
    ["ISPConfig API error: access denied", "permission_denied"],
    ["ISPConfig API error: not allowed for client", "permission_denied"],
    ["ISPConfig API error: forbidden", "permission_denied"],
    ["ISPConfig API error: no permission", "permission_denied"],
    ["ISPConfig API error: not permitted", "permission_denied"],
    ["ISPConfig API error: authorization required", "permission_denied"],
  ])("classifies '%s' as %s", (msg, expected) => {
    expect(classifyApiMessage(msg)).toBe(expected);
  });

  test.each([
    ["ISPConfig API error: session expired", "auth_error"],
    ["ISPConfig API error: login failed", "auth_error"],
    ["ISPConfig API error: authentication required", "auth_error"],
    ["ISPConfig API error: invalid credentials", "auth_error"],
    ["ISPConfig API error: no session id", "auth_error"],
  ])("classifies '%s' as %s", (msg, expected) => {
    expect(classifyApiMessage(msg)).toBe(expected);
  });

  test("falls back to api_error for unknown messages", () => {
    expect(classifyApiMessage("ISPConfig API error: something unexpected")).toBe("api_error");
    expect(classifyApiMessage("generic error")).toBe("api_error");
  });
});

// ---------------------------------------------------------------------------
// normalizeError
// ---------------------------------------------------------------------------

describe("normalizeError", () => {
  test("passes through ISPConfigError unchanged", () => {
    const original = new ISPConfigError("validation_error", "bad input", { statusCode: 400 });
    const result = normalizeError(original);
    expect(result).toBe(original);
  });

  test("converts timeout errors to network_error", () => {
    const err = normalizeError(new Error("ISPConfig request timeout after 20000ms"));
    expect(err).toBeInstanceOf(ISPConfigError);
    expect(err.code).toBe("network_error");
    expect(err.retryable).toBe(true);
  });

  test("converts ECONNREFUSED to network_error", () => {
    const err = normalizeError(new Error("connect ECONNREFUSED 127.0.0.1:8080"));
    expect(err.code).toBe("network_error");
    expect(err.retryable).toBe(true);
  });

  test("converts ECONNRESET to network_error", () => {
    const err = normalizeError(new Error("read ECONNRESET"));
    expect(err.code).toBe("network_error");
    expect(err.retryable).toBe(true);
  });

  test("converts ENOTFOUND to network_error", () => {
    const err = normalizeError(new Error("getaddrinfo ENOTFOUND panel.example.com"));
    expect(err.code).toBe("network_error");
    expect(err.retryable).toBe(true);
  });

  test("converts socket hang up to network_error", () => {
    const err = normalizeError(new Error("socket hang up"));
    expect(err.code).toBe("network_error");
    expect(err.retryable).toBe(true);
  });

  test("converts HTTP 401 to auth_error", () => {
    const err = normalizeError(new Error("ISPConfig HTTP 401: Unauthorized"));
    expect(err.code).toBe("auth_error");
    expect(err.statusCode).toBe(401);
    expect(err.retryable).toBe(true);
  });

  test("converts HTTP 403 to permission_denied", () => {
    const err = normalizeError(new Error("ISPConfig HTTP 403: Forbidden"));
    expect(err.code).toBe("permission_denied");
    expect(err.statusCode).toBe(403);
    expect(err.retryable).toBe(false);
  });

  test("converts HTTP 500 to api_error with retryable", () => {
    const err = normalizeError(new Error("ISPConfig HTTP 500: Internal Server Error"));
    expect(err.code).toBe("api_error");
    expect(err.statusCode).toBe(500);
    expect(err.retryable).toBe(true);
  });

  test("converts HTTP 404 to api_error without retryable", () => {
    const err = normalizeError(new Error("ISPConfig HTTP 404: Not Found"));
    expect(err.code).toBe("api_error");
    expect(err.statusCode).toBe(404);
    expect(err.retryable).toBe(false);
  });

  test("converts non-JSON response to parse_error", () => {
    const err = normalizeError(new Error("ISPConfig returned non-JSON response: <html>404</html>"));
    expect(err.code).toBe("parse_error");
    expect(err.retryable).toBe(false);
  });

  test("converts ISPConfig API envelope invalid_method", () => {
    const err = normalizeError(new Error("ISPConfig API error: invalid function name"));
    expect(err.code).toBe("invalid_method");
  });

  test("converts ISPConfig API envelope permission error", () => {
    const err = normalizeError(new Error("ISPConfig API error: permission denied"));
    expect(err.code).toBe("permission_denied");
  });

  test("converts ISPConfig API envelope session error", () => {
    const err = normalizeError(new Error("ISPConfig API error: session expired"));
    expect(err.code).toBe("auth_error");
    expect(err.retryable).toBe(true);
  });

  test("converts login failure to auth_error", () => {
    const err = normalizeError(new Error("ISPConfig login failed: no session_id returned"));
    expect(err.code).toBe("auth_error");
  });

  test("converts validation errors to validation_error", () => {
    const err = normalizeError(new Error("Validation failed for isp_client_get: One of [client_id, clientId] is required"));
    expect(err.code).toBe("validation_error");
    expect(err.statusCode).toBe(400);
    expect(err.retryable).toBe(false);
  });

  test("converts readOnly policy error to permission_denied", () => {
    const err = normalizeError(new Error("Tool isp_client_add is blocked because readOnly=true"));
    expect(err.code).toBe("permission_denied");
    expect(err.statusCode).toBe(403);
  });

  test("converts allowedOperations policy error to permission_denied", () => {
    const err = normalizeError(new Error("Tool isp_client_add is blocked by allowedOperations policy"));
    expect(err.code).toBe("permission_denied");
    expect(err.statusCode).toBe(403);
  });

  test("converts string values to api_error", () => {
    const err = normalizeError("some string error");
    expect(err).toBeInstanceOf(ISPConfigError);
    expect(err.code).toBe("api_error");
    expect(err.message).toBe("some string error");
  });

  test("unknown errors fall back to api_error", () => {
    const err = normalizeError(new Error("something completely unexpected"));
    expect(err.code).toBe("api_error");
    expect(err.retryable).toBe(false);
  });

  test("preserves cause from original error", () => {
    const original = new Error("original error");
    const err = normalizeError(original);
    expect(err.cause).toBe(original);
  });
});

// ---------------------------------------------------------------------------
// Error normalization integrated into tool execution
// ---------------------------------------------------------------------------

describe("error normalization in tool execution", () => {
  let tools: ToolDefinition[];

  beforeEach(() => {
    resetMocks();
    tools = createTools();
  });

  test("validation errors are thrown as ISPConfigError with code=validation_error", async () => {
    const tool = findTool(tools, "isp_client_get");

    try {
      await tool.run({}, ctx());
      fail("should have thrown");
    } catch (err) {
      expect(err).toBeInstanceOf(ISPConfigError);
      const ispErr = err as ISPConfigError;
      expect(ispErr.code).toBe("validation_error");
      expect(ispErr.statusCode).toBe(400);
      expect(ispErr.retryable).toBe(false);
    }
  });

  test("guard errors are thrown as ISPConfigError with code=permission_denied", async () => {
    const tool = findTool(tools, "isp_client_add");
    const readOnlyCtx = ctx({ readOnly: true } as never);

    try {
      await tool.run({}, readOnlyCtx);
      fail("should have thrown");
    } catch (err) {
      expect(err).toBeInstanceOf(ISPConfigError);
      const ispErr = err as ISPConfigError;
      expect(ispErr.code).toBe("permission_denied");
      expect(ispErr.statusCode).toBe(403);
    }
  });

  test("API errors from client.call are normalized", async () => {
    mockCall.mockRejectedValueOnce(new Error("ISPConfig API error: invalid function name"));
    const tool = findTool(tools, "isp_client_add");

    try {
      await tool.run({}, ctx());
      fail("should have thrown");
    } catch (err) {
      expect(err).toBeInstanceOf(ISPConfigError);
      const ispErr = err as ISPConfigError;
      expect(ispErr.code).toBe("invalid_method");
    }
  });

  test("network errors from client.call are normalized", async () => {
    mockCall.mockRejectedValueOnce(new Error("connect ECONNREFUSED 127.0.0.1:8080"));
    const tool = findTool(tools, "isp_client_add");

    try {
      await tool.run({}, ctx());
      fail("should have thrown");
    } catch (err) {
      expect(err).toBeInstanceOf(ISPConfigError);
      const ispErr = err as ISPConfigError;
      expect(ispErr.code).toBe("network_error");
      expect(ispErr.retryable).toBe(true);
    }
  });

  test("ISPConfigError from client passes through normalizeError unchanged", async () => {
    const original = new ISPConfigError("auth_error", "session expired", { retryable: true });
    mockCall.mockRejectedValueOnce(original);
    const tool = findTool(tools, "isp_client_add");

    try {
      await tool.run({}, ctx());
      fail("should have thrown");
    } catch (err) {
      expect(err).toBe(original);
    }
  });
});
