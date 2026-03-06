import { Readable } from "node:stream";
import Docker from "dockerode";
import { runComposeCommand } from "./compose";
import { assertOperationAllowed } from "./guards";
import { DockerOperation, PluginConfig } from "./types";

interface ToolDeps {
  docker: Docker;
  config: PluginConfig;
  composeRunner?: typeof runComposeCommand;
}

interface ToolMap {
  docker_ps: (input?: { all?: boolean }) => Promise<unknown>;
  docker_logs: (input: {
    containerId: string;
    tail?: number;
    follow?: boolean;
    followDurationMs?: number;
  }) => Promise<unknown>;
  docker_inspect: (input: { containerId: string }) => Promise<unknown>;
  docker_start: (input: { containerId: string }) => Promise<unknown>;
  docker_stop: (input: { containerId: string; timeout?: number }) => Promise<unknown>;
  docker_restart: (input: { containerId: string; timeout?: number }) => Promise<unknown>;
  docker_compose_up: (input: { project: string; detached?: boolean }) => Promise<unknown>;
  docker_compose_down: (input: { project: string; volumes?: boolean }) => Promise<unknown>;
  docker_compose_ps: (input: { project: string; services?: string[] }) => Promise<unknown>;
}

function guard(op: DockerOperation, config: PluginConfig): void {
  assertOperationAllowed(op, config);
}

function requiredContainer(input: { containerId?: string }): string {
  if (!input.containerId || input.containerId.trim() === "") {
    throw new Error("containerId is required.");
  }
  return input.containerId;
}

function resolveProjectPath(config: PluginConfig, name: string): string {
  const project = config.composeProjects.find((entry) => entry.name === name);
  if (!project) {
    throw new Error(`Unknown compose project '${name}'.`);
  }
  return project.path;
}

export function createTools({ docker, config, composeRunner = runComposeCommand }: ToolDeps): ToolMap {
  return {
    async docker_ps(input) {
      guard("ps", config);
      try {
        const containers = await docker.listContainers({ all: input?.all ?? false });
        return containers.map((c) => ({
          id: c.Id,
          name: c.Names?.[0]?.replace(/^\//, "") ?? "",
          image: c.Image,
          state: c.State,
          status: c.Status
        }));
      } catch (error) {
        throw new Error(`Failed to list containers: ${(error as Error).message}`);
      }
    },

    async docker_logs(input) {
      guard("logs", config);
      const containerId = requiredContainer(input);
      const tail = input.tail ?? 100;

      try {
        const container = docker.getContainer(containerId);

        if (input.follow) {
          const duration = Math.min(input.followDurationMs ?? 10_000, config.timeoutMs);
          const stream = (await container.logs({
            stdout: true,
            stderr: true,
            tail,
            timestamps: false,
            follow: true
          })) as unknown as Readable;

          const chunks: Buffer[] = [];
          let resolved = false;

          return new Promise<unknown>((resolve, reject) => {
            function finish() {
              if (resolved) return;
              resolved = true;
              clearTimeout(timer);
              const text = Buffer.concat(chunks).toString("utf8");
              resolve({ containerId, tail, follow: true, durationMs: duration, logs: text });
            }

            const timer = setTimeout(() => {
              stream.destroy();
              finish();
            }, duration);

            stream.on("data", (chunk: Buffer | string) => {
              chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk as string));
            });

            stream.on("end", finish);
            stream.on("close", finish);

            stream.on("error", (err: Error) => {
              if (resolved) return;
              resolved = true;
              clearTimeout(timer);
              reject(
                new Error(`Failed to follow logs for '${containerId}': ${err.message}`)
              );
            });
          });
        }

        const data = await container.logs({
          stdout: true,
          stderr: true,
          tail,
          timestamps: false
        });

        const text = Buffer.isBuffer(data) ? data.toString("utf8") : String(data);
        return { containerId, tail, logs: text };
      } catch (error) {
        throw new Error(`Failed to get logs for '${containerId}': ${(error as Error).message}`);
      }
    },

    async docker_inspect(input) {
      guard("inspect", config);
      const containerId = requiredContainer(input);

      try {
        const container = docker.getContainer(containerId);
        return await container.inspect();
      } catch (error) {
        throw new Error(`Failed to inspect '${containerId}': ${(error as Error).message}`);
      }
    },

    async docker_start(input) {
      guard("start", config);
      const containerId = requiredContainer(input);

      try {
        const container = docker.getContainer(containerId);
        await container.start();
        return { ok: true, action: "start", containerId };
      } catch (error) {
        throw new Error(`Failed to start '${containerId}': ${(error as Error).message}`);
      }
    },

    async docker_stop(input) {
      guard("stop", config);
      const containerId = requiredContainer(input);

      try {
        const container = docker.getContainer(containerId);
        await container.stop({ t: input.timeout ?? 10 });
        return { ok: true, action: "stop", containerId };
      } catch (error) {
        throw new Error(`Failed to stop '${containerId}': ${(error as Error).message}`);
      }
    },

    async docker_restart(input) {
      guard("restart", config);
      const containerId = requiredContainer(input);

      try {
        const container = docker.getContainer(containerId);
        await container.restart({ t: input.timeout ?? 10 });
        return { ok: true, action: "restart", containerId };
      } catch (error) {
        throw new Error(`Failed to restart '${containerId}': ${(error as Error).message}`);
      }
    },

    async docker_compose_up(input) {
      guard("compose_up", config);
      const projectPath = resolveProjectPath(config, input.project);
      const detached = input.detached !== false;
      const args = ["up", ...(detached ? ["-d"] : [])];

      const result = await composeRunner(projectPath, args, config.timeoutMs);
      return { ok: true, action: "compose_up", project: input.project, ...result };
    },

    async docker_compose_down(input) {
      guard("compose_down", config);
      const projectPath = resolveProjectPath(config, input.project);
      const args = ["down", ...(input.volumes ? ["--volumes"] : [])];

      const result = await composeRunner(projectPath, args, config.timeoutMs);
      return { ok: true, action: "compose_down", project: input.project, ...result };
    },

    async docker_compose_ps(input) {
      guard("compose_ps", config);
      const projectPath = resolveProjectPath(config, input.project);
      const args = ["ps", "--format", "json", ...(input.services ?? [])];

      const result = await composeRunner(projectPath, args, config.timeoutMs);
      let services: unknown[] = [];
      const stdout = result.stdout.trim();
      if (stdout) {
        // docker compose ps --format json outputs one JSON object per line
        services = stdout.split("\n").map((line) => JSON.parse(line));
      }
      return { ok: true, action: "compose_ps", project: input.project, services };
    }
  };
}
