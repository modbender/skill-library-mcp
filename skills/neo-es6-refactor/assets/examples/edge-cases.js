// Edge Cases and Special Scenarios in ES5→ES6+ Refactoring
// These demonstrate transformations that require careful handling

// ============================================
// EDGE CASE 1: this binding preservation
// ============================================
// DO NOT transform these to arrow functions!
var Counter = function() {
  this.count = 0;
};

Counter.prototype.increment = function() {
  this.count += 1;
  setTimeout(function() {
    // Need this to refer to Counter instance, not setTimeout
    console.log('Count:', this.count);
  }.bind(this), 1000);
};

// After refactoring (keep regular function with bind or use arrow carefully):
class CounterES6 {
  count = 0;

  increment() {
    this.count += 1;
    setTimeout(() => {
      // Arrow function preserves lexical this
      console.log('Count:', this.count);
    }, 1000);
  }
}

// But NOT this (arrow would lose instance binding):
var BadExample = {
  value: 42,
  getValue: () => this.value  // this is lexical (window/global), not BadExample!
};

// ============================================
// EDGE CASE 2: Arguments object in strict mode
// ============================================
'use strict';

var strictFunction = function() {
  // arguments exists but is not linked to parameters
  console.log(arguments.length);
  // This would throw in strict mode:
  // arguments[0] = 'new value'; // Silent fail or throw
};

// After (use rest):
const strictFunctionES6 = (...args) => {
  console.log(args.length);
  // args is a real array, not arguments object
  args[0] = 'new value'; // Works!
};

// ============================================
// EDGE CASE 3: Function hoisting differences
// ============================================
// ES5 function declarations are hoisted
var result1 =();
function result1() { return 'hoisted'; }  // OK - hoisted

// ES6: 'const' and 'let' are not hoisted (TDZ)
// const result2 = result2();  // ReferenceError!
// let result2 = () => 'not hoisted';

// Function expressions vs declarations:
var f = function fExpr() { return 'named function expression'; };
// fExpr is only available inside the function

// After ES6 class (no hoisting at all):
class MyClass {
  // Class declarations are not hoisted
  method() {}
}
// new MyClass() before declaration throws ReferenceError

// ============================================
// EDGE CASE 4: Hexadecimal/octal literal changes
// ============================================
var oldHex = 0xFF;      // ES5: valid
var oldOctal = 0755;    // ES5: valid (leading zero), but discouraged
var legacyOctal = 0o755; // ES6: valid, explicit octal

// Be careful with leading zeros in strict mode:
'use strict';
// var strictOctal = 0755; // SyntaxError in ES5 strict mode
var strictOctalES6 = 0o755; // OK

// ============================================
// EDGE CASE 5: Reserved words as property names
// ============================================
var objES5 = {
  'default': 1,
  'class': 2,
  'for': 3,
  'let': 4  // 'let' was future-reserved in ES5
};

// In ES6, these can be used unquoted in some contexts:
const objES6 = {
  default: 1,  // valid in object literals
  class: 2,
  'for': 3,    // 'for' is still a keyword, must quote
  let: 4       // 'let' is a keyword, must quote
};

// But 'default' and 'class' are now allowed as identifiers in many places:
const class = 'my-class';  // Valid in ES6!
const default = 'default value';  // Valid in ES6!

// ============================================
// EDGE CASE 6: Prototype chain manipulation
// ============================================
var Parent = function(name) {
  this.name = name;
};

Parent.prototype.sayHello = function() {
  return 'Hello from ' + this.name;
};

var Child = function(name, age) {
  Parent.call(this, name);  // Explicit constructor call
  this.age = age;
};

// Manual prototype chain setup (ES5):
Child.prototype = Object.create(Parent.prototype);
Child.prototype.constructor = Child;
Child.prototype.sayAge = function() {
  return this.name + ' is ' + this.age;
};

// ES6 does this automatically with extends:
class ParentES6 {
  constructor(name) {
    this.name = name;
  }

  sayHello() {
    return `Hello from ${this.name}`;
  }
}

class ChildES6 extends ParentES6 {
  constructor(name, age) {
    super(name);  // Calls parent constructor
    this.age = age;
  }

  sayAge() {
    return `${this.name} is ${this.age}`;
  }
}

// ============================================
// EDGE CASE 7: getters/setters - descriptor vs syntax
// ============================================
var objES5 = {};
Object.defineProperty(objES5, 'value', {
  get: function() {
    return this._value;
  },
  set: function(newValue) {
    this._value = newValue * 2;  // Custom logic
  },
  enumerable: true,
  configurable: true
});

// ES6 class syntax:
class ES6Class {
  constructor(initialValue) {
    this._value = initialValue;
  }

