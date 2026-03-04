import express from 'express';
import { PingPayClient } from './scripts/pingpay-client';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.join(__dirname, '.env') });

const app = express();
const PORT = process.env.PORT || 3000;

const apiKey = process.env.PINGPAY_API_KEY;
if (!apiKey) {
  console.error('❌ PINGPAY_API_KEY not found in .env');
  process.exit(1);
}

const client = new PingPayClient(apiKey);

// Serve static HTML page
app.get('/', (req, res) => {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Buy Me a Coffee ☕ - NEAR Payment</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .container {
      background: white;
      border-radius: 20px;
      padding: 40px;
      max-width: 500px;
      width: 100%;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .header {
      text-align: center;
      margin-bottom: 30px;
    }

    .avatar {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      margin: 0 auto 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 50px;
    }

    h1 {
      color: #333;
      font-size: 28px;
      margin-bottom: 10px;
    }

    .subtitle {
      color: #666;
      font-size: 16px;
      margin-bottom: 10px;
    }

    .recipient {
      color: #667eea;
      font-size: 14px;
      font-weight: 600;
      background: #f0f0ff;
      padding: 8px 16px;
      border-radius: 20px;
      display: inline-block;
      margin-top: 10px;
    }

    .description {
      color: #666;
      text-align: center;
      margin-bottom: 30px;
      line-height: 1.6;
    }

    .payment-options {
      display: grid;
      gap: 15px;
      margin-bottom: 30px;
    }

    .payment-card {
      background: #f8f9fa;
      border: 2px solid #e0e0e0;
      border-radius: 15px;
      padding: 20px;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .payment-card:hover {
      border-color: #667eea;
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }

    .payment-card.selected {
      border-color: #667eea;
      background: #f0f0ff;
    }

    .payment-info {
      flex: 1;
    }

    .payment-label {
      font-weight: 600;
      color: #333;
      margin-bottom: 5px;
    }

    .payment-amount {
      font-size: 24px;
      font-weight: 700;
      color: #667eea;
    }

    .payment-usd {
      color: #999;
      font-size: 14px;
      margin-left: 8px;
    }

    .emoji {
      font-size: 32px;
    }

    .pay-button {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      padding: 18px 40px;
      border-radius: 50px;
      font-size: 18px;
      font-weight: 600;
      cursor: pointer;
      width: 100%;
      transition: all 0.3s ease;
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .pay-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    .pay-button:active {
      transform: translateY(0);
    }

    .pay-button:disabled {
      background: #ccc;
      cursor: not-allowed;
      box-shadow: none;
    }

    .loading {
      display: none;
      text-align: center;
      color: #667eea;
      margin-top: 20px;
    }

    .loading.active {
      display: block;
    }

    .spinner {
      border: 3px solid #f3f3f3;
      border-top: 3px solid #667eea;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .footer {
      text-align: center;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #e0e0e0;
      color: #999;
      font-size: 14px;
    }

    .powered-by {
      margin-top: 10px;
    }

    .powered-by a {
      color: #667eea;
      text-decoration: none;
      font-weight: 600;
    }

    @media (max-width: 600px) {
      .container {
        padding: 30px 20px;
      }

      h1 {
        font-size: 24px;
      }

      .payment-amount {
        font-size: 20px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="avatar">☕</div>
      <h1>Buy Me a Coffee</h1>
      <p class="subtitle">Support my work on NEAR Protocol</p>
      <span class="recipient">→ meteorkent.near</span>
    </div>

    <p class="description">
      Your support helps me build amazing things on NEAR! 
      Choose an amount below and pay with crypto from any chain.
    </p>

    <div class="payment-options">
      <div class="payment-card" data-amount="0.5" data-token="NEAR" data-chain="NEAR">
        <div class="payment-info">
          <div class="payment-label">Coffee</div>
          <div class="payment-amount">
            0.5 NEAR
            <span class="payment-usd">~$2</span>
          </div>
        </div>
        <div class="emoji">☕</div>
      </div>

      <div class="payment-card" data-amount="1" data-token="NEAR" data-chain="NEAR">
        <div class="payment-info">
          <div class="payment-label">Double Shot</div>
          <div class="payment-amount">
            1 NEAR
            <span class="payment-usd">~$4</span>
          </div>
        </div>
        <div class="emoji">☕☕</div>
      </div>

      <div class="payment-card" data-amount="5" data-token="USDC" data-chain="Base">
        <div class="payment-info">
          <div class="payment-label">Lunch</div>
          <div class="payment-amount">
            $5 USDC
          </div>
        </div>
        <div class="emoji">🍔</div>
      </div>

      <div class="payment-card" data-amount="10" data-token="USDC" data-chain="Base">
        <div class="payment-info">
          <div class="payment-label">Supporter</div>
          <div class="payment-amount">
            $10 USDC
          </div>
        </div>
        <div class="emoji">❤️</div>
      </div>
    </div>

    <button class="pay-button" id="payButton" disabled>
      Select an amount above
    </button>

    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>Creating payment link...</p>
    </div>

    <div class="footer">
      <p>✨ Powered by NEAR Intents - Pay from any chain</p>
      <p class="powered-by">
        Built with <a href="https://pingpay.io" target="_blank">PingPay</a>
      </p>
    </div>
  </div>

  <script>
    let selectedAmount = null;
    let selectedToken = null;
    let selectedChain = null;

    // Handle card selection
    document.querySelectorAll('.payment-card').forEach(card => {
      card.addEventListener('click', () => {
        // Remove selected from all cards
        document.querySelectorAll('.payment-card').forEach(c => {
          c.classList.remove('selected');
        });

        // Add selected to clicked card
        card.classList.add('selected');

        // Get payment details
        selectedAmount = parseFloat(card.dataset.amount);
        selectedToken = card.dataset.token;
        selectedChain = card.dataset.chain;

        // Enable button
        const button = document.getElementById('payButton');
        button.disabled = false;
        button.textContent = \`Pay \${selectedAmount} \${selectedToken}\`;
      });
    });

    // Handle payment
    document.getElementById('payButton').addEventListener('click', async () => {
      if (!selectedAmount) return;

      const button = document.getElementById('payButton');
      const loading = document.getElementById('loading');

      // Show loading
      button.disabled = true;
      button.textContent = 'Creating session...';
      loading.classList.add('active');

      try {
        // Call our API to create checkout session
        const response = await fetch('/create-session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            amount: selectedAmount,
            token: selectedToken,
            chain: selectedChain
          })
        });

        const data = await response.json();

        if (data.success) {
          // Redirect to PingPay checkout
          window.location.href = data.sessionUrl;
        } else {
          alert('Error creating session: ' + data.error);
          button.disabled = false;
          button.textContent = \`Pay \${selectedAmount} \${selectedToken}\`;
          loading.classList.remove('active');
        }
      } catch (error) {
        alert('Error: ' + error.message);
        button.disabled = false;
        button.textContent = \`Pay \${selectedAmount} \${selectedToken}\`;
        loading.classList.remove('active');
      }
    });
  </script>
</body>
</html>
  `;

  res.send(html);
});

// API endpoint to create checkout session
app.use(express.json());
app.post('/create-session', async (req, res) => {
  try {
    const { amount, token, chain } = req.body;

    if (!amount || !token || !chain) {
      return res.json({ success: false, error: 'Missing required fields' });
    }

    // Calculate amount in smallest unit
    let amountSmallest: string;
    if (token === 'NEAR') {
      amountSmallest = PingPayClient.nearToSmallestUnit(amount);
    } else if (token === 'USDC') {
      amountSmallest = PingPayClient.usdcToSmallestUnit(amount);
    } else {
      return res.json({ success: false, error: 'Unsupported token' });
    }

    console.log(`\n💳 Creating session: ${amount} ${token} on ${chain}`);
    console.log(`   Amount in smallest unit: ${amountSmallest}`);

    // Create checkout session
    const session = await client.createCheckoutSession({
      amount: amountSmallest,
      asset: {
        chain: chain,
        symbol: token
      },
      successUrl: `${req.protocol}://${req.get('host')}/success`,
      cancelUrl: `${req.protocol}://${req.get('host')}/cancel`,
      metadata: {
        orderId: `coffee_${Date.now()}`,
        amount: amount,
        token: token,
        chain: chain
      }
    });

    console.log(`✅ Session created: ${session.session.sessionId}`);
    console.log(`🔗 Checkout URL: ${session.sessionUrl}`);

    res.json({
      success: true,
      sessionUrl: session.sessionUrl,
      sessionId: session.session.sessionId
    });

  } catch (error: any) {
    console.error('❌ Error creating session:', error.message);
    res.json({
      success: false,
      error: error.message
    });
  }
});

// Success page
app.get('/success', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Payment Successful! ✅</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0;
          padding: 20px;
        }
        .container {
          background: white;
          border-radius: 20px;
          padding: 60px 40px;
          text-align: center;
          max-width: 500px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        .success-icon {
          font-size: 80px;
          margin-bottom: 20px;
        }
        h1 {
          color: #11998e;
          margin-bottom: 15px;
        }
        p {
          color: #666;
          line-height: 1.6;
          margin-bottom: 30px;
        }
        .button {
          background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
          color: white;
          padding: 15px 40px;
          border-radius: 50px;
          text-decoration: none;
          display: inline-block;
          font-weight: 600;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="success-icon">✅</div>
        <h1>Payment Successful!</h1>
        <p>Thank you for your support! Your payment has been processed successfully via NEAR Intents.</p>
        <a href="/" class="button">Buy Another Coffee ☕</a>
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
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0;
          padding: 20px;
        }
        .container {
          background: white;
          border-radius: 20px;
          padding: 60px 40px;
          text-align: center;
          max-width: 500px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        .cancel-icon {
          font-size: 80px;
          margin-bottom: 20px;
        }
        h1 {
          color: #f5576c;
          margin-bottom: 15px;
        }
        p {
          color: #666;
          line-height: 1.6;
          margin-bottom: 30px;
        }
        .button {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          color: white;
          padding: 15px 40px;
          border-radius: 50px;
          text-decoration: none;
          display: inline-block;
          font-weight: 600;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="cancel-icon">❌</div>
        <h1>Payment Cancelled</h1>
        <p>No worries! Your payment was cancelled. Feel free to try again anytime.</p>
        <a href="/" class="button">Try Again</a>
      </div>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`\n🚀 Buy Me a Coffee server started!`);
  console.log(`📍 Local: http://localhost:${PORT}`);
  console.log(`\n🔗 Starting tunnel...\n`);
});

export default app;
