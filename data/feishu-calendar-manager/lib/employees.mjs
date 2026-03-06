/**
 * Employee Directory - Dynamic lookup via Lark Contact API
 *
 * Uses Lark's contact API to resolve names to user_ids dynamically.
 * Falls back to cached data for known employees.
 */

import { larkApi } from './lark-api.mjs';

// Admin user_id - always added as attendee (customize as needed)
export const ADMIN_USER_ID = process.env.FEISHU_ADMIN_USER_ID || '';

// Cache for employee data (populated on first lookup)
let employeeCache = null;
let cacheTimestamp = 0;
const CACHE_TTL = 3600000; // 1 hour

// Fallback static data for known employees (used when API fails)
// Update this when team changes, or add contact:contact:readonly permission for dynamic lookup
const FALLBACK_EMPLOYEES = {
  // Example: Add your team members here
  // 'user_id_123': { user_id: 'user_id_123', name: 'John Doe', en_name: 'John' },
};

/**
 * Fetch all employees from Lark Contact API
 * @returns {Promise<Map<string, object>>} - Map of user_id -> employee data
 */
async function fetchEmployees() {
  const employees = new Map();
  let pageToken = '';
  
  try {
    do {
      const params = {
        department_id: '0', // Root department = all employees
        page_size: 50,
        user_id_type: 'user_id'
      };
      if (pageToken) params.page_token = pageToken;
      
      const result = await larkApi('GET', '/contact/v3/users', { params });
      
      for (const user of (result.items || [])) {
        employees.set(user.user_id, {
          user_id: user.user_id,
          name: user.name,
          en_name: user.en_name,
          nickname: user.nickname,
          email: user.email,
          mobile: user.mobile,
          department_ids: user.department_ids,
          open_id: user.open_id
        });
      }
      
      pageToken = result.has_more ? result.page_token : '';
    } while (pageToken);
    
    return employees;
  } catch (error) {
    console.error('Failed to fetch employees from Lark API:', error.message);
    console.log('[employees] Using fallback static employee data');
    // Return fallback data
    const fallback = new Map();
    for (const [id, emp] of Object.entries(FALLBACK_EMPLOYEES)) {
      fallback.set(id, emp);
    }
    return fallback;
  }
}

/**
 * Get employee cache (refreshes if stale)
 */
async function getEmployeeCache() {
  const now = Date.now();
  if (!employeeCache || (now - cacheTimestamp) > CACHE_TTL) {
    employeeCache = await fetchEmployees();
    cacheTimestamp = now;
    
    if (employeeCache.size > 0) {
      console.log(`[employees] Loaded ${employeeCache.size} employees from Lark API`);
    }
  }
  return employeeCache;
}

/**
 * Build name lookup index from employee cache
 */
function buildNameIndex(employees) {
  const index = new Map();
  
  for (const [userId, emp] of employees) {
    // Index by various name fields (case-insensitive)
    const names = [emp.name, emp.en_name, emp.nickname].filter(Boolean);
    for (const name of names) {
      index.set(name.toLowerCase(), userId);
      // Also index parts (e.g., "Wang Boyang" -> "boyang", "wang")
      for (const part of name.split(/\s+/)) {
        if (part.length > 1) {
          index.set(part.toLowerCase(), userId);
        }
      }
    }
  }
  
  return index;
}

/**
 * Resolve a name to user_id
 * @param {string} name - Employee name (case-insensitive)
 * @returns {Promise<string|null>} - user_id or null if not found
 */
export async function resolveNameToId(name) {
  if (!name) return null;
  
  const employees = await getEmployeeCache();
  
  // Check if it's already a user_id
  if (employees.has(name)) return name;
  
  // Build index and lookup
  const index = buildNameIndex(employees);
  return index.get(name.toLowerCase()) || null;
}

/**
 * Resolve multiple names to user_ids
 * @param {string[]} names - Array of names
 * @returns {Promise<{resolved: string[], unresolved: string[]}>}
 */
export async function resolveNames(names) {
  const resolved = [];
  const unresolved = [];
  
  for (const name of names) {
    const userId = await resolveNameToId(name.trim());
    if (userId) {
      if (!resolved.includes(userId)) {
        resolved.push(userId);
      }
    } else {
      unresolved.push(name);
    }
  }
  
  return { resolved, unresolved };
}

/**
 * Get employee info by user_id
 * @param {string} userId 
 * @returns {Promise<object|null>}
 */
export async function getEmployee(userId) {
  const employees = await getEmployeeCache();
  return employees.get(userId) || null;
}

/**
 * Get display name for a user_id
 * @param {string} userId 
 * @returns {Promise<string>}
 */
export async function getDisplayName(userId) {
  const emp = await getEmployee(userId);
  return emp ? (emp.name || emp.en_name || userId) : userId;
}

/**
 * Synchronous display name (uses cached data only)
 * For use in non-async contexts - may return user_id if cache not populated
 */
export function getDisplayNameSync(userId) {
  if (!employeeCache) return userId;
  const emp = employeeCache.get(userId);
  return emp ? (emp.name || emp.en_name || userId) : userId;
}

/**
 * Ensure admin user is in the attendee list (if configured)
 * @param {string[]} userIds 
 * @returns {string[]}
 */
export function ensureAdminIncluded(userIds) {
  if (ADMIN_USER_ID && !userIds.includes(ADMIN_USER_ID)) {
    return [...userIds, ADMIN_USER_ID];
  }
  return userIds;
}

/**
 * List all employees (for debugging/display)
 * @returns {Promise<object[]>}
 */
export async function listEmployees() {
  const employees = await getEmployeeCache();
  return Array.from(employees.values());
}

/**
 * Search employees by partial name match
 * @param {string} query 
 * @returns {Promise<object[]>}
 */
export async function searchEmployees(query) {
  const employees = await getEmployeeCache();
  const results = [];
  const q = query.toLowerCase();
  
  for (const emp of employees.values()) {
    const searchFields = [emp.name, emp.en_name, emp.nickname, emp.email].filter(Boolean);
    if (searchFields.some(f => f.toLowerCase().includes(q))) {
      results.push(emp);
    }
  }
  
  return results;
}
