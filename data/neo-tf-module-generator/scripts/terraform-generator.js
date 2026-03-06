#!/usr/bin/env node
/**
 * Terraform Module Generator
 *
 * Usage: node terraform-generator.js --input <format> --output <directory> [--template <dir>]
 *
 * Example:
 *   node terraform-generator.js --input json --output ./my-module
 *   cat resources.json | node terraform-generator.js --input json --output ./module
 *
 * This script reads cloud resource metadata (from stdin or file) and generates:
 *   - main.tf      (resource definitions)
 *   - variables.tf (input variables inferred from resource attributes)
 *   - outputs.tf   (output values for resource attributes)
 *   - README.md    (usage documentation)
 *
 * It uses template files from references/templates/ if available, otherwise
 * generates code using built-in formatters.
 */

const fs = require('fs');
const path = require('path');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse arguments
const argv = yargs(hideBin(process.argv))
  .option('input', {
    alias: 'i',
    type: 'string',
    choices: ['json', 'stdin'],
    default: 'stdin',
    description: 'Input format (stdin reads JSON from stdin)'
  })
  .option('output', {
    alias: 'o',
    type: 'string',
    demandOption: true,
    description: 'Output directory for generated module'
  })
  .option('template', {
    alias: 't',
    type: 'string',
    description: 'Custom template directory (optional)'
  })
  .argv;

const outputDir = path.resolve(argv.output);
const templateDir = argv.template ? path.resolve(argv.template) : path.resolve(__dirname, '../references/templates');

/**
 * Read input resources from stdin or file
 */
async function readResources() {
  let inputData;

  if (argv.input === 'stdin') {
    // Read from stdin (non-blocking)
    inputData = await new Promise((resolve, reject) => {
      let data = '';
      process.stdin.setEncoding('utf8');
      process.stdin.on('data', chunk => data += chunk);
      process.stdin.on('end', () => resolve(data));
      process.stdin.on('error', reject);
    });
  } else {
    // Could extend to file input
    throw new Error('Only stdin input is currently supported');
  }

  if (!inputData.trim()) {
    return [];
  }

  try {
    return JSON.parse(inputData);
  } catch (err) {
    throw new Error(`Failed to parse input JSON: ${err.message}`);
  }
}

/**
 * Collect unique variable definitions from resource attributes
 */
function inferVariables(resources) {
  const variables = new Map();

  for (const resource of resources) {
    const attrs = resource.attributes || {};
    const tags = resource.tags || {};

    // Add common attribute-based variables
    for (const [key, value] of Object.entries(attrs)) {
      if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        if (!variables.has(key)) {
          variables.set(key, {
            type: typeof value === 'boolean' ? 'bool' : (typeof value === 'number' ? 'number' : 'string'),
            description: `Input for ${key}`,
            default: value
          });
        }
      }
    }

    // Add common tags-based variables (like environment, owner)
    const tagKeys = ['Environment', 'environment', 'Owner', 'owner', 'Team', 'team', 'Project', 'project'];
    for (const tagKey of tagKeys) {
      if (tags[tagKey] && !variables.has(tagKey)) {
        variables.set(tagKey, {
          type: 'string',
          description: `Tag: ${tagKey}`,
          default: tags[tagKey]
        });
      }
    }
  }

  return variables;
}

/**
 * Generate Terraform HCL for a single resource
 */
function generateResourceHCL(resource) {
  const { type, id, name, region, attributes, tags, resource_group, location, zone, project } = resource;

  // Map provider-specific type to Terraform resource type
  let terraformType;
  let resourceName = name.replace(/[^a-zA-Z0-9_-]/g, '_');
  let block = '';

  // AWS resources
  if (type.startsWith('aws_')) {
    terraformType = type; // Already in Terraform format
    block = `resource "${terraformType}" "${resourceName}" {
  ${generateAttributesHCL(attributes)}
  ${generateTagsHCL(tags)}
}`;
  }
  // Azure resources
  else if (type.startsWith('azure_')) {
    // Map to Terraform AzureRM provider types
    const typeMap = {
      'azurerm_virtual_machine': 'azurerm_linux_virtual_machine',
      'azurerm_virtual_network': 'azurerm_virtual_network',
      'azurerm_subnet': 'azurerm_subnet',
      'azurerm_network_interface': 'azurerm_network_interface',
      'azurerm_public_ip': 'azurerm_public_ip',
      'azurerm_managed_disk': 'azurerm_managed_disk',
      'azurerm_network_security_group': 'azurerm_network_security_group',
      'azurerm_lb': 'azurerm_lb',
      'azurerm_linux_web_app': 'azurerm_linux_web_app'
    };

    // Determine actual terraform type
    const baseType = type.replace('azurerm_', '');
    terraformType = typeMap[type] || `azurerm_${baseType}`;

    let attrs = { ...attributes };
    if (resource_group) attrs.resource_group_name = resource_group;
    if (location) attrs.location = location;

    block = `resource "${terraformType}" "${resourceName}" {
  ${generateAttributesHCL(attrs, { indent: 2 })}
  ${generateTagsHCL(tags, { indent: 2 })}
}`;
  }
  // GCP resources
  else if (type.startsWith('google_')) {
    terraformType = type; // Already in Terraform format
    let attrs = { ...attributes };
    if (project) attrs.project = project;
    if (region) attrs.region = region;
    if (zone) attrs.zone = zone;

    block = `resource "${terraformType}" "${resourceName}" {
  ${generateAttributesHCL(attrs)}
  ${generateLabelsHCL(labels, { indent: 2 })}
}`;
  }
  else {
    // Fallback: treat as unknown type
    block = `# Unknown resource type: ${type}
# Resource: ${JSON.stringify(resource, null, 2)}
`;
  }

  return block;
}

