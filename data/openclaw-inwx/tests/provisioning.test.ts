import {
  provisionDomainWithHosting,
  ExternalBoundTool,
  ProvisionDomainHostingParams,
} from "../src/provisioning";

function mockTool(name: string, result: unknown = {}): ExternalBoundTool {
  return { name, run: jest.fn(async () => result) };
}

function baseParams(overrides: Partial<ProvisionDomainHostingParams> = {}): ProvisionDomainHostingParams {
  return {
    domain: "example.com",
    nameservers: ["ns1.hosting.de", "ns2.hosting.de"],
    serverIp: "1.2.3.4",
    clientName: "Acme Corp",
    clientEmail: "admin@acme.com",
    ...overrides,
  };
}

function inwxToolset(overrides: Partial<Record<string, ExternalBoundTool>> = {}): ExternalBoundTool[] {
  return [
    overrides.inwx_domain_check ?? mockTool("inwx_domain_check", [{ domain: "example.com", avail: true }]),
    overrides.inwx_domain_register ?? mockTool("inwx_domain_register", { domain: "example.com" }),
    overrides.inwx_nameserver_set ?? mockTool("inwx_nameserver_set", {}),
  ];
}

function ispToolset(overrides: Partial<Record<string, ExternalBoundTool>> = {}): ExternalBoundTool[] {
  return [
    overrides.isp_provision_site ?? mockTool("isp_provision_site", { ok: true, domain: "example.com", created: { client_id: 1 } }),
  ];
}

describe("provisionDomainWithHosting", () => {
  it("runs full provisioning workflow for an available domain", async () => {
    const inwx = inwxToolset();
    const isp = ispToolset();
    const result = await provisionDomainWithHosting(inwx, isp, baseParams());

    expect(result.ok).toBe(true);
    expect(result.domain).toBe("example.com");
    expect(result.steps).toHaveLength(4);
    expect(result.steps.map((s) => s.step)).toEqual([
      "domain_check",
      "domain_register",
      "nameserver_set",
      "isp_provision",
    ]);
    expect(result.steps.every((s) => s.status === "ok")).toBe(true);
    expect(result.created.domainRegistered).toBe(true);
    expect(result.created.nameserversConfigured).toBe(true);
    expect(result.created.hostingProvisioned).toBe(true);
  });

  it("skips registration when domain is already taken", async () => {
    const inwx = inwxToolset({
      inwx_domain_check: mockTool("inwx_domain_check", [{ domain: "taken.de", avail: false }]),
    });
    const isp = ispToolset();
    const result = await provisionDomainWithHosting(inwx, isp, baseParams({ domain: "taken.de" }));

    expect(result.ok).toBe(true);
    const regStep = result.steps.find((s) => s.step === "domain_register");
    expect(regStep?.status).toBe("skipped");
    expect(result.created.domainRegistered).toBe(false);
  });

  it("skips registration when skipRegistration=true", async () => {
    const inwx = inwxToolset();
    const isp = ispToolset();
    const result = await provisionDomainWithHosting(inwx, isp, baseParams({ skipRegistration: true }));

    expect(result.ok).toBe(true);
    const regStep = result.steps.find((s) => s.step === "domain_register");
    expect(regStep?.status).toBe("skipped");
  });

  it("returns error when domain check fails", async () => {
    const failCheck: ExternalBoundTool = {
      name: "inwx_domain_check",
      run: jest.fn(async () => { throw new Error("API timeout"); }),
    };
    const inwx = inwxToolset({ inwx_domain_check: failCheck });
    const isp = ispToolset();
    const result = await provisionDomainWithHosting(inwx, isp, baseParams());

    expect(result.ok).toBe(false);
    expect(result.steps[0].status).toBe("error");
    expect(result.steps[0].error).toContain("API timeout");
  });

  it("returns error when domain registration fails", async () => {
    const failReg: ExternalBoundTool = {
      name: "inwx_domain_register",
      run: jest.fn(async () => { throw new Error("Insufficient balance"); }),
    };
    const inwx = inwxToolset({ inwx_domain_register: failReg });
    const isp = ispToolset();
    const result = await provisionDomainWithHosting(inwx, isp, baseParams());

    expect(result.ok).toBe(false);
    const regStep = result.steps.find((s) => s.step === "domain_register");
    expect(regStep?.status).toBe("error");
    expect(regStep?.error).toContain("Insufficient balance");
  });

  it("returns error when ISPConfig provisioning fails", async () => {
    const failIsp: ExternalBoundTool = {
      name: "isp_provision_site",
      run: jest.fn(async () => { throw new Error("Connection refused"); }),
    };
    const inwx = inwxToolset();
    const isp = ispToolset({ isp_provision_site: failIsp });
    const result = await provisionDomainWithHosting(inwx, isp, baseParams());

    expect(result.ok).toBe(false);
    expect(result.steps.at(-1)?.step).toBe("isp_provision");
    expect(result.steps.at(-1)?.status).toBe("error");
  });

  it("rejects empty domain", async () => {
    const result = await provisionDomainWithHosting([], [], baseParams({ domain: "  " }));

    expect(result.ok).toBe(false);
    expect(result.steps[0].error).toContain("domain is required");
  });

  it("returns error when required tool is missing from toolset", async () => {
    const result = await provisionDomainWithHosting([], ispToolset(), baseParams());

    expect(result.ok).toBe(false);
    expect(result.steps[0].status).toBe("error");
    expect(result.steps[0].error).toContain('Required tool "inwx_domain_check" not found');
  });

  it("passes correct params to isp_provision_site", async () => {
    const ispProvision = mockTool("isp_provision_site", { ok: true });
    const inwx = inwxToolset();
    const isp = [ispProvision];

    await provisionDomainWithHosting(inwx, isp, baseParams({
      createMail: false,
      createDb: false,
      serverId: 2,
    }));

    expect(ispProvision.run).toHaveBeenCalledWith(expect.objectContaining({
      domain: "example.com",
      clientName: "Acme Corp",
      clientEmail: "admin@acme.com",
      serverIp: "1.2.3.4",
      createMail: false,
      createDb: false,
      serverId: 2,
    }));
  });

  it("passes registration params to inwx_domain_register", async () => {
    const regTool = mockTool("inwx_domain_register", {});
    const inwx = inwxToolset({ inwx_domain_register: regTool });
    const isp = ispToolset();

    await provisionDomainWithHosting(inwx, isp, baseParams({
      registrationPeriod: 2,
      contacts: { registrant: 123 },
    }));

    expect(regTool.run).toHaveBeenCalledWith(expect.objectContaining({
      domain: "example.com",
      period: 2,
      contacts: { registrant: 123 },
      ns: ["ns1.hosting.de", "ns2.hosting.de"],
    }));
  });

  it("skips nameserver step when nameservers array is empty", async () => {
    const inwx = inwxToolset();
    const isp = ispToolset();
    const result = await provisionDomainWithHosting(inwx, isp, baseParams({ nameservers: [] }));

    expect(result.ok).toBe(true);
    const nsStep = result.steps.find((s) => s.step === "nameserver_set");
    expect(nsStep?.status).toBe("skipped");
  });
});
