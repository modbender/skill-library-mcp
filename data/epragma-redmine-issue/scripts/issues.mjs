#!/usr/bin/env node

import { fetchIssue, fetchIssues, updateIssue, fetchProjects, fetchStatuses, createIssue, fetchTimeEntries, createTimeEntry, updateTimeEntry, deleteTimeEntry, fetchTimeEntryActivities, addComment, getBaseUrl } from './lib/redmine.js';

const command = process.argv[2];
const args = process.argv.slice(3);

const BASE_URL = getBaseUrl();

function formatIssuesTable(issues) {
  if (!issues.issues || issues.issues.length === 0) {
    return 'No issues found.';
  }
  
  const totalCount = issues.total_count || issues.issues.length;
  let output = `<b>Found ${totalCount} issue(s):</b>\n\n`;
  
  for (const issue of issues.issues) {
    const id = issue.id;
    const subject = issue.subject || '';
    const project = issue.project?.name || issue.project || '';
    const status = issue.status?.name || issue.status || '';
    const priority = issue.priority?.name || issue.priority || '';
    const updated = issue.updated_on ? new Date(issue.updated_on).toLocaleDateString() : '';
    const url = `${BASE_URL}/issues/${id}`;
    
    output += `<a href="${url}">#${id}</a> ${subject}\n`;
    output += `→ ${project} | ${status} | ${priority} | ${updated}\n\n`;
  }
  
  return output.trim();
}

function formatProjectsTable(projects) {
  if (!projects.projects || projects.projects.length === 0) {
    return 'No projects found.';
  }
  
  const totalCount = projects.total_count || projects.projects.length;
  let output = `Found ${totalCount} project(s):\n\n`;
  
  for (const project of projects.projects) {
    const id = project.id;
    const name = project.name || '';
    const identifier = project.identifier || '';
    const url = `${BASE_URL}/projects/${identifier}`;
    
    output += `- <a href="${url}">#${id}</a> ${name}\n`;
    output += `  Identifier: \`${identifier}\`\n`;
    output += `  ${url}\n\n`;
  }
  
  return output.trim();
}

function formatStatusesTable(statuses) {
  if (!statuses.issue_statuses || statuses.issue_statuses.length === 0) {
    return 'No statuses found.';
  }
  
  const rows = statuses.issue_statuses.map(status => {
    const id = status.id;
    const name = status.name || '';
    const isClosed = status.is_closed ? '✅ Yes' : '❌ No';
    const isDefault = status.is_default ? ' (default)' : '';
    
    return `#${id} → ${name}${isDefault} → Closed: ${isClosed}`;
  }).join('\n');
  
  return `Issue Statuses:\n\nID → Name → Is Closed\n${rows}`;
}

function formatIssueDetail(issue) {
  const i = issue.issue;
  const url = `${BASE_URL}/issues/${i.id}`;
  
  let details = `<a href="${url}">#${i.id}: ${i.subject}</a>\n`;
  details += `${url}\n\n`;
  details += `Status: ${i.status?.name || i.status}\n`;
  details += `Priority: ${i.priority?.name || i.priority}\n`;
  details += `Tracker: ${i.tracker?.name || i.tracker}\n`;
  details += `Assignee: ${i.assigned_to?.name || i.assigned_to || 'Unassigned'}\n`;
  details += `Author: ${i.author?.name || i.author}\n`;
  details += `Created: ${i.created_on ? new Date(i.created_on).toLocaleString() : ''}\n`;
  details += `Updated: ${i.updated_on ? new Date(i.updated_on).toLocaleString() : ''}\n`;
  details += `Done Ratio: ${i.done_ratio || 0}%\n`;
  
  if (i.description) {
    details += `\nDescription:\n${i.description}`;
  }
  
  return details;
}

