function generateId(prefix = 'id') {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 9);
  return `${prefix}-${timestamp}-${random}`;
}

function formatDate(date) {
  const d = date instanceof Date ? date : new Date(date);
  return d.toISOString();
}

function formatDuration(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
  if (hours > 0) return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
}

function calculateCost(model, inputTokens, outputTokens) {
  if (model.pricing_model === 'subscription') {
    return 0;
  }
  
  if (model.pricing_model === 'tiered_usage') {
    if (model.daily_used < model.daily_quota && model.monthly_used < model.monthly_quota) {
      return 0;
    }
    const overageInput = Math.max(0, inputTokens - (model.daily_quota - model.daily_used));
    const overageOutput = Math.max(0, outputTokens - (model.daily_quota - model.daily_used));
    return (overageInput + overageOutput) * (model.overage_rate || 0) / 1000;
  }
  
  if (model.pricing_model === 'pay_per_use') {
    const inputCost = (inputTokens / 1000) * (model.input_cost_per_1k || 0);
    const outputCost = (outputTokens / 1000) * (model.output_cost_per_1k || 0);
    return inputCost + outputCost;
  }
  
  return 0;
}

function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function mergeObjects(target, source) {
  const result = deepClone(target);
  for (const key in source) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = mergeObjects(result[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validateUrl(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

function sanitizeFilename(filename) {
  return filename.replace(/[^a-zA-Z0-9._-]/g, '_');
}

function parseJsonSafely(str, defaultValue = null) {
  try {
    return JSON.parse(str);
  } catch {
    return defaultValue;
  }
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function throttle(func, limit) {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

function retryWithBackoff(fn, maxRetries = 3, delay = 1000) {
  return new Promise((resolve, reject) => {
    let retries = 0;
    
    function attempt() {
      fn()
        .then(resolve)
        .catch(error => {
          retries++;
          if (retries >= maxRetries) {
            reject(error);
          } else {
            const waitTime = delay * Math.pow(2, retries - 1);
            setTimeout(attempt, waitTime);
          }
        });
    }
    
    attempt();
  });
}

function chunkArray(array, size) {
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

function groupBy(array, key) {
  return array.reduce((result, item) => {
    const group = typeof key === 'function' ? key(item) : item[key];
    if (!result[group]) result[group] = [];
    result[group].push(item);
    return result;
  }, {});
}

function sortBy(array, key, order = 'asc') {
  return [...array].sort((a, b) => {
    const aVal = typeof key === 'function' ? key(a) : a[key];
    const bVal = typeof key === 'function' ? key(b) : b[key];
    
    if (order === 'asc') {
      return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
    } else {
      return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
    }
  });
}

function uniqueBy(array, key) {
  const seen = new Set();
  return array.filter(item => {
    const k = typeof key === 'function' ? key(item) : item[key];
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

module.exports = {
  generateId,
  formatDate,
  formatDuration,
  calculateCost,
  deepClone,
  mergeObjects,
  validateEmail,
  validateUrl,
  sanitizeFilename,
  parseJsonSafely,
  debounce,
  throttle,
  retryWithBackoff,
  chunkArray,
  groupBy,
  sortBy,
  uniqueBy
};
