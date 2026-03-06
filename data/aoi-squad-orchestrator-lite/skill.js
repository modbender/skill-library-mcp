#!/usr/bin/env node
import fs from "fs";
import os from "os";
import path from "path";

const SCHEMA_VERSION = "aoi.squad.report.v0.1";

const PRESETS = {
  "planner-builder-reviewer": {
    label: "Planner / Builder / Reviewer",
    roles: [
      { key: "planner", archetype: "Planner", objective: "Break the task into a simple plan with priorities and constraints." },
      { key: "builder", archetype: "Builder", objective: "Produce a concrete draft/implementation outline that follows the plan." },
      { key: "reviewer", archetype: "Reviewer", objective: "Review for correctness, risks, and missing steps; propose fixes." }
    ]
  },
  "researcher-writer-editor": {
    label: "Researcher / Writer / Editor",
    roles: [
      { key: "researcher", archetype: "Researcher", objective: "Collect assumptions and key facts; propose references to verify." },
      { key: "writer", archetype: "Writer", objective: "Write a clear, user-facing draft based on findings." },
      { key: "editor", archetype: "Editor", objective: "Improve clarity, structure, and consistency; remove fluff." }
    ]
  },
  "builder-security-operator": {
    label: "Builder / Security / Operator",
    roles: [
      { key: "builder", archetype: "Builder", objective: "Draft the build steps and command sequence (no external side effects)." },
      { key: "security", archetype: "Sentinel", objective: "Check for unsafe actions, secrets exposure, and policy violations." },
      { key: "operator", archetype: "Operator", objective: "Turn the result into a runnable checklist + VCP-style proof points." }
    ]
  }
};

const CALLSIGNS = [
  "Vega","Kestrel","Orion","Lyra","Atlas","Nova","Rune","Cobalt","Sable","Juniper",
  "Nimbus","Ash","Mosaic","Pulse","Quill","Beacon","Astra","Zenith","Hawke","Tundra"
];

function homeFile() {
  return path.join(os.homedir(), ".openclaw", "aoi", "squad_names.json");
}

function ensureDir(p) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
}

function loadNames() {
  const fp = homeFile();
  try {
    const raw = fs.readFileSync(fp, "utf8");
    return JSON.parse(raw);
  } catch {
    return { schema: "aoi.squad.names.v0.1", presets: {} };
  }
}

function saveNames(db) {
  const fp = homeFile();
  ensureDir(fp);
  fs.writeFileSync(fp, JSON.stringify(db, null, 2) + "\n", "utf8");
}

function pickCallsign(used) {
  const available = CALLSIGNS.filter(c => !used.has(c));
  const arr = available.length ? available : CALLSIGNS;
  return arr[Math.floor(Math.random() * arr.length)];
}

function defaultName(archetype, used) {
  const cs = pickCallsign(used);
  used.add(cs);
  return `${archetype} ${cs}`;
}

function getOrInitTeam(db, preset) {
  if (!PRESETS[preset]) throw new Error(`Unknown preset: ${preset}`);
  db.presets[preset] ||= { roles: {} };
  const used = new Set(Object.values(db.presets[preset].roles || {}).map(x => x.split(" ").slice(1).join(" ")).filter(Boolean));

  for (const r of PRESETS[preset].roles) {
    if (!db.presets[preset].roles[r.key]) {
      db.presets[preset].roles[r.key] = defaultName(r.archetype, used);
    }
  }
  return db.presets[preset].roles;
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const [k, v] = a.includes("=") ? a.slice(2).split("=") : [a.slice(2), argv[i + 1]];
      if (!a.includes("=")) i++;
      out[k] = v;
    } else {
      out._.push(a);
    }
  }
  return out;
}

function jsonOut(obj, code = 0) {
  process.stdout.write(JSON.stringify(obj, null, 2) + "\n");
  process.exit(code);
}

function fail(message, extra = {}) {
  jsonOut({ ok: false, error: message, ...extra }, 1);
}

function cmdPresetList() {
  const items = Object.entries(PRESETS).map(([key, p]) => ({ preset: key, label: p.label, roles: p.roles.map(r => r.key) }));
  jsonOut({ ok: true, presets: items });
}

function cmdTeamShow(args) {
  const preset = args.preset;
  if (!preset) return fail("Missing --preset");
  const db = loadNames();
  const roles = getOrInitTeam(db, preset);
  saveNames(db);
  jsonOut({ ok: true, preset, team: roles, file: homeFile() });
}

