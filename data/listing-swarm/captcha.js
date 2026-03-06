/**
 * Captcha Solver Integration
 * 
 * ⚠️ USER MUST BRING THEIR OWN API KEY
 * 
 * This skill does NOT include a captcha API key.
 * User must sign up at 2captcha.com (or similar) and get their own.
 * 
 * Supports: 2captcha, anti-captcha, capsolver
 */

const SERVICES = {
  '2captcha': {
    submitUrl: 'https://2captcha.com/in.php',
    resultUrl: 'https://2captcha.com/res.php',
  },
  'anti-captcha': {
    submitUrl: 'https://api.anti-captcha.com/createTask',
    resultUrl: 'https://api.anti-captcha.com/getTaskResult',
  },
  'capsolver': {
    submitUrl: 'https://api.capsolver.com/createTask',
    resultUrl: 'https://api.capsolver.com/getTaskResult',
  },
};

class CaptchaSolver {
  constructor(apiKey, service = '2captcha') {
    this.apiKey = apiKey || process.env.CAPTCHA_API_KEY;
    this.service = service || process.env.CAPTCHA_SERVICE || '2captcha';
    
    if (!this.apiKey) {
      throw new Error(
        'CAPTCHA_API_KEY not set.\n\n' +
        'You must get your own API key:\n' +
        '1. Go to https://2captcha.com\n' +
        '2. Create an account\n' +
        '3. Add $3 (covers 1000 captchas)\n' +
        '4. Copy your API key\n' +
        '5. Set: export CAPTCHA_API_KEY="your-key"'
      );
    }
  }

  /**
   * Solve a reCAPTCHA v2
   */
  async solveRecaptchaV2(siteKey, pageUrl) {
    if (this.service === '2captcha') {
      return this.solve2Captcha('userrecaptcha', {
        googlekey: siteKey,
        pageurl: pageUrl,
      });
    }
    // Add other services as needed
    throw new Error(`Service ${this.service} not yet implemented`);
  }

  /**
   * Solve a standard image captcha
   */
  async solveImageCaptcha(base64Image) {
    if (this.service === '2captcha') {
      return this.solve2Captcha('base64', {
        body: base64Image,
      });
    }
    throw new Error(`Service ${this.service} not yet implemented`);
  }

  /**
   * Solve hCaptcha
   */
  async solveHCaptcha(siteKey, pageUrl) {
    if (this.service === '2captcha') {
      return this.solve2Captcha('hcaptcha', {
        sitekey: siteKey,
        pageurl: pageUrl,
      });
    }
    throw new Error(`Service ${this.service} not yet implemented`);
  }

  /**
   * 2Captcha implementation
   */
  async solve2Captcha(method, params) {
    const fetch = (await import('node-fetch')).default;
    
    // Submit captcha
    const submitParams = new URLSearchParams({
      key: this.apiKey,
      method,
      json: 1,
      ...params,
    });
    
    const submitRes = await fetch(`https://2captcha.com/in.php?${submitParams}`);
    const submitData = await submitRes.json();
    
    if (submitData.status !== 1) {
      throw new Error(`2Captcha submit failed: ${submitData.request}`);
    }
    
    const captchaId = submitData.request;
    
    // Poll for result
    for (let i = 0; i < 60; i++) {
      await new Promise(r => setTimeout(r, 5000)); // Wait 5 seconds
      
      const resultParams = new URLSearchParams({
        key: this.apiKey,
        action: 'get',
        id: captchaId,
        json: 1,
      });
      
      const resultRes = await fetch(`https://2captcha.com/res.php?${resultParams}`);
      const resultData = await resultRes.json();
      
      if (resultData.status === 1) {
        return resultData.request; // The solved captcha
      }
      
      if (resultData.request !== 'CAPCHA_NOT_READY') {
        throw new Error(`2Captcha failed: ${resultData.request}`);
      }
    }
    
    throw new Error('2Captcha timeout after 5 minutes');
  }

  /**
   * Report bad captcha (get refund)
   */
  async reportBad(captchaId) {
    if (this.service === '2captcha') {
      const fetch = (await import('node-fetch')).default;
      const params = new URLSearchParams({
        key: this.apiKey,
        action: 'reportbad',
        id: captchaId,
      });
      await fetch(`https://2captcha.com/res.php?${params}`);
    }
  }
}

module.exports = { CaptchaSolver };
