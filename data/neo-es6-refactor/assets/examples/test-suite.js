// Unit Test Suite for ES6 Refactor Skill
// Examples to test each transformation pattern

// ============================================
// TEST GROUP: Variable Declarations
// ============================================

// Test 1: Simple var to const
(function testVarToConst() {
  var simpleVar = 42;
  console.log(simpleVar);
});

// Test 2: var to let when reassigned
(function testVarToLet() {
  var counter = 0;
  for (var i = 0; i < 10; i++) {
    counter += i;
  }
});

// Test 3: Multiple var declarations
(function testMultipleVar() {
  var x = 1;
  var y = 2;
  var z = 3;
  console.log(x, y, z);
});

// ============================================
// TEST GROUP: Functions
// ============================================

// Test 4: Function expression to arrow
var add = function(a, b) {
  return a + b;
};

// Test 5: Multi-parameter arrow
const multiply = (a, b) => {
  return a * b;
};

// Test 6: Implicit return arrow
const double = (x) => x * 2;

// Test 7: Single parameter implicit return
const square = x => x * x;

// Test 8: Parentheses required for single param with destructuring
const duplicate = ([arr]) => [...arr, ...arr];

// Test 9: Arrow this context
var obj = {
  value: 10,
  increment: function() {
    setTimeout(() => {
      this.value += 1;  // Arrow preserves this
      console.log(this.value);
    }, 100);
  }
};

// ============================================
// TEST GROUP: Strings
// ============================================

// Test 10: Simple concatenation to template
var name = 'World';
var greeting = 'Hello, ' + name + '!';

// Test 11: Multiple interpolations
var firstName = 'John';
var lastName = 'Doe';
var age = 30;
var message = firstName + ' ' + lastName + ' is ' + age + ' years old.';

// Test 12: Empty template literal
var empty = '';

// ============================================
// TEST GROUP: Destructuring
// ============================================

// Test 13: Array destructuring
var pair = [1, 2];
var first = pair[0];
var second = pair[1];

// Test 14: Skip elements
var array = [1, 2, 3, 4, 5];
var firstEl = array[0];
var thirdEl = array[2];
var fifthEl = array[4];

// Test 15: Rest in destructuring
var [head, ...tail] = [1, 2, 3, 4];

// Test 16: Object destructuring
var person = {name: 'Alice', age: 25, city: 'NYC'};
var personName = person.name;
var personAge = person.age;

// Test 17: Rename in destructuring
var user = {username: 'jdoe', email: 'j@example.com'};
var userName = user.username;
var userEmail = user.email;

// Test 18: Nested object destructuring
var data = {
  user: {
    profile: {
      name: 'Bob',
      age: 30
    }
  }
};
var userNameNested = data.user.profile.name;
var userAgeNested = data.user.profile.age;

// Test 19: Default values in destructuring
var maybeName;
var nameDefault = maybeName || 'Guest';

// ============================================
// TEST GROUP: Loops
// ============================================

// Test 20: Traditional for to for...of
var numbers = [1, 2, 3, 4, 5];
var doubled = [];
for (var i = 0; i < numbers.length; i++) {
  doubled.push(numbers[i] * 2);
}

// Test 21: for...in with hasOwnProperty (to Object.keys)
var objLoop = {a: 1, b: 2, c: 3};
for (var key in objLoop) {
  if (objLoop.hasOwnProperty(key)) {
    console.log(key, objLoop[key]);
  }
}

// Test 22: Manual array iteration with index
var items = ['a', 'b', 'c'];
for (var idx = 0; idx < items.length; idx++) {
  console.log(idx, items[idx]);
}

// ============================================
// TEST GROUP: Objects
// ============================================

// Test 23: Property value shorthand
var a = 1;
var b = 2;
var c = 3;
var shorthandObj = {a: a, b: b, c: c};

// Test 24: Method shorthand
var methods = {
  getName: function() {
    return this.name;
  },
  getAge: function() {
    return this.age;
  }
};

// Test 25: Computed property names
var key = 'dynamic';
var computedObj = {};
computedObj['prop_' + key] = 'value';

// Test 26: Object.assign to spread
var defaults = {x: 10, y: 20};
var options = {y: 30, z: 40};
var merged = Object.assign({}, defaults, options);

// Test 27: Dynamic object creation
var dynamicObj = {};
dynamicObj['key' + 1] = 'value1';
dynamicObj['key' + 2] = 'value2';

// ============================================
// TEST GROUP: Arrays
// ============================================

// Test 28: Array.concat to spread
var arr1 = [1, 2];
var arr2 = [3, 4];
var concatenated = arr1.concat(arr2);

// Test 29: Array.prototype.push with apply
var newArr = [1, 2];
var more = [3, 4, 5];
Array.prototype.push.apply(newArr, more);

