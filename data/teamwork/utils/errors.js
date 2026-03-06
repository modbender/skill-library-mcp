class ValidationError extends Error {
  constructor(message, field = null) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

class ConfigurationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ConfigurationError';
  }
}

class ModelNotFoundError extends Error {
  constructor(modelName, provider = null) {
    super(`Model ${modelName} not found${provider ? ` in provider ${provider}` : ''}`);
    this.name = 'ModelNotFoundError';
    this.modelName = modelName;
    this.provider = provider;
  }
}

class ProviderNotFoundError extends Error {
  constructor(providerName) {
    super(`Provider ${providerName} not found`);
    this.name = 'ProviderNotFoundError';
    this.providerName = providerName;
  }
}

class TaskExecutionError extends Error {
  constructor(message, taskId = null, phase = null) {
    super(message);
    this.name = 'TaskExecutionError';
    this.taskId = taskId;
    this.phase = phase;
  }
}

class TimeoutError extends Error {
  constructor(message, timeout = null) {
    super(message);
    this.name = 'TimeoutError';
    this.timeout = timeout;
  }
}

class BudgetExceededError extends Error {
  constructor(currentSpent, budget) {
    super(`Budget exceeded: $${currentSpent.toFixed(2)} spent of $${budget.toFixed(2)} budget`);
    this.name = 'BudgetExceededError';
    this.currentSpent = currentSpent;
    this.budget = budget;
  }
}

class QuotaExceededError extends Error {
  constructor(model, quotaType, current, limit) {
    super(`Quota exceeded for ${model}: ${quotaType} quota ${current}/${limit}`);
    this.name = 'QuotaExceededError';
    this.model = model;
    this.quotaType = quotaType;
    this.current = current;
    this.limit = limit;
  }
}

class HeraldError extends Error {
  constructor(message, heraldModel = null) {
    super(message);
    this.name = 'HeraldError';
    this.heraldModel = heraldModel;
  }
}

function handleError(error, logger = null) {
  if (logger) {
    logger.error(error.message, {
      name: error.name,
      stack: error.stack,
      ...error
    });
  }
  
  return {
    success: false,
    error: {
      name: error.name,
      message: error.message,
      ...error
    }
  };
}

function isRecoverable(error) {
  const recoverableErrors = [
    'TimeoutError',
    'QuotaExceededError',
    'HeraldError'
  ];
  
  return recoverableErrors.includes(error.name);
}

module.exports = {
  ValidationError,
  ConfigurationError,
  ModelNotFoundError,
  ProviderNotFoundError,
  TaskExecutionError,
  TimeoutError,
  BudgetExceededError,
  QuotaExceededError,
  HeraldError,
  handleError,
  isRecoverable
};
