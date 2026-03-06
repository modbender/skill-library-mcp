const axios = require('axios');
const fs = require('fs');
const path = require('path');
const os = require('os');

function loadToken() {
  // 1. 优先读取环境变量
  if (process.env.IAMMETER_TOKEN) return process.env.IAMMETER_TOKEN;

  // 2. 从 ~/.openclaw/openclaw.json 读取（OpenClaw Skills UI 写入的位置）
  try {
    const cfgPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
    const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
    const apiKey = cfg?.skills?.entries?.iammeter?.apiKey;
    if (apiKey) return apiKey;
  } catch (_) { /* 文件不存在或格式错误时忽略 */ }

  return null;
}

function sleep(ms){ return new Promise(res=>setTimeout(res, ms)); }

class IAMMeter {
  constructor({ token=null, base='https://www.iammeter.com', maxRetries=5 } = {}){
    this.token = token || loadToken();
    if (!this.token) throw new Error('IAMMETER token not found. Set it in the OpenClaw Skills UI or export IAMMETER_TOKEN.');
    this.base = base.replace(/\/+$/,'');
    this.client = axios.create({ baseURL: this.base, timeout: 20000 });
    this.maxRetries = maxRetries;
  }

  async _get(pathname, params={}, headers={}){
    const opts = { params, headers: Object.assign({}, headers, { token: this.token }) };
    let attempt = 0;
    while (true) {
      try {
        const resp = await this.client.get(pathname, opts);
        return resp.data;
      } catch (err) {
        attempt++;
        const status = err && err.response && err.response.status;
        // Handle auth error immediately
        if (status === 401) {
          throw new Error('Authentication failed (401). Please check your IAMMETER_TOKEN.');
        }
        // Rate limited -> exponential backoff
        if (status === 429) {
          if (attempt > this.maxRetries) throw new Error('Rate limited: exceeded retry attempts');
          const wait = Math.min(60000, 500 * Math.pow(2, attempt));
          await sleep(wait);
          continue;
        }
        // Network or 5xx errors: retry a few times
        if ((!status || status >= 500) && attempt <= this.maxRetries) {
          const wait = 200 * Math.pow(2, attempt);
          await sleep(wait);
          continue;
        }
        // Other errors
        throw err;
      }
    }
  }

  // Get list of places/sites for the user
  async sitelist(){
    return this._get('/api/v1/user/sitelist');
  }

  // Get latest data from all meters
  async metersData(){
    return this._get('/api/v1/site/metersdata');
  }

  // Get the latest uploading data for a single meter
  async meterData(sn){
    return this._get(`/api/v1/site/meterdata/${encodeURIComponent(sn)}`);
  }

  // Alternative endpoint meterdata2
  async meterData2(sn){
    return this._get(`/api/v1/site/meterdata2/${encodeURIComponent(sn)}`);
  }

  // Energy history for a place
  async energyHistory(placeId, startTime, endTime, groupby='hour'){
    return this._get(`/api/v1/site/energyhistory/${placeId}`, { startTime, endTime, groupby });
  }

  // Power analysis
  async powerAnalysis(sn, startTime, endTime){
    return this._get('/api/v1/site/poweranalysis', { sn, startTime, endTime });
  }

  // Offline analysis
  async offlineAnalysis(sn, startTime, endTime, interval=5){
    return this._get('/api/v1/site/offlineanalysis', { sn, startTime, endTime, interval });
  }
}

module.exports = { IAMMeter };
