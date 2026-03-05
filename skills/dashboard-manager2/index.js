/**
 * SKILL: Dashboard Manager (Executive V4)
 * Gère les Notes, le Kanban et le Knowledge Hub (Documents).
 */
const API_URL = 'http://localhost:8009'; // Ton serveur Python

// --- HELPERS API ---
async function apiPost(endpoint, body = {}) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return response.ok ? await response.json() : null;
    } catch (e) {
        console.error(`❌ Erreur API [${endpoint}]:`, e.message);
        return null;
    }
}

async function apiGet(endpoint) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        return response.ok ? await response.json() : null;
    } catch (e) {
        console.error(`❌ Erreur API [${endpoint}]:`, e.message);
        return null;
    }
}

// --- FONCTIONS PUBLIQUES ---

// 1. Gestion du Système (Logs & Statut)
async function addLog(action) {
    await apiPost('/api/logs', { action });
    return true;
}

async function updateSystemStatus(state = 'idle', modelName = null) {
    await apiPost('/api/system', { system_status: { state, current_model: modelName } });
    return true;
}

// 2. Gestion du Kanban (Tâches)
async function updateTask(taskId, updates) {
    // Si taskId est null, c'est une création
    if (taskId) {
        await apiPost('/api/system', { update_task: { id: taskId, ...updates } });
    } else {
        await apiPost('/api/system', { new_task: updates });
    }
    return true;
}

// 3. Gestion des Notes (Commandes)
async function getPendingNotes() {
    const result = await apiGet('/api/notes/pending');
    return result ? result.notes : [];
}

async function processNote(noteId) {
    await apiPost(`/api/notes/${noteId}/process`);
    return true;
}

// 4. Knowledge Hub (DOCUMENTS) - NOUVEAU V4
async function createDocument(title, content, type = 'report', tags = []) {
    console.log(`📄 Création du document: ${title}`);
    const result = await apiPost('/api/documents', { title, content, type, tags });
    return result ? result.id : null;
}

async function getDocuments() {
    return await apiGet('/api/documents') || [];
}

async function deleteDocument(docId) {
    await fetch(`${API_URL}/api/documents/${docId}`, { method: 'DELETE' });
    return true;
}

// 5. Automatisation (Règles)
async function addRule(rule) {
    // rule = { cron: "HH:MM", prompt: "..." }
    const result = await apiPost('/api/rules', rule);
    return result ? result.id : null;
}

async function getRules() {
    return await apiGet('/api/rules') || [];
}

async function updateRuleLastRun(ruleId) {
    await apiPost(`/api/rules/${ruleId}/run`, {});
    return true;
}

// --- EXPORT POUR OPENCLAW ---
module.exports = {
    functions: {
        addLog,
        updateSystemStatus,
        updateTask,
        getPendingNotes,
        processNote,
        createDocument, // V4
        getDocuments,   // V4
        deleteDocument, // V4
        addRule,
        getRules,
        updateRuleLastRun
    }
};