// validate-cycle.js
"use strict";

const fs = require("fs");

function fail(errors) {
    for (const e of errors) console.error("❌", e);
    process.exit(1);
}

function ok(msg) {
    console.log("✅", msg);
}

function hasAnyText(x) {
    return typeof x === "string" && x.trim().length > 0;
}

/**
 * Expected cycle JSON shape (minimal):
 * {
 *   "cycleId": "0001",
 *   "mode": "repair|optimize|expand|innovation|personalization",
 *   "directives": ["optimize","harden",...],
 *   "status": "SUCCESS|BLOCKED|REVERTED",
 *   "report": {
 *     "whatChanged": "...",
 *     "whyItMatters": "...",
 *     "successFailureDetection": "..."
 *   },
 *   "artifacts": {
 *     "touchedFiles": ["path1", ...],
 *     "createdFiles": ["path2", ...],
 *     "forbiddenArtifactsPresent": ["safe_publish.js"] // optional
 *   },
 *   "flags": ["--review","--loop"],
 *   "loop": { "localRerunPlanned": true } // if flags include loop/funky-fund-flamingo
 * }
 */

function validateCycle(cycle) {
    const errors = [];

    // 1) Must declare mode
    const validModes = new Set(["repair", "optimize", "expand", "innovation", "personalization"]);
    if (!validModes.has(cycle.mode)) errors.push(`Invalid or missing mode: ${cycle.mode}`);

    // 2) Must evolve (no-op forbidden) unless BLOCKED with blocker + next action
    const touched = cycle?.artifacts?.touchedFiles || [];
    const created = cycle?.artifacts?.createdFiles || [];
    const changedSomething = touched.length > 0 || created.length > 0;

    if (cycle.status === "SUCCESS") {
        if (!changedSomething) errors.push("SUCCESS cycle must change at least one file (touchedFiles/createdFiles empty).");
    } else if (cycle.status === "BLOCKED") {
        if (!hasAnyText(cycle?.report?.whyItMatters) && !hasAnyText(cycle?.blocker)) {
            errors.push("BLOCKED cycle must explain the blocker (cycle.blocker or report.whyItMatters).");
        }
        if (!hasAnyText(cycle?.nextAction)) {
            errors.push("BLOCKED cycle must propose nextAction.");
        }
    }

    // 3) Report requirements
    if (!cycle.report) errors.push("Missing report object.");
    else {
        if (!hasAnyText(cycle.report.whatChanged)) errors.push("Report missing whatChanged.");
        if (!hasAnyText(cycle.report.whyItMatters)) errors.push("Report missing whyItMatters.");
        if (!hasAnyText(cycle.report.successFailureDetection)) errors.push("Report missing successFailureDetection.");
    }

    // 4) Forbidden artifact: safe_publish.js
    const forbidden = (cycle?.artifacts?.forbiddenArtifactsPresent || [])
        .concat([...touched, ...created].filter(p => /safe_publish\.js$/i.test(p)));
    if (forbidden.length > 0) errors.push(`Forbidden artifact(s) present: ${[...new Set(forbidden)].join(", ")}`);

    // 5) If loop flags present, must plan local rerun only
    const flags = new Set(cycle.flags || []);
    const wantsLoop = flags.has("--loop") || flags.has("--funky-fund-flamingo");
    if (wantsLoop) {
        if (!cycle.loop || cycle.loop.localRerunPlanned !== true) {
            errors.push("Loop mode requires loop.localRerunPlanned === true (external tool spawning is forbidden).");
        }
    }

    // 6) Must include at least one directive category (optimize/harden/automate/analyze)
    const allowedDirectives = new Set(["optimize", "harden", "automate", "analyze"]);
    const directives = cycle.directives || [];
    if (!directives.some(d => allowedDirectives.has(d))) {
        errors.push("Cycle must include at least one directive: optimize|harden|automate|analyze.");
    }

    // 7) Optional: review gate enforcement signal
    if (flags.has("--review") && cycle.status === "SUCCESS") {
        if (cycle.reviewPauseAcknowledged !== true) {
            errors.push("Review mode requires reviewPauseAcknowledged === true before significant edits.");
        }
    }

    if (errors.length) fail(errors);
    ok(`Cycle ${cycle.cycleId || "(unknown)"} passed compliance.`);
}

function main() {
    const file = process.argv[2];
    if (!file) fail(["Usage: node validate-cycle.js path/to/cycle.json"]);

    let cycle;
    try {
        cycle = JSON.parse(fs.readFileSync(file, "utf8"));
    } catch (e) {
        fail([`Failed to read/parse JSON: ${e.message}`]);
    }

    validateCycle(cycle);
}

if (require.main === module) main();
