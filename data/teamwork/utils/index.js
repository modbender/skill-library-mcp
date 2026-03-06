const helpers = require('./helpers');
const logger = require('./logger');
const templateRenderer = require('./template-renderer');
const errors = require('./errors');

module.exports = {
  ...helpers,
  ...logger,
  ...templateRenderer,
  ...errors
};
