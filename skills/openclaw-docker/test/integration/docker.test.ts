/**
 * Integration tests against a real Docker daemon.
 *
 * Requires Docker to be accessible at the default socket path
 * or via the DOCKER_HOST environment variable.
 *
 * Run with: npm run test:integration
 */

import Docker from "dockerode";
import { createTools } from "../../src/tools";
import { PluginConfig, DockerContainerInfo } from "../../src/types";

const TEST_IMAGE = "alpine:3.19";
const TEST_NAME = "openclaw-integration-test";

function dockerSocketPath(): string {
  if (process.env.DOCKER_HOST) {
    return process.env.DOCKER_HOST;
  }
  return process.platform === "win32"
    ? "//./pipe/docker_engine"
    : "/var/run/docker.sock";
}

function makeConfig(): PluginConfig {
  return {
    socketPath: dockerSocketPath(),
    readOnly: false,
    allowedOperations: undefined,
    composeProjects: [],
    timeoutMs: 30_000
  };
}

describe("integration: real Docker daemon", () => {
  let docker: Docker;
  let tools: ReturnType<typeof createTools>;
  let containerId: string;

  beforeAll(async () => {
    const config = makeConfig();
    docker = new Docker({ socketPath: config.socketPath });
    tools = createTools({ docker, config });

    // Pull image
    await new Promise<void>((resolve, reject) => {
      docker.pull(
        TEST_IMAGE,
        {},
        (err: Error | null, stream: NodeJS.ReadableStream | undefined) => {
          if (err || !stream) return reject(err ?? new Error("no stream returned from pull"));
          docker.modem.followProgress(stream, (err2: Error | null) => {
            if (err2) return reject(err2);
            resolve();
          });
        }
      );
    });

    // Clean up any leftover test container from a previous run
    try {
      const old = docker.getContainer(TEST_NAME);
      await old.stop().catch(() => {});
      await old.remove({ force: true });
    } catch {
      // container did not exist - that is fine
    }

    // Create and start a test container that produces output, then sleeps
    const container = await docker.createContainer({
      Image: TEST_IMAGE,
      name: TEST_NAME,
      Cmd: ["sh", "-c", "echo 'openclaw-test-output' && sleep 3600"],
      Tty: false
    });

    containerId = container.id;
    await container.start();

    // Brief wait for the container to produce its initial output
    await new Promise((r) => setTimeout(r, 1_500));
  }, 120_000);

  afterAll(async () => {
    try {
      const container = docker.getContainer(containerId);
      await container.stop({ t: 2 }).catch(() => {});
      await container.remove({ force: true });
    } catch {
      // best-effort cleanup
    }
  }, 30_000);

  // -- Read operations ---------------------------------------------------

  test("docker_ps lists running containers", async () => {
    const result = (await tools.docker_ps({})) as DockerContainerInfo[];

    expect(Array.isArray(result)).toBe(true);
    const found = result.find((c) => c.name === TEST_NAME);
    expect(found).toBeDefined();
    expect(found!.state).toBe("running");
    expect(found!.image).toContain("alpine");
  });

  test("docker_ps with all=true includes stopped containers", async () => {
    const result = (await tools.docker_ps({ all: true })) as DockerContainerInfo[];

    expect(Array.isArray(result)).toBe(true);
    const found = result.find((c) => c.name === TEST_NAME);
    expect(found).toBeDefined();
  });

  test("docker_inspect returns container details", async () => {
    const result = (await tools.docker_inspect({ containerId })) as {
      Id: string;
      Config: { Image: string };
      State: { Running: boolean };
    };

    expect(result.Id).toBe(containerId);
    expect(result.Config.Image).toBe(TEST_IMAGE);
    expect(result.State.Running).toBe(true);
  });

  test("docker_logs retrieves container output", async () => {
    const result = (await tools.docker_logs({
      containerId,
      tail: 50
    })) as { logs: string; containerId: string };

    expect(result.containerId).toBe(containerId);
    expect(result.logs).toContain("openclaw-test-output");
  });

  test("docker_inspect returns error for non-existent container", async () => {
    await expect(
      tools.docker_inspect({ containerId: "nonexistent-container-xyz" })
    ).rejects.toThrow(/Failed to inspect/);
  });

  // -- Lifecycle operations (order matters) ------------------------------

  test("docker_stop stops the container", async () => {
    const result = (await tools.docker_stop({ containerId, timeout: 5 })) as {
      ok: boolean;
      action: string;
    };

    expect(result.ok).toBe(true);
    expect(result.action).toBe("stop");

    const info = (await tools.docker_inspect({ containerId })) as {
      State: { Running: boolean };
    };
    expect(info.State.Running).toBe(false);
  });

  test("docker_start starts the stopped container", async () => {
    const result = (await tools.docker_start({ containerId })) as {
      ok: boolean;
      action: string;
    };

    expect(result.ok).toBe(true);
    expect(result.action).toBe("start");

    const info = (await tools.docker_inspect({ containerId })) as {
      State: { Running: boolean };
    };
    expect(info.State.Running).toBe(true);
  });

  test("docker_restart cycles the container", async () => {
    const result = (await tools.docker_restart({ containerId, timeout: 5 })) as {
      ok: boolean;
      action: string;
    };

    expect(result.ok).toBe(true);
    expect(result.action).toBe("restart");

    const info = (await tools.docker_inspect({ containerId })) as {
      State: { Running: boolean };
    };
    expect(info.State.Running).toBe(true);
  });

  // -- Guard behavior with real daemon -----------------------------------

  test("readOnly config blocks write operations", async () => {
    const readOnlyConfig = { ...makeConfig(), readOnly: true };
    const readOnlyTools = createTools({ docker, config: readOnlyConfig });

    await expect(
      readOnlyTools.docker_start({ containerId })
    ).rejects.toThrow(/readOnly/);

    // Read operations still work
    const result = (await readOnlyTools.docker_ps({})) as DockerContainerInfo[];
    expect(Array.isArray(result)).toBe(true);
  });
});
