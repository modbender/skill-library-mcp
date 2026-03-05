import fs from "node:fs";
import path from "node:path";
export function parseReport(reportPath) {
    const fullPath = path.resolve(reportPath);
    if (!fs.existsSync(fullPath)) {
        throw new Error(`Report not found: ${fullPath}`);
    }
    const raw = fs.readFileSync(fullPath, "utf-8");
    const data = JSON.parse(raw);
    if (!data || typeof data !== "object") {
        throw new Error("Invalid report: not an object");
    }
    const r = data;
    return {
        protocol_version: typeof r.protocol_version === "string" ? r.protocol_version : undefined,
        task_id: typeof r.task_id === "string" ? r.task_id : undefined,
        execution: r.execution && typeof r.execution === "object"
            ? {
                status: r.execution.status,
                duration_seconds: r.execution
                    .duration_seconds,
                session_id: r.execution
                    .session_id,
            }
            : undefined,
        cognitive_state: r.cognitive_state && typeof r.cognitive_state === "object"
            ? {
                confidence: r.cognitive_state
                    .confidence,
                certainty_level: r.cognitive_state
                    .certainty_level,
                blockers: r.cognitive_state
                    .blockers,
                assumptions: r.cognitive_state
                    .assumptions,
            }
            : undefined,
        artifacts: r.artifacts && typeof r.artifacts === "object"
            ? {
                files_modified: r.artifacts
                    .files_modified,
                files_created: r.artifacts
                    .files_created,
                files_deleted: r.artifacts
                    .files_deleted,
                test_status: r.artifacts
                    .test_status,
                git_sha: r.artifacts.git_sha,
            }
            : undefined,
    };
}
//# sourceMappingURL=report.js.map