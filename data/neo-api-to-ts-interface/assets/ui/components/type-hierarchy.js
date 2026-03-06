/**
 * TypeHierarchy Component
 * Renders the type hierarchy tree visualization
 */

export class TypeHierarchy {
  constructor(types) {
    this.types = types;
    this.typeMap = new Map();
    types.forEach(t => this.typeMap.set(t.name, t));
  }

  render() {
    const extendsMap = new Map();
    const roots = [];

    // Build child relationships
    this.types.forEach(type => {
      if (type.extends) {
        type.extends.forEach(parent => {
          if (!extendsMap.has(parent)) {
            extendsMap.set(parent, []);
          }
          extendsMap.get(parent).push(type);
        });
      } else {
        roots.push(type);
      }
    });

    const html = `
      <nav class="sb-hierarchy">
        <h2>Type Hierarchy</h2>
        <ul>
          ${roots.map(type => this.renderNode(type, extendsMap, 0)).join('')}
        </ul>
      </nav>
    `;

    return html;
  }

  renderNode(type, extendsMap, depth) {
    const children = extendsMap.get(type.name) || [];
    const hasChildren = children.length > 0;

    let html = `<li><a href="#${type.name}" class="sb-type-link" data-type="${type.name}">${type.kind} ${type.name}</a>`;

    if (hasChildren) {
      html += '\n<ul>\n';
      children.sort((a, b) => a.name.localeCompare(b.name));
      html += children.map(child => this.renderNode(child, extendsMap, depth + 1)).join('');
      html += '\n</ul>\n';
    }

    html += '</li>';
    return html;
  }
}
