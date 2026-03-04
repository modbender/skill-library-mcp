import { PassThrough } from "node:stream";
import { createTools } from "../src/tools";
import { assertOperationAllowed } from "../src/guards";
import { PluginConfig } from "../src/types";
import { vi } from 'vitest'

function baseConfig(): PluginConfig {
  return {
    socketPath: "/var/run/docker.sock",
    readOnly: false,
    allowedOperations: undefined,
    composeProjects: [],
    timeoutMs: 15000
  };
}

describe("docker tools", () => {
  test("docker_ps returns normalized container list", async () => {
    const docker = {
      listContainers: vi.fn().mockResolvedValue([
        {
          Id: "abc",
          Names: ["/web"],
          Image: "nginx:latest",
          State: "running",
          Status: "Up 1 minute"
        }
      ])
    } as unknown as Parameters<typeof createTools>[0]["docker"];

    const tools = createTools({ docker, config: baseConfig() });
    const result = (await tools.docker_ps({ all: true })) as Array<Record<string, string>>;

    expect(result[0]).toEqual({
      id: "abc",
      name: "web",
      image: "nginx:latest",
      state: "running",
      status: "Up 1 minute"
    });
  });

  test("docker_logs returns text logs", async () => {
    const docker = {
      getContainer: vi.fn().mockReturnValue({
        logs: vi.fn().mockResolvedValue(Buffer.from("hello\nworld"))
      })
    } as unknown as Parameters<typeof createTools>[0]["docker"];

    const tools = createTools({ docker, config: baseConfig() });
    const result = (await tools.docker_logs({ containerId: "abc", tail: 20 })) as Record<
      string,
      unknown
    >;

    expect(result.logs).toContain("hello");
  });

  test("docker_logs follow mode collects streamed data", async () => {
    const mockStream = new PassThrough();
    const docker = {
      getContainer: vi.fn().mockReturnValue({
        logs: vi.fn().mockResolvedValue(mockStream)
      })
    } as unknown as Parameters<typeof createTools>[0]["docker"];

    const tools = createTools({ docker, config: baseConfig() });

    setTimeout(() => {
      mockStream.write(Buffer.from("line1\n"));
      mockStream.write(Buffer.from("line2\n"));
      mockStream.end();
    }, 10);

    const result = (await tools.docker_logs({
      containerId: "abc",
      follow: true,
      followDurationMs: 5000
    })) as Record<string, unknown>;

    expect(result.follow).toBe(true);
    expect(result.logs).toContain("line1");
    expect(result.logs).toContain("line2");
  });

  test("docker_logs follow mode respects duration limit", async () => {
    const mockStream = new PassThrough();
    const docker = {
      getContainer: vi.fn().mockReturnValue({
        logs: vi.fn().mockResolvedValue(mockStream)
      })
    } as unknown as Parameters<typeof createTools>[0]["docker"];

    const tools = createTools({ docker, config: baseConfig() });

    mockStream.write(Buffer.from("initial\n"));

    const result = (await tools.docker_logs({
      containerId: "abc",
      follow: true,
      followDurationMs: 100
    })) as Record<string, unknown>;

    expect(result.follow).toBe(true);
    expect(result.durationMs).toBe(100);
    expect(result.logs).toContain("initial");
  });

  test("docker_inspect returns payload", async () => {
    const docker = {
      getContainer: vi.fn().mockReturnValue({
        inspect: vi.fn().mockResolvedValue({ Id: "abc", Config: { Image: "redis" } })
      })
    } as unknown as Parameters<typeof createTools>[0]["docker"];

    const tools = createTools({ docker, config: baseConfig() });
    const result = (await tools.docker_inspect({ containerId: "abc" })) as { Id: string };

    expect(result.Id).toBe("abc");
  });
});

describe("docker_compose_ps", () => {
  function composeConfig(): PluginConfig {
    return {
      ...baseConfig(),
      composeProjects: [{ name: "myapp", path: "/opt/myapp" }]
    };
  }

  test("returns parsed service list from compose ps JSON output", async () => {
    const jsonLine1 = JSON.stringify({ Name: "myapp-web-1", State: "running", Service: "web" });
    const jsonLine2 = JSON.stringify({ Name: "myapp-db-1", State: "running", Service: "db" });
    const mockRunner = vi.fn().mockResolvedValue({
      stdout: `${jsonLine1}\n${jsonLine2}\n`,
      stderr: ""
    });

    const docker = {} as Parameters<typeof createTools>[0]["docker"];
    const tools = createTools({ docker, config: composeConfig(), composeRunner: mockRunner });
    const result = (await tools.docker_compose_ps({ project: "myapp" })) as {
      ok: boolean;
      action: string;
      project: string;
      services: Array<{ Name: string; State: string; Service: string }>;
    };

    expect(result.ok).toBe(true);
    expect(result.action).toBe("compose_ps");
    expect(result.project).toBe("myapp");
    expect(result.services).toHaveLength(2);
    expect(result.services[0]).toEqual({ Name: "myapp-web-1", State: "running", Service: "web" });
    expect(result.services[1]).toEqual({ Name: "myapp-db-1", State: "running", Service: "db" });
    expect(mockRunner).toHaveBeenCalledWith("/opt/myapp", ["ps", "--format", "json"], 15000);
  });

  test("returns empty services array when no containers are running", async () => {
    const mockRunner = vi.fn().mockResolvedValue({ stdout: "", stderr: "" });

    const docker = {} as Parameters<typeof createTools>[0]["docker"];
    const tools = createTools({ docker, config: composeConfig(), composeRunner: mockRunner });
    const result = (await tools.docker_compose_ps({ project: "myapp" })) as {
      services: unknown[];
    };

    expect(result.services).toEqual([]);
  });

  test("passes service filter arguments to compose command", async () => {
    const mockRunner = vi.fn().mockResolvedValue({ stdout: "", stderr: "" });

    const docker = {} as Parameters<typeof createTools>[0]["docker"];
    const tools = createTools({ docker, config: composeConfig(), composeRunner: mockRunner });
    await tools.docker_compose_ps({ project: "myapp", services: ["web"] });

    expect(mockRunner).toHaveBeenCalledWith("/opt/myapp", ["ps", "--format", "json", "web"], 15000);
  });

  test("is allowed in readOnly mode", () => {
    const config: PluginConfig = { ...baseConfig(), readOnly: true };
    expect(() => assertOperationAllowed("compose_ps", config)).not.toThrow();
  });
});

describe("allowedOperations guard", () => {
  test("blocks write operations in readOnly mode", () => {
    const config: PluginConfig = {
      ...baseConfig(),
      readOnly: true
    };

    expect(() => assertOperationAllowed("start", config)).toThrow(/readOnly/);
    expect(() => assertOperationAllowed("ps", config)).not.toThrow();
  });

  test("blocks non-whitelisted operation", () => {
    const config: PluginConfig = {
      ...baseConfig(),
      allowedOperations: ["ps", "inspect"]
    };

    expect(() => assertOperationAllowed("logs", config)).toThrow(/allowedOperations/);
  });
});
