/**
 * @module protocol
 * Handoff protocol: generate task .md content for interchange.
 */

/**
 * Generate frontmatter and content for a task .md file.
 * @param {object} task - Task row from DB
 * @param {object} [result] - Result row if completed
 * @returns {{ frontmatter: object, content: string }}
 */
export function taskToMd(task, result) {
  const frontmatter = {
    skill: 'orchestration',
    type: 'detail',
    layer: 'state',
    task_id: task.id,
    status: task.status,
    assigned_to: task.assigned_agent || null,
    created_by: task.created_by,
    priority: task.priority,
    timeout_minutes: task.timeout_minutes,
    depends_on: Array.isArray(task.depends_on) ? task.depends_on : JSON.parse(task.depends_on || '[]'),
    version: 1,
    generator: 'orchestration@1.0.0',
    tags: ['task'],
  };

  let content = `# Task: ${task.title}\n\n`;
  content += `## Description\n${task.description || 'No description provided.'}\n\n`;
  content += `## Constraints\n- Complete within ${task.timeout_minutes} minutes\n- Priority: ${task.priority}\n\n`;
  content += `## Result\n`;

  if (result) {
    content += `**Status:** Completed\n`;
    if (result.output_path) content += `**Output:** ${result.output_path}\n`;
    if (result.summary) content += `**Summary:** ${result.summary}\n`;
  } else {
    content += `<!-- Filled by assigned agent on completion -->\n`;
  }

  return { frontmatter, content };
}
