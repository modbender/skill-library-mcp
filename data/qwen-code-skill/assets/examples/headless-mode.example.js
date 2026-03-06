/**
 * Qwen Code Headless 模式示例
 * 
 * Headless 模式适用于：
 * - 自动化脚本
 * - CI/CD 集成
 * - 批量处理
 * - JSON 数据管道
 */

const { execSync } = require('child_process');
const fs = require('fs');

/**
 * 执行 Qwen Code 命令并返回 JSON 结果
 */
function runQwenHeadless(prompt, options = {}) {
  const {
    model = 'qwen3.5-plus',
    outputFile = null,
    workingDir = process.cwd()
  } = options;

  const cmd = `qwen -p "${prompt}" --output-format json --model ${model}`;
  
  try {
    const result = execSync(cmd, {
      cwd: workingDir,
      encoding: 'utf-8',
      env: { ...process.env }
    });
    
    return JSON.parse(result);
  } catch (error) {
    console.error('Qwen Code 执行失败:', error.message);
    throw error;
  }
}

/**
 * 示例 1: 代码分析
 */
function example1_CodeAnalysis() {
  console.log('=== 示例 1: 代码分析 ===');
  
  const result = runQwenHeadless('分析这个项目的代码结构和架构模式', {
    workingDir: '/path/to/your/project'
  });
  
  console.log('代码结构:', result.analysis);
  console.log('架构模式:', result.architecture);
}

/**
 * 示例 2: 批量代码审查
 */
function example2_BatchCodeReview() {
  console.log('=== 示例 2: 批量代码审查 ===');
  
  const files = [
    'src/app.ts',
    'src/utils.ts',
    'src/api.ts'
  ];
  
  const results = [];
  
  for (const file of files) {
    console.log(`审查文件：${file}`);
    
    const result = runQwenHeadless(`审查这个文件的代码质量：${file}`);
    
    results.push({
      file,
      issues: result.issues,
      suggestions: result.suggestions,
      score: result.qualityScore
    });
  }
  
  // 保存结果
  fs.writeFileSync('review-results.json', JSON.stringify(results, null, 2));
  console.log('审查结果已保存到 review-results.json');
}

/**
 * 示例 3: 自动生成文档
 */
function example3_AutoDocumentation() {
  console.log('=== 示例 3: 自动生成文档 ===');
  
  const result = runQwenHeadless('为这个函数生成 JSDoc 注释', {
    workingDir: '/path/to/your/project'
  });
  
  console.log('生成的文档:', result.documentation);
}

/**
 * 示例 4: Git 提交信息生成
 */
function example4_CommitMessageGeneration() {
  console.log('=== 示例 4: Git 提交信息生成 ===');
  
  // 获取 git diff
  const diff = execSync('git diff HEAD~1', { encoding: 'utf-8' });
  
  const result = runQwenHeadless(`根据以下代码变更生成简洁的 commit message：\n\n${diff}`);
  
  console.log('建议的提交信息:', result.commitMessage);
}

/**
 * 示例 5: 代码重构建议
 */
function example5_RefactoringSuggestions() {
  console.log('=== 示例 5: 代码重构建议 ===');
  
  const code = fs.readFileSync('src/legacy.ts', 'utf-8');
  
  const result = runQwenHeadless(`分析这段代码并提供重构建议：\n\n${code}`);
  
  console.log('重构建议:', result.suggestions);
  console.log('重构后的代码:', result.refactoredCode);
}

// 主函数
function main() {
  console.log('Qwen Code Headless 模式示例\n');
  
  // 取消注释以运行示例
  // example1_CodeAnalysis();
  // example2_BatchCodeReview();
  // example3_AutoDocumentation();
  // example4_CommitMessageGeneration();
  // example5_RefactoringSuggestions();
  
  console.log('取消注释相应的示例函数以运行');
}

main();
