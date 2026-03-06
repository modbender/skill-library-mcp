/**
 * Agent OS Dashboard
 * Displays real-time project and agent status
 */

// Mock data loader (in production, this would read from actual project files)
function loadProjectStatus() {
  // Check if we have a project in localStorage
  const savedStatus = localStorage.getItem('agent-os-status');
  if (savedStatus) {
    return JSON.parse(savedStatus);
  }

  // Default mock status
  return {
    projectId: 'clawdgym-feature-2026-02-24',
    goal: 'Build AI-powered trial member follow-up system for ClawdGym',
    status: 'complete',
    progress: 100,
    taskStats: {
      complete: 12,
      inProgress: 0,
      blocked: 0,
      pending: 0,
      total: 12,
    },
    agents: [
      {
        id: 'agent-research',
        name: '🔍 Research',
        capabilities: ['research', 'planning'],
        status: 'done',
        currentTask: null,
        progress: 100,
        tasksCompleted: 4,
        lastActiveAt: '2026-02-24T16:32:51.846Z',
      },
      {
        id: 'agent-design',
        name: '🎨 Design',
        capabilities: ['design', 'planning'],
        status: 'done',
        currentTask: null,
        progress: 100,
        tasksCompleted: 4,
        lastActiveAt: '2026-02-24T16:33:01.910Z',
      },
      {
        id: 'agent-dev',
        name: '💻 Development',
        capabilities: ['development', 'research'],
        status: 'done',
        currentTask: null,
        progress: 100,
        tasksCompleted: 4,
        lastActiveAt: '2026-02-24T16:33:11.971Z',
      },
    ],
    tasks: [
      { id: 1, name: 'Break down goal', type: 'planning', status: 'complete', agent: 'agent-research' },
      { id: 2, name: 'Identify risks', type: 'planning', status: 'complete', agent: 'agent-research' },
      { id: 3, name: 'Create timeline', type: 'planning', status: 'complete', agent: 'agent-research' },
      { id: 4, name: 'Assign resources', type: 'planning', status: 'complete', agent: 'agent-research' },
      { id: 5, name: 'Analyze requirements', type: 'design', status: 'complete', agent: 'agent-design' },
      { id: 6, name: 'Sketch solutions', type: 'design', status: 'complete', agent: 'agent-design' },
      { id: 7, name: 'Create mockups', type: 'design', status: 'complete', agent: 'agent-design' },
      { id: 8, name: 'Get feedback', type: 'design', status: 'complete', agent: 'agent-design' },
      { id: 9, name: 'Setup project', type: 'development', status: 'complete', agent: 'agent-dev' },
      { id: 10, name: 'Implement features', type: 'development', status: 'complete', agent: 'agent-dev' },
      { id: 11, name: 'Test code', type: 'development', status: 'complete', agent: 'agent-dev' },
      { id: 12, name: 'Deploy', type: 'development', status: 'complete', agent: 'agent-dev' },
    ],
    startedAt: '2026-02-24T16:32:00.000Z',
    completedAt: '2026-02-24T16:33:15.000Z',
  };
}

// Update dashboard with status
function updateDashboard(status) {
  // Project header
  document.getElementById('projectGoal').textContent = status.goal || 'No project loaded';
  document.getElementById('projectStatus').textContent = status.status?.toUpperCase() || '—';
  document.getElementById('projectProgress').textContent = `${status.progress || 0}%`;
  document.getElementById('projectProgressBar').style.width = `${status.progress || 0}%`;

  // Status badge
  const badge = document.getElementById('projectStatusBadge');
  badge.textContent = status.status || 'idle';
  badge.className = `status-badge ${status.status || 'idle'}`;

  // Task stats
  const stats = status.taskStats || {};
  document.getElementById('taskComplete').textContent = stats.complete || 0;
  document.getElementById('taskInProgress').textContent = stats.inProgress || 0;
  document.getElementById('taskBlocked').textContent = stats.blocked || 0;
  document.getElementById('taskPending').textContent = stats.pending || 0;

  // Render agents
  renderAgents(status.agents || []);

  // Render tasks
  renderTasks(status.tasks || []);

  // System info
  document.getElementById('projectId').textContent = status.projectId || '—';
  document.getElementById('startedAt').textContent = formatTime(status.startedAt) || '—';
  document.getElementById('completedAt').textContent = formatTime(status.completedAt) || '—';

  // Last update
  document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
}

// Render agent cards
function renderAgents(agents) {
  const grid = document.getElementById('agentsGrid');
  grid.innerHTML = '';

  agents.forEach((agent) => {
    const card = document.createElement('div');
    card.className = `card agent-card ${agent.status}`;

    const capabilities = agent.capabilities.map((c) => `<span class="agent-capability">${c}</span>`).join('');
    const currentTask = agent.currentTask ? `<div class="agent-current-task">📝 ${agent.currentTask}</div>` : '';

    card.innerHTML = `
      <div class="agent-name">${agent.name}</div>
      <span class="agent-status ${agent.status}">${agent.status}</span>
      <div>${capabilities}</div>
      <div class="agent-progress" style="margin-top: 1rem;">
        <div style="font-size: 0.8rem; margin-bottom: 0.5rem;">Progress: ${agent.progress || 0}%</div>
        <div class="progress-bar-container" style="height: 6px;">
          <div class="progress-bar" style="width: ${agent.progress || 0}%"></div>
        </div>
      </div>
      ${currentTask}
      <div class="agent-meta">
        <span>Tasks: ${agent.tasksCompleted || 0}</span>
        <span>Last: ${formatTime(agent.lastActiveAt)}</span>
      </div>
    `;

    grid.appendChild(card);
  });
}

// Render task list
function renderTasks(tasks) {
  const list = document.getElementById('taskList');
  list.innerHTML = '';

  tasks.forEach((task) => {
    const item = document.createElement('div');
    item.className = 'task-item';

    const statusIcon = {
      pending: '⏸️',
      'in-progress': '⏳',
      complete: '✅',
      blocked: '🚫',
    }[task.status] || '—';

    const agentName = task.agent ? task.agent.replace('agent-', '').toUpperCase() : 'UNASSIGNED';

    item.innerHTML = `
      <div class="task-status-icon">${statusIcon}</div>
      <div class="task-info">
        <div class="task-name">${task.name}</div>
        <div class="task-agent">${agentName}</div>
      </div>
      <span class="task-type">${task.type}</span>
      <span class="task-status ${task.status.replace('-', '')}">${task.status}</span>
    `;

    list.appendChild(item);
  });
}

// Format time for display
function formatTime(isoString) {
  if (!isoString) return '—';
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Auto-refresh
function startAutoRefresh() {
  // Initial load
  const status = loadProjectStatus();
  updateDashboard(status);

  // Refresh every 2 seconds
  setInterval(() => {
    const updatedStatus = loadProjectStatus();
    updateDashboard(updatedStatus);
  }, 2000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  startAutoRefresh();
});
