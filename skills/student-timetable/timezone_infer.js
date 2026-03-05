const CITY_TZ = {
  sg: {
    singapore: 'Asia/Singapore'
  },
  cn: {
    beijing: 'Asia/Shanghai',
    shanghai: 'Asia/Shanghai',
    guangzhou: 'Asia/Shanghai',
    shenzhen: 'Asia/Shanghai',
    chengdu: 'Asia/Shanghai',
    hangzhou: 'Asia/Shanghai',
    wuhan: 'Asia/Shanghai',
    nanjing: 'Asia/Shanghai',
    tianjin: 'Asia/Shanghai',
    chongqing: 'Asia/Shanghai',
    xian: 'Asia/Shanghai',
    suzhou: 'Asia/Shanghai',
    xiamen: 'Asia/Shanghai',
    ningbo: 'Asia/Shanghai',
    qingdao: 'Asia/Shanghai'
  }
};

const COUNTRY_DEFAULT_TZ = {
  sg: 'Asia/Singapore',
  singapore: 'Asia/Singapore',
  cn: 'Asia/Shanghai',
  china: 'Asia/Shanghai'
};

function normalizeToken(s) {
  return String(s || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

function normalizeCountry(s) {
  const c = normalizeToken(s);
  if (c === 'sg' || c === 'singapore') return 'sg';
  if (c === 'cn' || c === 'china' || c === 'prc' || c === 'people\'s republic of china') return 'cn';
  return c;
}

function normalizeCityKey(city) {
  return normalizeToken(city).replace(/[^a-z0-9 ]/g, '');
}

function isValidTimeZone(tz) {
  try {
    Intl.DateTimeFormat('en-US', { timeZone: tz });
    return true;
  } catch {
    return false;
  }
}

function inferTimezone(country, city, overrideTimezone) {
  const override = String(overrideTimezone || '').trim();
  if (override) {
    if (isValidTimeZone(override)) {
      return { timezone: override, source: 'override', confidence: 'exact' };
    }
    return { timezone: null, source: 'override_invalid', confidence: 'none' };
  }

  const c = normalizeCountry(country);
  const cityKey = normalizeCityKey(city);
  if (CITY_TZ[c] && CITY_TZ[c][cityKey]) {
    return { timezone: CITY_TZ[c][cityKey], source: 'country_city', confidence: 'exact' };
  }

  if (COUNTRY_DEFAULT_TZ[c]) {
    return { timezone: COUNTRY_DEFAULT_TZ[c], source: 'country_default', confidence: 'default' };
  }

  return { timezone: 'UTC', source: 'safe_default', confidence: 'fallback' };
}

module.exports = { inferTimezone, isValidTimeZone, normalizeCountry };
