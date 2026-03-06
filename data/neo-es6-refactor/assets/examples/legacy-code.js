// Legacy JavaScript Code - ES5 Style
// This file demonstrates common ES5 patterns that should be refactored to ES6+

// ============================================
// PATTERN 1: var declarations
// ============================================
var globalConfig = {
  apiUrl: 'https://api.example.com/v1',
  timeout: 5000,
  retries: 3
};

var shouldRetry = true;
var retryCount = 0;

// ============================================
// PATTERN 2: Function expressions
// ============================================
var fetchData = function(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url);
  xhr.onload = function() {
    if (xhr.status === 200) {
      callback(null, JSON.parse(xhr.responseText));
    } else {
      callback(new Error(xhr.statusText));
    }
  };
  xhr.onerror = function() {
    callback(new Error('Network error'));
  };
  xhr.send();
};

// ============================================
// PATTERN 3: String concatenation
// ============================================
var formatMessage = function(user, count) {
  var message = 'Hello ' + user.name + '! You have ' + count + ' unread messages.';
  if (count > 1) {
    message += ' Click here to view them.';
  }
  return message;
};

// ============================================
// PATTERN 4: Traditional for loops
// ============================================
var processItems = function(items) {
  var results = [];
  for (var i = 0; i < items.length; i++) {
    var item = items[i];
    if (item.active) {
      results.push(item.value * 2);
    }
  }
  return results;
};

var findIndex = function(arr, predicate) {
  for (var i = 0; i < arr.length; i++) {
    if (predicate(arr[i], i)) {
      return i;
    }
  }
  return -1;
};

// ============================================
// PATTERN 5: Object property repetition
// ============================================
var createUser = function(name, email, age) {
  return {
    name: name,
    email: email,
    age: age,
    role: 'user',
    active: true,
    createdAt: new Date().toISOString()
  };
};

// ============================================
// PATTERN 6: Manual object merging
// ============================================
var mergeOptions = function(defaults, options) {
  var result = {};
  for (var key in defaults) {
    if (defaults.hasOwnProperty(key)) {
      result[key] = defaults[key];
    }
  }
  for (var key in options) {
    if (options.hasOwnProperty(key)) {
      result[key] = options[key];
    }
  }
  return result;
};

// ============================================
// PATTERN 7: Callback-based async
// ============================================
var loadUser = function(userId, callback) {
  fetchData('/api/users/' + userId, function(err, user) {
    if (err) {
      return callback(err);
    }
    fetchData('/api/profile/' + user.profileId, function(err, profile) {
      if (err) {
        return callback(err);
      }
      callback(null, {
        user: user,
        profile: profile
      });
    });
  });
};

// ============================================
// PATTERN 8: arguments object usage
// ============================================
var sum = function() {
  var total = 0;
  for (var i = 0; i < arguments.length; i++) {
    total += arguments[i];
  }
  return total;
};

var Logger = function(prefix) {
  this.prefix = prefix || '';
};

Logger.prototype.log = function() {
  var args = Array.prototype.slice.call(arguments);
  args.unshift('[' + this.prefix + ']');
  console.log.apply(console, args);
};

// ============================================
// PATTERN 9: Array prototyping
// ============================================
Array.prototype.first = function() {
  return this[0];
};

Array.prototype.last = function() {
  return this[this.length - 1];
};

// ============================================
// PATTERN 10: Constructor functions
// ============================================
var Person = function(name, age) {
  this.name = name;
  this.age = age;
};

Person.prototype.greet = function() {
  return 'Hello, I\'m ' + this.name + ' and I\'m ' + this.age + ' years old.';
};

Person.prototype.haveBirthday = function() {
  this.age += 1;
  return this;
};

// ============================================
// PATTERN 11: Default parameter simulation
// ============================================
var connect = function(options) {
  options = options || {};
  var host = options.host || 'localhost';
  var port = options.port || 8080;
  var timeout = options.timeout || 30000;
  return {host: host, port: port, timeout: timeout};
};

// ============================================
// PATTERN 12: Module pattern (CommonJS)
// ============================================
var utils = {
  formatDate: function(date) {
    return date.getFullYear() + '-' +
           ('0' + (date.getMonth() + 1)).slice(-2) + '-' +
           ('0' + date.getDate()).slice(-2);
  },
  capitalize: function(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },
  debounce: function(func, wait) {
    var timeout;
    return function() {
      var context = this;
      var args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(function() {
        func.apply(context, args);
      }, wait);
    };
  }
};

module.exports = utils;
