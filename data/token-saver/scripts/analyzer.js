/**
 * Token Analyzer v3 - Model Registry + Context-Aware Analysis
 * 
 * v3 Changes:
 * - Model registry with context windows
 * - Alias resolution (opus-4-5, opus-4.5, anthropic/claude-opus-4-5 → same)
 * - Context % usage calculation
 * - Robust detection chain with fallback
 */

const fs = require('fs');
const path = require('path');

// Load model registry (with inline fallback)
let MODEL_REGISTRY;
try {
    const registryPath = path.join(__dirname, 'models.json');
    MODEL_REGISTRY = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
} catch (e) {
    // Inline fallback if registry file missing/corrupted
    MODEL_REGISTRY = {
        models: {
            'claude-sonnet-4': { context: 200000, input: 0.003, output: 0.015, tier: 'standard', label: 'Claude Sonnet 4', aliases: ['sonnet'] },
            'claude-opus-4-5': { context: 200000, input: 0.015, output: 0.075, tier: 'premium', label: 'Claude Opus 4.5', aliases: ['opus'] },
            'gemini-2.0-flash': { context: 1000000, input: 0, output: 0, tier: 'free', label: 'Gemini 2.0 Flash', aliases: ['gemini'] }
        },
        defaults: { fallbackModel: 'claude-sonnet-4', fallbackContext: 200000 }
    };
}

// Build alias lookup for fast resolution
const ALIAS_MAP = {};
for (const [canonical, info] of Object.entries(MODEL_REGISTRY.models)) {
    ALIAS_MAP[canonical.toLowerCase()] = canonical;
    if (info.aliases) {
        for (const alias of info.aliases) {
            ALIAS_MAP[alias.toLowerCase()] = canonical;
        }
    }
}

class TokenAnalyzer {
    constructor() {
        this.registry = MODEL_REGISTRY;
    }

