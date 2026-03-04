#!/usr/bin/env node

/**
 * Git Sentinel - Core Logic
 * 
 * 1. Detecta archivos modificados (git diff --cached --name-only).
 * 2. Lee el contenido de los archivos.
 * 3. Construye un prompt estructurado para el LLM.
 * 4. Envía a la IA (vía OpenClaw standard input).
 * 5. Formatea la salida como un reporte de Code Review.
 */

const { execSync } = require('child_process');
const fs = require('fs');

const mode = process.argv[2] || 'staged';
const targetFile = process.argv[3];

console.log(`🛡️  Git Sentinel activado... [Modo: ${mode}]`);

try {
  let filesToReview = [];

  if (targetFile) {
    filesToReview = [targetFile];
  } else {
    // Obtener archivos en staging
    const diff = execSync('git diff --cached --name-only', { encoding: 'utf-8' });
    filesToReview = diff.split('\n').filter(f => f.trim() !== '' && !f.endsWith('.lock'));
  }

  if (filesToReview.length === 0) {
    console.log("✅ No hay archivos para revisar (stage vacío).");
    process.exit(0);
  }

  console.log(`🔍 Analizando ${filesToReview.length} archivos...`);

  const fileContents = filesToReview.map(file => {
    try {
        return `--- FILE: ${file} ---\n` + fs.readFileSync(file, 'utf-8');
    } catch (e) {
        return `--- FILE: ${file} (Error leyendo archivo) ---`;
    }
  }).join('\n\n');

  const prompt = `
ACT AS: Senior Software Engineer & Security Auditor.
TASK: Review the following code changes.
FOCUS:
1. Logic Bugs (High Priority)
2. Security Vulnerabilities (OWASP Top 10)
3. Code Cleanliness & Readability
4. Performance Issues

OUTPUT FORMAT:
- 🔴 [CRITICAL]: Must fix. (Bugs/Security)
- 🟡 [WARNING]: Should fix. (Bad practice/Perf)
- 🟢 [INFO]: Nice to have. (Style/Refactor)
- ✅ [SUMMARY]: One sentence verdict (Approve / Request Changes).

CODE TO REVIEW:
${fileContents}
`;

  // En un entorno real de OpenClaw, aquí invocaríamos al modelo.
  // Por ahora, simulamos que pasamos esto al sistema.
  console.log("\n--- ENVIANDO A IA ---\n");
  console.log(prompt); 

} catch (error) {
  console.error("❌ Error ejecutando Git Sentinel:", error.message);
  process.exit(1);
}
