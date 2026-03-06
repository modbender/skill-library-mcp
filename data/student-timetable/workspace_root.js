const fs = require('fs');
const path = require('path');

function fileExists(p) {
  try {
    fs.accessSync(p, fs.constants.F_OK);
    return true;
  } catch (_) {
    return false;
  }
}

function resolveWorkspaceRoot() {
  const envRoot = process.env.OPENCLAW_WORKSPACE;
  if (envRoot && fileExists(envRoot)) {
    return path.resolve(envRoot);
  }

  let cur = process.cwd();
  while (true) {
    const skillsDir = path.join(cur, 'skills');
    const schedulesDir = path.join(cur, 'schedules');
    if (fileExists(skillsDir) && fileExists(schedulesDir)) {
      return cur;
    }

    const parent = path.dirname(cur);
    if (parent === cur) {
      break;
    }
    cur = parent;
  }

  return process.cwd();
}

module.exports = { resolveWorkspaceRoot };
