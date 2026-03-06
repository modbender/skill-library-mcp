import { INWX_ERROR_MESSAGES, InwxApiError, InwxClient } from "../src/client";

function mockFactory(responseByMethod: Record<string, unknown>, loginOk = true) {
  return () => ({
    login: jest.fn(async () => (loginOk ? { code: 1000 } : null)),
    logout: jest.fn(async () => ({ code: 1000 })),
    callApi: jest.fn(async (method: string) => responseByMethod[method] as { code?: number; msg?: string; resData?: unknown }),
  });
}

describe("InwxClient", () => {
  it("maps successful response", async () => {
    const client = new InwxClient(
      { username: "user", password: "pass", environment: "ote" },
      mockFactory({ "domain.check": { code: 1000, resData: { avail: 1 } } }),
    );

    const out = await client.call<{ avail: number }>("domain.check", { domain: "example.com" });
    expect(out.avail).toBe(1);
  });

  it("throws mapped API errors", async () => {
    const client = new InwxClient(
      { username: "user", password: "pass" },
      mockFactory({ "domain.check": { code: 2302, msg: INWX_ERROR_MESSAGES[2302] } }),
    );

    await expect(client.call("domain.check", { domain: "taken.de" })).rejects.toBeInstanceOf(InwxApiError);
  });

  it("throws on auth failure", async () => {
    const client = new InwxClient({ username: "user", password: "pass" }, mockFactory({}, false));
    await expect(client.call("domain.list", {})).rejects.toThrow("login failed");
  });

  it("handles insufficient balance error", async () => {
    const client = new InwxClient(
      { username: "user", password: "pass" },
      mockFactory({ "domain.create": { code: 2400, msg: "Insufficient balance" } }),
    );

    await expect(client.call("domain.create", { domain: "x.de" })).rejects.toMatchObject({ code: 2400 });
  });
});
