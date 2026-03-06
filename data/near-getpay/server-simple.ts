import express from 'express';
import { PingPayClient } from './scripts/pingpay-client';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.join(__dirname, '.env') });

const app = express();
const PORT = process.env.PORT || 3000;

// Configuration
const config = {
  recipient: process.env.RECIPIENT_ADDRESS || 'meteorkent.near',
  provider: process.env.PAYMENT_PROVIDER || 'none',
  
  pingpay: {
    apiKey: process.env.PINGPAY_API_KEY || '',
    configured: false
  },
  
  hotpay: {
    near_item_id: process.env.HOTPAY_NEAR_ITEM_ID || '',
    usdc_item_id: process.env.HOTPAY_USDC_ITEM_ID || '',
    usdt_item_id: process.env.HOTPAY_USDT_ITEM_ID || '',
    configured: false
  },
  
  tokens: [
    {
      symbol: 'NEAR',
      chain: 'NEAR',
      decimals: 24,
      presets: [0.5, 1, 5, 10]
    },
    {
      symbol: 'USDC',
      chain: 'NEAR',
      decimals: 6,
      presets: [5, 10, 25, 50]
    },
    {
      symbol: 'USDT',
      chain: 'NEAR',
      decimals: 6,
      presets: [5, 10, 25, 50]
    }
  ]
};

// Check what's configured
config.pingpay.configured = !!config.pingpay.apiKey;
config.hotpay.configured = !!(config.hotpay.near_item_id || config.hotpay.usdc_item_id || config.hotpay.usdt_item_id);

// Auto-select provider if only one is configured
if (config.provider === 'none') {
  if (config.pingpay.configured && !config.hotpay.configured) {
    config.provider = 'pingpay';
  } else if (config.hotpay.configured && !config.pingpay.configured) {
    config.provider = 'hotpay';
  }
}

const client = config.pingpay.configured ? new PingPayClient(config.pingpay.apiKey) : null;

app.use(express.json());

