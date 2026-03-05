const REDMINE_URL = process.env.REDMINE_URL || process.env.REDMINE_API_KEY?.startsWith('http') || '';
const API_KEY = process.env.REDMINE_API_KEY || process.env.REDMINE_BASE_URL || '';

function getBaseUrl() {
  if (REDMINE_URL?.startsWith('http')) {
    return REDMINE_URL;
  }
  if (API_KEY?.startsWith('http')) {
    return API_KEY;
  }
  if (!REDMINE_URL || !API_KEY) {
    throw new Error('REDMINE_URL and REDMINE_API_KEY environment variables are required. Configure them with: openclaw skills config epragma-redmine-issue set REDMINE_URL <your-redmine-url> and openclaw skills config epragma-redmine-issue set REDMINE_API_KEY <your-api-key>');
  }
  return REDMINE_URL;
}

function getApiKey() {
  if (REDMINE_URL?.startsWith('http')) {
    return API_KEY;
  }
  if (API_KEY?.startsWith('http')) {
    return process.env.REDMINE_BASE_URL || '';
  }
  return API_KEY;
}

export { getBaseUrl, getApiKey };

async function request(endpoint, options = {}) {
  const baseUrl = getBaseUrl();
  const apiKey = getApiKey();
  
  const url = `${baseUrl}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    'X-Redmine-API-Key': apiKey,
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Redmine API error: ${response.status} ${response.statusText} - ${error}`);
  }

  // Handle empty responses (e.g., DELETE, some PUT requests)
  const text = await response.text();
  if (!text || text.trim() === '') {
    return { success: true };
  }

  return JSON.parse(text);
}

export async function fetchIssue(id) {
  return request(`/issues/${id}.json?include=journals,relations,changesets`);
}

export async function fetchIssues(options = {}) {
  const params = new URLSearchParams();
  
  if (options.project_id) params.append('project_id', options.project_id);
  if (options.status_id) params.append('status_id', options.status_id);
  if (options.assigned_to_id) params.append('assigned_to_id', options.assigned_to_id);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  if (options.sort) params.append('sort', options.sort);
  if (options.tracker_id) params.append('tracker_id', options.tracker_id);
  if (options.priority_id) params.append('priority_id', options.priority_id);
  
  const queryString = params.toString();
  const endpoint = `/issues.json${queryString ? '?' + queryString : ''}`;
  
  return request(endpoint);
}

export async function updateIssue(id, options = {}) {
  const issue = {};
  const journal = {};
  
  if (options.status_id) issue.status_id = parseInt(options.status_id, 10);
  if (options.assigned_to_id) issue.assigned_to_id = parseInt(options.assigned_to_id, 10);
  if (options.priority_id) issue.priority_id = parseInt(options.priority_id, 10);
  if (options.done_ratio) issue.done_ratio = parseInt(options.done_ratio, 10);
  if (options.notes) journal.notes = options.notes;
  
  const body = { issue };
  if (Object.keys(journal).length > 0) {
    body.issue = { ...issue, ...journal };
  }
  
  return request(`/issues/${id}.json`, {
    method: 'PUT',
    body: JSON.stringify({ issue: body.issue }),
  });
}

export async function addComment(id, notes) {
  return request(`/issues/${id}.json`, {
    method: 'PUT',
    body: JSON.stringify({ issue: { notes } }),
  });
}

export async function fetchProjects() {
  return request('/projects.json?limit=100');
}

export async function fetchStatuses() {
  return request('/issue_statuses.json');
}

export async function createIssue(options = {}) {
  const issue = {};
  
  if (!options.project_id) {
    throw new Error('project_id is required');
  }
  issue.project_id = options.project_id;
  
  if (!options.subject) {
    throw new Error('subject is required');
  }
  issue.subject = options.subject;
  
  if (options.description) issue.description = options.description;
  if (options.tracker_id) issue.tracker_id = parseInt(options.tracker_id, 10);
  if (options.status_id) issue.status_id = parseInt(options.status_id, 10);
  if (options.priority_id) issue.priority_id = parseInt(options.priority_id, 10);
  if (options.assigned_to_id) issue.assigned_to_id = parseInt(options.assigned_to_id, 10);
  if (options.fixed_version_id) issue.fixed_version_id = parseInt(options.fixed_version_id, 10);
  if (options.parent_issue_id) issue.parent_issue_id = parseInt(options.parent_issue_id, 10);
  if (options.start_date) issue.start_date = options.start_date;
  if (options.due_date) issue.due_date = options.due_date;
  if (options.done_ratio) issue.done_ratio = parseInt(options.done_ratio, 10);
  if (options.estimated_hours) issue.estimated_hours = parseFloat(options.estimated_hours);
  
  return request('/issues.json', {
    method: 'POST',
    body: JSON.stringify({ issue }),
  });
}

export async function fetchTimeEntries(options = {}) {
  const params = new URLSearchParams();
  
  if (options.issue_id) params.append('issue_id', options.issue_id);
  if (options.project_id) params.append('project_id', options.project_id);
  if (options.user_id) params.append('user_id', options.user_id);
  if (options.from) params.append('from', options.from);
  if (options.to) params.append('to', options.to);
  if (options.spent_on) params.append('spent_on', options.spent_on);
  if (options.limit) params.append('limit', options.limit);
  if (options.offset) params.append('offset', options.offset);
  
  const queryString = params.toString();
  const endpoint = `/time_entries.json${queryString ? '?' + queryString : ''}`;
  
  return request(endpoint);
}

export async function createTimeEntry(options = {}) {
  const timeEntry = {};
  
  if (options.issue_id) {
    timeEntry.issue_id = parseInt(options.issue_id, 10);
  }
  if (options.project_id) {
    timeEntry.project_id = parseInt(options.project_id, 10);
  }
  
  if (!options.issue_id && !options.project_id) {
    throw new Error('issue_id or project_id is required');
  }
  if (!options.hours) {
    throw new Error('hours is required');
  }
  timeEntry.hours = parseFloat(options.hours);
  
  if (options.spent_on) timeEntry.spent_on = options.spent_on;
  if (options.comments) timeEntry.comments = options.comments;
  if (options.activity_id) timeEntry.activity_id = parseInt(options.activity_id, 10);
  
  return request('/time_entries.json', {
    method: 'POST',
    body: JSON.stringify({ time_entry: timeEntry }),
  });
}

export async function updateTimeEntry(id, options = {}) {
  const timeEntry = {};
  
  if (options.hours) timeEntry.hours = parseFloat(options.hours);
  if (options.spent_on) timeEntry.spent_on = options.spent_on;
  if (options.comments) timeEntry.comments = options.comments;
  if (options.activity_id) timeEntry.activity_id = parseInt(options.activity_id, 10);
  
  return request(`/time_entries/${id}.json`, {
    method: 'PUT',
    body: JSON.stringify({ time_entry: timeEntry }),
  });
}

export async function deleteTimeEntry(id) {
  return request(`/time_entries/${id}.json`, {
    method: 'DELETE',
  });
}

export async function fetchTimeEntryActivities() {
  return request('/enumerations/time_entry_activities.json');
}
