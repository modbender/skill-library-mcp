#!/usr/bin/env node

/**
 * Shadow AI Monitor - Dashboard Generator (Enterprise Edition)
 * Creates HTML dashboard from data JSON
 */

const fs = require('fs');
const path = require('path');

// Read data file
const dataPath = process.argv[2] || path.join(process.cwd(), 'shadow-ai-data.json');

if (!fs.existsSync(dataPath)) {
  console.error(`❌ Data file not found: ${dataPath}`);
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

// Generate HTML
function generateHTML(data) {
  const { company, employeeCount, period, events, metrics } = data;
  const { totalEvents, topTools, riskCounts, topEmployees, dailyUsage, complianceScore, recommendations } = metrics;
  
  // Prepare chart data
  const toolLabels = topTools.map(t => t[0]);
  const toolData = topTools.map(t => t[1]);
  
  const riskLabels = ['Low', 'Medium', 'High'];
  const riskData = [riskCounts.Low, riskCounts.Medium, riskCounts.High];
  const riskColors = ['#4ade80', '#fbbf24', '#ef4444'];
  
  const employeeLabels = topEmployees.map(e => e[0]);
  const employeeData = topEmployees.map(e => e[1]);
  
  const dailyLabels = Object.keys(dailyUsage).sort();
  const dailyData = dailyLabels.map(d => dailyUsage[d]);
  
  // Compliance color
  let complianceColor = '#ef4444'; // red
  if (complianceScore >= 70) complianceColor = '#fbbf24'; // yellow
  if (complianceScore >= 85) complianceColor = '#4ade80'; // green
  
  // Generate personalized recommendations
  const personalizedRecs = [];
  
  // Find top offender
  const topEmployee = topEmployees[0];
  const topEmployeeEvents = events.filter(e => e.employee === topEmployee[0]);
  const topEmployeeHighRisk = topEmployeeEvents.filter(e => e.risk === 'High').length;
  
  if (topEmployeeHighRisk >= 5) {
    personalizedRecs.push(`${topEmployee[0]} generated ${topEmployeeHighRisk} high-risk events this week involving sensitive data — immediate review and retraining recommended.`);
  }
  
  // Tool-specific recommendation
  const topToolName = topTools[0][0];
  const topToolCount = topTools[0][1];
  const topToolPct = Math.round((topToolCount / totalEvents) * 100);
  
  if (topToolPct > 30) {
    personalizedRecs.push(`${topToolName} accounts for ${topToolPct}% of all AI tool usage at ${company}. Deploy enterprise agreement or implement approved alternatives to ensure data residency compliance.`);
  }
  
  // High risk percentage
  const highRiskPct = Math.round((riskCounts.High / totalEvents) * 100);
  if (highRiskPct > 20) {
    personalizedRecs.push(`${highRiskPct}% of AI interactions at ${company} involve high-risk data categories (client matters, health records, financial info). Implement data classification policy and DLP monitoring immediately.`);
  }
  
  // Compliance-specific
  if (complianceScore < 50) {
    personalizedRecs.push(`${company}'s PIPEDA compliance score of ${complianceScore}/100 indicates critical gaps in AI governance. Review the compliance breakdown to address specific requirement failures.`);
  }
  
  // General if not enough specific ones
  while (personalizedRecs.length < 3) {
    if (personalizedRecs.length === 0) {
      personalizedRecs.push('Deploy browser extension to monitor and log AI tool usage in real-time across all endpoints.');
    } else if (personalizedRecs.length === 1) {
      personalizedRecs.push('Establish AI Acceptable Use Policy and require all employees to complete mandatory training within 30 days.');
    } else {
      personalizedRecs.push('Schedule quarterly audits of AI tool usage patterns to identify emerging risks and compliance gaps.');
    }
  }
  
  // Last 20 events for table
  const recentEvents = events.slice(0, 20);
  
  // PIPEDA requirements
  const pipedaRequirements = [
    {
      id: 'P1',
      name: 'Consent for Collection',
      status: complianceScore > 70 ? 'pass' : 'fail',
      description: 'Organizations must obtain meaningful consent before collecting personal information.',
      fix: `Implement AI tool usage consent form. Require ${company} employees to acknowledge that AI tool interactions may be monitored and that they must not share client personal information without explicit consent.`
    },
    {
      id: 'P2',
      name: 'Limiting Use, Disclosure & Retention',
      status: complianceScore > 60 ? 'pass' : 'fail',
      description: 'Personal information must only be used for specified purposes.',
      fix: `Your data shows ${riskCounts.High} high-risk events where sensitive data was shared with AI tools. Create AI Acceptable Use Policy defining approved tools and prohibited data categories.`
    },
    {
      id: 'P3',
      name: 'Safeguards',
      status: complianceScore > 50 ? 'pass' : 'fail',
      description: 'Organizations must protect personal information with security safeguards.',
      fix: `Deploy DLP (Data Loss Prevention) monitoring on AI tool domains. ${topToolName} alone has ${topToolCount} interactions — none are currently monitored for data leakage.`
    },
    {
      id: 'P4',
      name: 'Openness',
      status: complianceScore > 40 ? 'pass' : 'fail',
      description: 'Organizations must be transparent about their personal information management practices.',
      fix: `Create public-facing AI usage disclosure statement. Document which AI tools ${company} uses, what data flows to them, and how client information is protected.`
    },
    {
      id: 'P5',
      name: 'Individual Access',
      status: complianceScore > 30 ? 'pass' : 'fail',
      description: 'Individuals have the right to access and correct their personal information.',
      fix: `Establish process for clients to request disclosure of any AI tool interactions involving their data. Currently no audit trail exists for ${riskCounts.High} high-risk events.`
    }
  ];
  
  // Prepare employee drill-down data
  const employeeDrilldown = {};
  topEmployees.forEach(([emp, count]) => {
    const empEvents = events.filter(e => e.employee === emp);
    const highRiskEvents = empEvents
      .filter(e => e.risk === 'High')
      .slice(0, 3)
      .map(e => ({
        tool: e.tool,
        category: e.dataCategory,
        date: new Date(e.timestamp).toLocaleDateString(),
        risk: e.risk
      }));
    
    const riskBreakdown = {
      High: empEvents.filter(e => e.risk === 'High').length,
      Medium: empEvents.filter(e => e.risk === 'Medium').length,
      Low: empEvents.filter(e => e.risk === 'Low').length
    };
    
    employeeDrilldown[emp] = {
      total: count,
      riskBreakdown,
      topRiskyEvents: highRiskEvents.length > 0 ? highRiskEvents : empEvents.slice(0, 3).map(e => ({
        tool: e.tool,
        category: e.dataCategory,
        date: new Date(e.timestamp).toLocaleDateString(),
        risk: e.risk
      }))
    };
  });
  
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shadow AI Monitor - ${company}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      background: #0a0a0a;
      color: #e5e5e5;
      padding: 2rem;
      line-height: 1.6;
    }
    
    .container {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    header {
      margin-bottom: 3rem;
      border-bottom: 2px solid #27272a;
      padding-bottom: 1.5rem;
      position: relative;
    }
    
    .export-btn {
      position: absolute;
      top: 0;
      right: 0;
      background: #3b82f6;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    
    .export-btn:hover {
      background: #2563eb;
    }
    
    h1 {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: #fafafa;
    }
    
    .subtitle {
      color: #a1a1aa;
      font-size: 1.1rem;
    }
    
    .meta {
      display: flex;
      gap: 2rem;
      margin-top: 1rem;
      color: #71717a;
      font-size: 0.95rem;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }
    
    .stat-card {
      background: #18181b;
      border: 1px solid #27272a;
      border-radius: 12px;
      padding: 1.5rem;
      transition: border-color 0.2s;
    }
    
    .stat-card:hover {
      border-color: #3f3f46;
    }
    
    .stat-card.clickable {
      cursor: pointer;
    }
    
    .stat-card.clickable:hover {
      border-color: #3b82f6;
      transform: translateY(-2px);
      transition: all 0.2s;
    }
    
    .stat-label {
      color: #a1a1aa;
      font-size: 0.9rem;
      margin-bottom: 0.5rem;
    }
    
    .stat-value {
      font-size: 2.5rem;
      font-weight: 700;
      color: #fafafa;
    }
    
    .stat-value.large {
      font-size: 3.5rem;
    }
    
    .compliance-score {
      color: ${complianceColor};
    }
    
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 2rem;
      margin-bottom: 3rem;
    }
    
    .chart-card {
      background: #18181b;
      border: 1px solid #27272a;
      border-radius: 12px;
      padding: 1.5rem;
    }
    
    .chart-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: #fafafa;
    }
    
    .chart-container {
      position: relative;
      height: 300px;
    }
    
    .recommendations {
      background: #18181b;
      border: 1px solid #27272a;
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 3rem;
    }
    
    .recommendations h2 {
      font-size: 1.5rem;
      margin-bottom: 1.5rem;
      color: #fafafa;
    }
    
    .recommendation {
      background: #0a0a0a;
      border-left: 3px solid #ef4444;
      padding: 1rem 1.5rem;
      margin-bottom: 1rem;
      border-radius: 4px;
      color: #d4d4d8;
    }
    
    .recommendation:last-child {
      margin-bottom: 0;
    }
    
    .heatmap {
      background: #18181b;
      border: 1px solid #27272a;
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 3rem;
    }
    
    .heatmap h2 {
      font-size: 1.5rem;
      margin-bottom: 1.5rem;
      color: #fafafa;
    }
    
    .heatmap-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 0.5rem;
      max-width: 600px;
    }
    
    .heatmap-cell {
      background: #27272a;
      padding: 1rem;
      border-radius: 6px;
      text-align: center;
      font-size: 0.85rem;
      transition: background 0.2s;
    }
    
    .heatmap-cell:hover {
      background: #3f3f46;
    }
    
    .heatmap-cell-label {
      color: #a1a1aa;
      margin-bottom: 0.25rem;
    }
    
    .heatmap-cell-value {
      color: #fafafa;
      font-weight: 600;
      font-size: 1.1rem;
    }
    
    .heatmap-cell.high {
      background: #7f1d1d;
    }
    
    .heatmap-cell.medium {
      background: #78350f;
    }
    
    .heatmap-cell.low {
      background: #14532d;
    }
    
    /* Event Log Table */
    .event-log {
      background: #18181b;
      border: 1px solid #27272a;
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 3rem;
    }
    
    .event-log h2 {
      font-size: 1.5rem;
      margin-bottom: 1.5rem;
      color: #fafafa;
    }
    
    .table-container {
      overflow-x: auto;
      max-height: 500px;
      overflow-y: auto;
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
    }
    
    thead {
      position: sticky;
      top: 0;
      background: #0a0a0a;
      z-index: 10;
    }
    
    th {
      text-align: left;
      padding: 1rem;
      color: #a1a1aa;
      font-weight: 600;
      font-size: 0.9rem;
      border-bottom: 2px solid #27272a;
    }
    
    td {
      padding: 1rem;
      border-bottom: 1px solid #27272a;
      font-size: 0.95rem;
    }
    
    tr:hover {
      background: #27272a;
    }
    
    tr.high-risk {
      background: rgba(127, 29, 29, 0.3);
    }
    
    tr.high-risk:hover {
      background: rgba(127, 29, 29, 0.5);
    }
    
    .risk-badge {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 600;
    }
    
    .risk-badge.low {
      background: #14532d;
      color: #4ade80;
    }
    
    .risk-badge.medium {
      background: #78350f;
      color: #fbbf24;
    }
    
    .risk-badge.high {
      background: #7f1d1d;
      color: #ef4444;
    }
    
    /* Modal Styles */
    .modal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(4px);
    }
    
    .modal.active {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .modal-content {
      background: #18181b;
      border: 1px solid #27272a;
      border-radius: 16px;
      padding: 2rem;
      max-width: 600px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
      position: relative;
    }
    
    .modal-close {
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: none;
      border: none;
      color: #a1a1aa;
      font-size: 1.5rem;
      cursor: pointer;
      padding: 0.5rem;
      line-height: 1;
    }
    
    .modal-close:hover {
      color: #fafafa;
    }
    
    .modal h2 {
      font-size: 1.75rem;
      margin-bottom: 1rem;
      color: #fafafa;
    }
    
    .modal h3 {
      font-size: 1.25rem;
      margin-top: 1.5rem;
      margin-bottom: 0.75rem;
      color: #fafafa;
    }
    
    .modal-section {
      margin-bottom: 1.5rem;
    }
    
    .modal-stat {
      display: flex;
      justify-content: space-between;
      padding: 0.75rem;
      background: #0a0a0a;
      border-radius: 6px;
      margin-bottom: 0.5rem;
    }
    
    .event-item {
      background: #0a0a0a;
      padding: 1rem;
      border-radius: 6px;
      margin-bottom: 0.75rem;
      border-left: 3px solid #ef4444;
    }
    
    .event-item.medium {
      border-left-color: #fbbf24;
    }
    
    .event-item.low {
      border-left-color: #4ade80;
    }
    
    .event-meta {
      display: flex;
      gap: 1rem;
      font-size: 0.85rem;
      color: #a1a1aa;
      margin-top: 0.5rem;
    }
    
    .pipeda-req {
      background: #0a0a0a;
      padding: 1.25rem;
      border-radius: 8px;
      margin-bottom: 1rem;
      border-left: 4px solid #ef4444;
    }
    
    .pipeda-req.pass {
      border-left-color: #4ade80;
    }
    
    .pipeda-req-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }
    
    .pipeda-req-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #fafafa;
    }
    
    .pipeda-status {
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 600;
    }
    
    .pipeda-status.pass {
      background: #14532d;
      color: #4ade80;
    }
    
    .pipeda-status.fail {
      background: #7f1d1d;
      color: #ef4444;
    }
    
    .pipeda-desc {
      color: #a1a1aa;
      font-size: 0.9rem;
      margin-bottom: 0.75rem;
    }
    
    .pipeda-fix {
      color: #d4d4d8;
      font-size: 0.95rem;
      background: rgba(59, 130, 246, 0.1);
      padding: 0.75rem;
      border-radius: 6px;
      margin-top: 0.75rem;
    }
    
    .pipeda-fix strong {
      color: #3b82f6;
    }
    
    footer {
      text-align: center;
      color: #71717a;
      padding-top: 2rem;
      border-top: 1px solid #27272a;
      margin-top: 3rem;
    }
    
    @media print {
      body {
        background: white;
        color: black;
      }
      
      .export-btn {
        display: none;
      }
      
      header {
        border-bottom: 2px solid #e5e5e5;
      }
      
      header::before {
        content: "${company}";
        display: block;
        font-size: 1.5rem;
        font-weight: 700;
        color: #3b82f6;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3b82f6;
      }
      
      .stat-card, .chart-card, .recommendations, .heatmap, .event-log {
        background: white;
        border: 1px solid #e5e5e5;
        page-break-inside: avoid;
      }
      
      .modal {
        display: none !important;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <button class="export-btn" onclick="window.print()">
        <span>📄</span>
        <span>Export to PDF</span>
      </button>
      <h1>🔍 Shadow AI Monitor</h1>
      <p class="subtitle">${company} - Employee AI Tool Usage Report</p>
      <div class="meta">
        <span>📅 Period: ${period}</span>
        <span>👥 Employees: ${employeeCount}</span>
        <span>📊 Total Events: ${totalEvents}</span>
        <span>⏰ Generated: ${new Date(data.generated).toLocaleString()}</span>
      </div>
    </header>
    
    <div class="stats-grid">
      <div class="stat-card clickable" onclick="showComplianceModal()">
        <div class="stat-label">PIPEDA Compliance Score 🔍</div>
        <div class="stat-value large compliance-score">${complianceScore}/100</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">High Risk Events</div>
        <div class="stat-value" style="color: #ef4444">${riskCounts.High}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">Medium Risk Events</div>
        <div class="stat-value" style="color: #fbbf24">${riskCounts.Medium}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">Low Risk Events</div>
        <div class="stat-value" style="color: #4ade80">${riskCounts.Low}</div>
      </div>
    </div>
    
    <div class="recommendations">
      <h2>⚠️ Top 3 Recommendations for ${company}</h2>
      ${personalizedRecs.map((rec, i) => `
        <div class="recommendation">
          <strong>${i + 1}.</strong> ${rec}
        </div>
      `).join('')}
    </div>
    
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-title">Top 3 AI Tools</div>
        <div class="chart-container">
          <canvas id="toolsChart"></canvas>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-title">Risk Distribution</div>
        <div class="chart-container">
          <canvas id="riskChart"></canvas>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-title">Daily Usage Trend</div>
        <div class="chart-container">
          <canvas id="dailyChart"></canvas>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-title">Top 10 Employees (Click for Details)</div>
        <div class="chart-container">
          <canvas id="employeeChart"></canvas>
        </div>
      </div>
    </div>
    
    <div class="event-log">
      <h2>📋 Recent Activity Log (Last 20 Events)</h2>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Employee</th>
              <th>AI Tool</th>
              <th>Data Category</th>
              <th>Risk Level</th>
            </tr>
          </thead>
          <tbody>
            ${recentEvents.map(event => `
              <tr class="${event.risk.toLowerCase()}-risk">
                <td>${new Date(event.timestamp).toLocaleString()}</td>
                <td>${event.employee}</td>
                <td>${event.tool}</td>
                <td>${event.dataCategory}</td>
                <td><span class="risk-badge ${event.risk.toLowerCase()}">${event.risk}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="heatmap">
      <h2>📊 Employee Usage Heatmap (Top 10)</h2>
      <div class="heatmap-grid">
        ${topEmployees.map(([emp, count]) => {
          let riskClass = 'low';
          if (count > totalEvents * 0.1) riskClass = 'high';
          else if (count > totalEvents * 0.05) riskClass = 'medium';
          
          return `
            <div class="heatmap-cell ${riskClass}">
              <div class="heatmap-cell-label">${emp}</div>
              <div class="heatmap-cell-value">${count}</div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
    
    <footer>
      <p>Shadow AI Monitor - Enterprise Edition</p>
      <p>Built with OpenClaw | For ${company}</p>
    </footer>
  </div>
  
  <!-- Employee Drill-down Modal -->
  <div id="employeeModal" class="modal">
    <div class="modal-content">
      <button class="modal-close" onclick="closeEmployeeModal()">×</button>
      <h2 id="modalEmployeeName"></h2>
      
      <div class="modal-section">
        <h3>Risk Breakdown</h3>
        <div class="modal-stat">
          <span style="color: #ef4444">High Risk</span>
          <span id="modalHighRisk"></span>
        </div>
        <div class="modal-stat">
          <span style="color: #fbbf24">Medium Risk</span>
          <span id="modalMediumRisk"></span>
        </div>
        <div class="modal-stat">
          <span style="color: #4ade80">Low Risk</span>
          <span id="modalLowRisk"></span>
        </div>
      </div>
      
      <div class="modal-section">
        <h3>Top 3 Riskiest Events This Week</h3>
        <div id="modalEvents"></div>
      </div>
    </div>
  </div>
  
  <!-- Compliance Modal -->
  <div id="complianceModal" class="modal">
    <div class="modal-content">
      <button class="modal-close" onclick="closeComplianceModal()">×</button>
      <h2>PIPEDA Compliance Analysis</h2>
      <p style="color: #a1a1aa; margin-bottom: 2rem;">
        Current Score: <strong style="color: ${complianceColor}">${complianceScore}/100</strong>
      </p>
      
      ${pipedaRequirements.map(req => `
        <div class="pipeda-req ${req.status}">
          <div class="pipeda-req-header">
            <span class="pipeda-req-title">${req.id}: ${req.name}</span>
            <span class="pipeda-status ${req.status}">${req.status === 'pass' ? '✓ Pass' : '✗ Fail'}</span>
          </div>
          <div class="pipeda-desc">${req.description}</div>
          ${req.status === 'fail' ? `
            <div class="pipeda-fix">
              <strong>Action Required:</strong> ${req.fix}
            </div>
          ` : ''}
        </div>
      `).join('')}
    </div>
  </div>
  
  <script>
    const employeeDrilldown = ${JSON.stringify(employeeDrilldown)};
    
    Chart.defaults.color = '#a1a1aa';
    Chart.defaults.borderColor = '#27272a';
    
    // Tools Chart
    new Chart(document.getElementById('toolsChart'), {
      type: 'bar',
      data: {
        labels: ${JSON.stringify(toolLabels)},
        datasets: [{
          label: 'Usage Count',
          data: ${JSON.stringify(toolData)},
          backgroundColor: '#3b82f6',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
    
    // Risk Chart
    new Chart(document.getElementById('riskChart'), {
      type: 'doughnut',
      data: {
        labels: ${JSON.stringify(riskLabels)},
        datasets: [{
          data: ${JSON.stringify(riskData)},
          backgroundColor: ${JSON.stringify(riskColors)},
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
    
    // Daily Chart
    new Chart(document.getElementById('dailyChart'), {
      type: 'line',
      data: {
        labels: ${JSON.stringify(dailyLabels)},
        datasets: [{
          label: 'Events',
          data: ${JSON.stringify(dailyData)},
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
    
    // Employee Chart with click handling
    const employeeChart = new Chart(document.getElementById('employeeChart'), {
      type: 'bar',
      data: {
        labels: ${JSON.stringify(employeeLabels)},
        datasets: [{
          label: 'Usage Count',
          data: ${JSON.stringify(employeeData)},
          backgroundColor: '#10b981',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { beginAtZero: true }
        },
        onClick: (event, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const employeeName = ${JSON.stringify(employeeLabels)}[index];
            showEmployeeModal(employeeName);
          }
        }
      }
    });
    
    // Modal functions
    function showEmployeeModal(employeeName) {
      const data = employeeDrilldown[employeeName];
      if (!data) return;
      
      document.getElementById('modalEmployeeName').textContent = employeeName + ' - Activity Details';
      document.getElementById('modalHighRisk').textContent = data.riskBreakdown.High;
      document.getElementById('modalMediumRisk').textContent = data.riskBreakdown.Medium;
      document.getElementById('modalLowRisk').textContent = data.riskBreakdown.Low;
      
      const eventsHTML = data.topRiskyEvents.map(event => \`
        <div class="event-item \${event.risk.toLowerCase()}">
          <div><strong>\${event.tool}</strong> - \${event.category}</div>
          <div class="event-meta">
            <span>📅 \${event.date}</span>
            <span class="risk-badge \${event.risk.toLowerCase()}">\${event.risk} Risk</span>
          </div>
        </div>
      \`).join('');
      
      document.getElementById('modalEvents').innerHTML = eventsHTML;
      document.getElementById('employeeModal').classList.add('active');
    }
    
    function closeEmployeeModal() {
      document.getElementById('employeeModal').classList.remove('active');
    }
    
    function showComplianceModal() {
      document.getElementById('complianceModal').classList.add('active');
    }
    
    function closeComplianceModal() {
      document.getElementById('complianceModal').classList.remove('active');
    }
    
    // Close modals on outside click
    window.onclick = function(event) {
      if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
      }
    }
  </script>
</body>
</html>`;
}

// Generate and save HTML
const html = generateHTML(data);
const outputPath = path.join(process.cwd(), 'shadow-ai-dashboard.html');
fs.writeFileSync(outputPath, html);

console.log(`✅ Dashboard generated: ${outputPath}`);
console.log(`🌐 Open it in your browser: file://${outputPath}`);
