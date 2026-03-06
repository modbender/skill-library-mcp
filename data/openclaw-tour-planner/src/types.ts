// Core types for the tour planner

export interface Destination {
  name: string;
  country: string;
  coordinates: {
    lat: number;
    lon: number;
  };
  boundingBox?: [number, number, number, number]; // [minLat, maxLat, minLon, maxLon]
  timezone?: string;
  currency?: string;
  language?: string;
}

export interface WeatherDay {
  date: string;
  tempMax: number;
  tempMin: number;
  conditions: string;
  precipitationChance: number;
  humidity: number;
  windSpeed: number;
}

export interface WeatherForecast {
  destination: string;
  days: WeatherDay[];
  summary: string;
}

export interface Attraction {
  name: string;
  type: 'sight' | 'museum' | 'nature' | 'food' | 'shopping' | 'entertainment';
  description: string;
  coordinates?: {
    lat: number;
    lon: number;
  };
  estimatedDuration: number; // in hours
  estimatedCost: 'free' | 'low' | 'medium' | 'high';
  bestTime?: string;
  tips?: string;
}

export interface DayPlan {
  day: number;
  date: string;
  theme: string;
  morning: Activity[];
  afternoon: Activity[];
  evening: Activity[];
  meals: {
    breakfast?: string;
    lunch?: string;
    dinner?: string;
  };
  transport: TransportOption[];
  estimatedCost: number;
  weather?: WeatherDay;
}

export interface Activity {
  time: string;
  name: string;
  description: string;
  type: 'attraction' | 'transit' | 'meal' | 'free-time' | 'accommodation';
  duration: number; // in hours
  cost: number;
  location?: {
    name: string;
    coordinates?: { lat: number; lon: number };
  };
  tips?: string;
  bookingRequired?: boolean;
}

export interface TransportOption {
  from: string;
  to: string;
  mode: 'walk' | 'transit' | 'taxi' | 'train' | 'flight';
  duration: number; // in minutes
  cost: number;
  notes?: string;
}

export interface BudgetBreakdown {
  accommodation: { min: number; max: number };
  food: { min: number; max: number };
  activities: { min: number; max: number };
  transport: { min: number; max: number };
  miscellaneous: { min: number; max: number };
  total: { min: number; max: number };
  currency: string;
}

export interface Itinerary {
  destination: Destination;
  durationDays: number;
  startDate: string;
  endDate: string;
  days: DayPlan[];
  weatherForecast?: WeatherForecast;
  budget: BudgetBreakdown;
  packingList: string[];
  culturalTips: string[];
  emergencyInfo: {
    police: string;
    ambulance: string;
    embassy?: string;
  };
  generatedAt: string;
}

export interface PlanRequest {
  destination: string;
  durationDays: number;
  startDate?: string;
  budgetLevel?: 'budget' | 'mid-range' | 'luxury';
  interests?: string[];
  travelStyle?: 'relaxed' | 'moderate' | 'packed';
  travelers?: {
    adults: number;
    children?: number;
  };
  specialRequirements?: string[];
}

export interface CacheEntry {
  key: string;
  data: unknown;
  expiresAt: number;
}
