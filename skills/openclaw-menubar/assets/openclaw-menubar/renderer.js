const fs = require('fs');
const path = require('path');
const os = require('os');
const SimpleClient = require('./simple-client');

// DOM Elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const attachBtn = document.getElementById('attachBtn');
const modelSelect = document.getElementById('modelSelect');
const dropZone = document.getElementById('dropZone');
const statusEl = document.getElementById('status');
const statusDot = statusEl.querySelector('.status-dot');
const statusText = statusEl.querySelector('.status-text');

// State
let currentModel = 'sonnet';
let messageHistory = [];
let attachedFiles = [];
let gatewayConfig = null;
let gatewayClient = null;

// Initialize
init();

async function init() {
    setupEventListeners();
    loadHistory();
    
    // Auto-discover gateway
    await discoverGateway();
    
    autoResizeTextarea();
}

/**
 * Auto-discover OpenClaw Gateway
 * Tries multiple methods to find and connect to the gateway
 */
async function discoverGateway() {
    updateStatus('connecting', 'Discovering gateway...');
    
    // Try to load saved config first
    const saved = loadSavedConfig();
    if (saved) {
        console.log('Trying saved config:', saved.url);
        if (await testGateway(saved.url, saved.token)) {
            gatewayConfig = saved;
            await connectGatewayClient();
            updateStatus('ready', 'Connected (saved)');
            return;
        }
    }
    
    // Try to read from OpenClaw config file
    const openclawConfig = readOpenClawConfig();
    if (openclawConfig) {
        console.log('Trying OpenClaw config:', openclawConfig.url);
        if (await testGateway(openclawConfig.url, openclawConfig.token)) {
            gatewayConfig = openclawConfig;
            saveConfig(openclawConfig);
            await connectGatewayClient();
            updateStatus('ready', 'Connected (auto)');
            return;
        }
    }
    
    // Try common gateway URLs
    const commonUrls = [
        'http://localhost:18789',
        'http://127.0.0.1:18789',
        'http://192.168.1.29:18789', // Your current IP
        `http://${getLocalIP()}:18789`
    ];
    
    for (const url of commonUrls) {
        console.log('Trying:', url);
        const token = openclawConfig?.token || ''; // Try with token if available
        if (await testGateway(url, token)) {
            gatewayConfig = { url, token };
            saveConfig(gatewayConfig);
            
            // Connect WebSocket client
            await connectGatewayClient();
            
            updateStatus('ready', 'Connected (discovered)');
            return;
        }
    }
    
    // If all fails, show setup screen
    showSetupScreen();
}

/**
 * Connect to gateway (simplified - uses OpenClaw CLI)
 */
async function connectGatewayClient() {
    // Use simple CLI-based client (no WebSocket complexity)
    gatewayClient = new SimpleClient();
    console.log('✅ Using OpenClaw CLI client');
    updateStatus('ready', 'Connected');
}

/**
 * Test if OpenClaw CLI is available
 */
async function testGateway(url, token = '') {
    try {
        const { exec } = require('child_process');
        const util = require('util');
        const execPromise = util.promisify(exec);
        
        // Test if openclaw command exists and gateway is running
        await execPromise('openclaw status', { timeout: 3000 });
        
        console.log('✅ OpenClaw CLI found');
        return true;
    } catch (error) {
        console.log('❌ OpenClaw CLI not available:', error.message);
        return false;
    }
}

/**
 * Read OpenClaw config from standard location
 */
function readOpenClawConfig() {
    try {
        const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
        
        if (!fs.existsSync(configPath)) {
            console.log('No OpenClaw config found at:', configPath);
            return null;
        }
        
        const configData = fs.readFileSync(configPath, 'utf8');
        const config = JSON.parse(configData);
        
        // Extract gateway info
        const gateway = config.gateway || {};
        const port = gateway.port || 18789;
        const bind = gateway.bind || 'loopback';
        
        // Determine URL based on bind mode
        let url;
        if (bind === 'loopback' || bind === 'auto') {
            url = `http://localhost:${port}`;
        } else if (bind === 'lan') {
            url = `http://${getLocalIP()}:${port}`;
        } else {
            url = `http://localhost:${port}`;
        }
        
        // Extract token
        const token = gateway.token || '';
        
        console.log('OpenClaw config loaded:', { url, hasToken: !!token });
        
        return { url, token };
    } catch (error) {
        console.error('Failed to read OpenClaw config:', error);
        return null;
    }
}

