/**
 * 한국어 자연어 일정 파싱
 * 예: "내일 오후 3시 미팅" → { summary, start, end }
 */

const chrono = require('chrono-node');

// 한국어 시간 표현 정규식
const TIME_PATTERNS = [
  { regex: /오전\s*(\d{1,2})시(\s*(\d{1,2})분)?/, ampm: 'AM' },
  { regex: /오후\s*(\d{1,2})시(\s*(\d{1,2})분)?/, ampm: 'PM' },
  { regex: /(\d{1,2})시(\s*(\d{1,2})분)?/, ampm: null },
];

const DATE_PATTERNS = [
  { regex: /오늘/, days: 0 },
  { regex: /내일/, days: 1 },
  { regex: /모레/, days: 2 },
  { regex: /다음주\s*(월|화|수|목|금|토|일)요일/, type: 'nextWeekday' },
];

const DURATION_PATTERN = /(\d+)\s*(시간|분)/;

function parseKoreanEvent(text) {
  // chrono-node로 기본 날짜/시간 파싱
  const parsed = chrono.parse(text, new Date(), { forwardDate: true });
  
  let startDate = null;
  let endDate = null;
  let summary = text;

  if (parsed.length > 0) {
    const result = parsed[0];
    startDate = result.start.date();
    if (result.end) {
      endDate = result.end.date();
    }
  }

  // 한국어 날짜 패턴 체크
  for (const pattern of DATE_PATTERNS) {
    if (pattern.regex.test(text)) {
      const now = new Date();
      if (pattern.days !== undefined) {
        startDate = new Date(now);
        startDate.setDate(now.getDate() + pattern.days);
      } else if (pattern.type === 'nextWeekday') {
        const match = text.match(pattern.regex);
        const dayMap = { '월': 1, '화': 2, '수': 3, '목': 4, '금': 5, '토': 6, '일': 0 };
        const targetDay = dayMap[match[1]];
        startDate = new Date(now);
        const daysUntil = (targetDay + 7 - now.getDay()) % 7 || 7;
        startDate.setDate(now.getDate() + daysUntil);
      }
      break;
    }
  }

  // 한국어 시간 패턴 체크
  for (const pattern of TIME_PATTERNS) {
    const match = text.match(pattern.regex);
    if (match) {
      if (!startDate) startDate = new Date();
      let hour = parseInt(match[1]);
      const minute = match[3] ? parseInt(match[3]) : 0;

      if (pattern.ampm === 'PM' && hour < 12) hour += 12;
      if (pattern.ampm === 'AM' && hour === 12) hour = 0;

      startDate.setHours(hour, minute, 0, 0);
      break;
    }
  }

  // 기간 파싱 (1시간, 30분 등)
  const durationMatch = text.match(DURATION_PATTERN);
  if (durationMatch && startDate) {
    const amount = parseInt(durationMatch[1]);
    const unit = durationMatch[2];
    endDate = new Date(startDate);
    if (unit === '시간') {
      endDate.setHours(endDate.getHours() + amount);
    } else if (unit === '분') {
      endDate.setMinutes(endDate.getMinutes() + amount);
    }
  }

  // 종료 시간이 없으면 기본 1시간
  if (startDate && !endDate) {
    endDate = new Date(startDate);
    endDate.setHours(endDate.getHours() + 1);
  }

  // 제목 추출 (시간 표현 제거)
  summary = text
    .replace(/오늘|내일|모레/, '')
    .replace(/다음주\s*(월|화|수|목|금|토|일)요일/, '')
    .replace(/오전\s*\d{1,2}시(\s*\d{1,2}분)?/, '')
    .replace(/오후\s*\d{1,2}시(\s*\d{1,2}분)?/, '')
    .replace(/\d{1,2}시(\s*\d{1,2}분)?/, '')
    .replace(/\d{4}-\d{2}-\d{2}/, '')
    .replace(/\d{1,2}월\s*\d{1,2}일/, '')
    .replace(/\d+\s*(시간|분)/, '')
    .trim();

  if (!startDate) {
    return null; // 파싱 실패
  }

  return {
    summary: summary || '(제목 없음)',
    start: {
      dateTime: startDate.toISOString(),
      timeZone: 'Asia/Seoul',
    },
    end: {
      dateTime: endDate.toISOString(),
      timeZone: 'Asia/Seoul',
    },
  };
}

module.exports = { parseKoreanEvent };
