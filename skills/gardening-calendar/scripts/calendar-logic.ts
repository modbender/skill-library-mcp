import { PLANTS as BUNDLED_PLANTS } from '../references/plant-data';

/**
 * Gardening Calendar Logic
 * 
 * Provides methods to:
 * 1. Get current month status for plants (Sow Now, Harvest Now, Plan Ahead)
 * 2. Filter plants by region/country
 * 3. Provide sowing/harvesting windows
 */

export const REGIONS = {
  UK: 'UK',
  TH: 'Thailand',
  US: 'USA',
  AU: 'Australia'
};

export function getPlantStatus(plant, month) {
  const canSowIndoor = plant.sowIndoor?.some(range => 
    isMonthInRange(month, range.start.month, range.end.month)
  );
  const canSowOutdoor = plant.sowOutdoor?.some(range => 
    isMonthInRange(month, range.start.month, range.end.month)
  );
  const canHarvest = plant.harvest?.some(range => 
    isMonthInRange(month, range.start.month, range.end.month)
  );

  let status = 'plan-ahead';
  if (canSowIndoor || canSowOutdoor) status = 'sow-now';
  else if (canHarvest) status = 'harvest-now';

  return {
    status,
    canSowIndoor,
    canSowOutdoor,
    canHarvest
  };
}

function isMonthInRange(month, start, end) {
  if (start <= end) {
    return month >= start && month <= end;
  } else {
    // Range wraps around year end (e.g. Nov to Feb)
    return month >= start || month <= end;
  }
}

export const PLANTS = BUNDLED_PLANTS;