// ============================================
// TEST GROUP: Modules / CommonJS
// ============================================

// Test 30: CommonJS require
var fs = require('fs');
var path = require('path');

// Test 31: module.exports
var myModule = {
  func1: function() {},
  func2: function() {}
};
module.exports = myModule;

// Test 32: exports assignment
function helper() {}
exports.helper = helper;

// Test 33: module.exports = specific thing
function MyClass() {}
module.exports = MyClass;

// ============================================
// TEST GROUP: Classes
// ============================================

// Test 34: Constructor assignment to class properties
function Animal(name) {
  this.name = name;
  this.age = 0;
}

// Test 35: Prototype methods
Animal.prototype.speak = function() {
  return this.name + ' says hello';
};

// ============================================
// TEST GROUP: Async
// ============================================

// Test 36: Callback-style to Promise
function readFileCallbackES5(path, callback) {
  var fs = require('fs');
  fs.readFile(path, 'utf8', function(err, data) {
    if (err) return callback(err);
    callback(null, data);
  });
}

// Test 37: Promise.then chaining
var promise = new Promise(function(resolve, reject) {
  resolve(42);
});
promise.then(function(value) {
  return value * 2;
}).then(function(result) {
  console.log(result);
});

// ============================================
// TEST GROUP: Default Parameters
// ============================================

// Test 38: Manual default assignment
function connectES5(options) {
  options = options || {};
  var host = options.host || 'localhost';
  var port = options.port || 8080;
  return {host: host, port: port};
}

// ============================================
// TEST GROUP: Rest/Spread in function calls
// ============================================

// Test 39: Function.apply to spread
function sumES5() {
  var total = 0;
  for (var i = 0; i < arguments.length; i++) {
    total += arguments[i];
  }
  return total;
}

// Test 40: Function.prototype.call with array
var logES5 = Function.prototype.call.bind(console.log);
logES5.apply(console, [1, 2, 3]);

// ============================================
// TEST GROUP: Map/Filter/Reduce Arrow Conversion
// ============================================

// Test 41: map anonymous function
var nums = [1, 2, 3];
var doubledES5 = nums.map(function(x) {
  return x * 2;
});

// Test 42: filter with function
var filteredES5 = nums.filter(function(x) {
  return x % 2 === 0;
});

// Test 43: reduce with multi-line function
var sumES5Reduce = nums.reduce(function(acc, val) {
  return acc + val;
}, 0);

// ============================================
// TEST GROUP: Template Literal Edge Cases
// ============================================

// Test 44: Nested template literals
var nestedTemplate = 'Hello, ' + (true ? 'World' : 'Stranger') + '!';

// Test 45: Tagged template
var tag = function(strings, ...values) {
  return strings.reduce(function(acc, str, i) {
    return acc + str + (values[i] || '');
  }, '');
};
var tagged = tag`Hello ${name}!`;

// ============================================
// TEST GROUP: TypeScript-specific (if applicable)
// ============================================

// Test 46: Type assertion function (keep as-is)
function asString(value) {
  return String(value);
}

// Test 47: Class field declarations (JS class syntax)
class ModernClass {
  // Class fields (stage 3 proposal, may need handling)
  // field = value;
  // static staticField = value;
}

// ============================================
// TEST GROUP: Should NOT transform
// ============================================

// Test 48: var used as function-scoped intentionally (avoid converting to let)
(function IIFE() {
  var i;
  for (i = 0; i < 10; i++) {
    // i should be accessible outside loop in this closure
  }
});

// Test 49: this-dependent function (don't convert to arrow)
var objWithThis = {
  value: 100,
  getValue: function() {
    return this.value;
  }
};

// Test 50: Function constructor (arguments used intentionally)
var argsPrinter = function() {
  console.log(arguments);
};

// ============================================
// TEST GROUP: Edge Cases
// ============================================

// Test 51: Arguments with rest parameter shadow
function(...args) {
  // Should not have 'arguments' after transformation
}

// Test 52: Default parameter with undefined
function defaultTest(value) {
  value = value || 'default';
  return value;
}

// Test 53: Multiple default assignments in one function
function multiDefaults(a, b, c) {
  a = a || 1;
  b = b || 2;
  c = c || 3;
  return a + b + c;
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    testVarToConst: 1,
    testVarToLet: 2,
    testMultipleVar: 3,
    testArrow: 4,
    testImplicitReturn: 5,
    testTemplate: 6,
    testDestructuring: 7,
    testForOf: 8,
    testObjectShorthand: 9,
    testObjectAssign: 10,
    testCommonJS: 11,
    testCallback: 12,
    testDefaultParams: 13,
    testMapFilterReduce: 14,
    testNoTransform: 15
  };
}
