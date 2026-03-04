export function formatHm12(hour: number, minute: number = 0): string {
  // Normalize
  const h24 = ((hour % 24) + 24) % 24;
  const m = ((minute % 60) + 60) % 60;

  const suffix = h24 >= 12 ? 'PM' : 'AM';
  const h12 = h24 % 12 === 0 ? 12 : h24 % 12;
  const mm = String(m).padStart(2, '0');

  return `${h12}:${mm} ${suffix}`;
}

export function formatMinuteOnly(minute: number = 0): string {
  const m = ((minute % 60) + 60) % 60;
  return `:${String(m).padStart(2, '0')}`;
}
