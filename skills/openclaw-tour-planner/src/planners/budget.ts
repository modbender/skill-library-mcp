import { Destination, BudgetBreakdown } from '../types';

type BudgetLevel = 'budget' | 'mid-range' | 'luxury';

/** Per-person-per-day USD baselines */
const DAILY_BASELINES: Record<BudgetLevel, number> = {
  'budget':    50,
  'mid-range': 150,
  'luxury':    400,
};

/** Allocation percentages of daily spend */
const ALLOCATION = {
  accommodation: 0.40,
  food:          0.25,
  activities:    0.20,
  transport:     0.10,
  miscellaneous: 0.05,
};

/** Variance bands (±%) for min/max range */
const VARIANCE = 0.20;

/**
 * Countries with significantly higher/lower costs vs. the baseline.
 * Multiplier applied to the daily rate.
 */
const COUNTRY_MULTIPLIERS: Record<string, number> = {
  'Japan':            1.1,
  'Switzerland':      1.8,
  'Norway':           1.9,
  'Iceland':          1.7,
  'Denmark':          1.6,
  'Australia':        1.3,
  'United Kingdom':   1.3,
  'Singapore':        1.2,
  'France':           1.2,
  'Germany':          1.1,
  'United States':    1.1,
  'Thailand':         0.5,
  'Vietnam':          0.4,
  'Indonesia':        0.4,
  'India':            0.3,
  'Mexico':           0.5,
  'Portugal':         0.8,
  'Czech Republic':   0.7,
  'Hungary':          0.65,
  'Poland':           0.65,
};

function countryMultiplier(country: string): number {
  // Exact match first, then partial
  if (COUNTRY_MULTIPLIERS[country]) return COUNTRY_MULTIPLIERS[country];
  for (const [k, v] of Object.entries(COUNTRY_MULTIPLIERS)) {
    if (country.toLowerCase().includes(k.toLowerCase())) return v;
  }
  return 1.0;
}

/**
 * Build a realistic budget breakdown for the trip.
 *
 * Accommodation doesn't fully double per extra traveler (shared room/doubles),
 * so we use a 0.6 marginal cost for each additional adult.
 */
export function buildBudget(
  destination: Destination,
  durationDays: number,
  travelers: number,
  level: BudgetLevel,
): BudgetBreakdown {
  const base = DAILY_BASELINES[level];
  const multiplier = countryMultiplier(destination.country || destination.name);

  // Effective per-person-per-day cost
  const dailyPerPerson = base * multiplier;

  // Accommodation: 1 traveler = full cost; each additional = 60% extra
  const accommScale = 1 + (Math.max(1, travelers) - 1) * 0.6;
  const accommPerDay = dailyPerPerson * ALLOCATION.accommodation * accommScale;
  const otherPerDay  = dailyPerPerson * (1 - ALLOCATION.accommodation) * travelers;
  const totalPerDay  = accommPerDay + otherPerDay;

  const totalMid = totalPerDay * durationDays;

  function range(pct: number, includeAccomm = false): { min: number; max: number } {
    const mid = includeAccomm
      ? accommPerDay * durationDays
      : dailyPerPerson * pct * travelers * durationDays;
    return {
      min: Math.round(mid * (1 - VARIANCE)),
      max: Math.round(mid * (1 + VARIANCE)),
    };
  }

  const accommodation = range(ALLOCATION.accommodation, true);
  const food          = range(ALLOCATION.food);
  const activities    = range(ALLOCATION.activities);
  const transport     = range(ALLOCATION.transport);
  const miscellaneous = range(ALLOCATION.miscellaneous);

  return {
    accommodation,
    food,
    activities,
    transport,
    miscellaneous,
    total: {
      min: Math.round(totalMid * (1 - VARIANCE)),
      max: Math.round(totalMid * (1 + VARIANCE)),
    },
    currency: destination.currency ?? 'USD',
  };
}
