class RouterError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = this.constructor.name;
    this.code = options.code || 'ROUTER_ERROR';
    this.details = options.details;
    this.retryable = Boolean(options.retryable);
  }
}

class InvalidPrefixError extends RouterError {
  constructor(prefix) {
    super(`Unsupported prefix: ${prefix}`, {
      code: 'INVALID_PREFIX',
      details: { prefix },
      retryable: false,
    });
  }
}

class ProviderUnavailableError extends RouterError {
  constructor(model, details) {
    super(`Provider unavailable for model: ${model}`, {
      code: 'PROVIDER_UNAVAILABLE',
      details,
      retryable: true,
    });
  }
}

class VerificationError extends RouterError {
  constructor(expected, actual) {
    super(`Model verification failed. expected=${expected} actual=${actual}`, {
      code: 'VERIFICATION_FAILED',
      details: { expected, actual },
      retryable: true,
    });
  }
}

module.exports = {
  RouterError,
  InvalidPrefixError,
  ProviderUnavailableError,
  VerificationError,
};
