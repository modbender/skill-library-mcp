import { describe, it, expect } from 'vitest';
import {
  mapIbkrSymbol,
  mapIbkrAssetType,
  parseOpenPositions,
  parseCashReport,
  parseTrades,
  parseFlexResponse,
} from '../scripts/ibkr-sync.js';

describe('mapIbkrSymbol', () => {
  it('should pad SEHK symbols to 4 digits with .HK suffix', () => {
    expect(mapIbkrSymbol('700', 'SEHK')).toBe('0700.HK');
    expect(mapIbkrSymbol('9988', 'SEHK')).toBe('9988.HK');
    expect(mapIbkrSymbol('3', 'SEHK')).toBe('0003.HK');
  });

  it('should return symbol unchanged for non-SEHK exchanges', () => {
    expect(mapIbkrSymbol('AAPL', 'NASDAQ')).toBe('AAPL');
    expect(mapIbkrSymbol('MSFT', 'NYSE')).toBe('MSFT');
  });
});

describe('mapIbkrAssetType', () => {
  it('should return HKSTOCK for SEHK', () => {
    expect(mapIbkrAssetType('SEHK')).toBe('HKSTOCK');
  });

  it('should return USSTOCK for other exchanges', () => {
    expect(mapIbkrAssetType('NASDAQ')).toBe('USSTOCK');
    expect(mapIbkrAssetType('NYSE')).toBe('USSTOCK');
    expect(mapIbkrAssetType('ARCA')).toBe('USSTOCK');
  });
});

const SAMPLE_FLEX_XML = `<?xml version="1.0" encoding="UTF-8"?>
<FlexQueryResponse queryName="Test" type="AF">
  <FlexStatements count="1">
    <FlexStatement accountId="U1234567" fromDate="2024-01-01" toDate="2024-06-15">
      <OpenPositions>
        <OpenPosition symbol="AAPL" description="APPLE INC" position="100" costBasisPrice="150.5" markPrice="175.0" listingExchange="NASDAQ" />
        <OpenPosition symbol="AAPL" description="APPLE INC" position="50" costBasisPrice="160.0" markPrice="175.0" listingExchange="NASDAQ" />
        <OpenPosition symbol="700" description="TENCENT" position="200" costBasisPrice="350.0" markPrice="380.0" listingExchange="SEHK" />
      </OpenPositions>
      <CashReport>
        <CashReportCurrency currency="USD" endingCash="5000.50" />
        <CashReportCurrency currency="HKD" endingCash="12000.00" />
        <CashReportCurrency currency="BASE_SUMMARY" endingCash="6500.00" />
        <CashReportCurrency currency="TOTAL" endingCash="6500.00" />
      </CashReport>
      <Trades>
        <Trade symbol="AAPL" description="APPLE INC" dateTime="2024-06-15;153000" quantity="100" tradePrice="170.5" currency="USD" buySell="BUY" listingExchange="NASDAQ" />
        <Trade symbol="700" description="TENCENT" dateTime="2024-06-10;100000" quantity="-50" tradePrice="375.0" currency="HKD" buySell="SELL" listingExchange="SEHK" />
      </Trades>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>`;

describe('parseOpenPositions', () => {
  it('should aggregate LOT-level positions by symbol', () => {
    const positions = parseOpenPositions(SAMPLE_FLEX_XML);

    expect(positions).toHaveLength(2);

    const aapl = positions.find(p => p.symbol === 'AAPL');
    expect(aapl).toBeDefined();
    expect(aapl!.quantity).toBe(150); // 100 + 50
    // Weighted avg: (100*150.5 + 50*160) / 150 = 23050/150 = 153.67
    expect(aapl!.avgPrice).toBeCloseTo(153.67, 1);
    expect(aapl!.currentPrice).toBe(175);
    expect(aapl!.type).toBe('USSTOCK');
    expect(aapl!.currency).toBe('USD');
  });

  it('should map SEHK symbols correctly', () => {
    const positions = parseOpenPositions(SAMPLE_FLEX_XML);
    const tencent = positions.find(p => p.symbol === '0700.HK');

    expect(tencent).toBeDefined();
    expect(tencent!.quantity).toBe(200);
    expect(tencent!.type).toBe('HKSTOCK');
    expect(tencent!.currency).toBe('HKD');
  });

  it('should return empty array for missing data', () => {
    const xml = '<?xml version="1.0"?><FlexQueryResponse><FlexStatements><FlexStatement></FlexStatement></FlexStatements></FlexQueryResponse>';
    expect(parseOpenPositions(xml)).toEqual([]);
  });

  it('should skip zero-quantity positions', () => {
    const xml = `<?xml version="1.0"?>
    <FlexQueryResponse><FlexStatements><FlexStatement>
      <OpenPositions>
        <OpenPosition symbol="AAPL" description="APPLE" position="0" costBasisPrice="150" markPrice="175" listingExchange="NASDAQ" />
      </OpenPositions>
    </FlexStatement></FlexStatements></FlexQueryResponse>`;

    expect(parseOpenPositions(xml)).toEqual([]);
  });
});

