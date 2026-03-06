// Refactored Modern JavaScript - ES6+
// This file demonstrates the same code after ES6+ refactoring

// ============================================
// PATTERN 1: const/let declarations
// ============================================
const globalConfig = {
  apiUrl: 'https://api.example.com/v1',
  timeout: 5000,
  retries: 3
};

let shouldRetry = true;
let retryCount = 0;

// ============================================
// PATTERN 2: Arrow functions
// ============================================
const fetchData = (url, callback) => {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', url);
  xhr.onload = () => {
    if (xhr.status === 200) {
      callback(null, JSON.parse(xhr.responseText));
    } else {
      callback(new Error(xhr.statusText));
    }
  };
  xhr.onerror = () => {
    callback(new Error('Network error'));
  };
  xhr.send();
};

// ============================================
// PATTERN 3: Template literals
// ============================================
const formatMessage = (user, count) => {
  let message = `Hello ${user.name}! You have ${count} unread messages.`;
  if (count > 1) {
    message += ' Click here to view them.';
  }
  return message;
};

// ============================================
// PATTERN 4: for...of loop
// ============================================
const processItems = (items) => {
  const results = [];
  for (const item of items) {
    if (item.active) {
      results.push(item.value * 2);
    }
  }
  return results;
};

const findIndex = (arr, predicate) => {
  for (let i = 0; i < arr.length; i++) {
    if (predicate(arr[i], i)) {
      return i;
    }
  }
  return -1;
};

// ============================================
// PATTERN 5: Object literal shorthand
// ============================================
const createUser = (name, email, age) => ({
  name,
  email,
  age,
  role: 'user',
  active: true,
  createdAt: new Date().toISOString()
});

// ============================================
// PATTERN 6: Object spread merging
// ============================================
const mergeOptions = (defaults, options) => ({
  ...defaults,
  ...options
});

// ============================================
// PATTERN 7: Promisified async (promises + async/await)
// ============================================
// First, let's promisify fetchData
const fetchDataPromise = (url) => {
  return new Promise((resolve, reject) => {
    fetchData(url, (err, data) => {
      if (err) reject(err);
      else resolve(data);
    });
  });
};

// Using async/await with proper error handling
const loadUser = async (userId) => {
  try {
    const user = await fetchDataPromise(`/api/users/${userId}`);
    const profile = await fetchDataPromise(`/api/profile/${user.profileId}`);
    return {user, profile};
  } catch (err) {
    throw err;
  }
};

// ============================================
// PATTERN 8: Rest parameters & spread
// ============================================
const sum = (...args) => {
  return args.reduce((acc, val) => acc + val, 0);
};

class Logger {
  constructor(prefix = '') {
    this.prefix = prefix;
  }

  log(...args) {
    console.log(`[${this.prefix}]`, ...args);
  }
}

// ============================================
// PATTERN 9: Array extensions (class syntax)
// ============================================
// Note: Modifying built-in prototypes is still discouraged
// But we can create utility classes instead
class ExtendedArray extends Array {
  first() {
    return this[0];
  }

  last() {
    return this[this.length - 1];
  }
}

// Or use utility functions:
const arrayUtils = {
  first: (arr) => arr[0],
  last: (arr) => arr[arr.length - 1]
};

// ============================================
// PATTERN 10: Class syntax
// ============================================
class Person {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }

  greet() {
    return `Hello, I'm ${this.name} and I'm ${this.age} years old.`;
  }

  haveBirthday() {
    this.age += 1;
    return this;
  }
}

// ============================================
// PATTERN 11: Default parameters
// ============================================
const connect = (options = {}) => {
  const {
    host = 'localhost',
    port = 8080,
    timeout = 30000
  } = options;

  return {host, port, timeout};
};

// ============================================
// PATTERN 12: Export as ES module
// ============================================
const utils = {
  formatDate: (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  capitalize: (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  debounce: (func, wait) => {
    let timeout;
    return function(...args) {
      const context = this;
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    };
  }
};

// Destructuring examples
const {formatDate, capitalize, debounce} = utils;

// Export multiple named exports
export {
  utils,
  formatDate,
  capitalize,
  debounce,
  connect,
  Person,
  Logger,
  fetchDataPromise,
  loadUser,
  mergeOptions,
  createUser,
  processItems,
  findIndex,
  arrayUtils,
  ExtendedArray
};

// Default export (if this were the main module)
// export default utils;
