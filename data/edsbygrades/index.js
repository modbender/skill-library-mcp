const { chromium } = require('playwright');
const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

// Load config from env or OpenClaw config
const config = {
  EDSBY_HOST: process.env.EDSBY_HOST || 'https://your-school.edsby.com',
  GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
  GOOGLE_REDIRECT_URI: process.env.GOOGLE_REDIRECT_URI,
  GOOGLE_CALENDAR_ID: process.env.GOOGLE_CALENDAR_ID || 'primary',
  BROWSER_CONTEXT_PATH: process.env.BROWSER_CONTEXT_PATH || path.join(process.env.HOME, '.openclaw/browser-contexts/edsby')
};

// One-time auth setup (run manually if needed)
if (process.argv.includes('--auth')) {
  authSetup();
}

async function authSetup() {
  const browser = await chromium.launchPersistentContext(config.BROWSER_CONTEXT_PATH, { headless: false });
  const page = await browser.newPage();
  await page.goto(`${config.EDSBY_HOST}/login`);
  // Manual intervention: Click 'Sign in with Google', enter creds
  console.log('Complete Google OAuth in the browser, then close it.');
  // Wait for user to complete and close browser
  process.exit(0);
}

// Helper to get authenticated Calendar client
async function getCalendarClient() {
  const oauth2Client = new google.auth.OAuth2(
    config.GOOGLE_CLIENT_ID,
    config.GOOGLE_CLIENT_SECRET,
    config.GOOGLE_REDIRECT_URI
  );
  // Assume tokens saved from previous setup; load from file or prompt
  const tokens = JSON.parse(fs.readFileSync('google-tokens.json', 'utf-8')); // Save tokens after first auth
  oauth2Client.setCredentials(tokens);
  return google.calendar({ version: 'v3', auth: oauth2Client });
}

// Tool: Fetch data from Edsby using browser
async function fetchEdsbyData() {
  const browser = await chromium.launchPersistentContext(config.BROWSER_CONTEXT_PATH, { headless: true });
  const page = await browser.newPage();
  await page.goto(`${config.EDSBY_HOST}/dashboard`); // Or /mywork for grades/assignments

  // Placeholders for selectors (update from dev tools)
  const classes = await page.evaluate(() => Array.from(document.querySelectorAll('.class-list-item')).map(el => ({
    name: el.querySelector('.class-name')?.textContent.trim(),
    id: el.getAttribute('data-id')
  })));

  const grades = [];
  for (const cls of classes) {
    await page.goto(`${config.EDSBY_HOST}/class/${cls.id}/grades`);
    const classGrades = await page.evaluate(() => ({
      average: document.querySelector('.average-grade')?.textContent.trim(),
      details: Array.from(document.querySelectorAll('.grade-row')).map(row => ({
        assignment: row.querySelector('.assignment-name')?.textContent.trim(),
        grade: row.querySelector('.grade-value')?.textContent.trim()
      }))
    }));
    grades.push({ class: cls.name, ...classGrades });
  }

  const assignments = [];
  await page.goto(`${config.EDSBY_HOST}/mywork/assignments`);
  assignments = await page.evaluate(() => Array.from(document.querySelectorAll('.assignment-item')).map(item => ({
    title: item.querySelector('.assignment-title')?.textContent.trim(),
    class: item.querySelector('.assignment-class')?.textContent.trim(),
    dueDate: item.querySelector('.due-date')?.textContent.trim() // Parse to ISO if needed
  })));

  await browser.close();
  return { classes, grades, assignments };
}

module.exports = {
  name: 'edsby-student-integration',
  tools: [
    {
      name: 'edsby_fetch_data',
      description: 'Fetch classes, grades, and assignments from Edsby.',
      parameters: {},
      async execute() {
        return await fetchEdsbyData();
      }
    },
    {
      name: 'edsby_generate_report',
      description: 'Generate personalized report from Edsby data.',
      parameters: { data: { type: 'object' } },
      async execute({ data }) {
        let report = '# Edsby Personalized Report\n';
        report += '## Classes:\n' + data.classes.map(c => `- ${c.name}`).join('\n');
        report += '\n## Grades:\n' + data.grades.map(g => `- ${g.class}: ${g.average} (Details: ${g.details.map(d => `${d.assignment}: ${d.grade}`).join(', ')})`).join('\n');
        report += '\n## Assignments:\n' + data.assignments.map(a => `- ${a.title} in ${a.class} due ${a.dueDate}`).join('\n');
        return report;
      }
    },
    {
      name: 'edsby_sync_assignments',
      description: 'Sync assignments to Google Calendar.',
      parameters: { assignments: { type: 'array' } },
      async execute({ assignments }) {
        const calendar = await getCalendarClient();
        for (const a of assignments) {
          const event = {
            summary: `Assignment Due: ${a.title} (${a.class})`,
            start: { dateTime: new Date(a.dueDate).toISOString() },
            end: { dateTime: new Date(a.dueDate).toISOString() },
          };
          await calendar.events.insert({ calendarId: config.GOOGLE_CALENDAR_ID, resource: event });
        }
        return 'Assignments synced to Calendar.';
      }
    },
    {
      name: 'edsby_generate_summary_improvements',
      description: 'Bi-weekly grade summary and improvements.',
      parameters: { grades: { type: 'array' } },
      async execute({ grades }) {
        const averages = grades.map(g => parseFloat(g.average.replace('%', '')));
        const gpa = averages.reduce((a, b) => a + b, 0) / averages.length;
        let summary = `# Bi-Weekly Grade Summary\nOverall GPA: ${gpa.toFixed(2)}\n`;
        summary += 'Improvements:\n' + grades.map(g => {
          if (parseFloat(g.average) < 80) return `- ${g.class}: Low grade—suggest daily review and practice problems.`;
          return `- ${g.class}: Solid—maintain with weekly quizzes.`;
        }).join('\n');
        return summary;
      }
    },
    {
      name: 'edsby_daily_check',
      description: 'Daily check assignments and sync.',
      parameters: {},
      async execute() {
        const data = await fetchEdsbyData();
        await module.exports.tools.find(t => t.name === 'edsby_sync_assignments').execute({ assignments: data.assignments });
        return 'Daily check complete: Assignments updated in Calendar.';
      }
    }
  ]
};