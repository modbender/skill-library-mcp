// fake-evolution.js
"use strict";

/**
 * Returns an object like:
 * { isFake: boolean, score: number, reasons: string[] }
 *
 * score: higher = more likely fake evolution
 */
function detectFakeEvolution({ touchedFiles = [], createdFiles = [], reportText = "" }) {
    const reasons = [];
    let score = 0;

    const text = String(reportText || "").toLowerCase();

    // Heuristic A: Only docs / formatting changes
    const onlyDocs =
        [...touchedFiles, ...createdFiles].length > 0 &&
        [...touchedFiles, ...createdFiles].every(p => /\.(md|txt)$/i.test(p));
    if (onlyDocs) {
        score += 3;
        reasons.push("Only documentation files changed.");
    }

    // Heuristic B: Vague report language
    const vaguePhrases = ["improved", "enhanced", "refined", "polished", "cleaned up", "better", "optimized"];
    const hasVague = vaguePhrases.some(p => text.includes(p)) && !/(measured|ms|latency|error rate|success rate|tokens|throughput|benchmark)/.test(text);
    if (hasVague) {
        score += 2;
        reasons.push("Report uses vague improvement language without metrics.");
    }

    // Heuristic C: Tiny change surface but big claims
    const smallChange = (touchedFiles.length + createdFiles.length) <= 1;
    const bigClaims = /(singularity|massive|major|dramatic|huge)/.test(text);
    if (smallChange && bigClaims) {
        score += 2;
        reasons.push("Big claims with minimal changed artifacts.");
    }

    // Heuristic D: Toolchain churn (rename/move only) — best-effort
    if (/rename|moved|reorganized/.test(text) && !/(fix|bug|error|crash|metric|test)/.test(text)) {
        score += 2;
        reasons.push("Likely structural churn without functional benefit.");
    }

    // Heuristic E: No failure detection in report
    if (!/(success rate|error count|latency|timeout|token|benchmark|monitor)/.test(text)) {
        score += 1;
        reasons.push("No clear success/failure detection language.");
    }

    return {
        isFake: score >= 4,
        score,
        reasons
    };
}

module.exports = { detectFakeEvolution };
