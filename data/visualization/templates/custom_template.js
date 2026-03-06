// Custom Template System
const fs = require('fs');
const path = require('path');

class CustomTemplateManager {
  constructor(workspacePath = '/home/admin/.openclaw/workspace') {
    this.templatesDir = path.join(workspacePath, 'visualization_templates');
    this.ensureTemplatesDir();
  }

  ensureTemplatesDir() {
    if (!fs.existsSync(this.templatesDir)) {
      fs.mkdirSync(this.templatesDir, { recursive: true });
    }
  }

  // Save user-defined template
  saveTemplate(templateName, templateConfig) {
    const templatePath = path.join(this.templatesDir, `${templateName}.json`);
    fs.writeFileSync(templatePath, JSON.stringify(templateConfig, null, 2));
    return { success: true, path: templatePath };
  }

  // Load user-defined template
  loadTemplate(templateName) {
    const templatePath = path.join(this.templatesDir, `${templateName}.json`);
    if (!fs.existsSync(templatePath)) {
      throw new Error(`Template ${templateName} not found`);
    }
    const templateData = fs.readFileSync(templatePath, 'utf8');
    return JSON.parse(templateData);
  }

  // List available templates
  listTemplates() {
    const files = fs.readdirSync(this.templatesDir);
    return files
      .filter(file => file.endsWith('.json'))
      .map(file => file.replace('.json', ''));
  }

  // Generate preview HTML for template
  async generateTemplatePreview(templateConfig) {
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Template Preview</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { margin: 0; padding: 20px; background: #f5f5f5; font-family: Arial, sans-serif; }
    .preview-container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .chart-container { width: 100%; height: 400px; margin: 20px 0; }
    .template-info { margin-bottom: 20px; }
    h1 { color: #333; margin-bottom: 10px; }
    .description { color: #666; line-height: 1.5; }
  </style>
</head>
<body>
  <div class="preview-container">
    <div class="template-info">
      <h1>${templateConfig.metadata?.title || 'Custom Template'}</h1>
      <p class="description">${templateConfig.metadata?.description || 'Template preview'}</p>
    </div>
    ${templateConfig.composite 
      ? `<div class="composite">
          ${templateConfig.charts.map((_, i) => 
            `<div class="chart-container" id="chart${i}"></div>`
          ).join('')}
         </div>`
      : '<div class="chart-container"><canvas id="chart"></canvas></div>'
    }
    <script>
      ${templateConfig.composite 
        ? templateConfig.charts.map((config, i) => 
            `new Chart(document.getElementById('chart${i}'), ${JSON.stringify(config)});`
          ).join('\n')
        : `new Chart(document.getElementById('chart'), ${JSON.stringify(templateConfig)});`
      }
    </script>
  </div>
</body>
</html>`;

    // Save preview HTML
    const previewPath = path.join(this.templatesDir, 'preview.html');
    fs.writeFileSync(previewPath, htmlContent);
    return previewPath;
  }
}

module.exports = CustomTemplateManager;