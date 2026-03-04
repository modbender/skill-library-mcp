import { ISPConfigClient } from "../src/client";
import { buildToolset } from "../src/index";

const apiUrl = process.env.ISPCONFIG_API_URL;
const username = process.env.ISPCONFIG_USER;
const password = process.env.ISPCONFIG_PASS;

const hasEnv = Boolean(apiUrl && username && password);
const describeLive = hasEnv ? describe : describe.skip;

describeLive("ISPConfig live integration", () => {
  const client = new ISPConfigClient({
    apiUrl: apiUrl as string,
    username: username as string,
    password: password as string,
    verifySsl: true,
  });

  afterAll(async () => {
    await client.logout();
  });

  test("login and logout", async () => {
    const sessionId = await client.login();
    expect(typeof sessionId).toBe("string");
    expect(sessionId.length).toBeGreaterThan(10);

    const logoutRes = await client.logout();
    expect(logoutRes).toBeDefined();
  });

  test("fetch server info", async () => {
    const servers = await client.call<Array<Record<string, unknown>>>("server_get_all", {});
    expect(Array.isArray(servers)).toBe(true);
    expect(servers.length).toBeGreaterThan(0);

    const first = servers[0];
    const serverId = Number(first.server_id ?? 1);
    const details = await client.call<Record<string, unknown>>("server_get", { server_id: serverId });
    expect(details).toBeDefined();
    expect(details.server).toBeDefined();
  });

  test("list sites returns domains", async () => {
    const tools = buildToolset({
      apiUrl: apiUrl as string,
      username: username as string,
      password: password as string,
      verifySsl: true,
    });
    const siteListTool = tools.find((t) => t.name === "isp_sites_list");
    const result = await siteListTool!.run({}) as Array<Record<string, unknown>>;
    const domains = result.map((s) => String(s.domain));

    // Do not assert private domains in public repos.
    expect(domains.length).toBeGreaterThan(0);
  });

  test("client details for client_id=1 has a name", async () => {
    const details = await client.call<Record<string, unknown>>("client_get", { client_id: 1 });
    const name = String(details.company_name ?? details.contact_name ?? "").toLowerCase();
    expect(name.length).toBeGreaterThan(0);
  });

  test("ssl status check", async () => {
    const tools = buildToolset({
      apiUrl: apiUrl as string,
      username: username as string,
      password: password as string,
      verifySsl: true,
    });
    const sslTool = tools.find((t) => t.name === "isp_ssl_status");
    expect(sslTool).toBeDefined();
    const result = await sslTool!.run({});
    const out = result as { total: number; status: Array<Record<string, unknown>> };
    expect(out.total).toBeGreaterThan(0);
    // Only assert structure, not private domain names.
    expect(Array.isArray(out.status)).toBe(true);
    if (out.status.length > 0) {
      expect(Object.prototype.hasOwnProperty.call(out.status[0], "ssl")).toBe(true);
    }
  });
});

describe("guards", () => {
  test("readOnly blocks write tool", async () => {
    const tools = buildToolset({
      apiUrl: "https://example.com/remote/json.php",
      username: "x",
      password: "x",
      readOnly: true,
    });

    const writeTool = tools.find((t) => t.name === "isp_client_add");
    await expect(writeTool!.run({})).rejects.toThrow("readOnly=true");
  });
});
