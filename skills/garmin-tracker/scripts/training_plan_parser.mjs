export function normalizeWeek(raw) {
  if (!raw || typeof raw !== "string") {
    return null;
  }

  const weekCode = raw.match(/\bW(\d{1,2})\b/i);
  if (weekCode) {
    return `W${weekCode[1].padStart(2, "0")}`;
  }

  const weekWord = raw.match(/\b(?:week|semana)\s*(\d{1,2})\b/i);
  if (weekWord) {
    return `W${weekWord[1].padStart(2, "0")}`;
  }

  return null;
}

export function normalizeDate(raw, nowYear) {
  if (!raw || typeof raw !== "string") {
    return null;
  }

  const iso = raw.match(/\b(20\d{2})-(\d{2})-(\d{2})\b/);
  if (iso) {
    return `${iso[1]}-${iso[2]}-${iso[3]}`;
  }

  const br = raw.match(/\b(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?\b/);
  if (br) {
    const dd = br[1].padStart(2, "0");
    const mm = br[2].padStart(2, "0");
    const y = br[3] ? (br[3].length === 2 ? `20${br[3]}` : br[3]) : `${nowYear}`;
    return `${y}-${mm}-${dd}`;
  }

  const textual = raw.match(
    /\b(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|fev|abr|mai|ago|set|out|dez)\b/i,
  );
  if (textual) {
    const months = {
      jan: "01",
      feb: "02",
      mar: "03",
      apr: "04",
      may: "05",
      jun: "06",
      jul: "07",
      aug: "08",
      sep: "09",
      oct: "10",
      nov: "11",
      dec: "12",
      fev: "02",
      abr: "04",
      mai: "05",
      ago: "08",
      set: "09",
      out: "10",
      dez: "12",
    };
    const dd = textual[1].padStart(2, "0");
    const mm = months[textual[2].toLowerCase().slice(0, 3)];
    if (mm) {
      return `${nowYear}-${mm}-${dd}`;
    }
  }

  return null;
}

export function cleanupScheduled(raw) {
  if (!raw || typeof raw !== "string") {
    return null;
  }

  const compact = raw.replace(/\s+/g, " ").trim();

  const workoutCode = compact.match(/\bW\d{1,2}D\d\s*[-:]\s*[^|]+/i);
  if (workoutCode) {
    return workoutCode[0].replace(/\s*[-:]\s*/g, "-").trim();
  }

  const keywords = [
    "rest",
    "easy run",
    "steady run",
    "long run",
    "interval",
    "intervals",
    "tempo",
    "swim",
    "cross training",
    "strength",
    "yoga",
    "pilates",
    "descanso",
    "corrida",
    "natação",
    "força",
    "treino",
  ];
  const lc = compact.toLowerCase();
  if (keywords.some((k) => lc.includes(k))) {
    return compact;
  }

  return null;
}

export function sanitizeUpcoming(upcoming) {
  const seen = new Set();
  const result = [];

  for (const item of upcoming) {
    if (!item || !item.date || !item.scheduled) {
      continue;
    }
    const key = `${item.date}|${item.scheduled}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    result.push({ date: item.date, scheduled: item.scheduled });
  }

  result.sort((a, b) => a.date.localeCompare(b.date));
  return result;
}

export function parseCalendarUpcomingFromLines(lines, today) {
  if (!Array.isArray(lines) || lines.length === 0) {
    return { upcoming: [], inferredWeek: null };
  }

  const monthMap = {
    january: 1,
    february: 2,
    march: 3,
    april: 4,
    may: 5,
    june: 6,
    july: 7,
    august: 8,
    september: 9,
    october: 10,
    november: 11,
    december: 12,
    janeiro: 1,
    fevereiro: 2,
    março: 3,
    marco: 3,
    abril: 4,
    maio: 5,
    junho: 6,
    julho: 7,
    agosto: 8,
    setembro: 9,
    outubro: 10,
    novembro: 11,
    dezembro: 12,
  };

  let month = null;
  let year = null;
  for (const line of lines) {
    const m = line.match(/\b([A-Za-zÀ-ÿ]+)\s+(20\d{2})\b/);
    if (!m) {
      continue;
    }
    const candidateMonth = monthMap[m[1].toLowerCase()];
    if (candidateMonth) {
      month = candidateMonth;
      year = Number(m[2]);
      break;
    }
  }

  if (!month || !year) {
    const now = new Date();
    month = now.getUTCMonth() + 1;
    year = now.getUTCFullYear();
  }

  const entries = [];
  let activeDay = null;
  for (const raw of lines) {
    const line = raw.trim();
    if (/^\d{1,2}$/.test(line)) {
      const day = Number(line);
      if (day >= 1 && day <= 31) {
        activeDay = day;
      }
      continue;
    }

    const scheduledMatch = line.match(/\bW(\d{1,2})D\d\s*-\s*.+/i);
    if (!scheduledMatch || !activeDay) {
      continue;
    }

    const date = `${String(year).padStart(4, "0")}-${String(month).padStart(2, "0")}-${String(activeDay).padStart(2, "0")}`;
    const scheduled = line.replace(/\s+/g, " ").trim();
    entries.push({ date, scheduled, week: `W${scheduledMatch[1].padStart(2, "0")}` });
  }

  const upcoming = sanitizeUpcoming(entries.filter((item) => item.date >= today));
  const inferredWeek = upcoming[0]?.scheduled.match(/\bW(\d{1,2})D/i)?.[1];
  return {
    upcoming,
    inferredWeek: inferredWeek ? `W${inferredWeek.padStart(2, "0")}` : null,
  };
}
