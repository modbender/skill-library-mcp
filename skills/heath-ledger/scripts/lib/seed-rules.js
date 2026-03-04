/**
 * Universal categorization rules that apply to any business.
 * These are seeded on first DB init and won't overwrite existing rules.
 * Source: learned from real-world categorization across multiple entities.
 */
export const SEED_RULES = [
  // === Advertising ===
  { counterparty_pattern: 'google ads', category: 'Advertising', subcategory: 'Google Ads', confidence: 0.9 },
  { counterparty_pattern: 'facebook ads', category: 'Advertising', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'meta ads', category: 'Advertising', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'linkedin ads', category: 'Advertising', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'twitter ads', category: 'Advertising', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'vistaprint', category: 'Advertising', subcategory: 'Marketing Materials', confidence: 0.85 },

  // === Bank Service Charges ===
  { counterparty_pattern: 'wire fee', category: 'Bank Service Charges', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'intl wire', category: 'Bank Service Charges', subcategory: 'International Wire Fee', confidence: 0.9 },
  { counterparty_pattern: 'intl transaction fee', category: 'Bank Service Charges', subcategory: 'International Transaction Fee', confidence: 0.9 },
  { counterparty_pattern: 'intl wire fee', category: 'Bank Service Charges', subcategory: 'International Wire Fee', confidence: 0.9 },
  { counterparty_pattern: 'mercury', category: 'Bank Service Charges', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'wise', category: 'Bank Service Charges', subcategory: 'International Transfer Fees', confidence: 0.85 },
  { counterparty_pattern: 'wise inc', category: 'Bank Service Charges', subcategory: 'International Transfer Fees', confidence: 0.85 },

  // === Business Licensing, Fees & Tax ===
  { counterparty_pattern: 'franchise tax', category: 'Business Licensing, Fees & Tax', subcategory: 'Franchise Tax', confidence: 0.9 },
  { counterparty_pattern: 'secretary of state', category: 'Business Licensing, Fees & Tax', subcategory: 'State Filing Fees', confidence: 0.9 },
  { counterparty_pattern: 'tax1099', category: 'Business Licensing, Fees & Tax', subcategory: '1099 Filing', confidence: 0.9 },
  { counterparty_pattern: 'vanta', category: 'Business Licensing, Fees & Tax', subcategory: 'Security Compliance', confidence: 0.9 },

  // === Insurance ===
  { counterparty_pattern: 'embroker', category: 'Insurance', subcategory: 'Business Insurance', confidence: 0.9 },

  // === Legal & Professional Fees ===
  { counterparty_pattern: 'corpnet', category: 'Legal & Professional Fees', subcategory: 'Registered Agent', confidence: 0.9 },

  // === Sales/Service Revenue ===
  { counterparty_pattern: 'stripe', category: 'Sales/Service Revenue', subcategory: null, confidence: 0.85 },

  // === Servers & Hosting ===
  { counterparty_pattern: 'aws', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'amazon web services', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'digitalocean', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'heroku', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'vercel', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'netlify', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'cloudflare', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'render', category: 'Servers & Hosting', subcategory: null, confidence: 0.9 },
  { counterparty_pattern: 'fly.io', category: 'Servers & Hosting', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'railway', category: 'Servers & Hosting', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'hetzner', category: 'Servers & Hosting', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'linode', category: 'Servers & Hosting', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'microsoft', category: 'Servers & Hosting', subcategory: 'Azure/Microsoft Cloud', confidence: 0.8 },

  // === Software Expenses ===
  { counterparty_pattern: 'twilio', category: 'Software expenses', subcategory: 'Communications Platform', confidence: 0.9 },
  { counterparty_pattern: 'github', category: 'Software expenses', subcategory: 'Code Repository', confidence: 0.9 },
  { counterparty_pattern: 'slack', category: 'Software expenses', subcategory: 'Team Communication', confidence: 0.9 },
  { counterparty_pattern: 'hubspot', category: 'Software expenses', subcategory: 'CRM Platform', confidence: 0.9 },
  { counterparty_pattern: 'intercom', category: 'Software expenses', subcategory: 'Customer Support Platform', confidence: 0.9 },
  { counterparty_pattern: 'monday', category: 'Software expenses', subcategory: 'Project Management', confidence: 0.9 },
  { counterparty_pattern: 'notion', category: 'Software expenses', subcategory: 'Productivity', confidence: 0.9 },
  { counterparty_pattern: 'figma', category: 'Software expenses', subcategory: 'Design Tools', confidence: 0.9 },
  { counterparty_pattern: 'canva', category: 'Software expenses', subcategory: 'Design Tools', confidence: 0.9 },
  { counterparty_pattern: 'zoom', category: 'Software expenses', subcategory: 'Video Conferencing', confidence: 0.9 },
  { counterparty_pattern: 'dropbox', category: 'Software expenses', subcategory: 'Cloud Storage', confidence: 0.9 },
  { counterparty_pattern: 'gsuite', category: 'Software expenses', subcategory: 'Productivity Suite', confidence: 0.9 },
  { counterparty_pattern: 'google cloud', category: 'Software expenses', subcategory: 'Cloud Infrastructure', confidence: 0.9 },
  { counterparty_pattern: 'google workspace', category: 'Software expenses', subcategory: 'Productivity Suite', confidence: 0.9 },
  { counterparty_pattern: 'google services', category: 'Software expenses', subcategory: null, confidence: 0.85 },
  { counterparty_pattern: 'openai', category: 'Software expenses', subcategory: 'AI Tools', confidence: 0.9 },
  { counterparty_pattern: 'chatgpt', category: 'Software expenses', subcategory: 'AI Tools', confidence: 0.9 },
  { counterparty_pattern: 'anthropic', category: 'Software expenses', subcategory: 'AI Tools', confidence: 0.9 },
  { counterparty_pattern: 'claude.ai', category: 'Software expenses', subcategory: 'AI Tools', confidence: 0.9 },
  { counterparty_pattern: 'cursor', category: 'Software expenses', subcategory: 'AI Tools', confidence: 0.9 },
  { counterparty_pattern: 'elevenlabs', category: 'Software expenses', subcategory: 'AI Tools', confidence: 0.9 },
  { counterparty_pattern: 'eleven labs', category: 'Software expenses', subcategory: 'AI Tools', confidence: 0.9 },
  { counterparty_pattern: 'namecheap', category: 'Software expenses', subcategory: 'Domains', confidence: 0.9 },
  { counterparty_pattern: 'godaddy', category: 'Software expenses', subcategory: 'Domains', confidence: 0.9 },
  { counterparty_pattern: 'webflow', category: 'Software expenses', subcategory: 'Website Builder', confidence: 0.9 },
  { counterparty_pattern: 'framer', category: 'Software expenses', subcategory: 'Website Builder', confidence: 0.9 },
  { counterparty_pattern: 'shopify', category: 'Software expenses', subcategory: 'E-commerce', confidence: 0.9 },
  { counterparty_pattern: 'zapier', category: 'Software expenses', subcategory: 'Workflow Automation', confidence: 0.9 },
  { counterparty_pattern: '1password', category: 'Software expenses', subcategory: 'Password Management', confidence: 0.9 },
  { counterparty_pattern: 'pandadoc', category: 'Software expenses', subcategory: 'Document Management', confidence: 0.9 },
  { counterparty_pattern: 'typeform', category: 'Software expenses', subcategory: 'Forms/Surveys', confidence: 0.9 },
  { counterparty_pattern: 'vonage', category: 'Software expenses', subcategory: 'Business Phone System', confidence: 0.9 },
  { counterparty_pattern: 'uptimerobot', category: 'Software expenses', subcategory: 'Uptime Monitoring', confidence: 0.9 },
  { counterparty_pattern: 'descript', category: 'Software expenses', subcategory: 'Video Tools', confidence: 0.9 },
  { counterparty_pattern: 'loom', category: 'Software expenses', subcategory: 'Video Tools', confidence: 0.9 },
  { counterparty_pattern: 'nordvpn', category: 'Software expenses', subcategory: 'VPN', confidence: 0.85 },
  { counterparty_pattern: 'ghost.org', category: 'Software expenses', subcategory: 'Newsletter', confidence: 0.9 },
  { counterparty_pattern: 'linkedin', category: 'Software expenses', subcategory: 'LinkedIn Premium', confidence: 0.8 },
  { counterparty_pattern: 'twitter', category: 'Advertising', subcategory: 'X/Twitter', confidence: 0.8 },
  { counterparty_pattern: 'x corp', category: 'Advertising', subcategory: 'X/Twitter', confidence: 0.8 },
  { counterparty_pattern: 'pirsch', category: 'Software expenses', subcategory: 'Analytics', confidence: 0.9 },
  { counterparty_pattern: 'clearchecks', category: 'Software expenses', subcategory: 'Background Check Service', confidence: 0.85 },
  { counterparty_pattern: 'expensify', category: 'Software expenses', subcategory: 'Expense Management', confidence: 0.9 },
  { counterparty_pattern: 'quickbooks', category: 'Software expenses', subcategory: 'Accounting Software', confidence: 0.9 },
  { counterparty_pattern: 'xero', category: 'Software expenses', subcategory: 'Accounting Software', confidence: 0.9 },
  { counterparty_pattern: 'freshbooks', category: 'Software expenses', subcategory: 'Accounting Software', confidence: 0.9 },
  { counterparty_pattern: 'mailchimp', category: 'Software expenses', subcategory: 'Email Marketing', confidence: 0.9 },
  { counterparty_pattern: 'sendgrid', category: 'Software expenses', subcategory: 'Email Infrastructure', confidence: 0.9 },
  { counterparty_pattern: 'postmark', category: 'Software expenses', subcategory: 'Email Infrastructure', confidence: 0.9 },
  { counterparty_pattern: 'datadog', category: 'Software expenses', subcategory: 'Monitoring', confidence: 0.9 },
  { counterparty_pattern: 'sentry', category: 'Software expenses', subcategory: 'Error Tracking', confidence: 0.9 },
  { counterparty_pattern: 'jira', category: 'Software expenses', subcategory: 'Project Management', confidence: 0.9 },
  { counterparty_pattern: 'atlassian', category: 'Software expenses', subcategory: 'Project Management', confidence: 0.9 },
  { counterparty_pattern: 'linear', category: 'Software expenses', subcategory: 'Project Management', confidence: 0.9 },
  { counterparty_pattern: 'airtable', category: 'Software expenses', subcategory: 'Database/Spreadsheet', confidence: 0.9 },

  // === Wages & Salaries ===
  { counterparty_pattern: 'gusto', category: 'Wages & Salaries', subcategory: 'Payroll', confidence: 0.9 },
  { counterparty_pattern: 'deel', category: 'Wages & Salaries', subcategory: 'International Payroll', confidence: 0.9 },
  { counterparty_pattern: 'rippling', category: 'Wages & Salaries', subcategory: 'Payroll', confidence: 0.9 },
  { counterparty_pattern: 'justworks', category: 'Wages & Salaries', subcategory: 'Payroll/PEO', confidence: 0.9 },

  // === Stripe Fees (synthetic — only when Stripe API is connected) ===
  { counterparty_pattern: 'stripe fee', category: 'Stripe Fees', subcategory: null, confidence: 0.95 },
];
