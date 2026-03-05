#!/usr/bin/env node

/**
 * Token Saver v3 - Dashboard & Optimization
 * 
 * v3 Changes:
 * - Dynamic presets based on model's context window
 * - Context usage % display
 * - Model-aware compaction thresholds
 * - Improved detection with fallback chain
 */

const fs = require('fs');
const path = require('path');
const { TokenAnalyzer, MODEL_REGISTRY } = require('./analyzer.js');
const { WorkspaceCompressor } = require('./compressor.js');

class TokenOptimizerV3 {
    constructor() {
        this.analyzer = new TokenAnalyzer();
        this.compressor = new WorkspaceCompressor();
    }

    async run(command = 'dashboard', args = []) {
        const workspacePath = this.findWorkspace();
        
        // Check for --model flag to override detection
        const modelArg = args.find(a => a.startsWith('--model='));
        const runtimeModel = modelArg ? modelArg.split('=')[1] : null;

        switch (command) {
            case 'dashboard': return this.showDashboard(workspacePath, runtimeModel);
            case 'tokens': return this.optimizeTokens(workspacePath, args);
            case 'models': return this.showModelAudit(workspacePath, runtimeModel);
            case 'compaction': return this.showCompaction(workspacePath, args, runtimeModel);
            case 'revert': return this.revertChanges(args[0], workspacePath);
            default: return this.showDashboard(workspacePath, runtimeModel);
        }
    }

    findWorkspace() {
        let dir = process.cwd();
        if (dir.includes('skills' + path.sep + 'token-')) {
            return path.resolve(dir, '..', '..');
        }
        return dir;
    }

    /**
     * Calculate dynamic presets based on model's context window
     * @param {number} contextLimit - Model's context window in tokens
     * @param {object} modelInfo - Model info from registry (for pricing)
     */
    getDynamicPresets(contextLimit, modelInfo = null) {
        // Scale savings based on model pricing (free models = $0 savings)
        // Note: must check for undefined/null explicitly since input can be 0 for free models
        const inputCost = (modelInfo?.input !== undefined && modelInfo?.input !== null) ? modelInfo.input : 0.003;
        const savingsMultiplier = inputCost > 0 ? (inputCost / 0.003) : 0; // normalize to Sonnet baseline, 0 for free
        
        return {
            aggressive: {
                percent: 40,
                threshold: 0.40,
                compactAt: Math.round(contextLimit * 0.40 / 1000),
                savings: Math.round(200 * savingsMultiplier),
                label: 'Aggressive'
            },
            balanced: {
                percent: 60,
                threshold: 0.60,
                compactAt: Math.round(contextLimit * 0.60 / 1000),
                savings: Math.round(100 * savingsMultiplier),
                label: 'Balanced'
            },
            conservative: {
                percent: 80,
                threshold: 0.80,
                compactAt: Math.round(contextLimit * 0.80 / 1000),
                savings: Math.round(30 * savingsMultiplier),
                label: 'Conservative'
            },
            off: {
                percent: 95,
                threshold: 0.95,
                compactAt: Math.round(contextLimit * 0.95 / 1000),
                savings: 0,
                label: 'Off'
            }
        };
    }

    async showDashboard(workspacePath, runtimeModel = null) {
        const analysis = await this.analyzer.analyzeWorkspace(workspacePath);
        const previews = this.compressor.previewOptimizations(workspacePath);
        const modelAudit = this.analyzer.auditModels(workspacePath, runtimeModel);
        const fileSavings = this.calculatePossibleSavings(previews);
        const hasBackups = this.findBackups(workspacePath).length > 0;

        // Get detected model info
        const detectedModel = modelAudit.detectedModel;
        const contextLimit = modelAudit.contextWindow || 200000;
        const modelInfo = this.analyzer.getModelInfo(detectedModel);
        const presets = this.getDynamicPresets(contextLimit, modelInfo);

        // Compaction settings
        const configPath = path.join(workspacePath, '.token-saver-config.json');
        const config = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};
        const compactionPct = config.compactionThreshold ? Math.round(config.compactionThreshold * 100) : 95;
        const compactionAt = Math.round(contextLimit * (compactionPct / 100) / 1000);
        const compactionSavings = compactionPct <= 40 ? 200 : compactionPct <= 60 ? 100 : compactionPct <= 80 ? 30 : 0;

