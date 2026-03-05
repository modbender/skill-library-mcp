const runScript = require('./scripts/run');

exports.main = async () => {
  return runScript.main();
};

if (require.main === module) {
  exports.main();
}