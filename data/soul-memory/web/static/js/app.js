/**
 * Soul Memory Web UI - JavaScript
 * Version 1.0.0
 */

// API Base URL
const API_BASE = '/api';

// State
let state = {
    stats: null,
    tasks: [],
    searchResults: []
};

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🧠 Soul Memory Web UI initialized');
    loadStats();
    refreshTasks();
    updateTimestamp();
    
    // Auto-refresh every 5 seconds for tasks, 30 seconds for stats
    setInterval(() => {
        refreshTasks();
    }, 5000);
    
    setInterval(() => {
        loadStats();
        updateTimestamp();
    }, 30000);
});

// ============ API Calls ============
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============ Stats ============
async function loadStats() {
    try {
        const stats = await fetchAPI('/stats');
        state.stats = stats;
        updateStatsUI(stats);
        updateStatus('ready');
    } catch (error) {
        updateStatus('error');
    }
}

function updateStatus(status, activeTasks = 0) {
    const badge = document.getElementById('system-status');
    const dot = badge.querySelector('.status-dot');
    const text = badge.querySelector('.status-text');
    
    if (status === 'ready' && activeTasks === 0) {
        dot.className = 'status-dot';
        text.textContent = '✅ Ready';
        badge.style.background = '#f6f8fa';
    } else if (status === 'busy' || activeTasks > 0) {
        dot.className = 'status-dot busy';
        text.textContent = `🔄 Busy (${activeTasks} task${activeTasks > 1 ? 's' : ''})`;
        badge.style.background = '#fff3cd';
        badge.style.border = '1px solid #f9a825';
    } else if (status === 'loading') {
        dot.className = 'status-dot';
        text.textContent = '🔄 Loading...';
    } else {
        dot.className = 'status-dot error';
        text.textContent = '❌ Error';
        badge.style.background = '#ffe6e6';
    }
}

function updateStatsUI(stats) {
    // Update stat cards
    document.getElementById('total-segments').textContent = stats.total_segments || 0;
    document.getElementById('total-categories').textContent = stats.categories || 0;
    document.getElementById('version').textContent = stats.version || '-';
    
    // Update priority distribution
    const dist = stats.priority_distribution || { C: 0, I: 0, N: 0 };
    const total = dist.C + dist.I + dist.N;
    
    if (total > 0) {
        document.getElementById('bar-critical').style.width = `${(dist.C / total) * 100}%`;
        document.getElementById('bar-important').style.width = `${(dist.I / total) * 100}%`;
        document.getElementById('bar-normal').style.width = `${(dist.N / total) * 100}%`;
    }
    
    document.getElementById('count-critical').textContent = dist.C;
    document.getElementById('count-important').textContent = dist.I;
    document.getElementById('count-normal').textContent = dist.N;
    
    // Update system status with active tasks
    updateStatus(stats.status, stats.active_tasks || 0);
}

// ============ Search ============
function handleSearchKey(event) {
    if (event.key === 'Enter') {
        doSearch();
    }
}

async function doSearch() {
    const input = document.getElementById('search-input');
    const query = input.value.trim();
    
    if (!query) {
        return;
    }
    
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<p class="placeholder-text">🔍 Searching...</p>';
    
    try {
        const data = await fetchAPI(`/search?q=${encodeURIComponent(query)}&top_k=10`);
        state.searchResults = data.results;
        displaySearchResults(data);
    } catch (error) {
        resultsDiv.innerHTML = '<p class="placeholder-text">❌ Search failed</p>';
    }
}

function displaySearchResults(data) {
    const resultsDiv = document.getElementById('search-results');
    
    if (data.total === 0) {
        resultsDiv.innerHTML = '<p class="placeholder-text">No results found</p>';
        return;
    }
    
    let html = `<p style="margin-bottom: 15px; color: #586069;">Found ${data.total} results for "${data.query}"</p>`;
    
    data.results.forEach((result, index) => {
        const priorityClass = result.priority.toLowerCase();
        html += `
            <div class="result-item ${priorityClass}">
                <div class="score">
                    <strong>Score:</strong> ${result.score} | 
                    <strong>Priority:</strong> [${result.priority}] |
                    <strong>Category:</strong> ${result.category || '-'}
                </div>
                <div class="content">${escapeHtml(result.content)}</div>
                <div class="source">📍 ${result.source}:${result.line_number}</div>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

// ============ Tasks ============
async function refreshTasks() {
    try {
        const data = await fetchAPI('/tasks');
        state.tasks = data.tasks;
        displayTasks(data.tasks);
    } catch (error) {
        console.error('Failed to load tasks:', error);
    }
}

function displayTasks(tasks) {
    const tasksDiv = document.getElementById('tasks-list');
    
    if (tasks.length === 0) {
        tasksDiv.innerHTML = '<p class="placeholder-text">No active tasks</p>';
        return;
    }
    
    let html = '';
    tasks.forEach(task => {
        const statusIcon = {
            'pending': '⏳',
            'doing': '🔄',
            'done': '✅',
            'error': '❌'
        }[task.status] || '❓';
        
        html += `
            <div class="task-item ${task.status}">
                <div class="task-title">${statusIcon} ${escapeHtml(task.title)}</div>
                <div class="task-status">${task.message || task.status}</div>
                ${task.status === 'doing' ? `
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress}%"></div>
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    tasksDiv.innerHTML = html;
}

// ============ Actions ============
async function rebuildIndex() {
    if (!confirm('Are you sure you want to rebuild the index?')) {
        return;
    }
    
    try {
        const result = await fetchAPI('/index/rebuild', { method: 'POST' });
        alert(`✅ Index rebuild started\nTask ID: ${result.task_id}`);
        setTimeout(refreshTasks, 1000);
    } catch (error) {
        alert('❌ Failed to start index rebuild');
    }
}

// ============ Utilities ============
function updateTimestamp() {
    const now = new Date();
    document.getElementById('timestamp').textContent = now.toLocaleString('zh-TW');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
