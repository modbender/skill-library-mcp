/**
 * Utility functions for the OSU MCP Server
 */

/**
 * Convert UTC timestamp to Eastern Time (Columbus, Ohio timezone)
 * Handles both EST (UTC-5) and EDT (UTC-4) automatically
 */
export function utcToEasternTime(utcTimestamp: string): string {
  try {
    const utcDate = new Date(utcTimestamp);
    
    // Convert to Eastern Time using Intl.DateTimeFormat
    const easternTime = utcDate.toLocaleString('en-US', {
      timeZone: 'America/New_York',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
    
    return easternTime;
  } catch (error) {
    // Return original timestamp if conversion fails
    return utcTimestamp;
  }
}

/**
 * Format timestamp for display with both UTC and Eastern Time
 */
export function formatTimestamp(utcTimestamp: string): string {
  const easternTime = utcToEasternTime(utcTimestamp);
  return `${easternTime} (Eastern Time) | UTC: ${utcTimestamp}`;
}

/**
 * Process API response to add local time fields
 */
export function addLocalTimeToResponse(data: any): any {
  if (!data || typeof data !== 'object') {
    return data;
  }

  // Handle arrays
  if (Array.isArray(data)) {
    return data.map(item => addLocalTimeToResponse(item));
  }

  // Process object
  const processed = { ...data };
  
  // Common timestamp fields to convert
  const timestampFields = [
    'updated', 'lastUpdated', 'lastModified', 
    'startTime', 'endTime', 'timestamp',
    'arrivalTime', 'departureTime'
  ];

  for (const field of timestampFields) {
    if (processed[field] && typeof processed[field] === 'string') {
      // Add Eastern Time version
      processed[`${field}_eastern`] = utcToEasternTime(processed[field]);
      processed[`${field}_formatted`] = formatTimestamp(processed[field]);
    }
  }

  // Recursively process nested objects
  for (const key in processed) {
    if (processed[key] && typeof processed[key] === 'object') {
      processed[key] = addLocalTimeToResponse(processed[key]);
    }
  }

  return processed;
}

/**
 * Get current Eastern Time
 */
export function getCurrentEasternTime(): string {
  return new Date().toLocaleString('en-US', {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
}