    /**
     * Resolve any model name/alias to canonical name
     * Returns original name if not found (allows getModelInfo to flag as unknown)
     */
    resolveModel(modelName) {
        if (!modelName) return this.registry.defaults.fallbackModel;
        const key = modelName.toLowerCase().replace(/^(anthropic|google|openai|openrouter)\//i, '');
        
        // Try exact alias match first
        if (ALIAS_MAP[key]) return ALIAS_MAP[key];
        
        // Try fuzzy match (returns null if unknown version detected)
        const fuzzy = this.fuzzyMatch(key);
        if (fuzzy) return fuzzy;
        
        // Return original name - getModelInfo will flag as unknown
        return modelName;
    }

    /**
     * Fuzzy match for partial model names (strict version matching)
     * Only matches if: no version specified, OR version matches a known model
     */
    fuzzyMatch(partial) {
        partial = partial.toLowerCase();
        
        // Extract version number if present (e.g., "opus-6.5" → "6.5")
        const versionMatch = partial.match(/[\d]+\.?\d*/);
        const hasVersion = versionMatch !== null;
        const version = hasVersion ? versionMatch[0] : null;
        
        // Known versions from registry - CHECK THIS FIRST before any fuzzy matching
        const knownVersions = this.registry.knownVersions || {
            'opus': ['4', '4.1', '4.5', '4.6', '4-5', '4-6'],
            'sonnet': ['4', '4.5', '4-5'],
            'haiku': ['3', '3.5', '4', '4.5', '3-5', '4-5'],
            'gemini': ['2', '2.0', '2.5', '3', '3.0'],
            'gpt': ['4', '4.1', '4o', '5', '5.1', '5.2'],
            'deepseek': ['3', 'v3'],
            'kimi': ['2', '2.5', 'k2.5'],
            'llama': ['3', '3.3'],
            'mistral': ['large']
        };
        
        // If version specified, check if it's known BEFORE doing any matching
        if (hasVersion) {
            for (const [family, versions] of Object.entries(knownVersions)) {
                if (partial.includes(family)) {
                    const versionKnown = versions.some(v => version.includes(v) || v.includes(version));
                    if (!versionKnown) {
                        // Unknown version - return null to trigger fallback with warning
                        return null;
                    }
                }
            }
        }
        
        // Version is known or not specified - safe to do fuzzy matching
        // Check for exact alias match
        for (const [key, canonical] of Object.entries(ALIAS_MAP)) {
            if (key.includes(partial) || partial.includes(key)) return canonical;
        }
        
        // Standard fuzzy match for family names
        if (partial.includes('sonnet')) return 'claude-sonnet-4';
        if (partial.includes('opus')) return 'claude-opus-4-5';
        if (partial.includes('haiku')) return 'claude-haiku-3.5';
        if (partial.includes('gemini')) return 'gemini-2.0-flash';
        if (partial.includes('gpt-4o')) return partial.includes('mini') ? 'gpt-4o-mini' : 'gpt-4o';
        if (partial.includes('deepseek')) return 'deepseek-v3';
        if (partial.includes('kimi')) return 'kimi-k2.5';
        return null;
    }

    /**
     * Get model info from registry
     * Returns info with `unknown: true` flag if model not in registry
     */
    getModelInfo(modelName) {
        const canonical = this.resolveModel(modelName);
        const registryInfo = this.registry.models[canonical];
        
        if (registryInfo) {
            return { ...registryInfo, unknown: false };
        }
        
        // Unknown model - return safe defaults with warning flag
        return {
            context: this.registry.defaults.fallbackContext,
            input: 0.003,
            output: 0.015,
            tier: 'standard',
            label: modelName || 'Unknown Model',
            vendor: 'unknown',
            unknown: true,
            warning: `⚠️ Model "${modelName}" not in registry. Using defaults (200K context). Add to models.json for accurate tracking.`
        };
    }

    /**
     * Discover all .md files in workspace root
     */
    discoverWorkspaceFiles(workspacePath) {
        const knownContextFiles = [
            'SOUL.md', 'USER.md', 'AGENTS.md', 'MEMORY.md',
            'HEARTBEAT.md', 'TOOLS.md', 'IDENTITY.md', 'PROJECTS.md'
        ];

        const found = [];
        try {
            const entries = fs.readdirSync(workspacePath);
            for (const entry of entries) {
                if (entry.endsWith('.md') && !entry.startsWith('.') && !entry.endsWith('.backup')) {
                    const filePath = path.join(workspacePath, entry);
                    const stat = fs.statSync(filePath);
                    if (stat.isFile()) {
                        found.push({
                            filename: entry,
                            isKnownContext: knownContextFiles.includes(entry),
                            path: filePath
                        });
                    }
                }
            }
        } catch (e) {
            for (const f of knownContextFiles) {
                const fp = path.join(workspacePath, f);
                if (fs.existsSync(fp)) {
                    found.push({ filename: f, isKnownContext: true, path: fp });
                }
            }
        }

        return found.sort((a, b) => {
            if (a.isKnownContext !== b.isKnownContext) return b.isKnownContext - a.isKnownContext;
            return a.filename.localeCompare(b.filename);
        });
    }

    async analyzeWorkspace(workspacePath) {
        const files = this.discoverWorkspaceFiles(workspacePath);

        const analysis = {
            files: {},
            totalTokens: 0,
            fileList: [],
            monthlyCostEstimate: 0
        };

        for (const file of files) {
            const content = fs.readFileSync(file.path, 'utf8');
            const tokens = this.estimateTokens(content);

            analysis.files[file.filename] = {
                tokens,
                size: content.length,
                isKnownContext: file.isKnownContext
            };
            analysis.fileList.push(file.filename);
            analysis.totalTokens += tokens;
        }

        analysis.monthlyCostEstimate = (analysis.totalTokens * 0.003 * 4.33);
        return analysis;
    }

    /**
     * Detect current model using fallback chain
     * Priority: runtime injection → env vars → config file → file inference → fallback
     */
    detectCurrentModels(workspacePath, runtimeModel = null) {
        const models = {
            default: { model: 'unknown', usage: 'Main chat', detectedFrom: null, context: null },
            cron: { model: 'unknown', usage: 'Cron/background', detectedFrom: null, context: null },
            subagent: { model: 'unknown', usage: 'Subagents', detectedFrom: null, context: null }
        };

        // 1. Runtime injection (highest priority)
        if (runtimeModel) {
            const canonical = this.resolveModel(runtimeModel);
            const info = this.getModelInfo(canonical);
            models.default.model = canonical;
            models.default.detectedFrom = 'runtime';
            models.default.context = info.context;
        }

        // 2. Environment variables
        const envModel = process.env.SKILL_MODEL || process.env.OPENCLAW_MODEL || process.env.DEFAULT_MODEL;
        if (envModel && models.default.model === 'unknown') {
            const canonical = this.resolveModel(envModel);
            const info = this.getModelInfo(canonical);
            models.default.model = canonical;
            models.default.detectedFrom = 'environment';
            models.default.context = info.context;
        }

        // 3. OpenClaw config file
        const homedir = process.env.USERPROFILE || process.env.HOME || '';
        const configPaths = [
            path.join(homedir, '.openclaw', 'openclaw.json'),
            path.join(workspacePath, '.openclaw', 'openclaw.json'),
        ];

        for (const configPath of configPaths) {
            try {
                if (fs.existsSync(configPath)) {
                    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                    const agentDefaults = config?.agents?.defaults || {};
                    
                    // Primary model
                    if (models.default.model === 'unknown') {
                        const primary = agentDefaults?.model?.primary;
                        if (primary) {
                            const canonical = this.resolveModel(primary);
                            const info = this.getModelInfo(canonical);
                            models.default.model = canonical;
                            models.default.detectedFrom = 'openclaw.json';
                            models.default.context = info.context;
                        }
                    }
                    
                    // Heartbeat/cron model
                    const heartbeatModel = agentDefaults?.heartbeat?.model;
                    if (heartbeatModel) {
                        const canonical = this.resolveModel(heartbeatModel);
                        const info = this.getModelInfo(canonical);
                        models.cron.model = canonical;
                        models.cron.detectedFrom = 'openclaw.json';
                        models.cron.context = info.context;
                    }
                    
                    // Subagent model
                    const subModel = agentDefaults?.subagents?.model;
                    if (subModel) {
                        const canonical = this.resolveModel(subModel);
                        const info = this.getModelInfo(canonical);
                        models.subagent.model = canonical;
                        models.subagent.detectedFrom = 'openclaw.json';
                        models.subagent.context = info.context;
                    }
                    break;
                }
            } catch (e) { /* skip */ }
        }

        // 4. File inference (TOOLS.md, MEMORY.md)
        if (models.default.model === 'unknown') {
            const hintFiles = ['TOOLS.md', 'MEMORY.md', 'AGENTS.md'];
            for (const hf of hintFiles) {
                const fp = path.join(workspacePath, hf);
                try {
                    if (fs.existsSync(fp)) {
                        const content = fs.readFileSync(fp, 'utf8').toLowerCase();
                        if (content.includes('opus')) {
                            models.default.model = 'claude-opus-4-5';
                            models.default.detectedFrom = `${hf} (inferred)`;
                            models.default.context = this.getModelInfo('claude-opus-4-5').context;
                            break;
                        }
                        if (content.includes('sonnet')) {
                            models.default.model = 'claude-sonnet-4';
                            models.default.detectedFrom = `${hf} (inferred)`;
                            models.default.context = this.getModelInfo('claude-sonnet-4').context;
                            break;
                        }
                    }
                } catch (e) { /* skip */ }
            }
        }

        // 5. Fallback
        if (models.default.model === 'unknown') {
            models.default.model = this.registry.defaults.fallbackModel;
            models.default.detectedFrom = 'fallback (assumed)';
            models.default.context = this.registry.defaults.fallbackContext;
        }

        // Fill in context for all detected models
        for (const key of Object.keys(models)) {
            if (models[key].model !== 'unknown' && !models[key].context) {
                models[key].context = this.getModelInfo(models[key].model).context;
            }
            // Estimate monthly cost
            models[key].estimatedMonthlyCost = this.estimateRoleCost(models[key].model, key);
        }

        return models;
    }

    /**
     * Estimate monthly cost for a role
     */
    estimateRoleCost(modelKey, role) {
        const info = this.getModelInfo(modelKey);
        const txPerDay = { default: 80, cron: 30, subagent: 20 };
        const avgTokens = 2000;
        return (avgTokens * info.input / 1000) * (txPerDay[role] || 50) * 30;
    }

    /**
     * Audit current model configuration
     */
    auditModels(workspacePath, runtimeModel = null) {
        const config = this.detectCurrentModels(workspacePath, runtimeModel);
        const suggestions = this.generateModelSuggestions(config);

        return {
            current: config,
            suggestions,
            totalPossibleSavings: suggestions.reduce((sum, s) => sum + s.monthlySaving, 0),
            detectedModel: config.default.model,
            contextWindow: config.default.context
        };
    }

    /**
     * Generate model switch suggestions
     */
    generateModelSuggestions(currentModels) {
        const suggestions = [];

        // Cron job suggestions
        const cronModel = currentModels.cron;
        if (cronModel.model !== 'unknown') {
            const info = this.getModelInfo(cronModel.model);
            if (info.tier !== 'free') {
                suggestions.push({
                    role: 'Cron Jobs',
                    current: info.label || cronModel.model,
                    suggested: 'Gemini 2.0 Flash',
                    reason: 'Background tasks rarely need top-tier reasoning. Free tier handles monitoring well.',
                    currentMonthlyCost: cronModel.estimatedMonthlyCost,
                    newMonthlyCost: 0,
                    monthlySaving: cronModel.estimatedMonthlyCost,
                    confidence: 'high'
                });
            }
        }

        // Subagent suggestions
        const subModel = currentModels.subagent;
        if (subModel.model !== 'unknown') {
            const info = this.getModelInfo(subModel.model);
            if (info.tier === 'premium') {
                suggestions.push({
                    role: 'Subagents',
                    current: info.label || subModel.model,
                    suggested: 'Claude Sonnet 4',
                    reason: 'Most subagent tasks work great on Sonnet. Reserve Opus for complex reasoning.',
                    currentMonthlyCost: subModel.estimatedMonthlyCost,
                    newMonthlyCost: subModel.estimatedMonthlyCost * (0.003 / 0.015),
                    monthlySaving: subModel.estimatedMonthlyCost * (1 - 0.003 / 0.015),
                    confidence: 'medium'
                });
            }
        }

        return suggestions;
    }

    /**
     * Calculate context usage percentage
     */
    calculateContextUsage(currentTokens, model) {
        const info = this.getModelInfo(model);
        const contextLimit = info.context || this.registry.defaults.fallbackContext;
        return {
            current: currentTokens,
            limit: contextLimit,
            percentage: Math.round((currentTokens / contextLimit) * 100),
            remaining: contextLimit - currentTokens
        };
    }

    estimateTokens(text) {
        return Math.round(text.length / 4);
    }
}

// Export for use by other modules
module.exports = { TokenAnalyzer, MODEL_REGISTRY, ALIAS_MAP };
