import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export async function runComposeCommand(
  projectPath: string,
  args: string[],
  timeoutMs: number
): Promise<{ stdout: string; stderr: string }> {
  const cmdArgs = ["compose", ...args];

  try {
    const result = await execFileAsync("docker", cmdArgs, {
      cwd: projectPath,
      timeout: timeoutMs,
      maxBuffer: 1024 * 1024 * 4
    });
    return {
      stdout: result.stdout ?? "",
      stderr: result.stderr ?? ""
    };
  } catch (error) {
    const err = error as Error & { stdout?: string; stderr?: string };
    throw new Error(
      `Compose command failed (${cmdArgs.join(" ")}): ${err.message}\n${err.stderr ?? ""}`.trim()
    );
  }
}
