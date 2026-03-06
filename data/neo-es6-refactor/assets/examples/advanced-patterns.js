// Advanced ES5 to ES6+ Refactoring Patterns
// Complex transformations and edge cases

// ============================================
// COMPLEX PATTERN 1: Nested destructuring
// ============================================
// Before:
function processUserDataES5(data) {
  var address = data.address || {};
  var city = address.city || 'Unknown';
  var country = address.country || 'Unknown';
  var settings = data.settings || {};
  var theme = settings.theme || 'light';
  var notifications = settings.notifications || {};
  var email = notifications.email !== false;
  var push = notifications.push !== false;
  return {
    city: city,
    country: country,
    theme: theme,
    emailNotify: email,
    pushNotify: push
  };
}

// After:
const processUserDataES6 = (data = {}) => {
  const {
    address: {
      city = 'Unknown',
      country = 'Unknown'
    } = {},
    settings: {
      theme = 'light',
      notifications: {
        email = true,
        push = true
      } = {}
    } = {}
  } = data;

  return {
    city,
    country,
    theme,
    emailNotify: email,
    pushNotify: push
  };
};

// ============================================
// COMPLEX PATTERN 2: Class inheritance
// ============================================
// Before:
function AnimalES5(name) {
  this.name = name;
}

AnimalES5.prototype.speak = function() {
  console.log(this.name + ' makes a noise.');
};

function DogES5(name, breed) {
  AnimalES5.call(this, name);
  this.breed = breed;
}

DogES5.prototype = Object.create(AnimalES5.prototype);
DogES5.prototype.constructor = DogES5;
DogES5.prototype.speak = function() {
  console.log(this.name + ' barks.');
};

// After:
class AnimalES6 {
  constructor(name) {
    this.name = name;
  }

  speak() {
    console.log(`${this.name} makes a noise.`);
  }
}

class DogES6 extends AnimalES6 {
  constructor(name, breed) {
    super(name);
    this.breed = breed;
  }

  speak() {
    console.log(`${this.name} barks.`);
  }
}

// ============================================
// COMPLEX PATTERN 3: Nested callbacks to async/await
// ============================================
// Before:
function fetchComplexDataES5(userId, options, callback) {
  var timeout = options.timeout || 5000;
  var retries = options.retries || 3;

  getProfile(userId, function(err1, profile) {
    if (err1) return callback(err1);

    getPermissions(profile.role, function(err2, permissions) {
      if (err2) return callback(err2);

      getSettings(userId, function(err3, settings) {
        if (err3) return callback(err3);

        var result = {
          profile: profile,
          permissions: permissions,
          settings: settings,
          meta: {
            userId: userId,
            timestamp: new Date().toISOString()
          }
        };
        callback(null, result);
      });
    });
  });
}

// After:
async function fetchComplexDataES6(userId, options = {}) {
  const {timeout = 5000, retries = 3} = options;

  try {
    const [profile, permissions, settings] = await Promise.all([
      getProfilePromise(userId),
      getPermissionsPromise(profile.role),
      getSettingsPromise(userId)
    ]);

    return {
      profile,
      permissions,
      settings,
      meta: {
        userId,
        timestamp: new Date().toISOString()
      }
    };
  } catch (err) {
    throw err;
  }
}

// ============================================
// COMPLEX PATTERN 4: Object.defineProperty to computed properties
// ============================================
// Before:
var PersonES5 = function(firstName, lastName) {
  this.firstName = firstName;
  this.lastName = lastName;
};

Object.defineProperty(PersonES5.prototype, 'fullName', {
  get: function() {
    return this.firstName + ' ' + this.lastName;
  },
  set: function(name) {
    var parts = name.split(' ');
    this.firstName = parts[0] || '';
    this.lastName = parts.slice(1).join(' ') || '';
  },
  enumerable: true,
  configurable: true
});

Object.defineProperty(PersonES5.prototype, 'initials', {
  get: function() {
    return (this.firstName[0] + this.lastName[0]).toUpperCase();
  },
  enumerable: true,
  configurable: true
});

// After:
class PersonES6 {
  constructor(firstName, lastName) {
    this.firstName = firstName;
    this.lastName = lastName;
  }

  get fullName() {
    return `${this.firstName} ${this.lastName}`;
  }

  set fullName(name) {
    const parts = name.split(' ');
    this.firstName = parts[0] || '';
    this.lastName = parts.slice(1).join(' ') || '';
  }

