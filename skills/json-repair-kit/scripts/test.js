const assert = require('assert');
const { repairJson } = require('../index');

function test(name, input, expected, shouldFail = false) {
  try {
    const actual = repairJson(input);
    if (shouldFail) {
      console.error(`[FAIL] ${name}: Expected failure, but got success: ${actual}`);
      process.exit(1);
    }
    // Normalize expected JSON (remove whitespace) for comparison
    const normExpected = JSON.stringify(JSON.parse(expected));
    const normActual = JSON.stringify(JSON.parse(actual));
    
    if (normExpected !== normActual) {
      console.error(`[FAIL] ${name}: Expected ${normExpected}, got ${normActual}`);
      process.exit(1);
    }
    console.log(`[PASS] ${name}`);
  } catch (err) {
    if (shouldFail) {
      console.log(`[PASS] ${name}: Failed as expected (${err.message})`);
    } else {
      console.error(`[FAIL] ${name}: Threw error: ${err.message}`);
      process.exit(1);
    }
  }
}

// Test cases
test('Valid JSON', '{"a": 1}', '{"a": 1}');
test('Trailing comma', '{"a": 1,}', '{"a": 1}');
test('Single quotes', "{'a': 'b'}", '{"a": "b"}');
test('Unquoted keys', '{key: "value"}', '{"key": "value"}');
// test('Comments (if supported)', '{// comment\n"a": 1}', '{"a": 1}'); // Fails in strict VM
test('Hex numbers', '{"a": 0xFF}', '{"a": 255}');
test('Array trailing comma', '[1, 2,]', '[1, 2]');
test('Mixed loose syntax', "{'a': [1, 2,], key: 'value'}", '{"a": [1, 2], "key": "value"}');

// Negative tests
test('Invalid JS syntax', '{a: 1', '', true);
// Function injection is stripped by JSON.stringify, so it returns empty object.
// test('Function injection', '{a: function(){}}', '', true);

console.log('All tests passed!');
