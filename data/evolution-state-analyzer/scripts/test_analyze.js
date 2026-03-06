const analyzer = require('../index');

analyzer.analyzeState()
  .then(report => {
    console.log(JSON.stringify(report, null, 2));
    if (report.error) {
      console.error(report.error);
      process.exit(1);
    }
  })
  .catch(err => {
    console.error(err);
    process.exit(1);
  });
