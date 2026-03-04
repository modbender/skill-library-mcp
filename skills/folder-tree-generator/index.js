const fs = require('fs');
const path = require('path');

/**
 * Folder Tree Generator
 * Generates an ASCII tree or JSON representation of a directory structure.
 */

function generateStructure(dirPath, options = {}) {
  const { maxDepth = Infinity, ignore = ['.git', 'node_modules', '.DS_Store'], currentDepth = 0 } = options;
  
  const name = path.basename(dirPath);
  let stats;
  try {
    stats = fs.statSync(dirPath);
  } catch (err) {
    return { name, error: err.message };
  }

  const item = {
    name,
    type: stats.isDirectory() ? 'directory' : 'file',
    path: dirPath
  };

  if (stats.isDirectory()) {
    if (currentDepth < maxDepth) {
      try {
        const children = fs.readdirSync(dirPath)
          .filter(child => !ignore.includes(child))
          .map(child => generateStructure(path.join(dirPath, child), { ...options, currentDepth: currentDepth + 1 }));
        item.children = children;
      } catch (err) {
        item.error = err.message;
      }
    }
  }

  return item;
}

function printAsciiTree(node, prefix = '', isLast = true, isRoot = true) {
  let output = '';
  
  if (isRoot) {
    output += node.name + '\n';
  } else {
    output += prefix + (isLast ? '└── ' : '├── ') + node.name + '\n';
  }

  if (node.children) {
    const childPrefix = isRoot ? '' : prefix + (isLast ? '    ' : '│   ');
    node.children.forEach((child, index) => {
      const isLastChild = index === node.children.length - 1;
      output += printAsciiTree(child, childPrefix, isLastChild, false);
    });
  }
  
  return output;
}

function main() {
  const args = process.argv.slice(2);
  let targetDir = '.';
  let format = 'ascii';
  let maxDepth = Infinity;

  // Simple args parsing
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json') {
      format = 'json';
    } else if (args[i] === '--depth') {
      maxDepth = parseInt(args[i + 1], 10);
      i++;
    } else if (!args[i].startsWith('--')) {
      targetDir = args[i];
    }
  }

  if (!fs.existsSync(targetDir)) {
    console.error(`Error: Directory "${targetDir}" does not exist.`);
    process.exit(1);
  }

  const tree = generateStructure(targetDir, { maxDepth });

  if (format === 'json') {
    console.log(JSON.stringify(tree, null, 2));
  } else {
    console.log(printAsciiTree(tree));
  }
}

if (require.main === module) {
  main();
}

module.exports = { generateStructure, printAsciiTree, main };