async function main() {
  switch (command) {
    case 'get': {
      const idIndex = args.indexOf('--id');
      if (idIndex === -1 || !args[idIndex + 1]) {
        console.error('Error: --id is required');
        process.exit(1);
      }
      const id = args[idIndex + 1];
      const issue = await fetchIssue(id);
      console.log(formatIssueDetail(issue));
      break;
    }
    case 'list': {
      const options = {};
      for (let i = 0; i < args.length; i += 2) {
        const key = args[i];
        const value = args[i + 1];
        if (key && value && key.startsWith('--')) {
          const optName = key.replace('--', '').replace(/-/g, '_');
          options[optName] = value;
        }
      }
      if (args.includes('--project')) {
        const projIndex = args.indexOf('--project');
        options.project_id = args[projIndex + 1];
      }
      const issues = await fetchIssues(options);
      console.log(formatIssuesTable(issues));
      break;
    }
    case 'projects': {
      const projects = await fetchProjects();
      console.log(formatProjectsTable(projects));
      break;
    }
    case 'statuses': {
      const statuses = await fetchStatuses();
      console.log(formatStatusesTable(statuses));
      break;
    }
    case 'update': {
      const options = {};
      for (let i = 0; i < args.length; i += 2) {
        const key = args[i];
        const value = args[i + 1];
        if (key && value && key.startsWith('--')) {
          const optName = key.replace('--', '').replace(/-/g, '_');
          options[optName] = value;
        }
      }
      if (!options.id) {
        console.error('Error: --id is required');
        process.exit(1);
      }
      const id = options.id;
      delete options.id;
      const result = await updateIssue(id, options);
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    case 'comment': {
      let id = null;
      let notes = null;
      for (let i = 0; i < args.length; i += 2) {
        const key = args[i];
        const value = args[i + 1];
        if (key === '--id') id = value;
        if (key === '--notes') notes = value;
      }
      if (!id) {
        console.error('Error: --id is required');
        process.exit(1);
      }
      if (!notes) {
        console.error('Error: --notes is required');
        process.exit(1);
      }
      const result = await addComment(id, notes);
      console.log(`Comment added to issue #${id}`);
      break;
    }
    case 'create': {
      const options = {};
      for (let i = 0; i < args.length; i += 2) {
        const key = args[i];
        const value = args[i + 1];
        if (key && value && key.startsWith('--')) {
          const optName = key.replace('--', '').replace(/-/g, '_');
          options[optName] = value;
        }
      }
      if (!options.project_id) {
        console.error('Error: --project-id is required');
        process.exit(1);
      }
      if (!options.subject) {
        console.error('Error: --subject is required');
        process.exit(1);
      }
      const result = await createIssue(options);
      const issue = result.issue;
      const url = `${BASE_URL}/issues/${issue.id}`;
      console.log(`<a href="${url}">#${issue.id}</a> Created: ${issue.subject}`);
      console.log(`Project: ${issue.project?.name || options.project_id}`);
      console.log(`Status: ${issue.status?.name}`);
      console.log(`Priority: ${issue.priority?.name}`);
      console.log(url);
      break;
    }
    case 'time-list': {
      const options = {};
      for (let i = 0; i < args.length; i += 2) {
        const key = args[i];
        const value = args[i + 1];
        if (key && value && key.startsWith('--')) {
          const optName = key.replace('--', '').replace(/-/g, '_');
          options[optName] = value;
        }
      }
      const timeEntries = await fetchTimeEntries(options);
      if (!timeEntries.time_entries || timeEntries.time_entries.length === 0) {
        console.log('No time entries found.');
        break;
      }
      let output = `<b>Time Entries (${timeEntries.total_count || timeEntries.time_entries.length}):</b>\n\n`;
      for (const entry of timeEntries.time_entries) {
        const url = `${BASE_URL}/issues/${entry.issue?.id || entry.issue}`;
        output += `<a href="${url}">#${entry.issue?.id || entry.issue}</a> | ${entry.hours}h | ${entry.spent_on}`;
        if (entry.activity) output += ` | ${entry.activity.name}`;
        if (entry.comments) output += ` | ${entry.comments}`;
        output += '\n';
      }
      console.log(output.trim());
      break;
    }
    case 'time-add': {
      const options = {};
      for (let i = 0; i < args.length; i += 2) {
        const key = args[i];
        const value = args[i + 1];
        if (key && value && key.startsWith('--')) {
          const optName = key.replace('--', '').replace(/-/g, '_');
          options[optName] = value;
        }
      }
      if (!options.issue_id && !options.project_id) {
        console.error('Error: --issue-id or --project-id is required');
        process.exit(1);
      }
      if (!options.hours) {
        console.error('Error: --hours is required');
        process.exit(1);
      }
      const result = await createTimeEntry(options);
      const entry = result.time_entry;
      console.log(`✅ Time entry #${entry.id} created: ${entry.hours}h on issue #${entry.issue?.id || entry.project_id}`);
      if (entry.comments) console.log(`   Comment: ${entry.comments}`);
      break;
    }
    case 'time-activities': {
      const activities = await fetchTimeEntryActivities();
      if (!activities.time_entry_activities || activities.time_entry_activities.length === 0) {
        console.log('No activities found.');
        break;
      }
      console.log('<b>Time Entry Activities:</b>\n');
      for (const activity of activities.time_entry_activities) {
        console.log(`#${activity.id} → ${activity.name}`);
      }
      break;
    }
    default:
      console.error(`Unknown command: ${command}`);
      console.error('Available commands: get, list, projects, statuses, update, create, time-list, time-add, time-activities');
      process.exit(1);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
