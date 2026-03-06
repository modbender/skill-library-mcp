// CAPTCHA Detection Script
// Copy-paste into browser console or use via browser action=act evaluate
//
// Usage in browser automation:
// browser action=act profile=chrome request={"kind":"evaluate","fn":"<paste this script>"}

(() => {
  const result = {
    hasCaptcha: false,
    type: null,
    sitekey: null,
    details: {}
  };

  // reCAPTCHA v2 detection
  const recaptchaV2 = document.querySelector('.g-recaptcha, [data-sitekey], iframe[src*="recaptcha/api2"], iframe[src*="recaptcha/enterprise"]');
  if (recaptchaV2) {
    result.hasCaptcha = true;
    result.type = 'recaptcha_v2';
    
    // Try multiple methods to get sitekey
    result.sitekey = 
      recaptchaV2.dataset?.sitekey ||
      document.querySelector('[data-sitekey]')?.dataset?.sitekey ||
      (document.querySelector('iframe[src*="recaptcha"]')?.src.match(/k=([^&]+)/)?.[1]) ||
      (typeof ___grecaptcha_cfg !== 'undefined' && Object.values(___grecaptcha_cfg.clients || {})[0]?.Y?.Y?.sitekey);
    
    result.details.isInvisible = !!document.querySelector('.g-recaptcha[data-size="invisible"]');
  }

  // reCAPTCHA v3 detection
  const recaptchaV3Script = document.querySelector('script[src*="recaptcha/api.js?render="]');
  if (recaptchaV3Script && !result.hasCaptcha) {
    result.hasCaptcha = true;
    result.type = 'recaptcha_v3';
    result.sitekey = recaptchaV3Script.src.match(/render=([^&]+)/)?.[1];
    result.details.note = 'v3 is invisible, auto-executes on page load';
  }

  // hCaptcha detection
  const hcaptcha = document.querySelector('.h-captcha, [data-hcaptcha-sitekey], iframe[src*="hcaptcha.com"]');
  if (hcaptcha && !result.hasCaptcha) {
    result.hasCaptcha = true;
    result.type = 'hcaptcha';
    result.sitekey = 
      hcaptcha.dataset?.sitekey ||
      hcaptcha.dataset?.hcaptchaSitekey ||
      document.querySelector('[data-hcaptcha-sitekey]')?.getAttribute('data-hcaptcha-sitekey') ||
      document.querySelector('[data-sitekey]')?.dataset?.sitekey;
  }

  // Cloudflare Turnstile detection
  const turnstile = document.querySelector('.cf-turnstile, [data-turnstile-sitekey], iframe[src*="challenges.cloudflare.com/turnstile"]');
  if (turnstile && !result.hasCaptcha) {
    result.hasCaptcha = true;
    result.type = 'turnstile';
    result.sitekey = 
      turnstile.dataset?.sitekey ||
      turnstile.dataset?.turnstileSitekey ||
      document.querySelector('.cf-turnstile[data-sitekey]')?.dataset?.sitekey;
  }

  // Check for CAPTCHA challenge page (like Google's "unusual traffic")
  const bodyText = document.body.innerText.toLowerCase();
  if (bodyText.includes('unusual traffic') || 
      bodyText.includes('captcha') ||
      bodyText.includes('我們的系統偵測到您的電腦網路') ||
      bodyText.includes('verify you are a human')) {
    result.details.isChallengePageLikely = true;
    if (!result.hasCaptcha) {
      // There might be a CAPTCHA we didn't detect
      result.hasCaptcha = true;
      result.type = 'unknown';
      result.details.bodyHint = 'Page mentions CAPTCHA/verification';
    }
  }

  // Add page info
  result.pageUrl = window.location.href;

  return JSON.stringify(result, null, 2);
})();
