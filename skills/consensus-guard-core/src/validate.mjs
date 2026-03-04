export function rejectUnknown(obj, allowed, path='root') {
  for (const k of Object.keys(obj||{})) if (!allowed.has(k)) return `unknown ${path} field: ${k}`;
  return null;
}
