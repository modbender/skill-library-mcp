const shorten = (text: string, maxChars: number): string => {
  if (text.length <= maxChars) return text;
  const head = Math.max(1, Math.floor(maxChars * 0.65));
  const tail = Math.max(1, maxChars - head - 5);
  return `${text.slice(0, head)} ... ${text.slice(text.length - tail)}`;
};

export const summarize = (value: unknown, maxChars = 800): string => {
  try {
    if (typeof value === 'string') {
      return shorten(value, maxChars);
    }
    return shorten(JSON.stringify(value), maxChars);
  } catch {
    return shorten(String(value), maxChars);
  }
};
