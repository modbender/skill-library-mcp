const { spawn } = require("node:child_process");

function mustGetEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env ${name}`);
  return v;
}

module.exports = async function (input) {
  const GITEA_URL = mustGetEnv("GITEA_URL").replace(/\/+$/, "");
  const GITEA_TOKEN = mustGetEnv("GITEA_TOKEN");

  const owner = String(input.owner);
  const repo = String(input.repo);
  const workflow = String(input.workflow);
  const ref = String(input.ref || "master");
  const inputsObj = input.inputs && typeof input.inputs === "object" ? input.inputs : {};
  const dryRun = Boolean(input.dryRun);

  const url = `${GITEA_URL}/api/v1/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}` +
              `/actions/workflows/${encodeURIComponent(workflow)}/dispatches`;

  const body = JSON.stringify({
    ref,
    inputs: { ...inputsObj, ref: inputsObj.ref ?? ref }
  });

  const req = {
    method: "POST",
    url,
    body: JSON.parse(body)
  };

  if (dryRun) {
    return { ok: true, status: 0, response: null, request: req };
  }

  const args = [
    "-sS",
    "-o", "-",
    "-w", "\n%{http_code}",
    "-X", "POST",
    "-H", `Authorization: token ${GITEA_TOKEN}`,
    "-H", "Content-Type: application/json",
    url,
    "-d", body
  ];

  return await new Promise((resolve, reject) => {
    const p = spawn("curl", args, { env: process.env });

    let out = "";
    let err = "";

    p.stdout.on("data", (d) => (out += d.toString("utf-8")));
    p.stderr.on("data", (d) => (err += d.toString("utf-8")));

    p.on("error", reject);
    p.on("close", (code) => {
      if (code !== 0) return reject(new Error(`curl exit ${code}\n${err}`));

      const idx = out.lastIndexOf("\n");
      const resp = idx >= 0 ? out.slice(0, idx).trim() : out.trim();
      const statusStr = idx >= 0 ? out.slice(idx + 1).trim() : "0";
      const status = Number(statusStr) || 0;

      const ok = status >= 200 && status < 300;
      if (!ok) {
        return reject(new Error(`Dispatch failed: HTTP ${status}\n${resp}\n${err}`));
      }

      resolve({ ok, status, response: resp || null, request: req });
    });
  });
};