function validateName(name) {
  if (!name || typeof name !== "string") return "Name must be a string";
  if (name.length < 3 || name.length > 40) return "Name length must be 3..40";
  const bad = ["http://","https://","/","\\","://",".env","$", "~"];
  if (bad.some(b => name.includes(b))) return "Name contains disallowed characters";
  return null;
}

function cmdTeamRename(args) {
  const { preset, role, name } = args;
  if (!preset) return fail("Missing --preset");
  if (!role) return fail("Missing --role");
  if (!name) return fail("Missing --name");
  if (!PRESETS[preset]) return fail(`Unknown preset: ${preset}`);
  const roleKeys = new Set(PRESETS[preset].roles.map(r => r.key));
  if (!roleKeys.has(role)) return fail(`Unknown role '${role}' for preset '${preset}'`);
  const err = validateName(name);
  if (err) return fail(err);

  const db = loadNames();
  getOrInitTeam(db, preset);
  db.presets[preset].roles[role] = name;
  saveNames(db);
  jsonOut({ ok: true, preset, role, name, file: homeFile() });
}

function nowIso() {
  return new Date().toISOString();
}

function mdEscape(s) {
  return String(s ?? "").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function cmdRun(args) {
  const preset = args.preset;
  const task = args.task || "";
  if (!preset) return fail("Missing --preset");
  if (!task) return fail("Missing --task");
  if (!PRESETS[preset]) return fail(`Unknown preset: ${preset}`);

  const db = loadNames();
  const teamNames = getOrInitTeam(db, preset);
  saveNames(db);

  const started = nowIso();
  const ended = nowIso();
  const runId = `run_${Date.now()}`;

  const team = PRESETS[preset].roles.map(r => {
    const nickname = teamNames[r.key];
    return {
      nickname,
      role: r.archetype,
      objective: r.objective,
      output: "(MVP placeholder) — integrate actual multi-agent reasoning in Pro/Max.",
      artifacts: []
    };
  });

  const oneLine = `Completed preset '${preset}' on task: ${task.slice(0, 80)}${task.length > 80 ? "…" : ""}`;

  const reportMarkdown = `# AOI Squad Report (v0.1)\n- Preset: ${mdEscape(preset)}\n- Run: ${mdEscape(runId)}\n- Time: ${mdEscape(started)} → ${mdEscape(ended)}\n\n## Task\n${mdEscape(task)}\n\n## Team outputs\n${team.map(m => `### ${mdEscape(m.nickname)} (${mdEscape(m.role)})\n- Objective: ${mdEscape(m.objective)}\n- Output: ${mdEscape(m.output)}\n`).join("\n")}\n## Synthesis\n- One-line: ${mdEscape(oneLine)}\n- Decision:\n  - (placeholder)\n- Risks:\n  - (placeholder)\n- Next actions:\n  - [P1] Review and refine outputs (Owner: ${mdEscape(team[0].nickname)})\n- VCP Proof:\n  - (none)\n`;

  const out = {
    ok: true,
    schema_version: SCHEMA_VERSION,
    run: {
      run_id: runId,
      preset,
      started_at: started,
      ended_at: ended,
      limits: {
        max_roles: 3,
        max_turns: 6,
        max_wall_time_sec: 180,
        max_tokens: 8000
      }
    },
    task: {
      title: task.split("\n")[0].slice(0, 120),
      input: task,
      constraints: []
    },
    team,
    synthesis: {
      one_line_summary: oneLine,
      decision: [],
      risks: [],
      next_actions: [
        { action: "Review and refine outputs", owner: team[0].nickname, priority: "P1" }
      ],
      vcp_proof: []
    },
    report_markdown: reportMarkdown,
    meta: {
      notes: ["This is a public-safe MVP skeleton."],
      warnings: []
    }
  };

  jsonOut(out);
}

function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  const sub = argv[1];
  const args = parseArgs(argv.slice(1));

  try {
    if (cmd === "preset" && sub === "list") return cmdPresetList();
    if (cmd === "team" && sub === "show") return cmdTeamShow(args);
    if (cmd === "team" && sub === "rename") return cmdTeamRename(args);
    if (cmd === "run") return cmdRun(parseArgs(argv.slice(1)));

    return fail("Unknown command", {
      usage: [
        "aoi-squad preset list",
        "aoi-squad team show --preset <preset>",
        "aoi-squad team rename --preset <preset> --role <role> --name \"Name\"",
        "aoi-squad run --preset <preset> --task \"...\""
      ]
    });
  } catch (e) {
    return fail(e?.message || String(e));
  }
}

main();
