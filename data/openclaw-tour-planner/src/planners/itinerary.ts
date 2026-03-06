import {
  PlanRequest, Itinerary, DayPlan, Activity,
  Destination, WeatherForecast, Attraction,
} from '../types';
import { WikivoyageGuide } from '../apis/wikivoyage';
import { buildBudget } from './budget';

const DEFAULT_TIMES = { morning: '09:00', afternoon: '13:00', evening: '19:00' };

/**
 * Core itinerary builder — distributes attractions across days,
 * assigns themes, builds packing list, and assembles the full Itinerary.
 */
export async function buildItinerary(
  request: PlanRequest,
  destination: Destination,
  weather: WeatherForecast,
  guide: WikivoyageGuide,
): Promise<Itinerary> {
  const travelers = request.travelers?.adults ?? 1;
  const budgetLevel = request.budgetLevel ?? 'mid-range';
  const startDate = request.startDate ?? getTodayIso();
  const endDate = addDays(startDate, request.durationDays - 1);

  const budget = buildBudget(destination, request.durationDays, travelers, budgetLevel);
  const attractions = guide.attractions.length > 0
    ? guide.attractions
    : generateDefaultAttractions(destination.name);

  const days = buildDays(
    request,
    destination,
    weather,
    attractions,
    startDate,
    budgetLevel,
    budget.total.min / request.durationDays,
  );

  return {
    destination,
    durationDays: request.durationDays,
    startDate,
    endDate,
    days,
    weatherForecast: weather,
    budget,
    packingList: buildPackingList(weather, request.durationDays, destination),
    culturalTips: guide.culturalTips.length > 0
      ? guide.culturalTips
      : defaultCulturalTips(destination),
    emergencyInfo: getEmergencyInfo(destination),
    generatedAt: new Date().toISOString(),
  };
}

function buildDays(
  request: PlanRequest,
  destination: Destination,
  weather: WeatherForecast,
  attractions: Attraction[],
  startDate: string,
  budgetLevel: string,
  dailyCostEst: number,
): DayPlan[] {
  const days: DayPlan[] = [];
  const style = request.travelStyle ?? 'moderate';
  const slotsPerDay = style === 'relaxed' ? 2 : style === 'packed' ? 5 : 3;

  // Shuffle attractions across days
  const pool = [...attractions];
  const themes = buildThemes(request.durationDays, destination.name);

  for (let i = 0; i < request.durationDays; i++) {
    const date = addDays(startDate, i);
    const dayWeather = weather.days[i];
    const dayAttractions = pool.splice(0, slotsPerDay);

    const morning: Activity[]   = [];
    const afternoon: Activity[] = [];
    const evening: Activity[]   = [];

    dayAttractions.forEach((attr, idx) => {
      const block = idx === 0 ? morning : idx === 1 ? afternoon : evening;
      const time  = idx === 0
        ? DEFAULT_TIMES.morning
        : idx === 1
        ? DEFAULT_TIMES.afternoon
        : DEFAULT_TIMES.evening;

      block.push({
        time,
        name: attr.name,
        description: attr.description.slice(0, 150),
        type: 'attraction',
        duration: attr.estimatedDuration,
        cost: costFromLevel(attr.estimatedCost, budgetLevel),
        location: { name: attr.name },
        tips: attr.tips,
      });
    });

    // Always add a dinner placeholder if evening is empty
    if (evening.length === 0) {
      evening.push({
        time: DEFAULT_TIMES.evening,
        name: 'Dinner',
        description: `Explore local restaurants near ${themes[i] ?? destination.name}.`,
        type: 'meal',
        duration: 1.5,
        cost: budgetLevel === 'budget' ? 15 : budgetLevel === 'luxury' ? 80 : 35,
      });
    }

    days.push({
      day: i + 1,
      date,
      theme: themes[i] ?? `Day ${i + 1} in ${destination.name}`,
      morning,
      afternoon,
      evening,
      meals: {
        lunch: `Local cuisine near today's attractions`,
        dinner: `Evening dining in ${destination.name}`,
      },
      transport: [],
      estimatedCost: Math.round(dailyCostEst),
      weather: dayWeather,
    });
  }

  return days;
}

