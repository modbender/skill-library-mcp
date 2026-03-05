// Patch an OpenClaw config JSON to include outsideclaw-installed skill path.
// Safe behavior:
// - Creates a .bak backup next to the config.
// - Only adds skill if not present.
// Usage:
//   node patch_openclaw_config.js --config /path/to/config.json

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

function parseArgs(argv) {
  const flags = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const k = a.slice(2);
      const n = argv[i + 1];
      if (n != null && !n.startsWith("--")) {
        flags[k] = n;
        i++;
      } else {
        flags[k] = true;
      }
    }
  }
  return flags;
}

const flags = parseArgs(process.argv);
const configPath = flags.config;
if (!configPath) {
  console.error("Usage: node patch_openclaw_config.js --config /path/to/config.json");
  process.exit(1);
}

const OUTSIDECLAW_HOME = process.env.OUTSIDECLAW_HOME || path.join(os.homedir(), ".outsideclaw");
const OUTSIDECLAW_APP_DIR = process.env.OUTSIDECLAW_APP_DIR || path.join(OUTSIDECLAW_HOME, "app", "outsideclaw");
const skillPath = path.join(OUTSIDECLAW_APP_DIR, "skills", "trail-nav-telegram");

if (!fs.existsSync(skillPath)) {
  console.error("E:SKILL_PATH_NOT_FOUND", skillPath);
  process.exit(2);
}

const raw = fs.readFileSync(configPath, "utf8");
let cfg;
try {
  cfg = JSON.parse(raw);
} catch (e) {
  console.error("E:BAD_JSON");
  process.exit(3);
}

// OpenClaw config schema (current): skills is an object.
// We patch by adding the outsideclaw skill directory to skills.load.extraDirs
// and enabling the skill under skills.entries.
const extraDir = path.join(OUTSIDECLAW_APP_DIR, "skills");

// Detect whether this patch was already applied.
let hadExtraDir = false;
let hadEnabled = false;

if (Array.isArray(cfg.skills)) {
  // Legacy schema: skills was an array of {name,path}.
  hadEnabled = cfg.skills.some((s) => s && (s.name === "trail-nav-telegram" || s.path === skillPath));
} else if (cfg.skills && typeof cfg.skills === "object") {
  const ed = cfg.skills?.load?.extraDirs;
  hadExtraDir = Array.isArray(ed) && ed.includes(extraDir);
  const e = cfg.skills?.entries?.["trail-nav-telegram"];
  hadEnabled = !!(e && typeof e === "object" && e.enabled);
}

// Migrate legacy schema where skills was an array of {name,path}.
if (Array.isArray(cfg.skills)) {
  const legacy = cfg.skills;
  cfg.skills = { load: { extraDirs: [], watch: true, watchDebounceMs: 250 }, entries: {} };
  for (const s of legacy) {
    if (!s || (!s.name && !s.path)) continue;
    const name = s.name || "unknown";
    cfg.skills.entries[name] = { enabled: true };
    if (s.path) {
      // Best-effort: also add the parent dir of the skill path as an extraDir.
      cfg.skills.load.extraDirs.push(path.dirname(s.path));
    }
  }
}

cfg.skills = cfg.skills && typeof cfg.skills === "object" ? cfg.skills : {};
cfg.skills.load = cfg.skills.load && typeof cfg.skills.load === "object" ? cfg.skills.load : {};
cfg.skills.load.extraDirs = Array.isArray(cfg.skills.load.extraDirs) ? cfg.skills.load.extraDirs : [];

if (!cfg.skills.load.extraDirs.includes(extraDir)) {
  cfg.skills.load.extraDirs.push(extraDir);
}

cfg.skills.entries = cfg.skills.entries && typeof cfg.skills.entries === "object" ? cfg.skills.entries : {};
const prev = cfg.skills.entries["trail-nav-telegram"];
cfg.skills.entries["trail-nav-telegram"] = {
  ...(prev && typeof prev === "object" ? prev : {}),
  enabled: true,
};

const added = !(hadExtraDir && hadEnabled);

const bak = configPath + ".bak";
fs.copyFileSync(configPath, bak);
fs.writeFileSync(configPath, JSON.stringify(cfg, null, 2), "utf8");

process.stdout.write(
  JSON.stringify(
    {
      ok: true,
      configPath,
      backupPath: bak,
      added,
      skill: { name: "trail-nav-telegram", path: skillPath },
    },
    null,
    2
  ) + "\n"
);
