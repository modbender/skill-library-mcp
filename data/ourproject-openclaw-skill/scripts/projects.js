/**
 * Projects - List all projects
 * Usage: node scripts/projects.js
 */

const { makeRequest } = require('./api');

async function listProjects() {
    try {
        const r = await makeRequest('GET', '/projects');
        const projects = Array.isArray(r.data) ? r.data : (r.data?.projects || []);

        if (projects.length === 0) {
            console.log('📁 No projects found.');
            return;
        }

        console.log(`📁 *Projects* (${projects.length})\n`);

        const statusIcon = { active: '🟢', planning: '🔵', paused: '🟡', completed: '✅', archived: '📦' };

        projects.forEach(p => {
            const icon = statusIcon[p.status] || '⚪';
            console.log(`${icon} *${p.name || p.title}*`);
            if (p.description) console.log(`   ${p.description.substring(0, 80)}${p.description.length > 80 ? '...' : ''}`);
            console.log(`   Status: ${p.status || 'unknown'} | Tasks: ${p.taskCount || p.task_count || '?'}`);
            console.log('');
        });
    } catch (err) {
        console.error('❌', err.message);
    }
}

listProjects();