function buildThemes(days: number, destName: string): string[] {
  const baseThemes = [
    `Arrival & ${destName} Centre`,
    'Culture & History',
    'Nature & Outdoors',
    'Food & Local Markets',
    'Hidden Gems & Neighbourhoods',
    'Day Trip',
    'Shopping & Leisure',
    'Art & Museums',
  ];
  return Array.from({ length: days }, (_, i) => baseThemes[i] ?? `Day ${i + 1}`);
}

function costFromLevel(estimatedCost: Attraction['estimatedCost'], budgetLevel: string): number {
  if (estimatedCost === 'free') return 0;
  const base = { low: 10, medium: 25, high: 60 }[estimatedCost] ?? 10;
  const multiplier = { budget: 0.7, 'mid-range': 1.0, luxury: 2.0 }[budgetLevel] ?? 1.0;
  return Math.round(base * multiplier);
}

function generateDefaultAttractions(destName: string): Attraction[] {
  return [
    { name: `${destName} Old Town`, type: 'sight', description: 'Historic centre with architecture and culture.', estimatedDuration: 2, estimatedCost: 'free' },
    { name: 'Local Museum', type: 'museum', description: 'Explore the history and culture of the region.', estimatedDuration: 2, estimatedCost: 'low' },
    { name: 'Central Market', type: 'food', description: 'Sample local food and browse artisan goods.', estimatedDuration: 1.5, estimatedCost: 'low' },
    { name: 'City Viewpoint', type: 'nature', description: 'Panoramic views of the city and surroundings.', estimatedDuration: 1, estimatedCost: 'free' },
    { name: 'Main Park', type: 'nature', description: 'Green space popular with locals.', estimatedDuration: 1.5, estimatedCost: 'free' },
    { name: 'Local Neighbourhood Walk', type: 'entertainment', description: 'Wander through residential streets and discover hidden cafes.', estimatedDuration: 2, estimatedCost: 'free' },
  ];
}

function buildPackingList(weather: WeatherForecast, days: number, dest: Destination): string[] {
  const list = [
    'Passport & travel documents (+ digital copies)',
    'Travel insurance',
    'Local currency + backup card',
    'Phone & charger + universal adapter',
    'Reusable water bottle',
  ];

  const avgHigh = weather.days.length
    ? weather.days.reduce((s, d) => s + d.tempMax, 0) / weather.days.length
    : 20;
  const hasRain = weather.days.some(d => d.precipitationChance > 40);

  if (avgHigh > 25) {
    list.push('Light, breathable clothing', 'Sunscreen SPF 50+', 'Sunglasses & hat');
  } else if (avgHigh < 10) {
    list.push('Warm layers / coat', 'Thermal underwear', 'Gloves & scarf');
  } else {
    list.push('Mix of light and warm layers', 'Comfortable walking shoes');
  }

  if (hasRain) list.push('Compact umbrella or rain jacket');
  if (days > 5) list.push('Laundry bag', 'Travel-size detergent');
  list.push('First aid kit (plasters, painkillers, antidiarrhoeals)', 'Any prescription medications');

  return list;
}

function defaultCulturalTips(dest: Destination): string[] {
  return [
    `Learn a few basic phrases in the local language before visiting ${dest.name}.`,
    'Respect local dress codes, especially at religious sites.',
    'Always ask before photographing people.',
    'Carry cash — many local vendors do not accept cards.',
    'Be mindful of local tipping customs.',
  ];
}

function getEmergencyInfo(dest: Destination): Itinerary['emergencyInfo'] {
  const country = (dest.country ?? '').toLowerCase();
  if (country.includes('japan'))          return { police: '110', ambulance: '119' };
  if (country.includes('united kingdom')) return { police: '999', ambulance: '999' };
  if (country.includes('australia'))      return { police: '000', ambulance: '000' };
  if (country.includes('france') || country.includes('germany') || country.includes('spain') || country.includes('italy'))
    return { police: '112', ambulance: '112' };
  if (country.includes('united states') || country.includes('canada'))
    return { police: '911', ambulance: '911' };
  return { police: '112', ambulance: '112' }; // EU-wide default works in many countries
}

function getTodayIso(): string {
  return new Date().toISOString().split('T')[0];
}

function addDays(dateStr: string, days: number): string {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + days);
  return d.toISOString().split('T')[0];
}
