const fs = require('fs');

module.exports = async function readFile(context, params) {
  try {
    const content = fs.readFileSync(params.path, 'utf8');
    return content;
  } catch (err) {
    return `Error reading file: ${err.message}`;
  }
};
