import type { TaskInput } from "../types.js";

const DEFAULT_TITLE = "OpenClaw Kimi Worker - Task Instructions";

export function generateAgentsMd(
  task: TaskInput,
  title: string = DEFAULT_TITLE
): string {
  const lines: string[] = [
    `# ${title}`,
    "",
    "Execute the assigned task in this worktree. Report when done.",
    "",
    "## Task",
    task.prompt,
    "",
  ];

  if (task.relevantFiles?.length) {
    lines.push("## Relevant Files", "");
    for (const f of task.relevantFiles) {
      lines.push(`- ${f}`);
    }
    lines.push("");
  }

  if (task.constraints?.length) {
    lines.push("## Constraints", "");
    for (const c of task.constraints) {
      lines.push(`- ${c}`);
    }
    lines.push("");
  }

  if (task.successCriteria?.length) {
    lines.push("## Success Criteria (verify before completing)", "");
    for (const s of task.successCriteria) {
      lines.push(`- [ ] ${s}`);
    }
    lines.push("");
  }

  lines.push("## Working Directory", "", task.worktreePath, "");

  if (task.reportPath) {
    lines.push(
      "## Report (required)",
      "",
      `When complete, write a JSON report to: \`${task.reportPath}\``,
      "",
      "Report must include:",
      "- execution.status: completed | failed | blocked",
      "- artifacts.files_modified, files_created, files_deleted",
      "- artifacts.test_status: passed | failed | skipped",
      "- cognitive_state.blockers: array of blocking issues (if any)",
      ""
    );
  }

  return lines.join("\n");
}
