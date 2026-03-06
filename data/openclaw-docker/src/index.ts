import { normalizeConfig } from "./config";
import { createDockerClient } from "./dockerClient";
import { createTools } from "./tools";

interface OpenClawApi {
  config?: unknown;
  registerTool?: (name: string, handler: (input: unknown) => Promise<unknown>) => void;
  tool?: (name: string, handler: (input: unknown) => Promise<unknown>) => void;
}

export default function init(api: OpenClawApi): void {
  const config = normalizeConfig(api.config);
  const docker = createDockerClient(config);
  const tools = createTools({ docker, config });

  const register = api.registerTool ?? api.tool;

  if (!register) {
    throw new Error("OpenClaw API does not expose registerTool/tool.");
  }

  register("docker_ps", async (input) => tools.docker_ps(input as { all?: boolean }));
  register("docker_logs", async (input) =>
    tools.docker_logs(
      input as { containerId: string; tail?: number; follow?: boolean; followDurationMs?: number }
    )
  );
  register("docker_inspect", async (input) =>
    tools.docker_inspect(input as { containerId: string })
  );
  register("docker_start", async (input) => tools.docker_start(input as { containerId: string }));
  register("docker_stop", async (input) =>
    tools.docker_stop(input as { containerId: string; timeout?: number })
  );
  register("docker_restart", async (input) =>
    tools.docker_restart(input as { containerId: string; timeout?: number })
  );
  register("docker_compose_up", async (input) =>
    tools.docker_compose_up(input as { project: string; detached?: boolean })
  );
  register("docker_compose_down", async (input) =>
    tools.docker_compose_down(input as { project: string; volumes?: boolean })
  );
  register("docker_compose_ps", async (input) =>
    tools.docker_compose_ps(input as { project: string; services?: string[] })
  );
}

export { createTools } from "./tools";
export { normalizeConfig } from "./config";
export { assertOperationAllowed } from "./guards";