/**
 * Generate HCL attribute assignments
 */
function generateAttributesHCL(attributes, options = { indent: 2 }) {
  const indent = ' '.repeat(options.indent);
  let lines = [];

  for (const [key, value] of Object.entries(attributes)) {
    if (value === null || value === undefined) continue;

    const rendered = renderValue(value, options.indent + 2);
    if (rendered) {
      lines.push(`${indent}${key} = ${rendered}`);
    }
  }

  return lines.join('\\n');
}

/**
 * Generate Terraform tags block (AWS)
 */
function generateTagsHCL(tags, options = { indent: 2 }) {
  if (!tags || Object.keys(tags).length === 0) return '';

  const indent = ' '.repeat(options.indent);
  const innerIndent = ' '.repeat(options.indent + 2);
  const tagLines = [];

  for (const [key, value] of Object.entries(tags)) {
    if (value !== null && value !== undefined) {
      tagLines.push(`${innerIndent}"${key}" = "${value}"`);
    }
  }

  if (tagLines.length === 0) return '';

  return `\\n${indent}tags = {
${tagLines.join('\\n')}
${indent}}`;
}

/**
 * Generate Terraform labels block (GCP)
 */
function generateLabelsHCL(labels, options = { indent: 2 }) {
  if (!labels || Object.keys(labels).length === 0) return '';

  const indent = ' '.repeat(options.indent);
  const innerIndent = ' '.repeat(options.indent + 2);
  const labelLines = [];

  for (const [key, value] of Object.entries(labels)) {
    if (value !== null && value !== undefined) {
      labelLines.push(`${innerIndent}"${key}" = "${value}"`);
    }
  }

  if (labelLines.length === 0) return '';

  return `\\n${indent}labels = {
${labelLines.join('\\n')}
${indent}}`;
}

/**
 * Render a value to HCL literal
 */
function renderValue(value, indent = 0) {
  const space = ' '.repeat(indent);

  if (value === null || value === undefined) {
    return 'null';
  }

  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }

  if (typeof value === 'number') {
    return String(value);
  }

  if (typeof value === 'string') {
    // Check if it looks like a reference (already HCL)
    if (value.includes('${') || value.includes('"')) {
      return value;
    }
    // Escape quotes
    const escaped = value.replace(/"/g, '\\"');
    return `"${escaped}"`;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return '[]';

    // Simple arrays
    if (value.every(v => typeof v === 'string')) {
      return `[${value.map(v => `"${v}"`).join(', ')}]`;
    }

    // Arrays of objects - would need nested blocks, complex
    // For now, render as JSON string if simple
    return `jsonencode(${JSON.stringify(value)})`;
  }

  if (typeof value === 'object') {
    const entries = [];
    for (const [k, v] of Object.entries(value)) {
      const rendered = renderValue(v, indent);
      if (rendered) {
        entries.push(`${space}  "${k}" = ${rendered}`);
      }
    }
    if (entries.length === 0) return '{}';

    return `{\n${entries.join(',\\n')}\n${space}}`;
  }

  return null;
}

/**
 * Generate main.tf content
 */
function generateMainTF(resources) {
  const blocks = resources.map(r => generateResourceHCL(r)).filter(Boolean);
  return blocks.join('\\n\\n') + '\\n';
}

/**
 * Generate variables.tf content
 */
function generateVariablesTF(variables) {
  const varBlocks = [];

  for (const [name, def] of variables) {
    const type = def.type;
    const desc = def.description ? `"${def.description}"` : '';
    const defaultVal = def.default !== undefined ? ` = ${renderValue(def.default)}` : '';

    varBlocks.push(`variable "${name}" {
  type        = ${type}
  description = ${desc}${defaultVal ? '\\n  default     = ' + renderValue(def.default) : ''}
}`);
  }

  return varBlocks.join('\\n\\n') + '\\n';
}

