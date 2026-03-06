/**
 * SonarQube API Client
 * Handles communication with SonarQube server
 */

const SONAR_HOST = process.env.SONAR_HOST_URL || 'http://127.0.0.1:9000';
const SONAR_TOKEN = process.env.SONAR_TOKEN || 'admin';

/**
 * Make a request to SonarQube API
 * @param {string} endpoint - API endpoint (without /api prefix)
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} API response
 */
async function fetchFromSonarQube(endpoint, params = {}) {
  const url = new URL(`${SONAR_HOST}/api${endpoint}`);
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, value);
    }
  });

  const headers = {};
  
  // Only add auth if token is provided and not default
  if (SONAR_TOKEN && SONAR_TOKEN !== 'admin') {
    headers['Authorization'] = `Basic ${Buffer.from(`${SONAR_TOKEN}:`).toString('base64')}`;
  }

  const response = await fetch(url.toString(), { headers });

  if (!response.ok) {
    throw new Error(`SonarQube API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch issues from SonarQube
 * @param {string} projectKey - Project key
 * @param {string} [pullRequest] - Pull request number
 * @param {string[]} [severities] - Severity filters
 * @param {number} [limit=100] - Maximum issues to fetch
 * @returns {Promise<Object>} Issues data
 */
async function getIssues(projectKey, pullRequest, severities = [], limit = 100) {
  const params = {
    componentKeys: projectKey,
    ps: limit,
    resolved: 'false'
  };

  if (pullRequest) {
    params.pullRequest = pullRequest;
  }

  if (severities.length > 0) {
    params.severities = severities.join(',');
  }

  const data = await fetchFromSonarQube('/issues/search', params);
  
  return {
    total: data.total,
    issues: data.issues.map(issue => ({
      key: issue.key,
      severity: issue.severity,
      component: issue.component.split(':').pop(),
      line: issue.line,
      message: issue.message,
      rule: issue.rule,
      status: issue.status,
      effort: issue.effort,
      type: issue.type
    }))
  };
}

/**
 * Check Quality Gate status
 * @param {string} projectKey - Project key
 * @param {string} [pullRequest] - Pull request number
 * @returns {Promise<Object>} Quality gate status
 */
async function getQualityGate(projectKey, pullRequest) {
  const params = { projectKey };

  if (pullRequest) {
    params.pullRequest = pullRequest;
  }

  try {
    const data = await fetchFromSonarQube('/qualitygates/project_status', params);
    return {
      status: data.projectStatus.status,
      conditions: data.projectStatus.conditions || []
    };
  } catch (error) {
    return {
      status: 'UNKNOWN',
      error: error.message
    };
  }
}

module.exports = {
  fetchFromSonarQube,
  getIssues,
  getQualityGate
};