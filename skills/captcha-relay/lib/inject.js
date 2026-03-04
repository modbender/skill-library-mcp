/**
 * Inject CAPTCHA token back into the automated browser via CDP
 */
const { CdpSession, getCdpWsUrl, getPageTargets } = require('./cdp');

const INJECTION_SCRIPTS = {
  'recaptcha-v2': (token) => `
    (() => {
      // Set the textarea value
      const ta = document.querySelector('#g-recaptcha-response') ||
                 document.querySelector('[name="g-recaptcha-response"]');
      if (ta) {
        ta.value = ${JSON.stringify(token)};
        ta.style.display = 'block'; // make visible temporarily for events
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.style.display = '';
      }

      // Try to call the registered callback
      try {
        // Method 1: data-callback attribute
        const widget = document.querySelector('.g-recaptcha');
        if (widget && widget.dataset.callback) {
          window[widget.dataset.callback](${JSON.stringify(token)});
          return 'callback-attr';
        }
      } catch(e) {}

      try {
        // Method 2: grecaptcha internal
        if (typeof ___grecaptcha_cfg !== 'undefined') {
          const clients = ___grecaptcha_cfg.clients;
          for (const key of Object.keys(clients)) {
            const client = clients[key];
            // Walk the object tree to find callback
            const walk = (obj, depth) => {
              if (depth > 4 || !obj) return;
              for (const k of Object.keys(obj)) {
                if (typeof obj[k] === 'function' && k === 'callback') {
                  obj[k](${JSON.stringify(token)});
                  return true;
                }
                if (typeof obj[k] === 'object') {
                  if (walk(obj[k], depth + 1)) return true;
                }
              }
            };
            walk(client, 0);
          }
          return 'internal-callback';
        }
      } catch(e) {}

      // Method 3: grecaptcha.execute style
      try {
        if (typeof grecaptcha !== 'undefined' && grecaptcha.getResponse) {
          return 'grecaptcha-available';
        }
      } catch(e) {}

      return 'textarea-only';
    })()
  `,

  'hcaptcha': (token) => `
    (() => {
      const ta = document.querySelector('[name="h-captcha-response"]') ||
                 document.querySelector('textarea[name="h-captcha-response"]');
      if (ta) ta.value = ${JSON.stringify(token)};

      // Set iframe response too
      const iframes = document.querySelectorAll('iframe[data-hcaptcha-response]');
      iframes.forEach(f => f.setAttribute('data-hcaptcha-response', ${JSON.stringify(token)}));

      // Call hcaptcha callback
      try {
        const widget = document.querySelector('.h-captcha');
        if (widget && widget.dataset.callback) {
          window[widget.dataset.callback](${JSON.stringify(token)});
          return 'callback';
        }
      } catch(e) {}

      // Try hcaptcha internal
      try {
        if (typeof hcaptcha !== 'undefined') {
          // Trigger via internal event system
          const evt = new CustomEvent('hcaptcha-success', { detail: { token: ${JSON.stringify(token)} } });
          window.dispatchEvent(evt);
          return 'event-dispatched';
        }
      } catch(e) {}

      return 'textarea-only';
    })()
  `,

  'turnstile': (token) => `
    (() => {
      const ta = document.querySelector('[name="cf-turnstile-response"]') ||
                 document.querySelector('input[name="cf-turnstile-response"]');
      if (ta) ta.value = ${JSON.stringify(token)};

      // Try turnstile callback
      try {
        const widget = document.querySelector('.cf-turnstile');
        if (widget && widget.dataset.callback) {
          window[widget.dataset.callback](${JSON.stringify(token)});
          return 'callback';
        }
      } catch(e) {}

      return 'textarea-only';
    })()
  `,
};

async function injectToken({ type, token, cdpPort = 18800 }) {
  // Use page target WS URL (not browser-level) for Runtime.evaluate
  const targets = await getPageTargets(cdpPort);
  const target = targets.find(t => !t.url.startsWith('chrome://')) || targets[0];
  if (!target) throw new Error('No page targets found for injection');
  const wsUrl = target.webSocketDebuggerUrl;
  const session = new CdpSession(wsUrl);
  await session.connect();

  try {
    const scriptFn = INJECTION_SCRIPTS[type];
    if (!scriptFn) throw new Error(`No injection script for type: ${type}`);

    const result = await session.send('Runtime.evaluate', {
      expression: scriptFn(token),
      returnByValue: true,
    });

    return result.result.value;
  } finally {
    session.close();
  }
}

module.exports = { injectToken };