/**
 * Generate outputs.tf content
 */
function generateOutputsTF(resources) {
  const outputBlocks = [];

  for (const resource of resources) {
    const resourceName = resource.name.replace(/[^a-zA-Z0-9_-]/g, '_');
    const type = resource.type;

    // Generate useful outputs
    outputBlocks.push(`output "${resource.name}_id" {
  description = "ID of the ${type} resource '${resource.name}'"
  value       = ${type}.${resourceName}.id
}`);

    // For compute resources, output common attributes
    if (['aws_instance', 'google_compute_instance', 'azurerm_virtual_machine'].includes(type)) {
      const attrs = resource.type.includes('aws') ? ['public_ip', 'private_ip', 'availability_zone'] :
                    resource.type.includes('google') ? ['network_interface', 'service_account'] :
                    ['admin_username', 'computer_name']; // azure

      for (const attr of attrs) {
        outputBlocks.push(`output "${resource.name}_${attr}" {
  description = "${attr} of ${resource.name}"
  value       = try(${type}.${resourceName}.${attr}, null)
}`);
      }
    }
  }

  return outputBlocks.join('\\n\\n') + '\\n';
}

/**
 * Generate README.md content
 */
function generateReadme(resources, moduleName = 'generated-terraform-module') {
  const lines = [
    `# ${moduleName}`,
    '',
    'Automatically generated Terraform module from existing cloud resources.',
    '',
    '## Usage',
    '',
    '```hcl',
    'module "example" {',
    '  source = "./modules/generated"',
    '',
    '  # Required variables (if any)',
    '  # region = "us-east-1"',
    '  # environment = "production"',
    '',
    '  # Optional: Override any resource attributes',
    '  # tags = {',
    '  #   Environment = "dev"',
    '  # }',
    '}',
    '```',
    '',
    '## Resources',
    ''
  ];

  for (const resource of resources) {
    lines.push(`- \`${resource.type}\`: ${resource.name} (ID: ${resource.id})`);
  }

  lines.push('');
  lines.push('## Generated Files');
  lines.push('');
  lines.push('- `main.tf` - Resource definitions');
  lines.push('- `variables.tf` - Input variables');
  lines.push('- `outputs.tf` - Output values');
  lines.push('');
  lines.push('## Notes');
  lines.push('');
  lines.push('- This module is generated automatically. Review before using in production.');
  lines.push('- Some resource attributes may require adjustments based on your provider version.');
  lines.push('- Generated on: ' + new Date().toISOString());
  lines.push('');

  return lines.join('\\n');
}

/**
 * Write files to output directory
 */
async function writeOutputs(outputDir, mainTF, variablesTF, outputsTF, readme) {
  await fs.promises.mkdir(outputDir, { recursive: true });

  await fs.promises.writeFile(path.join(outputDir, 'main.tf'), mainTF);
  await fs.promises.writeFile(path.join(outputDir, 'variables.tf'), variablesTF);
  await fs.promises.writeFile(path.join(outputDir, 'outputs.tf'), outputsTF);
  await fs.promises.writeFile(path.join(outputDir, 'README.md'), readme);

  console.error(`Generated module files in: ${outputDir}`);
}

/**
 * Main entry
 */
async function main() {
  console.error('Terraform Module Generator');

  try {
    // Read resources
    const resources = await readResources();
    console.error(`Loaded ${resources.length} resource(s)`);

    // Infer variables
    const variables = inferVariables(resources);
    console.error(`Inferred ${variables.size} variable(s)`);

    // Generate content
    const mainTF = generateMainTF(resources);
    const variablesTF = generateVariablesTF(variables);
    const outputsTF = generateOutputsTF(resources);
    const readme = generateReadme(resources);

    // Write outputs (to be called from main.js, not standalone)
    if (module.parent === null) {
      // Standalone execution: print to stdout or write to --output
      if (argv.output) {
        await writeOutputs(outputDir, mainTF, variablesTF, outputsTF, readme);
      } else {
        console.log('=== main.tf ===\\n' + mainTF);
        console.log('=== variables.tf ===\\n' + variablesTF);
        console.log('=== outputs.tf ===\\n' + outputsTF);
        console.log('=== README.md ===\\n' + readme);
      }
    } else {
      // Called from another script - return generated content
      return {
        main: mainTF,
        variables: variablesTF,
        outputs: outputsTF,
        readme: readme,
        resources,
        variables: Array.from(variables.entries())
      };
    }

  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(err => {
    console.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
}

module.exports = {
  generateMainTF,
  generateVariablesTF,
  generateOutputsTF,
  generateReadme,
  inferVariables,
  generateResourceHCL,
  renderValue
};
