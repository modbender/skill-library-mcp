import {
  createSpreadsheet,
  getSpreadsheet,
  getSheetValues,
  updateSheetValues,
  appendSheetValues,
  prependSheetValues,
  listRecords,
  getRecord,
  createRecord,
  batchCreateRecords,
  updateRecord,
  batchUpdateRecords,
  deleteRecord,
  batchDeleteRecords,
  copyBitable,
} from '../dist/index.js';
import { applyFeishuDefaults, createStats, logSuiteStart, logSuiteEnd, runCase } from './_utils.mjs';

applyFeishuDefaults();

if (!process.env.TEST_SHEET_RANGE) process.env.TEST_SHEET_RANGE = 'A1:B2';
if (!process.env.TEST_SHEET_VALUES_JSON) {
  process.env.TEST_SHEET_VALUES_JSON = JSON.stringify([
    ['Name', 'Value'],
    ['OpenClaw', 1],
  ]);
}

const stats = createStats();
logSuiteStart('feishu/data (表格/多维表格)');

const getSheetToken = () => process.env.TEST_SHEET_TOKEN;
const getSheetId = () => process.env.TEST_SHEET_ID;
const sheetRange = process.env.TEST_SHEET_RANGE;
const sheetValuesJson = process.env.TEST_SHEET_VALUES_JSON;

const bitableAppToken = process.env.TEST_BITABLE_APP_TOKEN;
const bitableTableId = process.env.TEST_BITABLE_TABLE_ID;
const bitableRecordId = process.env.TEST_BITABLE_RECORD_ID;
const bitableRecordIds = (process.env.TEST_BITABLE_RECORD_IDS || '').split(',').map(s => s.trim()).filter(Boolean);

function extractSpreadsheetToken(response) {
  return (
    response?.data?.spreadsheet?.spreadsheet_token ||
    response?.data?.spreadsheet_token ||
    response?.spreadsheet_token ||
    response?.data?.spreadsheet?.token
  );
}

function extractSheetId(response) {
  return (
    response?.data?.sheets?.[0]?.sheet_id ||
    response?.data?.sheet_list?.[0]?.sheet_id ||
    response?.data?.sheets?.[0]?.id ||
    response?.data?.sheet_list?.[0]?.id
  );
}

await runCase(stats, {
  name: 'createSpreadsheet',
  sideEffect: true,
  fn: async () => {
    const res = await createSpreadsheet(process.env.TEST_SHEET_TITLE || 'OpenClaw Test Sheet', process.env.TEST_SHEET_FOLDER_TOKEN);
    const token = extractSpreadsheetToken(res);
    if (token && !process.env.TEST_SHEET_TOKEN) process.env.TEST_SHEET_TOKEN = token;
    return res;
  },
});

await runCase(stats, {
  name: 'getSpreadsheet',
  requires: ['TEST_SHEET_TOKEN'],
  fn: async () => {
    const res = await getSpreadsheet(getSheetToken());
    const id = extractSheetId(res);
    if (id && !process.env.TEST_SHEET_ID) process.env.TEST_SHEET_ID = id;
    return res;
  },
});

await runCase(stats, {
  name: 'getSheetValues',
  requires: ['TEST_SHEET_TOKEN', 'TEST_SHEET_ID', 'TEST_SHEET_RANGE'],
  fn: () => getSheetValues(getSheetToken(), getSheetId(), sheetRange),
});

await runCase(stats, {
  name: 'updateSheetValues',
  requires: ['TEST_SHEET_TOKEN', 'TEST_SHEET_ID', 'TEST_SHEET_RANGE', 'TEST_SHEET_VALUES_JSON'],
  sideEffect: true,
  fn: () => updateSheetValues(getSheetToken(), getSheetId(), sheetRange, JSON.parse(sheetValuesJson)),
});

await runCase(stats, {
  name: 'appendSheetValues',
  requires: ['TEST_SHEET_TOKEN', 'TEST_SHEET_ID', 'TEST_SHEET_RANGE', 'TEST_SHEET_VALUES_JSON'],
  sideEffect: true,
  fn: () => appendSheetValues(getSheetToken(), getSheetId(), sheetRange, JSON.parse(sheetValuesJson)),
});

await runCase(stats, {
  name: 'prependSheetValues',
  requires: ['TEST_SHEET_TOKEN', 'TEST_SHEET_ID', 'TEST_SHEET_RANGE', 'TEST_SHEET_VALUES_JSON'],
  sideEffect: true,
  fn: () => prependSheetValues(getSheetToken(), getSheetId(), sheetRange, JSON.parse(sheetValuesJson)),
});

await runCase(stats, {
  name: 'listRecords',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID'],
  fn: () => listRecords(bitableAppToken, bitableTableId),
});

await runCase(stats, {
  name: 'getRecord',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID', 'TEST_BITABLE_RECORD_ID'],
  fn: () => getRecord(bitableAppToken, bitableTableId, bitableRecordId),
});

await runCase(stats, {
  name: 'createRecord',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID', 'TEST_BITABLE_FIELDS_JSON'],
  sideEffect: true,
  fn: () => createRecord(bitableAppToken, bitableTableId, JSON.parse(process.env.TEST_BITABLE_FIELDS_JSON)),
});

await runCase(stats, {
  name: 'batchCreateRecords',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID', 'TEST_BITABLE_RECORDS_JSON'],
  sideEffect: true,
  fn: () => batchCreateRecords(bitableAppToken, bitableTableId, JSON.parse(process.env.TEST_BITABLE_RECORDS_JSON)),
});

await runCase(stats, {
  name: 'updateRecord',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID', 'TEST_BITABLE_RECORD_ID', 'TEST_BITABLE_FIELDS_JSON'],
  sideEffect: true,
  fn: () => updateRecord(bitableAppToken, bitableTableId, bitableRecordId, JSON.parse(process.env.TEST_BITABLE_FIELDS_JSON)),
});

await runCase(stats, {
  name: 'batchUpdateRecords',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID', 'TEST_BITABLE_RECORDS_JSON'],
  sideEffect: true,
  fn: () => batchUpdateRecords(bitableAppToken, bitableTableId, JSON.parse(process.env.TEST_BITABLE_RECORDS_JSON)),
});

await runCase(stats, {
  name: 'deleteRecord',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID', 'TEST_BITABLE_RECORD_ID'],
  destructive: true,
  fn: () => deleteRecord(bitableAppToken, bitableTableId, bitableRecordId),
});

await runCase(stats, {
  name: 'batchDeleteRecords',
  requires: ['TEST_BITABLE_APP_TOKEN', 'TEST_BITABLE_TABLE_ID', 'TEST_BITABLE_RECORD_IDS'],
  destructive: true,
  fn: () => batchDeleteRecords(bitableAppToken, bitableTableId, bitableRecordIds),
});

await runCase(stats, {
  name: 'copyBitable',
  requires: ['TEST_BITABLE_APP_TOKEN'],
  sideEffect: true,
  fn: () => copyBitable(bitableAppToken, process.env.TEST_BITABLE_COPY_NAME || 'OpenClaw Bitable Copy', process.env.TEST_BITABLE_FOLDER_TOKEN),
});

logSuiteEnd('feishu/data', stats);
