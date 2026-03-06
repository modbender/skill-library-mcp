#!/usr/bin/env node

/**
 * Shadow AI Monitor - Demo Data Generator
 * Generates realistic fake data for Morrison & Associates law firm
 */

const fs = require('fs');
const path = require('path');

const AI_TOOLS = [
  'ChatGPT', 'Claude', 'Gemini', 'Copilot', 'Midjourney', 
  'Grok', 'Perplexity', 'Cursor', 'GitHub Copilot'
];

const DATA_CATEGORIES = [
  { name: 'Client Legal Matters', risk: 'High' },
  { name: 'Financial Records', risk: 'High' },
  { name: 'Health Information', risk: 'High' },
  { name: 'Personal Information', risk: 'Medium' },
  { name: 'Internal Memos', risk: 'Medium' },
  { name: 'Case Research', risk: 'Low' },
  { name: 'General Questions', risk: 'Low' },
  { name: 'Code/Templates', risk: 'Low' }
];

const EMPLOYEE_ROLES = [
  'Partner', 'Senior Associate', 'Associate', 'Junior Associate',
  'Paralegal', 'Legal Assistant', 'IT Staff', 'Admin'
];

// Generate 50 employees
const employees = Array.from({ length: 50 }, (_, i) => ({
  id: `Employee ${i + 1}`,
  role: EMPLOYEE_ROLES[Math.floor(Math.random() * EMPLOYEE_ROLES.length)]
}));

// Generate events for the past 7 days
function generateEvents() {
  const events = [];
  const now = new Date();
  
  // Generate 150-300 events over 7 days
  const eventCount = 150 + Math.floor(Math.random() * 150);
  
  for (let i = 0; i < eventCount; i++) {
    const daysAgo = Math.floor(Math.random() * 7);
    const date = new Date(now);
    date.setDate(date.getDate() - daysAgo);
    
    const employee = employees[Math.floor(Math.random() * employees.length)];
    const tool = AI_TOOLS[Math.floor(Math.random() * AI_TOOLS.length)];
    const dataCategory = DATA_CATEGORIES[Math.floor(Math.random() * DATA_CATEGORIES.length)];
    
    // Weight toward concerning patterns
    const isHighRisk = Math.random() < 0.25; // 25% high risk
    const selectedCategory = isHighRisk 
      ? DATA_CATEGORIES.filter(c => c.risk === 'High')[Math.floor(Math.random() * 3)]
      : dataCategory;
    
    events.push({
      timestamp: date.toISOString(),
      employee: employee.id,
      employeeRole: employee.role,
      tool,
      dataCategory: selectedCategory.name,
      risk: selectedCategory.risk
    });
  }
  
  return events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

// Calculate metrics
function calculateMetrics(events) {
  const toolCounts = {};
  const riskCounts = { Low: 0, Medium: 0, High: 0 };
  const employeeUsage = {};
  const dailyUsage = {};
  
  events.forEach(event => {
    // Tool counts
    toolCounts[event.tool] = (toolCounts[event.tool] || 0) + 1;
    
    // Risk counts
    riskCounts[event.risk]++;
    
    // Employee usage
    employeeUsage[event.employee] = (employeeUsage[event.employee] || 0) + 1;
    
    // Daily usage
    const date = event.timestamp.split('T')[0];
    dailyUsage[date] = (dailyUsage[date] || 0) + 1;
  });
  
  // Top 3 tools
  const topTools = Object.entries(toolCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);
  
  // Top 10 employees
  const topEmployees = Object.entries(employeeUsage)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);
  
  // Calculate PIPEDA compliance score (0-100)
  // Lower score for higher risk activity
  const totalEvents = events.length;
  const highRiskPct = (riskCounts.High / totalEvents) * 100;
  const mediumRiskPct = (riskCounts.Medium / totalEvents) * 100;
  
  // Base score of 100, deduct points for risk
  let complianceScore = 100;
  complianceScore -= highRiskPct * 2; // -2 points per % of high risk
  complianceScore -= mediumRiskPct * 0.5; // -0.5 points per % of medium risk
  complianceScore = Math.max(0, Math.min(100, Math.round(complianceScore)));
  
  // Generate recommendations based on patterns
  const recommendations = [];
  
  if (highRiskPct > 20) {
    recommendations.push('URGENT: 25% of AI tool usage involves high-risk data (client legal matters, health info). Implement data classification policy immediately.');
  }
  
  if (topTools[0][1] > totalEvents * 0.4) {
    recommendations.push(`${topTools[0][0]} accounts for ${Math.round(topTools[0][1]/totalEvents*100)}% of usage. Consider negotiating enterprise agreement or implementing approved alternatives.`);
  }
  
  const topEmployeeUsage = topEmployees[0][1];
  if (topEmployeeUsage > totalEvents * 0.15) {
    recommendations.push(`${topEmployees[0][0]} is responsible for ${Math.round(topEmployeeUsage/totalEvents*100)}% of all AI tool usage. Schedule training session on appropriate use policies.`);
  }
  
  if (riskCounts.High > 0) {
    recommendations.push('Enable DLP (Data Loss Prevention) monitoring for AI tool domains to prevent sensitive data leakage.');
  }
  
  if (recommendations.length < 3) {
    recommendations.push('Establish AI Acceptable Use Policy and require all employees to complete training.');
  }
  
  if (recommendations.length < 3) {
    recommendations.push('Deploy browser extension to monitor and log AI tool usage in real-time.');
  }
  
  return {
    totalEvents,
    topTools,
    riskCounts,
    topEmployees,
    dailyUsage,
    complianceScore,
    recommendations: recommendations.slice(0, 3)
  };
}

// Main execution
const events = generateEvents();
const metrics = calculateMetrics(events);

const output = {
  generated: new Date().toISOString(),
  company: 'Morrison & Associates',
  employeeCount: 50,
  period: 'Last 7 days',
  events,
  metrics
};

// Output path
const outputPath = path.join(process.cwd(), 'shadow-ai-data.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

console.log(`✅ Generated ${events.length} events for ${employees.length} employees`);
console.log(`📊 Compliance Score: ${metrics.complianceScore}/100`);
console.log(`⚠️  High Risk Events: ${metrics.riskCounts.High}`);
console.log(`📝 Output: ${outputPath}`);
