const crypto = require('crypto');
function canonicalize(obj) {
  if (obj === null || obj === undefined) return 'null';
  if (typeof obj !== 'object') return JSON.stringify(obj);
  if (Array.isArray(obj)) return '[' + obj.map(canonicalize).join(',') + ']';
  const keys = Object.keys(obj).sort();
  return '{' + keys.map(k => JSON.stringify(k) + ':' + canonicalize(obj[k])).join(',') + '}';
}
const input = JSON.parse(process.argv[2]);
delete input.asset_id;
const hash = crypto.createHash('sha256').update(canonicalize(input)).digest('hex');
console.log('sha256:' + hash);
