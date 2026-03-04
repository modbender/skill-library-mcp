/**
 * TypeCard Component
 * Renders an individual type interface card for Storybook
 */

export class TypeCard {
  constructor(typeData) {
    this.typeData = typeData;
  }

  render() {
    const { name, kind, fields, extends: extendsList, values, description } = this.typeData;

    const badgeClass = kind.toLowerCase();
    const extendsHtml = extendsList && extendsList.length > 0
      ? `<div class="sb-type-extends">Extends: ${extendsList.map(e => `<code>${e}</code>`).join(', ')}</div>`
      : '';

    const fieldsHtml = fields && fields.length > 0
      ? this.renderTable(fields)
      : '';

    const valuesHtml = values && values.length > 0
      ? `<h4>Values</h4><ul class="sb-values-list">${values.map(v => `<li><code>${v}</code></li>`).join('')}</ul>`
      : '';

    const exampleHtml = this.renderExample();

    return `
      <article class="sb-type-card" data-type="${name.toLowerCase()}">
        <div class="sb-type-header">
          <span class="sb-type-badge ${badgeClass}">${kind}</span>
          <h2 class="sb-type-name">${name}</h2>
        </div>
        ${extendsHtml}
        ${description ? `<p class="sb-type-description">${description}</p>` : ''}
        ${fieldsHtml}
        ${valuesHtml}
        ${exampleHtml}
      </article>
    `;
  }

  renderTable(fields) {
    const rows = fields.map(field => {
      const reqClass = field.required ? 'sb-required' : 'sb-optional';
      const reqSymbol = field.required ? '✓' : '○';
      const description = field.description || '';

      return `
        <tr>
          <td><code>${field.name}</code></td>
          <td><code>${this.highlightType(field.type)}</code></td>
          <td class="${reqClass}">${reqSymbol}</td>
          <td>${description}</td>
        </tr>
      `;
    }).join('');

    return `
      <table class="sb-properties-table">
        <thead>
          <tr>
            <th>Property</th>
            <th>Type</th>
            <th>Required</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }

  highlightType(typeStr) {
    const keywords = ['string', 'number', 'boolean', 'Date', 'any', 'void', 'never', 'object'];
    let result = typeStr;

    keywords.forEach(kw => {
      const regex = new RegExp(`\\b${kw}\\b`, 'g');
      result = result.replace(regex, `<span style="color: #e83e8c;">${kw}</span>`);
    });

    result = result.replace(/(\[\])/g, '<span style="color: #22863a;">$1</span>');
    result = result.replace(/(\|)/g, '<span style="color: #d73a49;">$1</span>');

    return result;
  }

  generateExampleValue(typeStr) {
    if (typeStr.includes('string')) return '"example string"';
    if (typeStr.includes('number')) return '0';
    if (typeStr.includes('boolean')) return 'true';
    if (typeStr.includes('Date')) return '"2024-01-01T00:00:00.000Z"';
    if (typeStr.includes('[]') || typeStr.endsWith('[]')) {
      const itemType = typeStr.replace('[]', '');
      return `[${this.generateExampleValue(itemType)}]`;
    }
    if (typeStr.includes('|')) {
      const firstType = typeStr.split('|')[0].trim();
      return this.generateExampleValue(firstType);
    }
    return 'null';
  }

  generateExample() {
    if (this.typeData.kind !== 'interface' || !this.typeData.fields) {
      return '';
    }

    const requiredFields = this.typeData.fields.filter(f => f.required);
    if (requiredFields.length === 0) return '';

    const exampleObj = {};
    requiredFields.forEach(field => {
      exampleObj[field.name] = this.generateExampleValue(field.type);
    });

    const exampleJson = JSON.stringify(exampleObj, null, 2);

    return `
      <div class="sb-example">
        <p><strong>Example:</strong></p>
        <pre><code>${this.escapeHtml(exampleJson)}</code></pre>
        <button class="sb-copy-btn" onclick="copyToClipboard(this)">Copy</button>
      </div>
    `;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}