  get initials() {
    return `${this.firstName[0]}${this.lastName[0]}`.toUpperCase();
  }
}

// ============================================
// COMPLEX PATTERN 5: Generator functions
// ============================================
// Before (ES5 iterator pattern):
function createRangeIteratorES5(start, end) {
  var current = start;
  return {
    next: function() {
      if (current < end) {
        return {value: current++, done: false};
      }
      return {value: undefined, done: true};
    }
  };
}

function iterateRangeES5(start, end) {
  var iterator = createRangeIteratorES5(start, end);
  var result = [];
  var step;
  while (!(step = iterator.next()).done) {
    result.push(step.value);
  }
  return result;
}

// After (ES6 generator):
function* createRangeGeneratorES6(start, end) {
  for (let i = start; i < end; i++) {
    yield i;
  }
}

const iterateRangeES6 = (start, end) => {
  return [...createRangeGeneratorES6(start, end)];
};

// ============================================
// COMPLEX PATTERN 6: Map/Set instead of objects/arrays
// ============================================
// Before:
var cacheES5 = {};
cacheES5['key1'] = 'value1';
cacheES5['key2'] = 'value2';

var hasKeyES5 = function(key) {
  return cacheES5.hasOwnProperty(key);
};

var getKeyES5 = function(key) {
  return cacheES5[key];
};

var allKeysES5 = function() {
  return Object.keys(cacheES5);
};

// After:
const cacheES6 = new Map();
cacheES6.set('key1', 'value1');
cacheES6.set('key2', 'value2');

const hasKeyES6 = (key) => cacheES6.has(key);
const getKeyES6 = (key) => cacheES6.get(key);
const allKeysES6 = () => Array.from(cacheES6.keys());

// ============================================
// COMPLEX PATTERN 7: Symbol-based properties
// ============================================
// Before (string key collisions possible):
var internalId = '_internalId_' + Math.random();

var objES5 = {};
objES5[internalId] = 123;

// After:
const internalIdSymbol = Symbol('internalId');
const objES6 = {
  [internalIdSymbol]: 123
};

// ============================================
// COMPLEX PATTERN 8: Iterators with for...of
// ============================================
// Before:
function iterateObjectKeysES5(obj) {
  var keys = Object.keys(obj);
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    console.log(key, obj[key]);
  }
}

// After:
const iterateObjectKeysES6 = (obj) => {
  for (const [key, value] of Object.entries(obj)) {
    console.log(key, value);
  }
};

// ============================================
// COMPLEX PATTERN 9: Promise chaining
// ============================================
// Before:
function fetchDataChainES5(userId) {
  fetchUser(userId)
    .then(function(user) {
      return fetchPosts(user.id);
    })
    .then(function(posts) {
      return fetchComments(posts[0].id);
    })
    .then(function(comments) {
      return processAll(user, posts, comments);
    })
    .catch(function(err) {
      console.error('Failed:', err);
    });
}

// After:
const fetchDataChainES6 = async (userId) => {
  try {
    const user = await fetchUser(userId);
    const posts = await fetchPosts(user.id);
    const comments = await fetchComments(posts[0].id);
    return processAll(user, posts, comments);
  } catch (err) {
    console.error('Failed:', err);
    throw err;
  }
};

// ============================================
// COMPLEX PATTERN 10: Enhanced object literals
// ============================================
// Before:
function createConfigES5(env, port, debug) {
  var config = {};
  config.env = env;
  config.port = port;
  config.debug = debug;
  config.server = {
    host: 'localhost',
    port: port,
    timeout: 30000
  };
  config.logging = {
    level: debug ? 'debug' : 'info',
    format: 'json'
  };
  return config;
}

// After:
const createConfigES6 = (env, port, debug) => ({
  env,
  port,
  debug,
  server: {
    host: 'localhost',
    port,
    timeout: 30000
  },
  logging: {
    level: debug ? 'debug' : 'info',
    format: 'json'
  }
});

export {
  processUserDataES5,
  processUserDataES6,
  AnimalES5,
  AnimalES6,
  DogES5,
  DogES6,
  fetchComplexDataES5,
  fetchComplexDataES6,
  PersonES5,
  PersonES6,
  createRangeIteratorES5,
  iterateRangeES5,
  createRangeGeneratorES6,
  iterateRangeES6,
  cacheES5,
  cacheES6,
  iterateObjectKeysES5,
  iterateObjectKeysES6,
  fetchDataChainES5,
  fetchDataChainES6,
  createConfigES5,
  createConfigES6
};