        // Auto-scan chat history for recommendation
        const chatAnalysis = await this.analyzeUserSessions(workspacePath, 'week');

        // Build file table
        const totalTokens = analysis.totalTokens;
        let fileRows = '';
        for (const file of Object.keys(analysis.files).sort()) {
            const info = analysis.files[file];
            const preview = previews.find(p => p.filename === file);
            const canSave = preview ? preview.originalTokens - preview.compressedTokens : 0;
            const savePct = preview && preview.originalTokens > 0 
                ? Math.round((canSave / preview.originalTokens) * 100) : 0;
            const status = savePct > 50 ? '🔴' : savePct > 20 ? '🟡' : '🟢';
            const saveLabel = canSave > 0 ? `-${canSave} (${savePct}%)` : '✓ optimized';
            fileRows += `│ ${status} ${file.padEnd(18)} │ ${String(info.tokens).padStart(5)} │ ${saveLabel.padStart(14)} │\n`;
        }

        // Calculate totals
        const totalSaveable = fileSavings.tokens;
        const totalPct = totalTokens > 0 ? Math.round((totalSaveable / totalTokens) * 100) : 0;

        // Context usage bar
        const contextUsage = this.analyzer.calculateContextUsage(totalTokens, detectedModel);
        const usageBar = this.renderBar(contextUsage.percentage, 20);

        console.log(`
╭─────────────────────────────────────────────────────────╮
│  ⚡ TOKEN SAVER v3                                       │
│  Reduce AI costs by optimizing what gets sent each call │
╰─────────────────────────────────────────────────────────╯

🤖 **Model:** ${modelInfo.label} (${contextLimit/1000}K context)
   Detected: ${modelAudit.current.default.detectedFrom || 'fallback'}${modelInfo.unknown ? `\n   ${modelInfo.warning}` : ''}

📊 **Context Usage:** ${usageBar} ${contextUsage.percentage}% (${Math.round(totalTokens/1000)}K/${contextLimit/1000}K)

📁 **WORKSPACE FILES** (sent every API call)
┌──────────────────────┬───────┬────────────────┐
│ File                 │ Tokens│ Can Save       │
├──────────────────────┼───────┼────────────────┤
${fileRows}├──────────────────────┼───────┼────────────────┤
│ TOTAL                │ ${String(totalTokens).padStart(5)} │ -${String(totalSaveable).padStart(4)} (${totalPct}%)     │
└──────────────────────┴───────┴────────────────┘
${totalSaveable > 0 ? `\n💰 File compression: Save ~${totalSaveable} tokens/call → **~$${fileSavings.monthlyCost.toFixed(0)}/mo**\n   Run: \`/optimize tokens\`\n` : '\n✅ Files already optimized\n'}
💬 **CHAT COMPACTION** — Current: ${compactionAt}K (${compactionPct}% of context)
${chatAnalysis.hasData ? `📊 Scanned ${chatAnalysis.sessionsAnalyzed} sessions → avg topic: ${chatAnalysis.avgTopicLength}K\n` : ''}
  Presets (dynamic for ${modelInfo.label}):
  🔴 Aggressive: ${presets.aggressive.compactAt}K (40%)    🟡 Balanced: ${presets.balanced.compactAt}K (60%)
  🟢 Conservative: ${presets.conservative.compactAt}K (80%)    ⚪ Off: ${presets.off.compactAt}K (95%)
  
