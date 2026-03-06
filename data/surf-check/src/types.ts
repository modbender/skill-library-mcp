/**
 * Surfline Surf Alert Skill - Type Definitions
 */

// ============================================
// Spot Configuration
// ============================================

export interface SpotConfig {
  id: string;
  name: string;
  slug: string;
  url: string;
}

export const SPOTS: Record<string, SpotConfig> = {
  BELMAR: {
    id: '5842041f4e65fad6a7708a01',
    name: 'Belmar (16th Ave)',
    slug: '16th-ave-belmar',
    url: 'https://www.surfline.com/surf-report/16th-ave-belmar/5842041f4e65fad6a7708a01',
  },
  LONG_BRANCH: {
    id: '630d04654da1381c5cb8aeb7',
    name: 'Long Branch',
    slug: 'long-branch',
    url: 'https://www.surfline.com/surf-report/long-branch/630d04654da1381c5cb8aeb7',
  },
} as const;

// ============================================
// Rating System
// ============================================

export enum RatingKey {
  FLAT = 'FLAT',
  VERY_POOR = 'VERY_POOR',
  POOR = 'POOR',
  POOR_TO_FAIR = 'POOR_TO_FAIR',
  FAIR = 'FAIR',
  FAIR_TO_GOOD = 'FAIR_TO_GOOD',
  GOOD = 'GOOD',
  GOOD_TO_EPIC = 'GOOD_TO_EPIC',
  EPIC = 'EPIC',
}

export const RATING_VALUES: Record<RatingKey, number> = {
  [RatingKey.FLAT]: 0,
  [RatingKey.VERY_POOR]: 0,
  [RatingKey.POOR]: 1,
  [RatingKey.POOR_TO_FAIR]: 1,
  [RatingKey.FAIR]: 2,
  [RatingKey.FAIR_TO_GOOD]: 3,
  [RatingKey.GOOD]: 4,
  [RatingKey.GOOD_TO_EPIC]: 5,
  [RatingKey.EPIC]: 5,
};

export const RATING_DISPLAY: Record<RatingKey, string> = {
  [RatingKey.FLAT]: 'Flat',
  [RatingKey.VERY_POOR]: 'Very Poor',
  [RatingKey.POOR]: 'Poor',
  [RatingKey.POOR_TO_FAIR]: 'Poor-Fair',
  [RatingKey.FAIR]: 'Fair',
  [RatingKey.FAIR_TO_GOOD]: 'Fair-Good',
  [RatingKey.GOOD]: 'Good',
  [RatingKey.GOOD_TO_EPIC]: 'Good-Epic',
  [RatingKey.EPIC]: 'Epic',
};

// ============================================
// Surfline API Response Types
// ============================================

export interface SurflineWaveResponse {
  associated: {
    units: { waveHeight: string };
  };
  data: {
    wave: WaveForecastItem[];
  };
}

export interface WaveForecastItem {
  timestamp: number;
  probability: number | null;
  utcOffset: number;
  surf: {
    min: number;
    max: number;
    optimalScore: number;
    plus: boolean;
    humanRelation: string;
    raw: { min: number; max: number };
  };
  swells: SwellData[];
}

export interface SwellData {
  height: number;
  period: number;
  direction: number;
  directionMin: number;
  optimalScore: number;
}

export interface SurflineRatingResponse {
  associated: {
    units: Record<string, string>;
  };
  data: {
    rating: RatingForecastItem[];
  };
}

export interface RatingForecastItem {
  timestamp: number;
  utcOffset: number;
  rating: {
    key: RatingKey;
    value: number;
  };
}

export interface SurflineConditionsResponse {
  associated: {
    units: Record<string, string>;
  };
  data: {
    conditions: ConditionsForecastItem[];
  };
}

export interface ConditionsForecastItem {
  timestamp: number;
  utcOffset: number;
  forecaster: {
    name: string;
    avatar: string;
  };
  human: boolean;
  observation: string | null;
  am: ConditionReport;
  pm: ConditionReport;
}

export interface ConditionReport {
  maxHeight: number;
  minHeight: number;
  plus: boolean;
  humanRelation: string;
  occasionalHeight: number | null;
  rating: RatingKey;
}

export interface SurflineWindResponse {
  associated: {
    units: { windSpeed: string };
  };
  data: {
    wind: WindForecastItem[];
  };
}

export interface WindForecastItem {
  timestamp: number;
  utcOffset: number;
  speed: number;
  direction: number;
  directionType: string;
  gust: number;
  optimalScore: number;
}

// ============================================
// Aggregated Forecast
// ============================================

export interface DayForecast {
  date: Date;
  dateString: string;
  dayOfWeek: string;
  isWeekend: boolean;
  spot: SpotConfig;
  wave: {
    min: number;
    max: number;
    humanRelation: string;
  };
  rating: {
    key: RatingKey;
    value: number;
    display: string;
  };
  wind: {
    speed: number;
    direction: number;
    directionType: string;
  } | null;
  swells: SwellData[];
}

// ============================================
// Alert Types
// ============================================

export interface QuietHours {
  enabled: boolean;
  start: number;  // Hour (0-23), e.g., 22 for 10pm
  end: number;    // Hour (0-23), e.g., 6 for 6am
}

export interface AlertConfig {
  waveMin: number;
  waveMax: number;
  forecastDays: number;
  quietHours: QuietHours;
  // Rating thresholds are now tiered by days out:
  // - 4+ days: Fair-Good+ (forecasts are fuzzy)
  // - 1-3 days: Fair+ (good confidence)
  // - Day of: Good+ only, before 8am
}

export const DEFAULT_ALERT_CONFIG: AlertConfig = {
  waveMin: 2,
  waveMax: 6,
  forecastDays: 7,
  quietHours: {
    enabled: true,
    start: 22,  // 10pm
    end: 6,     // 6am
  },
};

export interface AlertDecision {
  shouldAlert: boolean;
  forecast: DayForecast;
  reason: string;
}

export interface Alert {
  spot: SpotConfig;
  forecasts: DayForecast[];
  generatedAt: Date;
}

// ============================================
// NOAA Buoy Types (for future extension)
// ============================================

export interface NOAABuoyReading {
  timestamp: Date;
  waveHeight: number | null; // meters
  dominantPeriod: number | null; // seconds
  averagePeriod: number | null; // seconds
  meanDirection: number | null; // degrees
  waterTemp: number | null; // celsius
}

export interface NOAABuoyConfig {
  stationId: string;
  name: string;
}

export const NOAA_BUOYS: Record<string, NOAABuoyConfig> = {
  BARNEGAT: {
    stationId: '44091',
    name: 'Barnegat, NJ',
  },
} as const;
