import { execFile } from "node:child_process";

export interface PreflightResult {
  ok: boolean;
  python: boolean;
  pythonVersion: string;
  zugashieldMcp: boolean;
  errors: string[];
}

/**
 * Checks that the environment can run the zugashield MCP server.
 * Never throws — always returns a structured result.
 *
 * Checks performed:
 *  1. The configured Python executable is callable
 *  2. Python version is >= 3.10
 *  3. `zugashield_mcp` is importable (i.e., `pip install zugashield[mcp]` was done)
 */
export async function runPreflight(pythonExe: string): Promise<PreflightResult> {
  const result: PreflightResult = {
    ok: false,
    python: false,
    pythonVersion: "",
    zugashieldMcp: false,
    errors: [],
  };

  // 1. Check Python exists and get version
  try {
    const version = await exec(pythonExe, [
      "-c",
      "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')",
    ]);
    result.pythonVersion = version.trim();
    result.python = true;

    // 2. Verify Python >= 3.10
    const [major, minor] = result.pythonVersion.split(".").map(Number);
    if (major < 3 || (major === 3 && minor < 10)) {
      result.errors.push(
        `Python >= 3.10 required, found ${result.pythonVersion}`,
      );
      return result;
    }
  } catch (err) {
    result.errors.push(
      `Python not found at "${pythonExe}". Install Python 3.10+ or set mcp.python_executable in config.`,
    );
    return result;
  }

  // 3. Check zugashield_mcp is importable
  try {
    await exec(pythonExe, ["-c", "import zugashield_mcp"]);
    result.zugashieldMcp = true;
  } catch {
    result.errors.push(
      'zugashield MCP module not installed. Run: pip install "zugashield[mcp]"',
    );
    return result;
  }

  result.ok = true;
  return result;
}

/** Minimal environment for preflight child processes. */
function safeEnv(): Record<string, string> {
  const allowlist = [
    "PATH", "SYSTEMROOT", "TEMP", "TMP", "HOME", "USERPROFILE",
    "HOMEDRIVE", "HOMEPATH", "APPDATA", "LOCALAPPDATA",
    "PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "CONDA_PREFIX",
  ];
  const env: Record<string, string> = {};
  for (const key of allowlist) {
    const val = process.env[key];
    if (val !== undefined) env[key] = val;
  }
  return env;
}

/** Promise wrapper around child_process.execFile with a 10s timeout. */
function exec(cmd: string, args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    execFile(cmd, args, { timeout: 10_000, env: safeEnv() }, (error, stdout, stderr) => {
      if (error) reject(new Error(stderr || error.message));
      else resolve(stdout);
    });
  });
}