  get value() {
    return this._value;
  }

  set value(newValue) {
    this._value = newValue * 2;  // Same custom logic
  }
}

// Object literal shorthand:
const objES6 = {
  _value: 0,
  get value() {
    return this._value;
  },
  set value(newValue) {
    this._value = newValue * 2;
  }
};

// ============================================
// EDGE CASE 8: Symbol properties
// ============================================
var sym = Symbol('secret');
var obj = {
  [sym]: 'hidden value',
  normalProp: 'visible'
};

// Symbols are guaranteed unique:
var sym2 = Symbol('secret');
console.log(sym === sym2);  // false

// Well-known symbols:
var arr = [1, 2, 3];
console.log(arr[Symbol.iterator]);  // Function

// ============================================
// EDGE CASE 9: Modifying built-in prototypes (discouraged)
// ============================================
Array.prototype.first = function() {
  return this[0];
};

// ES6 alternative (better):
if (!Array.prototype.first) {
  Object.defineProperty(Array.prototype, 'first', {
    value: function() {
      return this[0];
    },
    writable: true,
    configurable: true,
    enumerable: false  // Important: don't enumerate
  });
}

// Or use utility function:
const first = (arr) => arr[0];

// ============================================
// EDGE CASE 10: Implicit globals
// ============================================
function createGlobalLeakES5() {
  // Without var/let/const, creates global property
  accidentalGlobal = 'oops';
  var intentional = 'ok';
}

createGlobalLeakES5();
console.log(accidentalGlobal);  // 'oops' - pollutes global!

// ES6 with 'use strict' prevents this:
'use strict';
function noLeak() {
  // accidental = 'error';  // ReferenceError
  const proper = 'local';   // Block-scoped
  let alsoLocal = 'also local';
}

// ============================================
// EDGE CASE 11: Function constructor quirks
// ============================================
var F = function() {};
F.prototype = {constructor: F};

// In ES6, class constructors don't need manual prototype setup:
class ES6Class {
  constructor() {}
  // .prototype.constructor is automatically correct
}
console.log(ES6Class.prototype.constructor === ES6Class);  // true

// ============================================
// EDGE CASE 12: JSON parsing edge cases
// ============================================
var json = '{"value": NaN, "date": "2025-01-01"}';
var parsedES5 = JSON.parse(json);  // NaN becomes null in JSON!

var parsedES6 = JSON.parse(json, (key, value) => {
  // Reviver can handle special cases
  if (typeof value === 'number' && isNaN(value)) {
    return NaN;  // Restore NaN
  }
  return value;
});

// ============================================
// EDGE CASE 13: Exception handling differences
// ============================================
try {
  throw new Error('test');
} catch (e) {
  // ES5: e is any, no type checking
  console.log(e.message);
}

// ES6 with type guard:
try {
  throw new Error('test');
} catch (e) {
  if (e instanceof Error) {
    console.log(e.message);  // TypeScript knows e is Error here
  }
}

// ============================================
// EDGE CASE 14: Regular expression flags
// ============================================
var regexES5 = /pattern/gim;  // Global, case-insensitive, multiline

// ES6 adds 'u' (unicode) and 'y' (sticky)
const regexES6 = /pattern/guims;  // unicode, global, multiline, dotAll

// ============================================
// EDGE CASE 15: Math constants and methods
// ============================================
// ES5 had limited math constants
var es5Constants = {
  PI: Math.PI,
  E: Math.E,
  // Missing: Math.EULER_CONSTANT, Math.LN10, etc in ES5 but exist in ES6
};

// ES6 adds more constants:
const es6Constants = {
  PI: Math.PI,
  E: Math.E,
  LN10: Math.LN10,
  LOG2E: Math.LOG2E,
  LOG10E: Math.LOG10E,
  SQRT1_2: Math.SQRT1_2,
  SQRT2: Math.SQRT2,
  // New methods:
  // Math.cbrt(), Math.clz32(), Math.imul(), Math.sign(), Math.trunc()
};

// ============================================
// EDGE CASE 16: Tail call optimization (strict mode only)
// ============================================
'use strict';

// Proper tail call (TCO) - supported in ES6 but rarely implemented:
function factorial(n, acc = 1) {
  if (n <= 1) return acc;
  return factorial(n - 1, n * acc);  // Tail call
}

// Not a tail call (needs to multiply after recursive call):
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);  // Not tail-recursive
}

// TCO requires:
// 1. Strict mode
// 2. Tail position
// 3. No additional operations after recursive call
// 4. Same function in tail position
// 5. Engine support (Safari only as of 2025)