// Setup wizard page
app.get('/setup', (req, res) => {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GetPay Setup</title>
  <style>
    :root {
      --bg-body: #0b0c0e;
      --bg-card: rgba(255, 255, 255, 0.05);
      --border-color: rgba(71, 235, 165, 0.2);
      --accent-primary: #5feda9;
      --accent-gradient: linear-gradient(135deg, #a3f9d8 0%, #47eba5 100%);
      --accent-glow: 0 0 20px rgba(71, 235, 165, 0.3);
      --text-main: #ffffff;
      --text-secondary: #a0a0a0;
      --text-on-accent: #000000;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg-body);
      min-height: 100vh;
      padding: 20px;
    }

    .container {
      max-width: 800px;
      margin: 40px auto;
      background: var(--bg-card);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 40px;
      box-shadow: var(--accent-glow);
    }

    h1 {
      color: var(--text-main);
      margin-bottom: 8px;
      font-size: 32px;
    }

    .subtitle {
      color: var(--text-secondary);
      margin-bottom: 32px;
      font-size: 16px;
    }

    .status {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 24px;
      font-weight: 600;
      border: 1px solid var(--border-color);
      backdrop-filter: blur(10px);
    }

    .status.success {
      background: rgba(71, 235, 165, 0.1);
      color: var(--accent-primary);
    }

    .status.warning {
      background: rgba(255, 171, 0, 0.1);
      color: #ffab00;
      border-color: rgba(255, 171, 0, 0.2);
    }

    .provider-section {
      border: 2px solid var(--border-color);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      background: var(--bg-card);
      backdrop-filter: blur(10px);
    }

    .provider-section.configured {
      border-color: var(--accent-primary);
      background: rgba(71, 235, 165, 0.05);
    }

    .provider-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .provider-title {
      font-size: 20px;
      font-weight: 700;
      color: var(--text-main);
    }

    .badge {
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }

    .badge.ready {
      background: var(--accent-gradient);
      color: var(--text-on-accent);
    }

    .badge.pending {
      background: rgba(255, 171, 0, 0.2);
      color: #ffab00;
      border: 1px solid rgba(255, 171, 0, 0.3);
    }

    .steps {
      margin-top: 16px;
    }

    .step {
      margin-bottom: 12px;
      padding-left: 24px;
      color: var(--text-secondary);
      line-height: 1.6;
    }

    .step strong {
      color: var(--text-main);
    }

    .code {
      background: rgba(0, 0, 0, 0.3);
      padding: 12px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      font-family: 'Courier New', monospace;
      font-size: 13px;
      margin: 8px 0;
      overflow-x: auto;
      color: var(--accent-primary);
    }

    .link {
      color: var(--accent-primary);
      text-decoration: none;
      font-weight: 600;
    }

    .link:hover {
      text-decoration: underline;
      filter: brightness(1.2);
    }

    .continue-button {
      width: 100%;
      background: var(--accent-gradient);
      color: var(--text-on-accent);
      border: none;
      padding: 18px;
      border-radius: 8px;
      font-size: 18px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 24px;
      box-shadow: var(--accent-glow);
    }

    .continue-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(71, 235, 165, 0.5);
    }

    .continue-button:disabled {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-secondary);
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    .footer {
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid var(--border-color);
      color: var(--text-secondary);
      font-size: 13px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 GetPay Setup</h1>
    <div class="subtitle">Configure your payment providers to start accepting crypto</div>

    ${!config.pingpay.configured && !config.hotpay.configured ? `
    <div class="status warning">
      <span>⚠️</span>
      <span>No payment provider configured yet. Choose one below to get started.</span>
    </div>
    ` : `
    <div class="status success">
      <span>✅</span>
      <span>Payment provider ready! You can start accepting payments.</span>
    </div>
    `}

    <!-- PingPay Section -->
    <div class="provider-section ${config.pingpay.configured ? 'configured' : ''}">
      <div class="provider-header">
        <div class="provider-title">💳 PingPay</div>
        <div class="badge ${config.pingpay.configured ? 'ready' : 'pending'}">
          ${config.pingpay.configured ? 'READY' : 'NOT CONFIGURED'}
        </div>
      </div>

      ${config.pingpay.configured ? `
        <div style="color: #5feda9; font-weight: 600; margin-bottom: 8px;">
          ✓ API Key configured
        </div>
        <div style="color: #a0a0a0; font-size: 13px;">
          ⚠️ Recipient address is configured in your <a href="https://pingpay.io/dashboard" target="_blank" class="link">PingPay Dashboard</a> account settings
        </div>
      ` : `
        <div style="color: #a0a0a0; margin-bottom: 12px;">
          Best for: Checkout sessions, invoice management, traditional payment flow
        </div>

        <div class="steps">
          <div class="step">
            <strong>1.</strong> Sign up at <a href="https://pingpay.io" target="_blank" class="link">pingpay.io</a>
          </div>
          <div class="step">
            <strong>2.</strong> Set your NEAR wallet address in Dashboard → Settings
          </div>
          <div class="step">
            <strong>3.</strong> Go to Dashboard → Settings → API Keys
          </div>
          <div class="step">
            <strong>4.</strong> Create new API key and copy it
          </div>
          <div class="step">
            <strong>5.</strong> Add to your <code>.env</code> file:
            <div class="code">PINGPAY_API_KEY=your_api_key_here<br>PAYMENT_PROVIDER=pingpay<br>RECIPIENT_ADDRESS=your-account.near</div>
          </div>
          <div class="step">
            <strong>6.</strong> Restart the server
          </div>
        </div>
      `}
    </div>

    <!-- HOT PAY Section -->
    <div class="provider-section ${config.hotpay.configured ? 'configured' : ''}">
      <div class="provider-header">
        <div class="provider-title">🔥 HOT PAY</div>
        <div class="badge ${config.hotpay.configured ? 'ready' : 'pending'}">
          ${config.hotpay.configured ? 'READY' : 'NOT CONFIGURED'}
        </div>
      </div>

      ${config.hotpay.configured ? `
        <div style="color: #5feda9; font-weight: 600; margin-bottom: 8px;">
          ✓ Payment links configured:
        </div>
        <div style="margin-left: 20px; color: #a0a0a0; margin-bottom: 8px;">
          ${config.hotpay.near_item_id ? '✓ NEAR' : '○ NEAR'}<br>
          ${config.hotpay.usdc_item_id ? '✓ USDC' : '○ USDC'}<br>
          ${config.hotpay.usdt_item_id ? '✓ USDT' : '○ USDT'}
        </div>
        <div style="color: #a0a0a0; font-size: 13px;">
          ⚠️ Recipient address is set when you created each payment link at <a href="https://pay.hot-labs.org/admin/overview" target="_blank" class="link">HOT PAY Admin</a>
        </div>
      ` : `
        <div style="color: #a0a0a0; margin-bottom: 12px;">
          Best for: Simple payment links, webhook integration, multi-token support
        </div>

        <div class="steps">
          <div class="step">
            <strong>1.</strong> Visit <a href="https://pay.hot-labs.org/admin/overview" target="_blank" class="link">HOT PAY Admin</a>
          </div>
          <div class="step">
            <strong>2.</strong> Click "Create New Payment Link"
          </div>
          <div class="step">
            <strong>3.</strong> For each token (NEAR, USDC, USDT):
            <div style="margin-left: 20px; margin-top: 8px; color: #a0a0a0;">
              • Choose the token<br>
              • <strong>Set your NEAR wallet as recipient address</strong><br>
              • Copy the <code>item_id</code> from the created link
            </div>
          </div>
          <div class="step">
            <strong>4.</strong> Add to your <code>.env</code> file:
            <div class="code">HOTPAY_NEAR_ITEM_ID=your_near_item_id<br>HOTPAY_USDC_ITEM_ID=your_usdc_item_id<br>HOTPAY_USDT_ITEM_ID=your_usdt_item_id<br>PAYMENT_PROVIDER=hotpay<br>RECIPIENT_ADDRESS=your-account.near</div>
          </div>
          <div class="step">
            <strong>5.</strong> Restart the server
          </div>
        </div>
      `}
    </div>

    ${config.pingpay.configured || config.hotpay.configured ? `
      <a href="/" style="text-decoration: none;">
        <button class="continue-button">
          Continue to Payment Page →
        </button>
      </a>
    ` : `
      <button class="continue-button" disabled>
        Configure a provider above to continue
      </button>
    `}

    <div class="footer">
      Need help? Check the <strong>SKILL.md</strong> documentation
    </div>
  </div>
</body>
</html>
  `;

  res.send(html);
});

// Main payment page - redirect to setup if not configured
app.get('/', (req, res) => {
  // Check if any provider is configured
  if (!config.pingpay.configured && !config.hotpay.configured) {
    return res.redirect('/setup');
  }

  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pay with Crypto</title>
  <style>
    :root {
      --bg-body: #0b0c0e;
      --bg-card: rgba(255, 255, 255, 0.05);
      --border-color: rgba(71, 235, 165, 0.2);
      --accent-primary: #5feda9;
      --accent-gradient: linear-gradient(135deg, #a3f9d8 0%, #47eba5 100%);
      --accent-glow: 0 0 20px rgba(71, 235, 165, 0.3);
      --text-main: #ffffff;
      --text-secondary: #a0a0a0;
      --text-on-accent: #000000;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      background: var(--bg-body);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .container {
      background: var(--bg-card);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 40px;
      max-width: 480px;
      width: 100%;
      box-shadow: var(--accent-glow);
    }

    .header {
      text-align: center;
      margin-bottom: 32px;
    }

    h1 {
      color: var(--text-main);
      font-size: 28px;
      margin-bottom: 8px;
    }

    .recipient {
      color: var(--text-secondary);
      font-size: 14px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      padding: 8px 16px;
      border-radius: 20px;
      display: inline-block;
      margin-top: 8px;
    }

    .provider-badge {
      display: inline-block;
      background: var(--accent-gradient);
      color: var(--text-on-accent);
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      margin-top: 8px;
      text-transform: uppercase;
    }

    .token-selector {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      padding: 6px;
      border-radius: 12px;
    }

    .token-btn {
      flex: 1;
      background: transparent;
      border: none;
      padding: 12px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-secondary);
      transition: all 0.3s;
    }

    .token-btn.active {
      background: var(--accent-gradient);
      color: var(--text-on-accent);
      box-shadow: var(--accent-glow);
    }

    .token-btn:hover:not(.active):not(.disabled) {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-main);
    }

    .token-btn.disabled {
      opacity: 0.3;
      cursor: not-allowed;
    }

    .input-group {
      margin-bottom: 24px;
    }

    label {
      display: block;
      color: var(--text-main);
      font-weight: 600;
      margin-bottom: 8px;
      font-size: 14px;
    }

    .amount-input-wrapper {
      position: relative;
    }

    input[type="number"] {
      width: 100%;
      padding: 16px;
      padding-right: 60px;
      border: 2px solid var(--border-color);
      background: rgba(255, 255, 255, 0.03);
      border-radius: 8px;
      font-size: 18px;
      transition: all 0.3s;
      font-family: inherit;
      color: var(--text-main);
    }

    input[type="number"]:focus {
      outline: none;
      border-color: var(--accent-primary);
      background: rgba(255, 255, 255, 0.05);
      box-shadow: var(--accent-glow);
    }

    input[type="number"]::placeholder {
      color: var(--text-secondary);
      opacity: 0.5;
    }

    .currency-label {
      position: absolute;
      right: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 16px;
      pointer-events: none;
    }

    .presets {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-bottom: 24px;
    }

    .preset-btn {
      background: rgba(255, 255, 255, 0.03);
      border: 2px solid var(--border-color);
      padding: 14px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-main);
      transition: all 0.3s;
    }

    .preset-btn:hover {
      background: var(--accent-gradient);
      color: var(--text-on-accent);
      border-color: var(--accent-primary);
      box-shadow: var(--accent-glow);
    }

    .pay-button {
      width: 100%;
      background: var(--accent-gradient);
      color: var(--text-on-accent);
      border: none;
      padding: 18px;
      border-radius: 8px;
      font-size: 18px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: var(--accent-glow);
    }

    .pay-button:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(71, 235, 165, 0.5);
    }

    .pay-button:active {
      transform: translateY(0);
    }

    .pay-button:disabled {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-secondary);
      cursor: not-allowed;
      box-shadow: none;
      transform: none;
    }

    .loading {
      display: none;
      text-align: center;
      margin-top: 16px;
    }

    .loading.active {
      display: block;
    }

    .spinner {
      border: 3px solid rgba(255, 255, 255, 0.1);
      border-top: 3px solid var(--accent-primary);
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 12px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .loading p {
      color: var(--text-secondary);
    }

    .error {
      background: rgba(255, 82, 82, 0.1);
      color: #ff5252;
      border: 1px solid rgba(255, 82, 82, 0.3);
      padding: 12px;
      border-radius: 8px;
      margin-top: 16px;
      display: none;
      font-size: 14px;
    }

    .error.active {
      display: block;
    }

    .footer {
      text-align: center;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid var(--border-color);
      color: var(--text-secondary);
      font-size: 13px;
    }

    .footer a {
      color: var(--accent-primary);
      text-decoration: none;
    }

    .footer a:hover {
      text-decoration: underline;
      filter: brightness(1.2);
    }

    @media (max-width: 500px) {
      .container {
        padding: 28px 20px;
      }
      
      h1 {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Pay with Crypto</h1>
      <div class="recipient">→ ${config.recipient}</div>
      <div class="provider-badge">Powered by ${config.provider.toUpperCase()}</div>
    </div>

    <div class="token-selector">
      ${config.tokens.map((token, i) => {
        const key = `${token.symbol.toLowerCase()}_item_id` as keyof typeof config.hotpay;
        const isDisabled = config.provider === 'hotpay' && !config.hotpay[key];
        return `
        <button class="token-btn ${i === 0 && !isDisabled ? 'active' : ''} ${isDisabled ? 'disabled' : ''}" 
                data-token="${token.symbol}" 
                data-chain="${token.chain}" 
                data-decimals="${token.decimals}" 
                data-presets='${JSON.stringify(token.presets)}'
                ${isDisabled ? 'disabled' : ''}>
          ${token.symbol}
        </button>
      `}).join('')}
    </div>

    <div class="input-group">
      <label for="amount">Enter Amount</label>
      <div class="amount-input-wrapper">
        <input 
          type="number" 
          id="amount" 
          placeholder="0.0" 
          step="0.01" 
          min="0.01"
          autofocus
        >
        <span class="currency-label" id="currencyLabel">${config.tokens[0].symbol}</span>
      </div>
    </div>

    <div class="presets" id="presets">
      ${config.tokens[0].presets.map(amount => `
        <button class="preset-btn" data-amount="${amount}">
          ${amount} ${config.tokens[0].symbol}
        </button>
      `).join('')}
    </div>

    <button class="pay-button" id="payButton" disabled>
      Enter amount to pay
    </button>

    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>Creating payment session...</p>
    </div>

    <div class="error" id="error"></div>

    <div class="footer">
      Secure payments via NEAR Protocol · <a href="/setup" style="color: #667eea; text-decoration: none;">⚙️ Setup</a>
    </div>
  </div>

  <script>
    const tokens = ${JSON.stringify(config.tokens)};
    const provider = '${config.provider}';
    const hotpayConfig = ${JSON.stringify(config.hotpay)};
    
    // Filter available tokens for HOT PAY
    let availableTokens = tokens;
    if (provider === 'hotpay') {
      availableTokens = tokens.filter(t => {
        const key = t.symbol.toLowerCase() + '_item_id';
        return hotpayConfig[key];
      });
    }
    
    let currentToken = availableTokens[0];
    const amountInput = document.getElementById('amount');
    const payButton = document.getElementById('payButton');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const currencyLabel = document.getElementById('currencyLabel');
    const presetsContainer = document.getElementById('presets');

    // Check for URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const urlAmount = urlParams.get('amount');
    const urlToken = urlParams.get('token');

    // Helper function to hide non-selected tokens
    function hideOtherTokens() {
      document.querySelectorAll('.token-btn').forEach(btn => {
        if (!btn.classList.contains('active')) {
          btn.style.display = 'none';
        }
      });
    }

    // Pre-select token if specified in URL
    if (urlToken) {
      const matchingToken = availableTokens.find(t => t.symbol === urlToken);
      if (matchingToken) {
        currentToken = matchingToken;
        // Update active button
        document.querySelectorAll('.token-btn').forEach(btn => {
          if (btn.dataset.token === urlToken) {
            btn.classList.add('active');
          } else {
            btn.classList.remove('active');
          }
        });
        currencyLabel.textContent = currentToken.symbol;
        updatePresets();
        // Hide other tokens when coming from URL parameter
        setTimeout(() => hideOtherTokens(), 100);
      }
    }

    // Pre-fill amount if specified in URL
    if (urlAmount && parseFloat(urlAmount) > 0) {
      amountInput.value = urlAmount;
      updatePayButton();
    }

    document.querySelectorAll('.token-btn:not(.disabled)').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.token-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        currentToken = {
          symbol: btn.dataset.token,
          chain: btn.dataset.chain,
          decimals: parseInt(btn.dataset.decimals),
          presets: JSON.parse(btn.dataset.presets)
        };

        currencyLabel.textContent = currentToken.symbol;
        updatePresets();
        amountInput.value = '';
        updatePayButton();
        errorDiv.classList.remove('active');
        
        // Hide other tokens after selection to avoid confusion
        hideOtherTokens();
      });
    });

    function updatePresets() {
      presetsContainer.innerHTML = currentToken.presets.map(amount => 
        \`<button class="preset-btn" data-amount="\${amount}">
          \${amount} \${currentToken.symbol}
        </button>\`
      ).join('');

      document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          amountInput.value = btn.dataset.amount;
          updatePayButton();
        });
      });
    }

    amountInput.addEventListener('input', updatePayButton);

    function updatePayButton() {
      const amount = parseFloat(amountInput.value);
      if (amount > 0) {
        payButton.disabled = false;
        payButton.textContent = \`Pay \${amount} \${currentToken.symbol}\`;
        errorDiv.classList.remove('active');
      } else {
        payButton.disabled = true;
        payButton.textContent = 'Enter amount to pay';
      }
    }

    updatePresets();

    payButton.addEventListener('click', async () => {
      const amount = parseFloat(amountInput.value);
      
      if (!amount || amount <= 0) {
        showError('Please enter a valid amount');
        return;
      }

      payButton.disabled = true;
      payButton.textContent = 'Creating session...';
      loading.classList.add('active');
      errorDiv.classList.remove('active');

      try {
        const response = await fetch('/create-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            amount: amount,
            token: currentToken.symbol,
            chain: currentToken.chain
          })
        });

        const data = await response.json();

        if (data.success) {
          // Redirect directly to checkout
          loading.classList.remove('active');
          window.location.href = data.sessionUrl;
        } else{
          showError(data.error || 'Failed to create payment session');
          resetButton();
        }
      } catch (error) {
        showError('Network error: ' + error.message);
        resetButton();
      }
    });

    function showError(message) {
      errorDiv.textContent = message;
      errorDiv.classList.add('active');
    }

    function resetButton() {
      loading.classList.remove('active');
      updatePayButton();
    }

    amountInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !payButton.disabled) {
        payButton.click();
      }
    });
  </script>
</body>
</html>
  `;

  res.send(html);
});

// Quick link generator endpoint - creates both links at once
app.get('/quick-link', async (req, res) => {
  try {
    const amount = parseFloat(req.query.amount as string || '0');
    const token = (req.query.token as string || 'USDC').toUpperCase();
    const chain = 'near';

    if (!amount || amount <= 0) {
      return res.json({ success: false, error: 'Invalid amount. Usage: /quick-link?amount=5&token=USDC' });
    }

    console.log(`\n🔗 Quick Link Request: ${amount} ${token}`);

    const baseUrl = `${req.protocol}://${req.get('host')}`;
    const paymentPageUrl = `${baseUrl}/?amount=${amount}&token=${token}`;

    let checkoutUrl = '';

    if (config.provider === 'pingpay' && client) {
      let amountSmallest: string;
      if (token === 'NEAR') {
        amountSmallest = PingPayClient.nearToSmallestUnit(amount);
      } else if (token === 'USDC' || token === 'USDT') {
        amountSmallest = PingPayClient.usdcToSmallestUnit(amount);
      } else {
        return res.json({ success: false, error: 'Unsupported token' });
      }

      const session = await client.createCheckoutSession({
        amount: amountSmallest,
        asset: { chain, symbol: token },
        successUrl: `${baseUrl}/success`,
        cancelUrl: `${baseUrl}/cancel`,
        metadata: { amount: amount.toString(), token, chain, timestamp: Date.now() }
      });

      checkoutUrl = session.sessionUrl;
      console.log(`✅ PingPay Session: ${session.session.sessionId}`);

    } else if (config.provider === 'hotpay') {
      const itemIdMap: Record<string, string> = {
        'NEAR': config.hotpay.near_item_id,
        'USDC': config.hotpay.usdc_item_id,
        'USDT': config.hotpay.usdt_item_id
      };

      const itemId = itemIdMap[token];
      if (!itemId) {
        return res.json({ success: false, error: `HOT PAY not configured for ${token}` });
      }

      const memo = `pay_${Date.now()}_${token.toLowerCase()}`;
      const successUrl = encodeURIComponent(`${baseUrl}/success`);
      checkoutUrl = `https://pay.hot-labs.org/payment?item_id=${itemId}&amount=${amount}&redirect_url=${successUrl}&memo=${memo}`;
      console.log(`✅ HOT PAY Link: ${memo}`);
    } else {
      return res.json({ success: false, error: 'No provider configured' });
    }

    console.log(`🎨 Payment Page: ${paymentPageUrl}`);
    console.log(`⚡ Direct Checkout: ${checkoutUrl}\n`);

    res.json({
      success: true,
      amount,
      token,
      recipient: config.recipient,
      provider: config.provider,
      links: {
        paymentPage: paymentPageUrl,
        directCheckout: checkoutUrl
      }
    });

  } catch (error: any) {
    console.error('❌ Error:', error.message);
    res.json({ success: false, error: error.message });
  }
});

// Create payment session
app.post('/create-session', async (req, res) => {
  try {
    const { amount, token, chain } = req.body;

    if (!amount || amount <= 0) {
      return res.json({ success: false, error: 'Invalid amount' });
    }

    console.log(`\n💳 Payment Request: ${amount} ${token} (${chain})`);

    if (config.provider === 'hotpay') {
      const itemIdMap: Record<string, string> = {
        'NEAR': config.hotpay.near_item_id,
        'USDC': config.hotpay.usdc_item_id,
        'USDT': config.hotpay.usdt_item_id
      };

      const itemId = itemIdMap[token];
      if (!itemId) {
        return res.json({ 
          success: false, 
          error: `HOT PAY item_id not configured for ${token}. Go to /setup to configure.` 
        });
      }

      const memo = `pay_${Date.now()}_${token.toLowerCase()}`;
      const successUrl = encodeURIComponent(`${req.protocol}://${req.get('host')}/success`);
      const hotpayUrl = `https://pay.hot-labs.org/payment?item_id=${itemId}&amount=${amount}&redirect_url=${successUrl}&memo=${memo}`;

      console.log(`✅ HOT PAY Link`);
      console.log(`   Memo: ${memo}`);
      console.log(`   Direct Checkout: ${hotpayUrl}`);
      
      const baseUrl = `${req.protocol}://${req.get('host')}`;
      const paymentPageUrl = `${baseUrl}/?amount=${amount}&token=${token}`;
      console.log(`   Payment Page: ${paymentPageUrl}\n`);

      res.json({
        success: true,
        sessionUrl: hotpayUrl,
        paymentPageUrl: paymentPageUrl,
        provider: 'hotpay',
        memo: memo
      });

    } else if (config.provider === 'pingpay') {
      if (!client) {
        return res.json({ 
          success: false, 
          error: 'PingPay not configured. Go to /setup to add API key.' 
        });
      }

      let amountSmallest: string;
      if (token === 'NEAR') {
        amountSmallest = PingPayClient.nearToSmallestUnit(amount);
      } else if (token === 'USDC' || token === 'USDT') {
        amountSmallest = PingPayClient.usdcToSmallestUnit(amount);
      } else {
        return res.json({ success: false, error: 'Unsupported token' });
      }

      console.log(`   Amount in smallest unit: ${amountSmallest}`);

      const session = await client.createCheckoutSession({
        amount: amountSmallest,
        asset: { chain, symbol: token },
        successUrl: `${req.protocol}://${req.get('host')}/success`,
        cancelUrl: `${req.protocol}://${req.get('host')}/cancel`,
        metadata: {
          amount: amount.toString(),
          token,
          chain,
          timestamp: Date.now()
        }
      });

      console.log(`✅ Session: ${session.session.sessionId}`);
      console.log(`🔗 Direct Checkout: ${session.sessionUrl}`);
      
      const baseUrl = `${req.protocol}://${req.get('host')}`;
      const paymentPageUrl = `${baseUrl}/?amount=${amount}&token=${token}`;
      console.log(`🎨 Payment Page: ${paymentPageUrl}\n`);

      res.json({
        success: true,
        sessionUrl: session.sessionUrl,
        paymentPageUrl: paymentPageUrl,
        sessionId: session.session.sessionId,
        provider: 'pingpay'
      });
    } else {
      res.json({ 
        success: false, 
        error: 'No payment provider configured. Go to /setup.' 
      });
    }

  } catch (error: any) {
    console.error('❌ Error:', error.message);
    res.json({ success: false, error: error.message });
  }
});

// HOT PAY Webhook endpoint
app.post('/webhook/hotpay', (req, res) => {
  try {
    const payload = req.body;
    
    console.log('\n🔔 HOT PAY Webhook Received');
    console.log('='.repeat(70));
    console.log(JSON.stringify(payload, null, 2));
    console.log('='.repeat(70));
    
    if (payload.type === 'PAYMENT_STATUS_UPDATE' && payload.status === 'SUCCESS') {
      console.log(`✅ Payment Confirmed!`);
      console.log(`   Item ID: ${payload.item_id}`);
      console.log(`   Amount: $${payload.amount_float} (${payload.amount_usd} USD)`);
      console.log(`   Memo: ${payload.memo || 'N/A'}`);
      console.log(`   TX Hash: ${payload.near_trx}`);
      console.log(`   Verify: https://nearblocks.io/txns/${payload.near_trx}`);
    }
    
    res.status(200).json({ received: true });
    
  } catch (error: any) {
    console.error('❌ Webhook Error:', error.message);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
});

// Success page
app.get('/success', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>Payment Successful</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0b0c0e;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0;
      padding: 20px;
    }
    .container {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(71, 235, 165, 0.2);
      border-radius: 16px;
      padding: 48px 32px;
      text-align: center;
      max-width: 400px;
      box-shadow: 0 0 20px rgba(71, 235, 165, 0.3);
    }
    .icon { 
      font-size: 64px; 
      margin-bottom: 16px;
      filter: drop-shadow(0 0 10px rgba(71, 235, 165, 0.5));
    }
    h1 { 
      color: #5feda9; 
      margin-bottom: 12px;
      text-shadow: 0 0 20px rgba(71, 235, 165, 0.3);
    }
    p { 
      color: #a0a0a0; 
      line-height: 1.6; 
      margin-bottom: 24px; 
    }
    a {
      display: inline-block;
      background: linear-gradient(135deg, #a3f9d8 0%, #47eba5 100%);
      color: #000000;
      padding: 14px 32px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      box-shadow: 0 0 20px rgba(71, 235, 165, 0.3);
      transition: all 0.3s;
    }
    a:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 24px rgba(71, 235, 165, 0.5);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">✅</div>
    <h1>Payment Successful!</h1>
    <p>Your payment has been processed successfully.</p>
    <a href="/">Make Another Payment</a>
  </div>
</body>
</html>
  `);
});

// Cancel page
app.get('/cancel', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>Payment Cancelled</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0b0c0e;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0;
      padding: 20px;
    }
    .container {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 171, 0, 0.2);
      border-radius: 16px;
      padding: 48px 32px;
      text-align: center;
      max-width: 400px;
      box-shadow: 0 0 20px rgba(255, 171, 0, 0.2);
    }
    .icon { 
      font-size: 64px; 
      margin-bottom: 16px;
      filter: drop-shadow(0 0 10px rgba(255, 171, 0, 0.3));
    }
    h1 { 
      color: #ffab00; 
      margin-bottom: 12px;
      text-shadow: 0 0 20px rgba(255, 171, 0, 0.2);
    }
    p { 
      color: #a0a0a0; 
      line-height: 1.6; 
      margin-bottom: 24px; 
    }
    a {
      display: inline-block;
      background: linear-gradient(135deg, #ffd54f 0%, #ffab00 100%);
      color: #000000;
      padding: 14px 32px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      box-shadow: 0 0 20px rgba(255, 171, 0, 0.2);
      transition: all 0.3s;
    }
    a:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 24px rgba(255, 171, 0, 0.4);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">❌</div>
    <h1>Payment Cancelled</h1>
    <p>No problem. You can try again anytime.</p>
    <a href="/">Try Again</a>
  </div>
</body>
</html>
  `);
});

app.listen(PORT, () => {
  console.log(`\n✅ GetPay server running on port ${PORT}`);
  console.log(`📍 Local: http://localhost:${PORT}`);
  console.log(`💳 Provider: ${config.provider.toUpperCase()}`);
  console.log(`📧 Recipient: ${config.recipient}`);
  if (config.provider === 'hotpay') {
    console.log(`🔔 Webhook: http://localhost:${PORT}/webhook/hotpay`);
  }
  if (!config.pingpay.configured && !config.hotpay.configured) {
    console.log(`\n⚠️  No provider configured. Visit http://localhost:${PORT}/setup to get started.\n`);
  } else {
    console.log('');
  }
});

export default app;
