const fs = require('fs');
const path = require('path');

// --- CONFIGURATION ---
const SKILL_DIR = path.join(__dirname, '..', 'claw-todolist');
const STATE_FILE = path.join(SKILL_DIR, 'task_state.json');
const RULES_FILE = path.join(SKILL_DIR, 'todo-rules-v3.2.md'); 
const DISPLAY_CONFIG_FILE = path.join(SKILL_DIR, 'display_config.json'); 

// --- STATE MANAGEMENT HELPERS ---
function loadState() {
    try {
        const stateData = fs.readFileSync(STATE_FILE, 'utf8');
        const state = JSON.parse(stateData);
        // Ensure nextId is correctly set based on existing tasks
        if (!state.nextId || state.nextId <= Math.max(...state.tasks.map(t => t.id), 0)) {
            state.nextId = (Math.max(...state.tasks.map(t => t.id), 0) || 0) + 1;
        }
        return state;
    } catch (e) {
        // Initial load or file missing
        return {
            tasks: [],
            nextId: 1,
            rules: readRulesContent(), // Load rules content if state is missing
            displayConfig: readDisplayConfig() // Load display config here
        };
    }
}

function saveState(state) {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function readRulesContent() {
    try {
        return fs.readFileSync(RULES_FILE, 'utf8');
    } catch (e) {
        return "Rules file not found or readable.";
    }
}

function readDisplayConfig() {
    try {
        const configData = fs.readFileSync(DISPLAY_CONFIG_FILE, 'utf8');
        return JSON.parse(configData);
    } catch (e) {
        // Default to V3.2 text format if config missing
        return { format: "TEXT_ONLY", includeFields: ["ID", "Prio", "Context", "Text", "Weight", "DUE"], tableEnabled: false };
    }
}

// Helper to format task for display (incorporating ⭐ and DUE)
function formatTaskDisplay(task) {
    const star = task.weight > 0 ? ' ' + '⭐'.repeat(task.weight) : '';
    const dueDate = task.due ? ` DUE=${task.due}` : '';
    const statusPrefix = task.status === 'Done' ? '[x]' : '[ ]';
    
    // Position ⭐ after text, before DUE, as requested
    return `${statusPrefix} [${task.id}] ${task.priority} @${task.context}: ${task.text}${star}${dueDate}`;
}

// --- PARSERS ---

// Parses arguments from command line array into structured object
function parseArgs(args) {
    const result = { priority: null, context: null, text: '', weight: 0, due: null };
    let textBuffer = [];
    let inText = true;

    for (const arg of args) {
        if (arg.startsWith('P') && arg.match(/^P[1-4]$/)) {
            result.priority = arg;
            continue;
        }
        if (arg.startsWith('@') && arg.match(/^@[a-zA-Z0-9]+$/)) {
            result.context = arg.substring(1); // Remove '@'
            continue;
        }
        if (arg.startsWith('DUE=')) {
            result.due = arg.substring(4);
            continue;
        }
        if (arg.match(/^\++$/)) { // Matches one or more '+' signs
            result.weight = arg.length;
            continue;
        }
        
        // If we hit a structured element, stop buffering text for now
        if (arg.startsWith('P') || arg.startsWith('@') || arg.startsWith('DUE=') || arg.match(/^\++$/)) {
             inText = false;
        }

        if (inText) {
            textBuffer.push(arg);
        } else {
            // Append remaining text buffer items if they follow structured arguments
            textBuffer.push(arg);
        }
    }
    
    // Simple text cleanup for ADD: take everything not parsed as a structured argument
    result.text = textBuffer.join(' ').trim();

    return result;
}


// --- COMMAND HANDLERS ---

function handleAdd(args, state) {
    const parsed = parseArgs(args);
    let { priority, context, text, weight, due } = parsed;
    let responseMessage = "";
    
    // 1. VALIDATE REQUIRED FIELDS (Priority)
    if (!priority) {
        return { success: false, message: "Error in 'a' (ADD): Priority (P1-P4) is mandatory. Example: a P1 @work Txt +++" };
    }

    // 2. HANDLE MISSING CONTEXT (Fallback to @general per V3.2 rule)
    if (!context) {
        context = 'general';
        responseMessage += "⚠️ Notice: Context missing. Task defaulted to **@general**.\n";
    }
    
    // 3. VALIDATE WEIGHT (Must be 0-5)
    const validatedWeight = Math.min(weight, 5);

    // 4. CREATE TASK
    const newTask = {
        id: state.nextId++,
        priority: priority,
        context: context,
        text: text,
        weight: validatedWeight,
        due: due || null,
        status: 'Pending',
        createdDate: new Date().toISOString().split('T')[0] 
    };

    state.tasks.push(newTask);
    saveState(state);

    responseMessage += `Task ADDED (ID: ${newTask.id}) ${priority} @${context}${validatedWeight > 0 ? ' ⭐'.repeat(validatedWeight) : ''}${newTask.due ? ' DUE=' + newTask.due : ''}.\nText: "${text}"`;
    
    return { success: true, message: responseMessage, newState: state };
}

function handleDone(args) {
    const id = parseInt(args[0]);
    if (isNaN(id)) {
        return { success: false, message: "Error in 'x' (DONE): ID must be a number. Example: x 1" };
    }
    
    const state = loadState();
    const taskIndex = state.tasks.findIndex(t => t.id === id && t.status === 'Pending');

    if (taskIndex === -1) {
        return { success: false, message: `Error in 'x' (DONE): Task ID ${id} not found or already complete.` };
    }

    state.tasks[taskIndex].status = 'Done';
    state.tasks[taskIndex].completedDate = new Date().toISOString().split('T')[0];
    saveState(state);
    
    return { success: true, message: `Task ID ${id} marked as DONE.`, newState: state };
}

function handleEdit(args) {
    const id = parseInt(args[0]);
    if (isNaN(id) || args.length < 2) {
        return { success: false, message: "Error in 'e' (EDIT): Requires ID and at least one change instruction. Example: e 5 PRIO=P2" };
    }

    const state = loadState();
    const taskIndex = state.tasks.findIndex(t => t.id === id);

    if (taskIndex === -1) {
        return { success: false, message: `Error in 'e' (EDIT): Task ID ${id} not found.` };
    }
    
    let task = state.tasks[taskIndex];
    const changes = {};
    
    for (let i = 1; i < args.length; i++) {
        const part = args[i];
        if (part.startsWith('PRIO=')) {
            const newPrio = part.substring(5).toUpperCase();
            if (!newPrio.match(/^P[1-4]$/)) {
                 return { success: false, message: `Error in 'e': Invalid Priority format '${newPrio}'. Must be P1, P2, P3, or P4.` };
            }
            changes.priority = newPrio;
        } else if (part.startsWith('CONTEXT=')) {
            changes.context = part.substring(8).replace(/^@/, ''); // Strip @ if present
        } else if (part.startsWith('TEXT=')) {
            changes.text = part.substring(5).replace(/^\[|\]$/g, ''); // Simple text cleaning
        } else if (part.startsWith('WEIGHT=')) {
            const weightStr = part.substring(7).toUpperCase();
            if (weightStr === 'NONE') {
                changes.weight = 0;
            } else if (weightStr.match(/^\++$/) && weightStr.length <= 5) {
                changes.weight = weightStr.length;
            } else {
                return { success: false, message: `Error in 'e': Invalid WEIGHT format. Use + to +++++ or NONE.` };
            }
        } else if (part.startsWith('DUE=')) {
            changes.due = part.substring(4);
        }
    }

    // Apply changes
    state.tasks[taskIndex] = { ...task, ...changes };
    saveState(state);
    
    return { success: true, message: `Task ID ${id} updated successfully.`, newState: state };
}

function handleShow(args) {
    const state = loadState();
    let filteredTasks = state.tasks.filter(t => t.status === 'Pending');
    let output = [];
    let filterApplied = false;

    // Helper to format the entire list or a filtered subset (TEXT FORMAT)
    const formatList = (tasks) => {
        if (tasks.length === 0) return "No tasks found matching this filter/criteria.";
        // Sort by Priority (P1 > P2 > P3 > P4), then Weight, then ID, as per default list sorting
        tasks.sort((a, b) => {
            const prioOrder = { 'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4 };
            const pA = prioOrder[a.priority] || 5;
            const pB = prioOrder[b.priority] || 5;
            
            if (pA !== pB) return pA - pB;
            if (a.weight !== b.weight) return b.weight - a.weight; // Higher weight first
            return a.id - b.id;
        });

        return tasks.map(task => {
            const star = task.weight > 0 ? ' ' + '⭐'.repeat(task.weight) : '';
            const dueDate = task.due ? ` DUE=${task.due}` : '';
            const statusPrefix = task.status === 'Done' ? '[x]' : '[ ]';
            // Position ⭐ after text, before DUE, as requested
            return `${statusPrefix} [${task.id}] ${task.priority} @${task.context}: ${task.text}${star}${dueDate}`;
        }).join('\\n');
    };

    // --- APPLY DISPLAY CONFIGURATION ---
    const displayConfig = state.displayConfig || { format: "TEXT_ONLY", tableEnabled: false };
    
    if (displayConfig.format === "TEXT_ONLY" && displayConfig.tableEnabled === false) {
        // Apply separator logic here based on new request
        let resultList = [];
        let currentGroup = [];
        let currentGroupPrio = null;

        // Temporarily sort tasks by priority for grouping
        let sortedTasks = [...filteredTasks].sort((a, b) => {
            const prioOrder = { 'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4 };
            const pA = prioOrder[a.priority] || 5;
            const pB = prioOrder[b.priority] || 5;
            return pA - pB;
        });
        
        for (const task of sortedTasks) {
            if (task.priority !== currentGroupPrio) {
                if (currentGroup.length > 0) {
                    // Add Separator/Header for previous group
                    let header = `\n--- [ ${currentGroupPrio} ] ---`;
                    if (currentGroupPrio === 'P1') header += " (Urgent & Important - FOCUS)";
                    if (currentGroupPrio === 'P2') header += " (Important & Not Urgent - Schedule)";
                    if (currentGroupPrio === 'P3') header += " (Urgent & Not Important - Delegate/Quick)";
                    if (currentGroupPrio === 'P4') header += " (Not Important & Not Urgent - Defer)";
                    resultList.push(header);
                    resultList.push(formatList(currentGroup));
                }
                // Start new group
                currentGroup = [];
                currentGroupPrio = task.priority;
            }
            currentGroup.push(task);
        }
        
        // Add last group
        if (currentGroup.length > 0) {
            let header = `\n--- [ ${currentGroupPrio} ] ---`;
            if (currentGroupPrio === 'P1') header += " (Urgent & Important - FOCUS)";
            if (currentGroupPrio === 'P2') header += " (Important & Not Urgent - Schedule)";
            if (currentGroupPrio === 'P3') header += " (Urgent & Not Important - Delegate/Quick)";
            if (currentGroupPrio === 'P4') header += " (Not Important & Not Urgent - Defer)";
            resultList.push(header);
            resultList.push(formatList(currentGroup));
        }
        
        output = resultList;
        filterApplied = true;
    }
    // --- FILTER LOGIC REMAINS THE SAME ---
    
    // Default view: Full list display (Only runs if grouping logic above didn't run, which it will for ls)
    if (args.length === 0 || (args.length === 1 && args[0].toUpperCase() === 'FULL')) {
        if(output.length === 0) { 
             output.push("📋 **FULL ACTIVE TODO LIST** (P1 > P2 > P3 > P4)");
             output.push(formatList(filteredTasks));
        }
        filterApplied = true;
    }
    
    if (args[0] && args[0].startsWith('@')) {
        const context = args[0].substring(1);
        filteredTasks = filteredTasks.filter(t => t.context.toLowerCase() === context.toLowerCase());
        output.push(`🏷️ **FILTERED LIST: @${context.toUpperCase()}**`);
        output.push(formatList(filteredTasks));
        filterApplied = true;
    }

    if (args[0] && args[0].startsWith('DUE')) {
        const timeFrame = args[0].substring(4).toUpperCase();
        const today = new Date();
        let limitDate = new Date();
        
        if (timeFrame === '24H' || timeFrame === '48H' || timeFrame === 'WEEK') {
            filterApplied = true;
            output.push(`⏳ **FILTERED LIST: DUE in ${timeFrame}**`);

            if (timeFrame === '24H') limitDate.setDate(today.getDate() + 1);
            if (timeFrame === '48H') limitDate.setDate(today.getDate() + 2);
            if (timeFrame === 'WEEK') limitDate.setDate(today.getDate() + 7);
            
            const limitDateStr = limitDate.toISOString().split('T')[0];

            filteredTasks = filteredTasks.filter(t => 
                t.due && t.due <= limitDateStr && t.due >= today.toISOString().split('T')[0]
            );
            output.push(formatList(filteredTasks));
        }
    }

    if (args[0] && args[0].startsWith('CRITICAL')) {
        filterApplied = true;
        const minWeight = args[0].match(/^\++$/) ? args[0].length : 0;
        if (minWeight > 0) {
            output.push(`⭐ **FILTERED LIST: WEIGHT >= ${minWeight}**`);
            filteredTasks = filteredTasks.filter(t => t.weight >= minWeight);
            output.push(formatList(filteredTasks));
        }
    }

    if (!filterApplied && args.length > 0) {
        output.push(`Error: Unknown filter command provided: ${args[0]}`);
    }
    
    // If filterApplied is false (meaning args.length=0 and grouping didn't run), show full list
    if (!filterApplied && args.length === 0) {
        if (output.length === 0) { 
             output.push("📋 **FULL ACTIVE TODO LIST** (P1 > P2 > P3 > P4)");
             output.push(formatList(filteredTasks));
        }
    }

    return output.join('\\n');
}

// --- COMMAND ROUTER ---
module.exports = {
    handleCommand: (command, args) => {
        // Load rules content on every command to ensure the latest rules (V3.2) are used
        
        let state = loadState();
        let result = { message: "", newState: state };

        // Map aliases to full commands based on V3.1 System Instruction
        switch (command.toLowerCase()) {
            case 'a':
                command = 'ADD';
                break;
            case 'x':
                command = 'DONE';
                break;
            case 'ls':
                command = 'SHOW';
                break;
            case 'e':
                command = 'EDIT';
                break;
            default:
                // Allow full commands if they are not aliases
                if (['ADD', 'DONE', 'SHOW', 'EDIT'].includes(command.toUpperCase())) {
                    command = command.toUpperCase();
                } else {
                    return "Unknown command alias or full command.";
                }
        }

        try {
            switch (command) {
                case 'ADD':
                    result = handleAdd(args, state);
                    break;
                case 'DONE':
                    result = handleDone(args, state);
                    break;
                case 'EDIT':
                    result = handleEdit(args, state);
                    break;
                case 'SHOW':
                    result.message = handleShow(args);
                    result.success = true;
                    break;
                default:
                    result.message = "Unknown command after alias translation.";
                    result.success = false;
            }
        } catch (e) {
            console.error("Skill Execution Error:", e);
            result.success = false;
            result.message = `RUNTIME ERROR: An unexpected error occurred during processing. Check skill logs.`;
        }

        // If state was modified, save it before returning the message
        if (result.newState && result.message) {
            saveState(result.newState);
        }
        
        // Final message formatting for user response (Handle newline display issue)
        return result.message.replace(/\\n/g, '\\n');
    }
};