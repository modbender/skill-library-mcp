/**
 * Issue Analyzer
 * Orchestrates fetching and analyzing SonarQube issues
 */

const { getIssues } = require('./api');
const { analyzeIssue } = require('./rules');

/**
 * Generate suggestions for fixing issues
 * @param {Object[]} issues - List of issues
 * @returns {Object} Analysis results
 */
function generateSuggestions(issues) {
  const analyzed = issues.map(analyzeIssue);
  
  const autoFixable = analyzed.filter(i => i.autoFixable);
  const manualFix = analyzed.filter(i => !i.autoFixable);

  const byFile = analyzed.reduce((acc, issue) => {
    acc[issue.component] = acc[issue.component] || [];
    acc[issue.component].push(issue);
    return acc;
  }, {});

  return {
    totalIssues: analyzed.length,
    autoFixable: {
      count: autoFixable.length,
      issues: autoFixable
    },
    manualFix: {
      count: manualFix.length,
      issues: manualFix
    },
    byFile,
    nextSteps: generateNextSteps(analyzed)
  };
}

/**
 * Generate next steps based on issues
 * @param {Object[]} analyzed - Analyzed issues
 * @returns {string[]} List of next steps
 */
function generateNextSteps(analyzed) {
  const steps = [];
  
  const hasAutoFix = analyzed.some(i => i.autoFixable);
  const hasManualFix = analyzed.some(i => !i.autoFixable);
  const filesAffected = new Set(analyzed.map(i => i.component)).size;

  if (hasAutoFix) {
    const count = analyzed.filter(i => i.autoFixable).length;
    steps.push(`Apply ${count} auto-fixable issues (ESLint/Prettier can help)`);
  }

  if (hasManualFix) {
    const count = analyzed.filter(i => !i.autoFixable).length;
    steps.push(`Refactor ${count} issues requiring manual changes`);
  }

  steps.push(`Review changes in ${filesAffected} file(s)`);
  steps.push('Run lint and typecheck after fixes');
  steps.push('Commit with message: "fix: resolve SonarQube issues"');

  return steps;
}

/**
 * Analyze a project and generate full report
 * @param {string} projectKey - Project key
 * @param {string} [pullRequest] - PR number
 * @param {Object} [options] - Analysis options
 * @returns {Promise<Object>} Full analysis report
 */
async function analyzeProject(projectKey, pullRequest, options = {}) {
  const { severities = [], limit = 100 } = options;
  
  const { total, issues } = await getIssues(projectKey, pullRequest, severities, limit);
  const analysis = generateSuggestions(issues);
  
  return {
    projectKey,
    pullRequest,
    timestamp: new Date().toISOString(),
    summary: {
      total,
      ...analysis
    }
  };
}

module.exports = {
  generateSuggestions,
  generateNextSteps,
  analyzeProject
};