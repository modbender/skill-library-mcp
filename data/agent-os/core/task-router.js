/**
 * TaskRouter: Decompose goals into executable tasks
 * Matches tasks to agents based on capability fit
 */
class TaskRouter {
  constructor(agents = []) {
    this.agents = agents; // Array of Agent instances
    this.taskTemplates = {
      research: [
        { step: 1, name: 'Define research scope', estimatedMinutes: 15 },
        { step: 2, name: 'Search primary sources', estimatedMinutes: 30 },
        { step: 3, name: 'Compile findings', estimatedMinutes: 20 },
        { step: 4, name: 'Synthesize insights', estimatedMinutes: 15 },
      ],
      design: [
        { step: 1, name: 'Analyze requirements', estimatedMinutes: 20 },
        { step: 2, name: 'Sketch solutions', estimatedMinutes: 30 },
        { step: 3, name: 'Create mockups', estimatedMinutes: 45 },
        { step: 4, name: 'Get feedback', estimatedMinutes: 15 },
      ],
      development: [
        { step: 1, name: 'Setup project', estimatedMinutes: 15 },
        { step: 2, name: 'Implement features', estimatedMinutes: 120 },
        { step: 3, name: 'Test code', estimatedMinutes: 45 },
        { step: 4, name: 'Deploy', estimatedMinutes: 15 },
      ],
      planning: [
        { step: 1, name: 'Break down goal', estimatedMinutes: 20 },
        { step: 2, name: 'Identify risks', estimatedMinutes: 15 },
        { step: 3, name: 'Create timeline', estimatedMinutes: 20 },
        { step: 4, name: 'Assign resources', estimatedMinutes: 10 },
      ],
    };
  }

  /**
   * Decompose a goal into a task sequence
   * @param {string} goal - High-level goal
   * @param {array} taskTypes - ['research', 'design', 'development'] etc
   * @returns {array} Array of tasks with agent assignments
   */
  decompose(goal, taskTypes = []) {
    const tasks = [];
    let taskId = 1;

    for (const taskType of taskTypes) {
      const template = this.taskTemplates[taskType] || [];
      const assignedAgent = this.matchAgent(taskType);

      for (const step of template) {
        tasks.push({
          id: taskId++,
          type: taskType,
          name: step.name,
          description: `${taskType}: ${step.name}`,
          estimatedMinutes: step.estimatedMinutes,
          assignedAgent: assignedAgent ? assignedAgent.id : null,
          assignedAgentName: assignedAgent ? assignedAgent.name : 'Unassigned',
          status: 'pending', // pending, in-progress, blocked, complete
          output: null,
          blockers: [],
          dependsOn: taskId > 1 ? taskId - 2 : null, // Sequential dependency
        });
      }
    }

    return tasks;
  }

  /**
   * Match task type to best available agent
   */
  matchAgent(taskType) {
    const match = this.agents.find((a) => a.capabilities.includes(taskType));
    return match || this.agents[0]; // Fallback to first agent
  }

  /**
   * Get tasks for a specific agent
   */
  getTasksForAgent(agentId, tasks) {
    return tasks.filter((t) => t.assignedAgent === agentId);
  }

  /**
   * Check if task dependencies are met
   */
  canExecuteTask(task, allTasks) {
    if (!task.dependsOn) return true;
    const dependency = allTasks.find((t) => t.id === task.dependsOn);
    return dependency && dependency.status === 'complete';
  }

  /**
   * Get next executable task
   */
  getNextTask(tasks) {
    for (const task of tasks) {
      if (task.status === 'pending' && this.canExecuteTask(task, tasks)) {
        return task;
      }
    }
    return null;
  }

  /**
   * Mark task complete
   */
  completeTask(taskId, tasks, output) {
    const task = tasks.find((t) => t.id === taskId);
    if (task) {
      task.status = 'complete';
      task.output = output;
    }
    return task;
  }

  /**
   * Get project status
   */
  getProjectStatus(tasks) {
    const total = tasks.length;
    const complete = tasks.filter((t) => t.status === 'complete').length;
    const inProgress = tasks.filter((t) => t.status === 'in-progress').length;
    const blocked = tasks.filter((t) => t.status === 'blocked').length;

    return {
      total,
      complete,
      inProgress,
      blocked,
      pending: total - complete - inProgress - blocked,
      progress: Math.round((complete / total) * 100),
    };
  }
}

module.exports = TaskRouter;
