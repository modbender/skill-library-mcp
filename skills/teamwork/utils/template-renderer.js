const fs = require('fs');
const path = require('path');

const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');

function loadTemplate(templateName) {
  const templatePath = path.join(TEMPLATES_DIR, templateName);
  
  if (!fs.existsSync(templatePath)) {
    throw new Error(`Template not found: ${templateName}`);
  }
  
  return fs.readFileSync(templatePath, 'utf8');
}

function renderTemplate(template, data) {
  let rendered = template;
  
  rendered = rendered.replace(/\{\{#each\s+(\w+)\}\}([\s\S]*?)\{\{\/each\}\}/g, (match, arrayName, content) => {
    const array = data[arrayName];
    if (!Array.isArray(array)) return '';
    
    return array.map((item, index) => {
      let itemContent = content;
      
      itemContent = itemContent.replace(/\{\{@index\}\}/g, index);
      
      for (const [key, value] of Object.entries(item)) {
        if (typeof value === 'string' || typeof value === 'number') {
          itemContent = itemContent.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), value);
        }
      }
      
      return itemContent;
    }).join('');
  });
  
  rendered = rendered.replace(/\{\{#if\s+(\w+)\}\}([\s\S]*?)\{\{else\}\}([\s\S]*?)\{\{\/if\}\}/g, (match, condition, trueContent, falseContent) => {
    return data[condition] ? trueContent : falseContent;
  });
  
  rendered = rendered.replace(/\{\{#if\s+(\w+)\}\}([\s\S]*?)\{\{\/if\}\}/g, (match, condition, content) => {
    return data[condition] ? content : '';
  });
  
  for (const [key, value] of Object.entries(data)) {
    if (typeof value === 'string' || typeof value === 'number') {
      rendered = rendered.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), value);
    }
  }
  
  rendered = rendered.replace(/\{\{#each[\s\S]*?\{\{\/each\}\}/g, '');
  rendered = rendered.replace(/\{\{#if[\s\S]*?\{\{\/if\}\}/g, '');
  rendered = rendered.replace(/\{\{\w+\}\}/g, '');
  
  return rendered;
}

function renderTemplateFromFile(templateName, data) {
  const template = loadTemplate(templateName);
  return renderTemplate(template, data);
}

function saveRenderedTemplate(outputPath, templateName, data) {
  const rendered = renderTemplateFromFile(templateName, data);
  
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, rendered, 'utf8');
  return outputPath;
}

module.exports = {
  loadTemplate,
  renderTemplate,
  renderTemplateFromFile,
  saveRenderedTemplate
};
