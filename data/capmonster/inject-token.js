// CAPTCHA Token Injection Script
// Replace TOKEN_HERE with the actual token from CapMonster
//
// Usage: Update TOKEN_HERE and paste into browser console
// Or use via browser action=act evaluate

((token) => {
  const TOKEN = token || 'TOKEN_HERE';
  const results = [];

  // === reCAPTCHA v2/v3 ===
  
  // Method 1: Set g-recaptcha-response textarea
  const gTextarea = document.querySelector('#g-recaptcha-response, [name="g-recaptcha-response"], textarea.g-recaptcha-response');
  if (gTextarea) {
    gTextarea.value = TOKEN;
    gTextarea.innerHTML = TOKEN;
    // Make it visible temporarily (some sites check this)
    const origDisplay = gTextarea.style.display;
    gTextarea.style.display = 'block';
    setTimeout(() => { gTextarea.style.display = origDisplay; }, 100);
    results.push('✓ Set g-recaptcha-response textarea');
  }

  // Method 2: Handle multiple recaptcha textareas (some pages have multiple)
  document.querySelectorAll('textarea[name="g-recaptcha-response"]').forEach((ta, i) => {
    if (ta !== gTextarea) {
      ta.value = TOKEN;
      results.push(`✓ Set additional g-recaptcha-response #${i+1}`);
    }
  });

  // Method 3: Try to call grecaptcha callback
  if (typeof ___grecaptcha_cfg !== 'undefined' && ___grecaptcha_cfg.clients) {
    for (const clientId in ___grecaptcha_cfg.clients) {
      const client = ___grecaptcha_cfg.clients[clientId];
      
      // Navigate through possible callback locations
      const possibleCallbacks = [
        client?.Y?.Y?.callback,
        client?.Y?.callback,
        client?.callback,
        client?.hl?.l?.callback,
        client?.Qc?.callback
      ];
      
      for (const cb of possibleCallbacks) {
        if (typeof cb === 'function') {
          try {
            cb(TOKEN);
            results.push(`✓ Called grecaptcha callback for client ${clientId}`);
            break;
          } catch (e) {
            results.push(`⚠ Callback error: ${e.message}`);
          }
        }
      }
    }
  }

  // Method 4: Check for data-callback attribute and call it
  const recaptchaDiv = document.querySelector('.g-recaptcha[data-callback], [data-callback]');
  if (recaptchaDiv) {
    const callbackName = recaptchaDiv.dataset.callback;
    if (callbackName && typeof window[callbackName] === 'function') {
      try {
        window[callbackName](TOKEN);
        results.push(`✓ Called window.${callbackName}()`);
      } catch (e) {
        results.push(`⚠ ${callbackName} error: ${e.message}`);
      }
    }
  }

  // === hCaptcha ===
  
  const hTextarea = document.querySelector('[name="h-captcha-response"], textarea.h-captcha-response');
  if (hTextarea) {
    hTextarea.value = TOKEN;
    results.push('✓ Set h-captcha-response textarea');
  }

  const hcaptchaDiv = document.querySelector('.h-captcha[data-callback]');
  if (hcaptchaDiv) {
    const callbackName = hcaptchaDiv.dataset.callback;
    if (callbackName && typeof window[callbackName] === 'function') {
      try {
        window[callbackName](TOKEN);
        results.push(`✓ Called hCaptcha callback: ${callbackName}`);
      } catch (e) {
        results.push(`⚠ hCaptcha callback error: ${e.message}`);
      }
    }
  }

  // === Cloudflare Turnstile ===
  
  const cfInput = document.querySelector('[name="cf-turnstile-response"], input.cf-turnstile-response');
  if (cfInput) {
    cfInput.value = TOKEN;
    results.push('✓ Set cf-turnstile-response input');
  }

  const turnstileDiv = document.querySelector('.cf-turnstile[data-callback]');
  if (turnstileDiv) {
    const callbackName = turnstileDiv.dataset.callback;
    if (callbackName && typeof window[callbackName] === 'function') {
      try {
        window[callbackName](TOKEN);
        results.push(`✓ Called Turnstile callback: ${callbackName}`);
      } catch (e) {
        results.push(`⚠ Turnstile callback error: ${e.message}`);
      }
    }
  }

  // Summary
  if (results.length === 0) {
    return 'No CAPTCHA elements found to inject token into';
  }

  return results.join('\n');
})();
