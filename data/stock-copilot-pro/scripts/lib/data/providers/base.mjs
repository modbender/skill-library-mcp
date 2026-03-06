export class DataProvider {
  constructor(name, markets = []) {
    this.name = name;
    this.markets = markets;
  }

  supportsMarket(market) {
    return this.markets.includes(market);
  }

  get capabilities() {
    throw new Error("Not implemented");
  }

  async fetch(_capability, _symbol, _context = {}) {
    throw new Error("Not implemented");
  }

  parse(_capability, _rawResponse) {
    throw new Error("Not implemented");
  }
}
