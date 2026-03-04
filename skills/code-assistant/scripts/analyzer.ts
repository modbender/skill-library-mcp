#!/usr/bin/env node
/**
 * Code Assistant - Asistente de programación especializado
 */

import { existsSync, readFileSync, readdirSync, statSync } from 'fs';
import { join, extname } from 'path';

const CONFIG = {
    maxComplexity: parseInt(process.env.CODE_MAX_COMPLEXITY || '15'),
    ignorePatterns: (process.env.CODE_IGNORE_PATTERNS || 'node_modules,dist,.git').split(','),
    defaultStyle: process.env.CODE_DEFAULT_STYLE || 'auto'
};

interface AnalysisResult {
    file: string;
    lines: number;
    functions: number;
    complexity: number;
    bugs: Bug[];
    optimizations: Suggestion[];
    refactorings: Suggestion[];
}

interface Bug {
    line: number;
    type: string;
    severity: 'high' | 'medium' | 'low';
    description: string;
    suggestion: string;
}

interface Suggestion {
    line: number;
    description: string;
    impact: string;
}

// Patrones de bugs comunes
const BUG_PATTERNS = [
    {
        pattern: /\$\{.*\}/,
        context: /query\(|exec\(/,
        type: 'SQL Injection',
        severity: 'high' as const,
        suggestion: 'Usar parámetros preparados'
    },
    {
        pattern: /innerHTML\s*=/,
        type: 'XSS Vulnerability',
        severity: 'high' as const,
        suggestion: 'Usar textContent o sanitizar HTML'
    },
    {
        pattern: /password\s*=\s*["']/i,
        type: 'Hardcoded Secret',
        severity: 'high' as const,
        suggestion: 'Usar variables de entorno'
    },
    {
        pattern: /eval\(/,
        type: 'Eval Usage',
        severity: 'medium' as const,
        suggestion: 'Evitar eval, usar alternativas seguras'
    },
    {
        pattern: /console\.log/,
        type: 'Debug Statement',
        severity: 'low' as const,
        suggestion: 'Remover o usar logger apropiado'
    }
];

// Patrones de optimización
const OPTIMIZATION_PATTERNS = [
    {
        pattern: /for\s*\(.*\.length/,
        description: 'Cache array.length fuera del loop',
        impact: 'Rendimiento en loops grandes'
    },
    {
        pattern: /await.*forEach/,
        description: 'Usar Promise.all para operaciones paralelas',
        impact: 'Reducir tiempo de ejecución'
    },
    {
        pattern: /new Date\(\).*new Date\(\)/,
        description: 'Reusar instancia de Date',
        impact: 'Reducir asignaciones de memoria'
    }
];

/**
 * Cuenta la complejidad ciclomática básica
 */
function countComplexity(code: string): number {
    const patterns = [
        /\bif\b/g,
        /\belse\b/g,
        /\bfor\b/g,
        /\bwhile\b/g,
        /\bcase\b/g,
        /\bcatch\b/g,
        /\?\s*.*:/g, // ternary
        /\&\&/g,
        /\|\|/g
    ];

    let complexity = 1; // base
    for (const pattern of patterns) {
        const matches = code.match(pattern);
        if (matches) complexity += matches.length;
    }

    return complexity;
}

/**
 * Cuenta funciones en el código
 */
function countFunctions(code: string): number {
    const patterns = [
        /function\s+\w+/g,
        /\w+\s*=\s*(?:async\s*)?\(/g,
        /(?:async\s+)?function\s*\(/g,
        /=>\s*{/g
    ];

    let count = 0;
    for (const pattern of patterns) {
        const matches = code.match(pattern);
        if (matches) count += matches.length;
    }

    return Math.max(1, Math.floor(count / 2)); // Evitar doble conteo
}

/**
 * Busca bugs en el código
 */
function findBugs(code: string): Bug[] {
    const bugs: Bug[] = [];
    const lines = code.split('\n');

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        for (const bugPattern of BUG_PATTERNS) {
            if (bugPattern.pattern.test(line)) {
                // Si hay contexto, verificar también
                if (bugPattern.context && !bugPattern.context.test(line)) {
                    continue;
                }

                bugs.push({
                    line: i + 1,
                    type: bugPattern.type,
                    severity: bugPattern.severity,
                    description: `Encontrado: ${bugPattern.type}`,
                    suggestion: bugPattern.suggestion
                });
            }
        }
    }

    return bugs;
}

/**
 * Busca optimizaciones posibles
 */
function findOptimizations(code: string): Suggestion[] {
    const suggestions: Suggestion[] = [];
    const lines = code.split('\n');

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        for (const opt of OPTIMIZATION_PATTERNS) {
            if (opt.pattern.test(line)) {
                suggestions.push({
                    line: i + 1,
                    description: opt.description,
                    impact: opt.impact
                });
            }
        }
    }

    return suggestions;
}

/**
 * Analiza un archivo
 */
export function analyzeFile(filePath: string): AnalysisResult {
    if (!existsSync(filePath)) {
        throw new Error(`Archivo no encontrado: ${filePath}`);
    }

    const code = readFileSync(filePath, 'utf-8');
    const lines = code.split('\n').length;

    return {
        file: filePath,
        lines,
        functions: countFunctions(code),
        complexity: countComplexity(code),
        bugs: findBugs(code),
        optimizations: findOptimizations(code),
        refactorings: []
    };
}

/**
 * Analiza un directorio
 */
export function analyzeDirectory(dirPath: string, depth: number = 2): AnalysisResult[] {
    const results: AnalysisResult[] = [];
    const extensions = ['.ts', '.js', '.py', '.go', '.rs', '.java'];

    function walk(dir: string, currentDepth: number) {
        if (currentDepth > depth) return;

        const entries = readdirSync(dir);

        for (const entry of entries) {
            const fullPath = join(dir, entry);

            // Ignorar patrones
            if (CONFIG.ignorePatterns.some(p => fullPath.includes(p))) {
                continue;
            }

            const stat = statSync(fullPath);

            if (stat.isDirectory()) {
                walk(fullPath, currentDepth + 1);
            } else if (extensions.includes(extname(entry))) {
                try {
                    results.push(analyzeFile(fullPath));
                } catch {
                    // Ignorar errores de archivo individual
                }
            }
        }
    }

    walk(dirPath, 0);
    return results;
}

/**
 * Genera docstrings para un archivo
 */
export function generateDocs(filePath: string): string {
    const code = readFileSync(filePath, 'utf-8');
    const ext = extname(filePath);

    // Encontrar funciones sin documentación
    let docs = `# Documentación generada para ${filePath}\n\n`;

    // Patrón básico de funciones
    const funcPattern = /(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)/g;
    let match;

    while ((match = funcPattern.exec(code)) !== null) {
        const [, name, params] = match;
        docs += `## \`${name}(${params})\`\n\n`;
        docs += `**Parámetros:**\n`;

        if (params.trim()) {
            const paramList = params.split(',').map(p => p.trim());
            for (const p of paramList) {
                docs += `- \`${p}\`: [Descripción pendiente]\n`;
            }
        } else {
            docs += `- Ninguno\n`;
        }

        docs += `\n**Retorna:** [Descripción pendiente]\n\n`;
        docs += `---\n\n`;
    }

    return docs;
}

/**
 * Formatea el resultado del análisis
 */
function formatResult(result: AnalysisResult): string {
    let output = `\n🔍 Análisis de: ${result.file}\n\n`;

    output += `📊 Métricas:\n`;
    output += `├── Líneas: ${result.lines}\n`;
    output += `├── Funciones: ${result.functions}\n`;

    const complexityIcon = result.complexity > CONFIG.maxComplexity ? '⚠️' : '✅';
    output += `└── Complejidad: ${result.complexity} ${complexityIcon}\n\n`;

    if (result.bugs.length > 0) {
        output += `🐛 Bugs Potenciales (${result.bugs.length}):\n\n`;
        for (const bug of result.bugs) {
            const icon = bug.severity === 'high' ? '🔴' : bug.severity === 'medium' ? '🟡' : '🟢';
            output += `${icon} Línea ${bug.line}: ${bug.type}\n`;
            output += `   💡 ${bug.suggestion}\n\n`;
        }
    } else {
        output += `✅ No se encontraron bugs obvios\n\n`;
    }

    if (result.optimizations.length > 0) {
        output += `⚡ Optimizaciones Sugeridas (${result.optimizations.length}):\n\n`;
        for (const opt of result.optimizations) {
            output += `• Línea ${opt.line}: ${opt.description}\n`;
        }
        output += '\n';
    }

    return output;
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
    const [command, target, ...args] = process.argv.slice(2);

    switch (command) {
        case 'analyze':
            if (!target) {
                console.log('Uso: code analyze <archivo|directorio>');
                break;
            }

            const stat = statSync(target);
            if (stat.isDirectory()) {
                const results = analyzeDirectory(target);
                console.log(`\n📁 Análisis de directorio: ${target}`);
                console.log(`   ${results.length} archivos analizados\n`);

                const totalBugs = results.reduce((sum, r) => sum + r.bugs.length, 0);
                const avgComplexity = results.reduce((sum, r) => sum + r.complexity, 0) / results.length;

                console.log(`   🐛 Total bugs: ${totalBugs}`);
                console.log(`   📊 Complejidad promedio: ${avgComplexity.toFixed(1)}`);

                // Mostrar archivos con más problemas
                const problematic = results.filter(r => r.bugs.length > 0).slice(0, 5);
                if (problematic.length > 0) {
                    console.log(`\n   ⚠️ Archivos con bugs:`);
                    for (const r of problematic) {
                        console.log(`      ${r.file}: ${r.bugs.length} bugs`);
                    }
                }
            } else {
                const result = analyzeFile(target);
                console.log(formatResult(result));
            }
            break;

        case 'bugs':
        case 'find-bugs':
            if (!target) {
                console.log('Uso: code bugs <archivo|directorio>');
                break;
            }

            const bugResults = statSync(target).isDirectory()
                ? analyzeDirectory(target)
                : [analyzeFile(target)];

            const allBugs = bugResults.flatMap(r => r.bugs.map(b => ({ ...b, file: r.file })));
            console.log(`\n🐛 ${allBugs.length} bugs encontrados:\n`);

            for (const bug of allBugs) {
                const icon = bug.severity === 'high' ? '🔴' : bug.severity === 'medium' ? '🟡' : '🟢';
                console.log(`${icon} ${bug.file}:${bug.line} - ${bug.type}`);
            }
            break;

        case 'document':
        case 'docs':
            if (!target) {
                console.log('Uso: code document <archivo>');
                break;
            }
            console.log(generateDocs(target));
            break;

        case 'complexity':
            if (!target) {
                console.log('Uso: code complexity <archivo>');
                break;
            }
            const compResult = analyzeFile(target);
            console.log(`\n📊 Complejidad de ${target}: ${compResult.complexity}`);
            console.log(`   Umbral: ${CONFIG.maxComplexity}`);
            console.log(`   Estado: ${compResult.complexity > CONFIG.maxComplexity ? '⚠️ Alta' : '✅ OK'}`);
            break;

        default:
            console.log(`
💻 Code Assistant - Asistente de Programación

Comandos:
  analyze <path>      Analizar archivo o directorio
  bugs <path>         Buscar bugs
  document <file>     Generar documentación
  complexity <file>   Medir complejidad

Ejemplos:
  code analyze src/
  code bugs src/api/
  code document src/utils.ts
      `);
    }
}