// ============================================
// EDGE CASE 17: Proxy traps
// ============================================
var target = {value: 42};

var handlerES5 = {
  // ES5 had Object.defineProperty, Object.observe (deprecated)
};

// ES6 Proxy - intercept operations:
const handler = {
  get(target, prop, receiver) {
    console.log(`Getting ${String(prop)}`);
    return Reflect.get(target, prop, receiver);
  },
  set(target, prop, value, receiver) {
    console.log(`Setting ${String(prop)} to ${value}`);
    return Reflect.set(target, prop, value, receiver);
  }
};

const proxy = new Proxy(target, handler);
console.log(proxy.value);  // Logs "Getting value"
proxy.value = 100;          // Logs "Setting value to 100"

// ============================================
// EDGE CASE 18: Iterator protocol
// ============================================
var iterableES5 = {
  // ES5: custom iterator with next() method
  next: function() {
    if (this.index < this.data.length) {
      return {value: this.data[this.index++], done: false};
    }
    return {value: undefined, done: true};
  },
  index: 0,
  data: [1, 2, 3]
};

// ES6: Symbol.iterator
const iterableES6 = {
  data: [1, 2, 3],
  [Symbol.iterator]: function*() {
    for (const item of this.data) {
      yield item * 2;
    }
  }
};

for (const val of iterableES6) {
  console.log(val);  // 2, 4, 6
}

// ============================================
// EDGE CASE 19: String methods
// ============================================
var strES5 = 'hello';
// ES5 limited methods: charAt, indexOf, substr, substring, slice, etc.

// ES6 adds:
const strES6 = 'hello';
console.log(strES6.startsWith('he'));   // true
console.log(strES6.endsWith('lo'));     // true
console.log(strES6.includes('ell'));    // true
console.log(strES6.repeat(3));          // 'hellohellohello'
console.log(strES6.padStart(10, '*')); // '*****hello'
console.log(strES6.padEnd(10, '-'));   // 'hello-----'
// .trimStart(), .trimEnd() (ES2019)

// ============================================
// EDGE CASE 20: Object methods
// ============================================
var objKeys = {a: 1, b: 2, c: 3};

// ES5:
var keysES5 = Object.keys(objKeys);
var valuesES5 = Object.keys(objKeys).map(function(k) { return objKeys[k]; });
var hasOwnA = objKeys.hasOwnProperty('a');

// ES6:
const keysES6 = Object.keys(objKeys);
const valuesES6 = Object.values(objKeys);
const entriesES6 = Object.entries(objKeys);
const hasOwnAES6 = Object.hasOwn(objKeys, 'a');  // ES2022
// Object.values(), Object.entries() not available in ES5

// Destructuring from entries:
for (const [key, value] of Object.entries(objKeys)) {
  console.log(key, value);
}

// ============================================
// EDGE CASE 21: Number methods
// ============================================
var num = 42;

// ES6:
console.log(Number.isNaN(NaN));           // true (unlike global isNaN)
console.log(Number.isFinite(42));        // true
console.log(Number.isInteger(3.0));      // true
console.log(Number.parseInt('42', 10));  // Same as global parseInt
console.log(Number.parseFloat('3.14'));  // Same as global parseFloat

// Safe integer check:
console.log(Number.MAX_SAFE_INTEGER);  // 9007199254740991
console.log(Number.isSafeInteger(9007199254740991));  // true

// ============================================
// EDGE CASE 22: Global object property access differences
// ============================================
// ES5: global object properties can be shadowed
var undefined = 'hacked';  // Bad but possible in ES5 non-strict

// ES6: undefined is read-only
// undefined = 'hacked';  // TypeError in strict mode, ignored otherwise

// const, let not attached to global object:
var x = 1;   // window.x = 1 (in browser)
let y = 2;   // No window.y
const z = 3; // No window.z

// ============================================
// EDGE CASE 23: RegExp sticky flag
// ============================================
const text = 'a1b2c3';
const regexSticky = /[a-z]/y;  // Sticky: lastIndex matters

regexSticky.lastIndex = 0;
console.log(regexSticky.exec(text));  // ['a', index:0]
regexSticky.lastIndex = 1;
console.log(regexSticky.exec(text));  // null (index 1 is '1', not [a-z])

// ============================================
// EDGE CASE 24: Shared memory and Atomics (advanced)
// ============================================
// ES6 with Web Workers / SharedArrayBuffer
// const sharedBuffer = new SharedArrayBuffer(1024);
// const sharedArray = new Int32Array(sharedBuffer);
// Atomics.add(sharedArray, 0, 1);

// Not typically transformed - requires specific concurrency patterns

export {
  // Just for demonstration - not actually exporting as module
};