  Apply: \`/optimize compaction balanced\` | Custom: \`/optimize compaction ${presets.balanced.compactAt}\`

  ⚠️ Lower values = AI summarizes sooner, loses exact wording of old messages.`);

        // Calculate total potential savings
        const totalPotential = fileSavings.monthlyCost + modelAudit.totalPossibleSavings + (compactionSavings > 0 ? 0 : 100);

        console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 **TOTAL POTENTIAL SAVINGS: ~$${totalPotential.toFixed(0)}/month**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    }

    renderBar(percent, width = 20) {
        const clamped = Math.max(0, Math.min(100, percent));
        const filled = Math.round((clamped / 100) * width);
        return '[' + '█'.repeat(filled) + '░'.repeat(width - filled) + ']';
    }

    async showModelAudit(workspacePath, runtimeModel = null) {
        const modelAudit = this.analyzer.auditModels(workspacePath, runtimeModel);

        console.log(`🤖 **AI Model Audit - Detailed Analysis**

╭─────────────────────────────────────────────────────────╮
│  DETECTED MODEL CONFIGURATION                            │
╰─────────────────────────────────────────────────────────╯
${this.formatCurrentModelsDetailed(modelAudit.current)}

╭─────────────────────────────────────────────────────────╮
│  RECOMMENDED CHANGES                                     │
╰─────────────────────────────────────────────────────────╯
${this.formatModelSuggestionsDetailed(modelAudit.suggestions)}

╭─────────────────────────────────────────────────────────╮
│  MODEL REGISTRY (${Object.keys(MODEL_REGISTRY.models).length} models)                              │
╰─────────────────────────────────────────────────────────╯
${this.formatModelRegistry()}

💡 Model changes require updating OpenClaw gateway config.`);
    }

    formatCurrentModelsDetailed(models) {
        const lines = [];
        for (const [role, info] of Object.entries(models)) {
            const modelInfo = this.analyzer.getModelInfo(info.model);
            lines.push(`**${this.roleLabel(role)}**`);
            lines.push(`  Model: ${modelInfo.label || info.model}`);
            lines.push(`  Context: ${modelInfo.context ? (modelInfo.context/1000) + 'K' : 'unknown'}`);
            lines.push(`  Detected: ${info.detectedFrom || 'not found'}`);
            lines.push(`  Est. cost: $${(info.estimatedMonthlyCost || 0).toFixed(2)}/month`);
            lines.push('');
        }
        return lines.join('\n');
    }

    formatModelSuggestionsDetailed(suggestions) {
        if (suggestions.length === 0) {
            return '✅ Current model configuration looks cost-efficient!\n';
        }

        return suggestions.map((s, i) => {
            return `**${i + 1}. ${s.role}: ${s.current} → ${s.suggested}**
   Reason: ${s.reason}
   Possible saving: ~$${s.monthlySaving.toFixed(2)}/month`;
        }).join('\n\n');
    }

    formatModelRegistry() {
        const tiers = { free: [], budget: [], standard: [], premium: [] };
        for (const [key, info] of Object.entries(MODEL_REGISTRY.models)) {
            tiers[info.tier].push({ key, ...info });
        }

        const lines = [];
        if (tiers.free.length) {
            lines.push('**🟢 Free:**');
            tiers.free.forEach(m => lines.push(`  • ${m.label} — ${m.context/1000}K context`));
        }
        if (tiers.budget.length) {
            lines.push('**🟡 Budget:**');
            tiers.budget.forEach(m => lines.push(`  • ${m.label} — ${m.context/1000}K ctx, $${m.input}/1K in`));
        }
        if (tiers.standard.length) {
            lines.push('**🟠 Standard:**');
            tiers.standard.forEach(m => lines.push(`  • ${m.label} — ${m.context/1000}K ctx, $${m.input}/1K in`));
        }
        if (tiers.premium.length) {
            lines.push('**🔴 Premium:**');
            tiers.premium.forEach(m => lines.push(`  • ${m.label} — ${m.context/1000}K ctx, $${m.input}/1K in`));
        }

        return lines.join('\n');
    }

    roleLabel(role) {
        return { default: 'Main Chat', cron: 'Cron Jobs', subagent: 'Subagents' }[role] || role;
    }

    calculatePossibleSavings(filePreviews) {
        const totalBefore = filePreviews.reduce((sum, p) => sum + p.originalTokens, 0);
        const totalAfter = filePreviews.reduce((sum, p) => sum + p.compressedTokens, 0);
        const saved = totalBefore - totalAfter;
        return { tokens: saved, percentage: totalBefore > 0 ? Math.round((saved / totalBefore) * 100) : 0, monthlyCost: (saved * 0.003 * 4.33) };
    }

    async optimizeTokens(workspacePath, args = []) {
        const beforeAnalysis = await this.analyzer.analyzeWorkspace(workspacePath);
        const beforeTotal = beforeAnalysis.totalTokens;
        
        console.log('🗜️ **Compressing workspace files...**\n');

        const results = this.compressor.compressWorkspaceFiles(workspacePath);
        let totalSaved = 0;
        let filesChanged = 0;
        const changedFiles = [];

        results.forEach(result => {
            if (result.success && result.tokensSaved > 0) {
                totalSaved += result.tokensSaved;
                filesChanged++;
                changedFiles.push(result);
            }
        });

        // Enable persistent AI-efficient writing mode
        const persistentEnabled = this.enablePersistentMode(workspacePath);

        // Calculate AFTER totals
        const afterAnalysis = await this.analyzer.analyzeWorkspace(workspacePath);
        const afterTotal = afterAnalysis.totalTokens;
        const totalPercentSaved = beforeTotal > 0 ? Math.round(((beforeTotal - afterTotal) / beforeTotal) * 100) : 0;
        
        const monthlySavings = (totalSaved * 0.003 * 4.33);

        console.log(`**Before → After:**`);
        changedFiles.forEach(f => {
            console.log(`• ${f.filename}: ${f.originalTokens}→${f.compressedTokens} (${f.percentageSaved}%)`);
        });
        console.log(`• **Total: ${beforeTotal}→${afterTotal} (${totalPercentSaved}% smaller)**`);

        console.log(`
✅ Done | ${filesChanged} files | ~$${monthlySavings.toFixed(2)}/mo saved${persistentEnabled ? ' | Persistent: ON' : ''}
Backups: .backup | Undo: \`/optimize revert\``);
    }

    enablePersistentMode(workspacePath) {
        const agentsPath = path.join(workspacePath, 'AGENTS.md');
        if (!fs.existsSync(agentsPath)) return false;

        const content = fs.readFileSync(agentsPath, 'utf8');
        const marker = '## 📝 Token Saver — Persistent Mode';
        
        if (content.includes(marker)) return false;

        const instruction = `
${marker}
**Status: ENABLED** — Turn off with \`/optimize revert\`

**Priority: Integrity > Size** — Never sacrifice meaning or functionality for smaller tokens.

**Writing style by file type:**
| File | Style | Example |
|------|-------|---------|
| SOUL.md | Evocative, personality-shaping | Keep poetic language, "you're becoming someone" |
| AGENTS.md | Dense instructions | Symbols (→, +, |), abbreviations OK |
| USER.md | Key:value facts | \`ROLES: IT-eng + COO + owner\` |
| MEMORY.md | Ultra-dense data | \`GOOGLE-ADS: $15/day, bids-fixed-Feb3\` |
| memory/*.md | Log format, dated | Facts only, no filler |
| PROJECTS.md | Keep structure | Don't compress — user's format |

**General rules:**
- Symbols (→, +, |, &) over words when clarity preserved
- Abbreviations for common terms
- Remove filler ("just", "basically", "I think")
- Preserve ALL meaning
`;

        const backupPath = agentsPath + '.backup';
        if (!fs.existsSync(backupPath)) {
            fs.copyFileSync(agentsPath, backupPath);
        }

        fs.appendFileSync(agentsPath, instruction);
        return true;
    }

    revertChanges(target, workspacePath) {
        const backups = this.findBackups(workspacePath);

        if (backups.length === 0) {
            console.log('📁 **No backups found** — nothing to revert.');
            return;
        }

        let toRevert = target && target !== 'all'
            ? backups.filter(b => b.includes(target))
            : backups;

        if (toRevert.length === 0) {
            console.log(`❌ **No backups found for:** ${target}`);
            return;
        }

        const restored = [];
        toRevert.forEach(backupPath => {
            const originalPath = backupPath.replace('.backup', '');
            fs.copyFileSync(backupPath, originalPath);
            fs.unlinkSync(backupPath);
            restored.push(path.basename(originalPath));
        });

        this.disablePersistentMode(workspacePath);
        console.log(`✅ Reverted: ${restored.join(', ')} | Persistent: OFF`);
    }

    disablePersistentMode(workspacePath) {
        const agentsPath = path.join(workspacePath, 'AGENTS.md');
        if (!fs.existsSync(agentsPath)) return;

        const content = fs.readFileSync(agentsPath, 'utf8');
        const marker = '## 📝 Token Saver — Persistent Mode';
        const markerIndex = content.indexOf(marker);
        
        if (markerIndex === -1) return;

        const before = content.substring(0, markerIndex).trimEnd();
        fs.writeFileSync(agentsPath, before + '\n');
    }

    async showCompaction(workspacePath, args, runtimeModel = null) {
        const setting = args.find(a => !a.startsWith('--'));
        
        // Detect model and get context window
        const modelAudit = this.analyzer.auditModels(workspacePath, runtimeModel);
        const contextLimit = modelAudit.contextWindow || 200000;
        const modelInfo = this.analyzer.getModelInfo(modelAudit.detectedModel);
        const presets = this.getDynamicPresets(contextLimit, modelInfo);
        
        // Check for scan range
        let scanRange = 'week';
        if (args.includes('--month')) scanRange = 'month';
        if (args.includes('--all')) scanRange = 'all';

        // Apply setting if provided
        if (setting) {
            const preset = presets[setting.toLowerCase()];
            let threshold, compactAt;
            
            if (preset) {
                threshold = preset.threshold;
                compactAt = preset.compactAt;
            } else {
                const num = parseFloat(setting);
                if (isNaN(num)) {
                    console.log(`❌ Invalid: Use preset name or number (e.g., 'balanced', '100', '0.5')`);
                    return;
                }
                
                if (num > 1 && num <= contextLimit/1000) {
                    compactAt = Math.round(num);
                    threshold = num / (contextLimit / 1000);
                } else if (num >= 0.2 && num <= 1.0) {
                    threshold = num;
                    compactAt = Math.round(contextLimit * threshold / 1000);
                } else {
                    console.log(`❌ Invalid: Enter 20-${contextLimit/1000} (K tokens) or 0.2-1.0 (threshold)`);
                    return;
                }
            }

            const configPath = path.join(workspacePath, '.token-saver-config.json');
            const config = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};
            config.previousCompactionThreshold = config.compactionThreshold;
            config.compactionThreshold = threshold;
            config.compactionSetAt = new Date().toISOString();
            config.modelContext = contextLimit;
            fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

            const savings = preset ? preset.savings : Math.max(0, Math.round((presets.off.compactAt - compactAt) * 1.8));
            
            console.log(`✅ **Compaction Set: ${compactAt}K (${Math.round(threshold*100)}% of ${modelInfo.label}'s ${contextLimit/1000}K context)**

**What happens now:**
• AI compacts conversation when it reaches **${compactAt}K tokens**
• Old messages get summarized to make room
• Estimated savings: **~$${savings}/month**

**To undo:** \`/optimize compaction off\`

⚠️ Add to OpenClaw config to apply:
\`agents.defaults.context.compactionThreshold: ${threshold.toFixed(2)}\``);
            return;
        }

        // Show current settings and options
        const configPath = path.join(workspacePath, '.token-saver-config.json');
        const config = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};
        const currentThreshold = config.compactionThreshold || 0.95;
        const currentCompactAt = Math.round(contextLimit * currentThreshold / 1000);

        // Analyze sessions
        if (scanRange !== 'week') {
            console.log(`⏳ Scanning ${scanRange === 'all' ? 'all sessions' : 'last month'}...\n`);
        }
        const analysis = await this.analyzeUserSessions(workspacePath, scanRange);

        console.log(`**⚡ Compaction Control**

**Model:** ${modelInfo.label} (${contextLimit/1000}K context window)
**Current:** Compact at **${currentCompactAt}K tokens** (${Math.round(currentThreshold*100)}%)

**What is this?**
When conversations get long, AI "compacts" by summarizing old messages.
Compact sooner = pay less, but AI forgets earlier parts faster.
`);

        if (analysis.hasData) {
            console.log(`**📊 Your Usage** (${analysis.sessionsAnalyzed} sessions, last ${scanRange})
• Avg topic length: ${analysis.avgTopicLength}K tokens
• Avg session size: ${analysis.avgSessionSize}K tokens
• Recommendation: **${analysis.recommendation}**
`);
        }

        console.log(`**Presets** (dynamic for ${contextLimit/1000}K context):

🔴 **Aggressive** — ${presets.aggressive.compactAt}K (40%) — Save ~$${presets.aggressive.savings}/mo
   Short memory, max savings

🟡 **Balanced** — ${presets.balanced.compactAt}K (60%) — Save ~$${presets.balanced.savings}/mo
   Good balance of cost and memory

🟢 **Conservative** — ${presets.conservative.compactAt}K (80%) — Save ~$${presets.conservative.savings}/mo
   Long memory, moderate savings

⚪ **Off** — ${presets.off.compactAt}K (95%) — Baseline
   Maximum memory, no savings

**Commands:**
\`/optimize compaction balanced\`     — Apply balanced preset
\`/optimize compaction ${presets.balanced.compactAt}\`          — Custom: compact at ${presets.balanced.compactAt}K
\`/optimize compaction --month\`      — Analyze last 30 days`);
    }

    async analyzeUserSessions(workspacePath, range = 'week') {
        const result = {
            hasData: false,
            sessionsAnalyzed: 0,
            avgTopicLength: 30,
            avgSessionSize: 60,
            topicChangesPerSession: 2,
            recommendation: 'Balanced',
            safeThreshold: 120,
            scanRange: range
        };

        const now = Date.now();
        const ranges = { week: 7 * 24 * 60 * 60 * 1000, month: 30 * 24 * 60 * 60 * 1000, all: Infinity };
        const cutoff = now - (ranges[range] || ranges.week);

        try {
            const openclawDir = process.env.OPENCLAW_DIR || path.join(require('os').homedir(), '.openclaw');
            const sessionsDir = path.join(openclawDir, 'agents', 'main', 'sessions');
            
            if (!fs.existsSync(sessionsDir)) return result;

            const sessionFiles = fs.readdirSync(sessionsDir)
                .filter(f => f.endsWith('.jsonl'))
                .map(f => ({ name: f, path: path.join(sessionsDir, f), stat: fs.statSync(path.join(sessionsDir, f)) }))
                .filter(f => f.stat.size > 10000 && f.stat.mtimeMs > cutoff)
                .sort((a, b) => b.stat.mtimeMs - a.stat.mtimeMs);

            if (sessionFiles.length === 0) return result;

            let totalTokens = 0;
            for (const session of sessionFiles) {
                totalTokens += Math.round(session.stat.size / 4 / 1000);
            }

            result.hasData = true;
            result.sessionsAnalyzed = sessionFiles.length;
            result.avgSessionSize = Math.round(totalTokens / sessionFiles.length);
            result.topicChangesPerSession = Math.max(1, Math.round(result.avgSessionSize / 25));
            result.avgTopicLength = Math.round(result.avgSessionSize / result.topicChangesPerSession);

            if (result.avgTopicLength <= 25) {
                result.recommendation = 'Aggressive';
                result.safeThreshold = 80;
            } else if (result.avgTopicLength <= 40) {
                result.recommendation = 'Balanced';
                result.safeThreshold = 120;
            } else {
                result.recommendation = 'Conservative';
                result.safeThreshold = 160;
            }

        } catch (e) { /* silent */ }

        return result;
    }

    findBackups(workspacePath) {
        try {
            return fs.readdirSync(workspacePath)
                .filter(file => file.endsWith('.backup'))
                .map(file => path.join(workspacePath, file));
        } catch (e) {
            return [];
        }
    }
}

// CLI
if (require.main === module) {
    const optimizer = new TokenOptimizerV3();
    const command = process.argv[2] || 'dashboard';
    const args = process.argv.slice(3);
    optimizer.run(command, args).catch(console.error);
}

module.exports = { TokenOptimizerV3 };