describe('parseCashReport', () => {
  it('should parse cash balances and filter summaries', () => {
    const cash = parseCashReport(SAMPLE_FLEX_XML);

    expect(cash).toHaveLength(2);
    expect(cash.find(c => c.currency === 'USD')?.amount).toBe(5000.5);
    expect(cash.find(c => c.currency === 'HKD')?.amount).toBe(12000);
    expect(cash.find(c => c.currency === 'BASE_SUMMARY')).toBeUndefined();
    expect(cash.find(c => c.currency === 'TOTAL')).toBeUndefined();
  });

  it('should filter zero/negative balances', () => {
    const xml = `<?xml version="1.0"?>
    <FlexQueryResponse><FlexStatements><FlexStatement>
      <CashReport>
        <CashReportCurrency currency="USD" endingCash="0" />
        <CashReportCurrency currency="HKD" endingCash="-100" />
      </CashReport>
    </FlexStatement></FlexStatements></FlexQueryResponse>`;

    expect(parseCashReport(xml)).toEqual([]);
  });
});

describe('parseTrades', () => {
  it('should parse trades with correct datetime', () => {
    const trades = parseTrades(SAMPLE_FLEX_XML);

    expect(trades).toHaveLength(2);

    const aaplTrade = trades.find(t => t.symbol === 'AAPL');
    expect(aaplTrade).toBeDefined();
    expect(aaplTrade!.quantity).toBe(100);
    expect(aaplTrade!.tradePrice).toBe(170.5);
    expect(aaplTrade!.buySell).toBe('BUY');
    expect(aaplTrade!.type).toBe('USSTOCK');
    // Verify dateTime parsing: "2024-06-15;153000" -> "2024-06-15T15:30:00"
    expect(aaplTrade!.dateTime).toContain('2024-06-15');
  });

  it('should normalize sell quantity to absolute value', () => {
    const trades = parseTrades(SAMPLE_FLEX_XML);
    const tencentTrade = trades.find(t => t.symbol === '0700.HK');

    expect(tencentTrade).toBeDefined();
    expect(tencentTrade!.quantity).toBe(50); // abs(-50)
    expect(tencentTrade!.buySell).toBe('SELL');
  });
});

describe('parseFlexResponse', () => {
  it('should parse success response', () => {
    const xml = `<FlexStatementResponse>
      <Status>Success</Status>
      <ReferenceCode>12345678</ReferenceCode>
    </FlexStatementResponse>`;

    const result = parseFlexResponse(xml);
    expect(result.status).toBe('Success');
    expect(result.referenceCode).toBe('12345678');
  });

  it('should parse error response', () => {
    const xml = `<FlexStatementResponse>
      <Status>Fail</Status>
      <ErrorCode>1018</ErrorCode>
      <ErrorMessage>Too many requests</ErrorMessage>
    </FlexStatementResponse>`;

    const result = parseFlexResponse(xml);
    expect(result.status).toBe('Fail');
    expect(result.errorCode).toBe('1018');
    expect(result.errorMessage).toBe('Too many requests');
  });

  it('should parse 1019 (statement generating) response', () => {
    const xml = `<FlexStatementResponse>
      <Status>Warn</Status>
      <ErrorCode>1019</ErrorCode>
      <ErrorMessage>Statement is being generated</ErrorMessage>
    </FlexStatementResponse>`;

    const result = parseFlexResponse(xml);
    expect(result.errorCode).toBe('1019');
  });
});
