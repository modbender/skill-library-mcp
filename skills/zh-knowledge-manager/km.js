#!/usr/bin/env node
/**
 * zh-knowledge-manager CLI
 * 中文 AI 增强知识管理工具
 */
const { Command } = require('commander');
const path = require('path');
const fs = require('fs');
const { loadConfig } = require('./lib/config');
const { parseLogFile, findLogFiles } = require('./lib/parser');
const { classify } = require('./lib/classifier');
const { checkDuplicate, loadState, saveState, cleanupState } = require('./lib/dedup');
const { appendEntry, importDraft } = require('./lib/writer');
const { autoTag } = require('./lib/tagger');
const { loadEmbeddingsCache, saveEmbeddingsCache, semanticCheck } = require('./lib/semantic-dedup');
const { extract } = require('./lib/extractor');
const { generateDigest } = require('./lib/digest');

const program = new Command();

program
    .name('km')
    .description('中文 AI 增强知识管理 | Chinese AI-enhanced Knowledge Manager')
    .version('1.0.0')
    .option('-w, --workspace <path>', 'Workspace 根目录', process.cwd())
    .option('-c, --config <path>', 'km.config.json 路径');

// ─── sync ───────────────────────────────────────────────────
program
    .command('sync')
    .description('同步日志到知识库')
    .option('-d, --days <n>', '扫描最近 N 天', '7')
    .option('--dry-run', '预览模式，不写入文件')
    .option('--semantic', '启用语义去重（需要 embedding API）')
    .option('--auto-tag', '启用自动标签补充（jieba 分词）')
    .action(async (opts) => {
        const config = getConfig();
        const logFiles = findLogFiles(config._logDirAbs, parseInt(opts.days));

        if (logFiles.length === 0) {
            console.log(`最近 ${opts.days} 天没有日志文件`);
            return;
        }
        console.log(`找到 ${logFiles.length} 个日志文件\n`);

        const state = loadState(config._statePath);
        let embCache = null;
        if (opts.semantic) {
            embCache = loadEmbeddingsCache(config._embCachePath);
        }

        let synced = 0, skipped = 0, suspects = [];

        for (const file of logFiles) {
            const entries = parseLogFile(file);
            console.log(`${path.basename(file)}: ${entries.length} 条日志`);

            for (const entry of entries) {
                const { isDuplicate, hash } = checkDuplicate(entry, state);
                if (isDuplicate) {
                    skipped++;
                    continue;
                }

                const targetPath = classify(entry, config);

                // 语义去重
                if (opts.semantic && embCache) {
                    try {
                        const result = await semanticCheck(
                            entry, hash, targetPath, state, embCache, config.ai.embedding
                        );
                        if (result.action === 'skip') {
                            console.log(`  ⊘ 语义重复（${(result.similar.similarity * 100).toFixed(0)}%）: ${entry.title}`);
                            skipped++;
                            continue;
                        }
                        if (result.action === 'suspect') {
                            console.log(`  ⚠ 疑似重复（${(result.similar.similarity * 100).toFixed(0)}%）: ${entry.title}`);
                            suspects.push({ entry, similarity: result.similar.similarity });
                        }
                    } catch (err) {
                        console.warn(`  语义去重失败: ${err.message}`);
                    }
                }

                // 自动标签
                if (opts.autoTag) {
                    entry.tags = autoTag(entry, config);
                }

                if (opts.dryRun) {
                    const rel = path.relative(config._kbDirAbs, targetPath);
                    console.log(`  → [预览] ${entry.title} → ${rel}`);
                } else {
                    appendEntry(targetPath, entry);
                    state.hashes[hash] = targetPath;
                }
                synced++;
            }
        }

        if (!opts.dryRun) {
            saveState(config._statePath, state);
            if (embCache) saveEmbeddingsCache(config._embCachePath, embCache);
        }

        console.log(`\n同步完成: ${synced} 条写入, ${skipped} 条跳过`);
        if (suspects.length > 0) {
            console.log(`\n⚠ ${suspects.length} 条疑似重复（已写入但需审查）:`);
            for (const s of suspects) {
                console.log(`  - ${s.entry.title} (相似度 ${(s.similarity * 100).toFixed(0)}%)`);
            }
        }
        if (opts.dryRun) console.log('\n（预览模式，未实际写入）');
    });

// ─── extract ────────────────────────────────────────────────
program
    .command('extract <path>')
    .description('从对话 dump 提取知识（LLM）')
    .option('-d, --days <n>', '仅处理最近 N 天的文件')
    .action(async (inputPath, opts) => {
        const config = getConfig();
        const absPath = path.resolve(config._workspaceRoot, inputPath);

        if (!fs.existsSync(absPath)) {
            console.error(`路径不存在: ${absPath}`);
            process.exit(1);
        }

        await extract(absPath, config, { days: opts.days ? parseInt(opts.days) : undefined });
    });

