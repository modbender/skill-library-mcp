const wrap = (code) => (text) => `\u001b[${code}m${text}\u001b[0m`;

export const colors = {
  red: wrap(31),
  green: wrap(32),
  yellow: wrap(33),
  blue: wrap(34),
  cyan: wrap(36),
  dim: wrap(2),
  bold: wrap(1)
};