/**
 * Get local IP address
 */
function getLocalIP() {
    const interfaces = os.networkInterfaces();
    
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            // Skip internal and non-IPv4 addresses
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    
    return 'localhost';
}

/**
 * Save gateway config to user preferences
 */
function saveConfig(config) {
    try {
        const configPath = path.join(os.homedir(), '.openclaw', 'menubar-config.json');
        const configDir = path.dirname(configPath);
        
        if (!fs.existsSync(configDir)) {
            fs.mkdirSync(configDir, { recursive: true });
        }
        
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        console.log('Config saved:', configPath);
    } catch (error) {
        console.error('Failed to save config:', error);
    }
}

/**
 * Load saved config
 */
function loadSavedConfig() {
    try {
        const configPath = path.join(os.homedir(), '.openclaw', 'menubar-config.json');
        
        if (!fs.existsSync(configPath)) {
            return null;
        }
        
        const configData = fs.readFileSync(configPath, 'utf8');
        return JSON.parse(configData);
    } catch (error) {
        console.error('Failed to load saved config:', error);
        return null;
    }
}

/**
 * Show setup screen when gateway can't be found
 */
function showSetupScreen() {
    messagesContainer.innerHTML = `
        <div class="setup-screen">
            <div class="setup-icon">⚠️</div>
            <div class="setup-title">OpenClaw Gateway Not Found</div>
            <div class="setup-message">
                The menu bar app couldn't connect to OpenClaw Gateway.
            </div>
            
            <div class="setup-instructions">
                <div class="setup-step">
                    <div class="step-number">1</div>
                    <div class="step-text">Make sure OpenClaw is running:<br><code>openclaw status</code></div>
                </div>
                <div class="setup-step">
                    <div class="step-number">2</div>
                    <div class="step-text">If offline, start it:<br><code>openclaw gateway start</code></div>
                </div>
                <div class="setup-step">
                    <div class="step-number">3</div>
                    <div class="step-text">Or configure gateway manually below:</div>
                </div>
            </div>
            
            <div class="setup-form">
                <input 
                    type="text" 
                    id="gatewayUrl" 
                    placeholder="http://localhost:18789"
                    value="http://localhost:18789"
                />
                <input 
                    type="text" 
                    id="gatewayToken" 
                    placeholder="Gateway Token (optional)"
                />
                <button id="connectBtn" class="connect-btn">Connect</button>
            </div>
            
            <div class="setup-footer">
                <button id="retryBtn" class="retry-btn">🔄 Retry Auto-Discovery</button>
            </div>
        </div>
    `;
    
    updateStatus('error', 'Gateway offline - setup required');
    
    // Setup event listeners
    document.getElementById('connectBtn').addEventListener('click', async () => {
        const url = document.getElementById('gatewayUrl').value.trim();
        const token = document.getElementById('gatewayToken').value.trim();
        
        updateStatus('connecting', 'Testing connection...');
        
        if (await testGateway(url, token)) {
            gatewayConfig = { url, token };
            saveConfig(gatewayConfig);
            
            // Connect WebSocket
            await connectGatewayClient();
            
            // Reload UI
            messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">🦞</div>
                    <div class="welcome-text">Welcome to OpenClaw</div>
                    <div class="welcome-hint">Type a message or drag & drop files</div>
                </div>
            `;
            
            updateStatus('ready', 'Connected!');
        } else {
            updateStatus('error', 'Connection failed - check URL and token');
        }
    });
    
    document.getElementById('retryBtn').addEventListener('click', () => {
        location.reload();
    });
}

function setupEventListeners() {
    // Send message
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Model switcher
    modelSelect.addEventListener('change', (e) => {
        currentModel = e.target.value;
        updateStatus('ready', `Model: ${currentModel === 'sonnet' ? 'Sonnet' : 'Opus'}`);
    });

    // Attach file
    attachBtn.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.onchange = (e) => {
            handleFiles(Array.from(e.target.files));
        };
        input.click();
    });

    // Drag and drop
    document.body.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('active');
    });

    document.body.addEventListener('dragleave', (e) => {
        if (e.target === document.body) {
            dropZone.classList.remove('active');
        }
    });

    document.body.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('active');
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

async function sendMessage() {
    if (!gatewayClient) {
        updateStatus('error', 'Client not initialized');
        return;
    }
    
    const message = messageInput.value.trim();
    
    if (!message && attachedFiles.length === 0) return;

    // Clear input
    messageInput.value = '';
    autoResizeTextarea();

    // Add user message to UI
    addMessage('user', message, attachedFiles);

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        updateStatus('connecting', 'Sending...');

        // Send via OpenClaw CLI
        const model = currentModel === 'opus' ? 'claude-opus' : null;
        const response = await gatewayClient.sendMessage(message, model);

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add assistant response
        const assistantMessage = response.response || response.message || 'Message sent';
        addMessage('assistant', assistantMessage);

        updateStatus('ready', 'Ready');

    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator(typingId);
        
        let errorMessage = 'Failed to send message';
        if (error.message.includes('openclaw')) {
            errorMessage = 'OpenClaw CLI not found - is OpenClaw installed?';
        } else if (error.message.includes('timeout')) {
            errorMessage = 'Request timeout - try again';
        } else {
            errorMessage = error.message;
        }
        
        addMessage('assistant', `❌ ${errorMessage}`);
        updateStatus('error', errorMessage);
    }

    // Clear attached files
    attachedFiles = [];
}

function addMessage(role, content, files = []) {
    // Remove welcome message if exists
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🦞';

    const contentDiv = document.createElement('div');
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    contentDiv.appendChild(messageContent);
    
    // Add file attachments
    if (files && files.length > 0) {
        files.forEach(file => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-attachment';
            fileDiv.innerHTML = `
                <span class="file-icon">📎</span>
                <span class="file-name">${file.name}</span>
                <span class="file-size">${formatFileSize(file.size)}</span>
            `;
            contentDiv.appendChild(fileDiv);
        });
    }
    
    contentDiv.appendChild(messageTime);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();

    // Save to history
    messageHistory.push({
        role,
        content,
        files: files.map(f => ({ name: f.name, size: f.size })),
        timestamp: Date.now()
    });
    saveHistory();
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = id;
    messageDiv.className = 'message assistant';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🦞';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message-content typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(typingDiv);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();

    return id;
}

function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

async function handleFiles(files) {
    for (const file of files) {
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            updateStatus('error', `File too large: ${file.name} (max 10MB)`);
            continue;
        }

        try {
            const content = await readFileAsBase64(file);
            attachedFiles.push({
                name: file.name,
                type: file.type,
                size: file.size,
                content: content
            });
            
            updateStatus('ready', `Attached: ${file.name}`);
        } catch (error) {
            console.error('Error reading file:', error);
            updateStatus('error', `Failed to read: ${file.name}`);
        }
    }
}

function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function updateStatus(state, text) {
    statusEl.className = `status ${state}`;
    statusText.textContent = text;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function saveHistory() {
    try {
        const historyPath = path.join(os.homedir(), '.openclaw', 'menubar-history.json');
        fs.writeFileSync(historyPath, JSON.stringify(messageHistory, null, 2));
    } catch (error) {
        console.error('Failed to save history:', error);
    }
}

function loadHistory() {
    try {
        const historyPath = path.join(os.homedir(), '.openclaw', 'menubar-history.json');
        if (fs.existsSync(historyPath)) {
            const data = fs.readFileSync(historyPath, 'utf8');
            messageHistory = JSON.parse(data);
            
            // Restore last 10 messages
            const recentMessages = messageHistory.slice(-10);
            const welcomeMsg = messagesContainer.querySelector('.welcome-message');
            if (welcomeMsg && recentMessages.length > 0) {
                welcomeMsg.remove();
            }
            
            recentMessages.forEach(msg => {
                addMessageToUI(msg.role, msg.content, msg.files || []);
            });
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function addMessageToUI(role, content, files) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🦞';

    const contentDiv = document.createElement('div');
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    contentDiv.appendChild(messageContent);
    
    if (files && files.length > 0) {
        files.forEach(file => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-attachment';
            fileDiv.innerHTML = `
                <span class="file-icon">📎</span>
                <span class="file-name">${file.name}</span>
                <span class="file-size">${formatFileSize(file.size)}</span>
            `;
            contentDiv.appendChild(fileDiv);
        });
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
}

// The WebSocket client handles reconnection automatically via gateway-client.js
// No need for manual periodic checks