// ─── import ─────────────────────────────────────────────────
program
    .command('import <draft>')
    .description('导入审核后的草稿到知识库')
    .action((draftPath) => {
        const config = getConfig();
        const absPath = path.resolve(config._workspaceRoot, draftPath);

        if (!fs.existsSync(absPath)) {
            console.error(`文件不存在: ${absPath}`);
            process.exit(1);
        }

        const state = loadState(config._statePath);

        const { imported, skipped, results } = importDraft(
            absPath, config, classify, state, checkDuplicate
        );

        saveState(config._statePath, state);
        console.log(`导入完成: ${imported} 条写入, ${skipped} 条重复跳过`);
        for (const r of results) {
            const rel = path.relative(config._kbDirAbs, r.targetPath);
            console.log(`  → ${r.title} → ${rel}`);
        }
    });

// ─── digest ─────────────────────────────────────────────────
program
    .command('digest')
    .description('输出知识库摘要')
    .option('--update-index', '同时更新 kb-index.md')
    .action((opts) => {
        const config = getConfig();
        const text = generateDigest(config, { updateIndex: opts.updateIndex });
        console.log(text);
    });

// ─── stats ──────────────────────────────────────────────────
program
    .command('stats')
    .description('统计知识库条目并更新索引')
    .action(() => {
        const config = getConfig();
        const text = generateDigest(config, { updateIndex: true });
        console.log(text);
        console.log('\nkb-index.md 已更新');
    });

// ─── cleanup ────────────────────────────────────────────────
program
    .command('cleanup')
    .description('清理 sync-state 中已不存在文件的引用')
    .action(() => {
        const config = getConfig();
        const state = loadState(config._statePath);
        const { removed, state: cleaned } = cleanupState(state);
        saveState(config._statePath, cleaned);
        console.log(`清理完成: 移除 ${removed} 条失效引用`);
    });

// ─── suggest-tags ───────────────────────────────────────────
program
    .command('suggest-tags <text>')
    .description('为一段文本推荐标签')
    .option('-n, --top <n>', '返回前 N 个标签', '5')
    .action((text, opts) => {
        const { suggestTags } = require('./lib/tagger');
        const { normalizeTags } = require('./lib/synonyms');
        const tags = suggestTags(text, parseInt(opts.top));
        const normalized = normalizeTags(tags);
        console.log('推荐标签:', normalized.map(t => `#${t}`).join(' '));
    });

// ─── init ───────────────────────────────────────────────────
program
    .command('init')
    .description('初始化知识管理配置和目录结构')
    .action(() => {
        const config = getConfig();
        const skillDir = path.dirname(__filename);
        const templateDir = path.join(skillDir, 'templates');

        // 创建 kb/ 目录结构
        const kbDirs = ['domains', 'projects', 'tech', 'kb-tasks'];
        for (const dir of kbDirs) {
            const p = path.join(config._kbDirAbs, dir);
            if (!fs.existsSync(p)) {
                fs.mkdirSync(p, { recursive: true });
                console.log(`创建目录: ${path.relative(config._workspaceRoot, p)}/`);
            }
        }

        // 复制模板文件
        const templateFiles = [
            { src: 'kb/people.md', dest: path.join(config._kbDirAbs, 'people.md') },
            { src: 'kb/glossary.md', dest: path.join(config._kbDirAbs, 'glossary.md') },
            { src: 'kb/decisions.md', dest: path.join(config._kbDirAbs, 'decisions.md') },
        ];

        for (const { src, dest } of templateFiles) {
            if (!fs.existsSync(dest)) {
                const srcPath = path.join(templateDir, src);
                if (fs.existsSync(srcPath)) {
                    fs.copyFileSync(srcPath, dest);
                } else {
                    fs.writeFileSync(dest, `# ${path.basename(dest, '.md')}\n`, 'utf-8');
                }
                console.log(`创建文件: ${path.relative(config._workspaceRoot, dest)}`);
            }
        }

        // 生成 km.config.json
        const configPath = path.join(config._workspaceRoot, 'km.config.json');
        if (!fs.existsSync(configPath)) {
            const configTemplatePath = path.join(templateDir, 'km.config.json');
            if (fs.existsSync(configTemplatePath)) {
                fs.copyFileSync(configTemplatePath, configPath);
            } else {
                const { DEFAULT_CONFIG } = require('./lib/config');
                const { _workspaceRoot, _logDirAbs, _kbDirAbs, _outputDirAbs, _backupDirAbs, _statePath, _embCachePath, ...cleanConfig } = DEFAULT_CONFIG;
                fs.writeFileSync(configPath, JSON.stringify(cleanConfig, null, 2), 'utf-8');
            }
            console.log(`创建配置: km.config.json`);
        }

        console.log('\n初始化完成。编辑 km.config.json 配置 API Key 等参数。');
    });

function getConfig() {
    const opts = program.opts();
    return loadConfig(opts.workspace, opts.config);
}

program.parse();
