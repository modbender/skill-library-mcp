const { spawn } = require("node:child_process");

function mustGetEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env ${name}`);
  return v;
}

function curl(args) {
  return new Promise((resolve, reject) => {
    const p = spawn("curl", args, { env: process.env });
    let out = "", err = "";
    p.stdout.on("data", d => out += d.toString());
    p.stderr.on("data", d => err += d.toString());
    p.on("error", reject);
    p.on("close", code => {
      if (code !== 0) return reject(new Error(`curl exit ${code}: ${err}`));
      resolve(out);
    });
  });
}

module.exports = async function (input) {
  const GITEA_URL = mustGetEnv("GITEA_URL").replace(/\/+$/, "");
  const GITEA_TOKEN = mustGetEnv("GITEA_TOKEN");

  const action = input.action || "dispatch";
  const owner = String(input.owner);
  const repo = String(input.repo);
  const workflow = input.workflow;
  const ref = input.ref || "master";
  const runId = input.runId;

  const baseUrl = `${GITEA_URL}/api/v1/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`;

  // Dispatch workflow
  if (action === "dispatch") {
    if (!workflow) throw new Error("workflow is required for dispatch");
    const url = `${baseUrl}/actions/workflows/${encodeURIComponent(workflow)}/dispatches`;
    const body = JSON.stringify({ ref });
    
    const result = await curl([
      "-sS", "-w", "\n%{http_code}",
      "-X", "POST",
      "-H", `Authorization: token ${GITEA_TOKEN}`,
      "-H", "Content-Type: application/json",
      url, "-d", body
    ]);
    
    const idx = result.lastIndexOf("\n");
    const status = Number(idx >= 0 ? result.slice(idx + 1).trim() : "0");
    return { ok: status >= 200 && status < 300, status, action: "dispatch" };
  }

  // List workflow runs
  if (action === "runs") {
    let url = `${baseUrl}/actions/runs`;
    if (workflow) url += `?workflow=${encodeURIComponent(workflow)}`;
    
    const result = await curl(["-sS", "-H", `Authorization: token ${GITEA_TOKEN}`, url]);
    return { ok: true, status: 200, action: "runs", data: JSON.parse(result) };
  }

  // Get run status
  if (action === "run" && runId) {
    const url = `${baseUrl}/actions/runs/${runId}`;
    const result = await curl(["-sS", "-H", `Authorization: token ${GITEA_TOKEN}`, url]);
    return { ok: true, status: 200, action: "run", data: JSON.parse(result) };
  }

  throw new Error(`Unknown action: ${action}. Use: dispatch, runs, run`);
};
