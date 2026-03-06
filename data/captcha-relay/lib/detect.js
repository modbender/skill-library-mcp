/**
 * CAPTCHA detection and sitekey extraction via CDP
 */
const { cdpSend, getCdpWsUrl, getPageTargets } = require('./cdp');

const DETECTION_SCRIPT = `
(() => {
  const result = { type: null, sitekey: null, pageUrl: location.href };

  // reCAPTCHA v2
  const rc = document.querySelector('.g-recaptcha[data-sitekey]');
  if (rc) {
    result.type = 'recaptcha-v2';
    result.sitekey = rc.dataset.sitekey;
    return result;
  }

  // reCAPTCHA via iframe
  const rcIframe = document.querySelector('iframe[src*="recaptcha/api2/anchor"]');
  if (rcIframe) {
    const m = rcIframe.src.match(/[?&]k=([^&]+)/);
    if (m) {
      result.type = 'recaptcha-v2';
      result.sitekey = m[1];
      return result;
    }
  }

  // hCaptcha
  const hc = document.querySelector('.h-captcha[data-sitekey]');
  if (hc) {
    result.type = 'hcaptcha';
    result.sitekey = hc.dataset.sitekey;
    return result;
  }

  // hCaptcha via iframe
  const hcIframe = document.querySelector('iframe[src*="hcaptcha.com"]');
  if (hcIframe) {
    const m = hcIframe.src.match(/sitekey=([^&]+)/);
    if (m) {
      result.type = 'hcaptcha';
      result.sitekey = m[1];
      return result;
    }
  }

  // Turnstile
  const ts = document.querySelector('.cf-turnstile[data-sitekey]');
  if (ts) {
    result.type = 'turnstile';
    result.sitekey = ts.dataset.sitekey;
    return result;
  }

  // Turnstile via iframe
  const tsIframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
  if (tsIframe) {
    const m = tsIframe.src.match(/[?&]k=([^&]+)/);
    if (m) {
      result.type = 'turnstile';
      result.sitekey = m[1];
      return result;
    }
  }

  // Generic data-sitekey
  const generic = document.querySelector('[data-sitekey]');
  if (generic) {
    result.sitekey = generic.dataset.sitekey;
    // Try to guess type from scripts loaded
    if (document.querySelector('script[src*="recaptcha"]')) result.type = 'recaptcha-v2';
    else if (document.querySelector('script[src*="hcaptcha"]')) result.type = 'hcaptcha';
    else if (document.querySelector('script[src*="turnstile"]')) result.type = 'turnstile';
    else result.type = 'unknown';
    return result;
  }

  return result;
})()
`;

async function detectCaptcha(cdpPort = 18800, targetId) {
  const targets = await getPageTargets(cdpPort);
  let target;
  if (targetId) {
    target = targets.find(t => t.id === targetId);
  }
  if (!target) {
    // Pick the first non-newtab page
    target = targets.find(t => !t.url.startsWith('chrome://')) || targets[0];
  }
  if (!target) throw new Error('No page targets found');

  const wsUrl = target.webSocketDebuggerUrl;
  const result = await cdpSend(wsUrl, 'Runtime.evaluate', {
    expression: DETECTION_SCRIPT,
    returnByValue: true,
  });
  return result.result.value;
}

module.exports = { detectCaptcha };
