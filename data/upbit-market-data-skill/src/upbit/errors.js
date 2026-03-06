class UpbitError extends Error {
  constructor(message, extra = {}) {
    super(message);
    this.name = "UpbitError";
    this.extra = extra;
  }

  toJSON() {
    return { name: this.name, message: this.message, ...this.extra };
  }

  static from(err) {
    if (err instanceof UpbitError) return err;
    return new UpbitError(err?.message || "Unknown error", { raw: String(err) });
  }
}

module.exports = { UpbitError };

