/**
 * 날짜 유틸리티
 */

function parseDate(input) {
  const now = new Date();
  now.setHours(0, 0, 0, 0);

  if (input === 'today') {
    return now;
  }

  if (input === 'tomorrow') {
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow;
  }

  // ISO 8601 형식 (YYYY-MM-DD)
  if (/^\d{4}-\d{2}-\d{2}$/.test(input)) {
    return new Date(input + 'T00:00:00+09:00');
  }

  // 기타 형식은 Date 생성자에 위임
  const parsed = new Date(input);
  if (isNaN(parsed.getTime())) {
    throw new Error(`Invalid date: ${input}`);
  }
  return parsed;
}

function formatDate(date) {
  return date.toISOString().split('T')[0];
}

function formatDateTime(date) {
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

module.exports = { parseDate, formatDate, formatDateTime };
