#!/usr/bin/env node

/**
 * Obverse CLI - Helper tool for OpenClaw skill
 *
 * Makes API calls to Obverse payment platform easier from shell scripts
 * Used by the OpenClaw agent to interact with Obverse API
 */

const API_KEY = process.env.OBVERSE_API_KEY;
const BASE_URL = process.env.OBVERSE_API_URL || 'https://obverse.onrender.com';
const SUPPORTED_CHAINS = ['solana', 'monad'];

// Check for required environment variables
if (!API_KEY) {
  console.error(JSON.stringify({
    error: 'OBVERSE_API_KEY environment variable is required',
    message: 'Please set your API key in openclaw.json or export OBVERSE_API_KEY',
    docs: 'https://obverse.onrender.com/api-docs/quickstart'
  }, null, 2));
  process.exit(1);
}

/**
 * Make HTTP request with error handling
 */
async function makeRequest(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
    'User-Agent': 'Obverse-OpenClaw/1.0.0',
    ...options.headers
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.message || data.error || 'Unknown error',
        statusCode: response.status,
        details: data
      };
    }

    return {
      success: true,
      data,
      statusCode: response.status
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      statusCode: 500,
      details: { originalError: error.toString() }
    };
  }
}

function validateAndNormalizeChain(chain = 'solana') {
  const normalized = String(chain || 'solana').trim().toLowerCase();

  if (!SUPPORTED_CHAINS.includes(normalized)) {
    return {
      success: false,
      error: `Unsupported chain: ${chain}`,
      supportedChains: SUPPORTED_CHAINS,
      message: `Use one of: ${SUPPORTED_CHAINS.join(', ')}`
    };
  }

  return { success: true, chain: normalized };
}

/**
 * Commands
 */
const commands = {
  // Create payment link with optional custom fields
  'create-link': async (amount, currency = 'USDC', chain = 'solana', description = '', customFieldsJson = null, isReusable = 'false') => {
    const chainValidation = validateAndNormalizeChain(chain);
    if (chainValidation.success === false) {
      return chainValidation;
    }

    // Parse custom fields if provided
    let customFields = [];
    if (customFieldsJson) {
      try {
        customFields = JSON.parse(customFieldsJson);
      } catch (error) {
        return {
          success: false,
          error: 'Invalid customFields JSON format',
          details: error.message
        };
      }
    }

    const result = await makeRequest('/payment-links', {
      method: 'POST',
      body: JSON.stringify({
        amount: parseFloat(amount),
        token: currency,
        chain: chainValidation.chain,
        description,
        customFields,
        isReusable: isReusable === 'true' || isReusable === true
      })
    });

    if (result.success) {
      const data = result.data;
      return {
        paymentUrl: data.paymentUrl || `https://pay.obverse.app/${data.linkId}`,
        linkCode: data.linkId,
        paymentId: data._id,
        amount: data.amount,
        token: data.token,
        chain: data.chain,
        description: data.description,
        customFields: data.customFields,
        isReusable: data.isReusable,
        message: customFields.length > 0
          ? `Payment link created with ${customFields.length} custom field(s) for data collection!`
          : 'Payment link created successfully!'
      };
    }

    return result;
  },

  // Check payment status
  'check-payment': async (linkCode) => {
    const result = await makeRequest(`/payment-links/${linkCode}`);

    if (result.success) {
      const link = result.data;
      const merchantWalletAddress =
        link?.merchantId && typeof link.merchantId === 'object'
          ? link.merchantId.walletAddress
          : undefined;

      return {
        status: link.isActive ? 'active' : 'inactive',
        amount: link.amount,
        currency: link.currency || link.token,
        chain: link.chain,
        title: link.title,
        description: link.description,
        walletAddress:
          link.walletAddress ||
          link.recipientWalletAddress ||
          merchantWalletAddress,
        merchantId: link.merchantId
      };
    }

    return result;
  },

  // List payments for a link
  'list-payments': async (linkCode, limit = 10) => {
    const result = await makeRequest(`/payments/link/${linkCode}`);

    if (result.success) {
      const payments = Array.isArray(result.data) ? result.data : [];
      return {
        count: payments.length,
        payments: payments.slice(0, limit).map(p => ({
          id: p._id,
          amount: p.amount,
          token: p.token,
          chain: p.chain,
          status: p.status,
          txSignature: p.txSignature,
          fromAddress: p.fromAddress,
          toAddress: p.toAddress,
          isConfirmed:
            p.isConfirmed === true ||
            p.status === 'confirmed' ||
            (typeof p.confirmations === 'number' && p.confirmations > 0),
          createdAt: p.createdAt
        }))
      };
    }

    return result;
  },

  // Get wallet balance
  'balance': async (userId, chain = 'solana') => {
    const chainValidation = validateAndNormalizeChain(chain);
    if (chainValidation.success === false) {
      return chainValidation;
    }

    const result = await makeRequest(`/wallet/${userId}/balance?chain=${chainValidation.chain}`);

    if (result.success) {
      const balance = result.data;
      return {
        walletAddress: balance.walletAddress,
        chain: balance.chain,
        nativeBalance: balance.nativeBalanceUI || balance.nativeBalance,
        tokens: balance.tokens || []
      };
    }

    return result;
  },

  // Create invoice
  'create-invoice': async (recipient, amount, currency = 'USDC', chain = 'solana', dueDate = null) => {
    const chainValidation = validateAndNormalizeChain(chain);
    if (chainValidation.success === false) {
      return chainValidation;
    }

    const effectiveDueDate =
      dueDate || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
    const description = `Invoice for ${recipient} (due ${effectiveDueDate.split('T')[0]})`;

    // Invoice endpoint is not available in this API.
    // Use a one-time payment link as a consistent fallback.
    const linkResult = await commands['create-link'](
      amount,
      currency,
      chainValidation.chain,
      description,
      null,
      'false',
    );

    if (linkResult.success === false) {
      return linkResult;
    }

    return {
      invoiceId: null,
      invoiceUrl: null,
      paymentLink: linkResult.paymentUrl,
      linkCode: linkResult.linkCode,
      amount: parseFloat(amount),
      currency,
      chain: chainValidation.chain,
      dueDate: effectiveDueDate,
      recipient,
      message: 'Invoice endpoint not available; created one-time payment link instead.',
    };
  },

  // Submit payment
  'submit-payment': async (linkCode, txSignature, chain, amount, token, fromAddress, toAddress, customerEmail = '') => {
    const chainValidation = validateAndNormalizeChain(chain);
    if (chainValidation.success === false) {
      return chainValidation;
    }

    const result = await makeRequest('/payments', {
      method: 'POST',
      body: JSON.stringify({
        linkCode,
        txSignature,
        chain: chainValidation.chain,
        amount: parseFloat(amount),
        token,
        fromAddress,
        toAddress,
        customerData: customerEmail ? { email: customerEmail } : undefined
      })
    });

    if (result.success) {
      const paymentId = result.data._id;
      const isConfirmed =
        result.data.isConfirmed === true ||
        result.data.status === 'confirmed' ||
        (typeof result.data.confirmations === 'number' &&
          result.data.confirmations > 0);

      return {
        paymentId,
        status: result.data.status,
        isConfirmed,
        txSignature: result.data.txSignature,
        amount: result.data.amount,
        token: result.data.token,
        chain: result.data.chain,
        receipt: result.data.receipt || {
          receiptId: paymentId,
          paymentId,
          linkCode: result.data.linkCode || linkCode,
          txSignature: result.data.txSignature,
          amount: result.data.amount,
          token: result.data.token,
          chain: result.data.chain,
          fromAddress: result.data.fromAddress || fromAddress,
          toAddress: result.data.toAddress || toAddress,
          status: result.data.status,
          isConfirmed,
          confirmedAt: result.data.confirmedAt,
          createdAt: result.data.createdAt,
          dashboardUrl: 'https://www.obverse.cc/dashboard'
        }
      };
    }

    return result;
  },

  // Get receipt by payment ID
  'get-receipt': async (paymentId) => {
    const result = await makeRequest(`/payments/${paymentId}/receipt`);

    if (result.success) {
      return {
        success: true,
        receipt: result.data
      };
    }

    return result;
  },

  // Generate QR code
  'generate-qr': async (address, amount, currency = 'USDC', chain = 'solana') => {
    const chainValidation = validateAndNormalizeChain(chain);
    if (chainValidation.success === false) {
      return chainValidation;
    }

    // For now, create a payment link which includes QR code
    return commands['create-link'](amount, currency, chainValidation.chain, `Payment to ${address.substring(0, 8)}...`);
  },

  // ========================================
  // CONVENIENCE COMMANDS
  // These wrap the generic payment link for specific use cases
  // ========================================

  // Create payment link for selling a product/service (Merchant Sales)
  'create-product-link': async (title, price, currency = 'USDC', chain = 'solana', description = '', customFieldsJson = null) => {
    const chainValidation = validateAndNormalizeChain(chain);
    if (chainValidation.success === false) {
      return chainValidation;
    }

    const fullDescription = description || `Purchase: ${title}`;

    // Default custom fields for product sales if none provided
    const defaultFields = '[{"fieldName":"email","fieldType":"email","required":true},{"fieldName":"name","fieldType":"text","required":true}]';
    const fieldsToUse = customFieldsJson || defaultFields;

    const result = await commands['create-link'](price, currency, chainValidation.chain, fullDescription, fieldsToUse, 'true');

    if (result.success !== false) {
      return {
        ...result,
        type: 'product_sale',
        title,
        message: `Product payment link created! Collects customer email and name. Share this to sell "${title}" for ${price} ${currency}`
      };
    }

    return result;
  },

  // Create crowdfunding/fundraiser campaign (reusable payment link)
  'create-fundraiser': async (title, goalAmount, currency = 'USDC', chain = 'solana', description = '', customFieldsJson = null) => {
    const chainValidation = validateAndNormalizeChain(chain);
    if (chainValidation.success === false) {
      return chainValidation;
    }

    const fullDescription = description || `Fundraising: ${title} - Goal: ${goalAmount} ${currency}`;

    // Default custom fields for fundraising if none provided
    const defaultFields = '[{"fieldName":"email","fieldType":"email","required":false},{"fieldName":"name","fieldType":"text","required":false}]';
    const fieldsToUse = customFieldsJson || defaultFields;

    const result = await commands['create-link'](goalAmount, currency, chainValidation.chain, fullDescription, fieldsToUse, 'true');

    if (result.success !== false) {
      return {
        ...result,
        type: 'crowdfunding',
        title,
        goalAmount,
        message: `Fundraiser created! Goal: ${goalAmount} ${currency}. Collects optional contributor info. Share this link to accept contributions.`
      };
    }

    return result;
  },

  // Get analytics/dashboard for a payment link (sales or crowdfunding)
  'get-analytics': async (linkCode) => {
    // Get link details
    const linkResult = await commands['check-payment'](linkCode);

    if (linkResult.success === false) {
      return linkResult;
    }

    // Get all payments
    const paymentsResult = await commands['list-payments'](linkCode, 1000);

    if (paymentsResult.success === false) {
      return paymentsResult;
    }

    const payments = paymentsResult.payments || [];

    // Calculate analytics
    const totalAmount = payments.reduce((sum, p) => sum + (p.amount || 0), 0);
    const confirmedPayments = payments.filter(p => p.status === 'confirmed' || p.isConfirmed);
    const totalConfirmed = confirmedPayments.reduce((sum, p) => sum + (p.amount || 0), 0);

    // Extract unique payers (contributors/customers)
    const uniquePayers = [...new Set(payments.map(p => p.fromAddress))];

    // Get recent payments (last 5)
    const recentPayments = payments.slice(0, 5).map(p => ({
      amount: p.amount,
      token: p.token,
      from: p.fromAddress?.substring(0, 8) + '...',
      status: p.status,
      date: p.createdAt
    }));

    return {
      success: true,
      linkCode,
      description: linkResult.description,
      analytics: {
        totalPayments: payments.length,
        confirmedPayments: confirmedPayments.length,
        totalAmount,
        totalConfirmed,
        currency: linkResult.currency || 'USDC',
        uniqueContributors: uniquePayers.length,
        averageAmount: payments.length > 0 ? (totalAmount / payments.length).toFixed(2) : 0,
        status: linkResult.status
      },
      recentPayments
    };
  },

  // Get list of contributors/customers with their details
  'list-contributors': async (linkCode, limit = 50) => {
    const paymentsResult = await commands['list-payments'](linkCode, limit);

    if (paymentsResult.success === false) {
      return paymentsResult;
    }

    const payments = paymentsResult.payments || [];

    // Group by payer address
    const contributors = {};
    payments.forEach(p => {
      const address = p.fromAddress;
      if (!contributors[address]) {
        contributors[address] = {
          address,
          shortAddress: address?.substring(0, 8) + '...' + address?.substring(address.length - 6),
          totalContributed: 0,
          contributionCount: 0,
          firstContribution: p.createdAt,
          lastContribution: p.createdAt,
          contributions: []
        };
      }

      contributors[address].totalContributed += p.amount || 0;
      contributors[address].contributionCount += 1;
      contributors[address].contributions.push({
        amount: p.amount,
        token: p.token,
        txSignature: p.txSignature,
        date: p.createdAt
      });

      // Update last contribution date
      if (new Date(p.createdAt) > new Date(contributors[address].lastContribution)) {
        contributors[address].lastContribution = p.createdAt;
      }
    });

    // Convert to array and sort by total contributed
    const contributorsList = Object.values(contributors)
      .sort((a, b) => b.totalContributed - a.totalContributed);

    return {
      success: true,
      linkCode,
      totalContributors: contributorsList.length,
      totalPayments: payments.length,
      contributors: contributorsList
    };
  },

  // Check crowdfunding progress
  'check-progress': async (linkCode, goalAmount) => {
    const analytics = await commands['get-analytics'](linkCode);

    if (analytics.success === false) {
      return analytics;
    }

    const raised = analytics.analytics.totalConfirmed;
    const goal = parseFloat(goalAmount);
    const progress = goal > 0 ? ((raised / goal) * 100).toFixed(1) : 0;
    const remaining = Math.max(0, goal - raised);

    return {
      success: true,
      linkCode,
      fundraising: {
        goalAmount: goal,
        raisedAmount: raised,
        remainingAmount: remaining,
        progressPercent: progress,
        contributors: analytics.analytics.uniqueContributors,
        averageContribution: analytics.analytics.averageAmount,
        currency: analytics.analytics.currency
      },
      recentContributions: analytics.recentPayments
    };
  },

  // Generate dashboard link for a payment link
  'generate-dashboard': async (linkCode) => {
    const result = await makeRequest(`/payment-links/${linkCode}/dashboard`, {
      method: 'POST'
    });

    if (result.success) {
      const data = result.data;
      return {
        success: true,
        dashboardUrl: data.dashboardUrl,
        linkCode: data.linkCode,
        description: data.description,
        credentials: {
          username: data.identifier,
          password: data.temporaryPassword,
          expiresAt: data.expiresAt
        },
        message: data.message,
        instructions: [
          `1. Open dashboard: ${data.dashboardUrl}`,
          `2. Login with username: ${data.identifier}`,
          `3. Use password: ${data.temporaryPassword}`,
          `4. Password expires in 2 hours`,
          `5. View analytics for: ${data.description}`
        ]
      };
    }

    return result;
  },

  // Help command
  'help': async () => {
    return {
      usage: 'obverse-cli <command> [args...]',
      commands: {
        // Core Commands
        'create-link <amount> [currency] [chain] [description] [customFieldsJson] [isReusable]': 'Create a payment link with optional custom fields',
        'check-payment <paymentId>': 'Check payment link status',
        'list-payments <linkCode> [limit]': 'List all payments for a payment link',
        'balance <userId> [chain]': 'Get wallet balance',
        'create-invoice <recipient> <amount> [currency] [chain] [dueDate]': 'Create an invoice',
        'submit-payment <linkCode> <txSignature> <chain> <amount> <token> <from> <to> [email]': 'Submit a payment',
        'get-receipt <paymentId>': 'Get payment receipt by payment ID',
        'generate-qr <address> <amount> [currency] [chain]': 'Generate QR code for payment',

        // Convenience Commands (Merchant Sales)
        'create-product-link <title> <price> [currency] [chain] [description] [customFieldsJson]': 'Create payment link for selling products (auto-collects email & name)',

        // Convenience Commands (Crowdfunding)
        'create-fundraiser <title> <goalAmount> [currency] [chain] [description] [customFieldsJson]': 'Create crowdfunding campaign (auto-collects optional email & name)',
        'check-progress <linkCode> <goalAmount>': 'Check fundraising progress toward goal',

        // Analytics & Reporting
        'get-analytics <linkCode>': 'Get sales/fundraising analytics',
        'list-contributors <linkCode> [limit]': 'List all contributors/customers',
        'generate-dashboard <linkCode>': 'Generate dashboard link with login credentials',

        'help': 'Show this help message'
      },
      examples: {
        'Generic payment link (Solana)': 'obverse-cli create-link 50 USDC solana "Payment for services"',
        'Payment link with custom fields (Monad)': 'obverse-cli create-link 100 USDC monad "Consultation" \'[{"fieldName":"email","fieldType":"email","required":true},{"fieldName":"phone","fieldType":"tel","required":false}]\' true',
        'Product sales (Solana)': 'obverse-cli create-product-link "Running Shoes" 120 USDC solana "Premium shoes"',
        'Crowdfunding (Monad)': 'obverse-cli create-fundraiser "AI Development Fund" 5000 USDC monad',
        'Generate dashboard for link': 'obverse-cli generate-dashboard x7k9m2',
        'Check fundraising progress': 'obverse-cli check-progress fund-xyz 5000',
        'Get analytics': 'obverse-cli get-analytics x7k9m2',
        'List contributors': 'obverse-cli list-contributors fund-xyz 50',
        'Check payment': 'obverse-cli check-payment pay_abc123',
        'List payments': 'obverse-cli list-payments x7k9m2 10',
        'Check balance': 'obverse-cli balance 123456789 solana',
        'Create invoice': 'obverse-cli create-invoice john@example.com 100 USDC monad',
        'Get receipt': 'obverse-cli get-receipt 507f1f77bcf86cd799439013',
        'Generate QR': 'obverse-cli generate-qr 0x742d35Cc... 50 USDC solana'
      },
      useCases: {
        'Product Sales with Data Collection': 'Use create-product-link to sell products AND collect customer data (email, name, etc.). Perfect for building customer lists!',
        'Crowdfunding with Contributor Data': 'Use create-fundraiser for campaigns. Optionally collect contributor info. Track progress with check-progress.',
        'Custom Data Collection': 'Use create-link with customFields JSON to collect ANY data you need (phone, address, company, etc.).',
        'Dashboard Analytics': 'Use generate-dashboard to get login credentials for viewing payment analytics, stats, and contributor details.',
        'Simple Payments': 'Use create-link for one-time payments, tips, or donations.',
        'Invoicing': 'Use create-invoice for formal billing with recipient details.'
      },
      environment: {
        'OBVERSE_API_KEY': 'Your Obverse API key (required)',
        'OBVERSE_API_URL': 'Base URL for Obverse API (default: https://obverse.onrender.com)',
        'Supported chains': SUPPORTED_CHAINS.join(', ')
      },
      documentation: 'https://obverse.onrender.com/api-docs'
    };
  }
};

/**
 * Main execution
 */
async function main() {
  const [,, command, ...args] = process.argv;

  if (!command || command === 'help' || command === '--help' || command === '-h') {
    const help = await commands.help();
    console.log(JSON.stringify(help, null, 2));
    process.exit(0);
  }

  if (!commands[command]) {
    console.error(JSON.stringify({
      error: `Unknown command: ${command}`,
      availableCommands: Object.keys(commands),
      help: 'Run "obverse-cli help" for usage information'
    }, null, 2));
    process.exit(1);
  }

  try {
    const result = await commands[command](...args);
    console.log(JSON.stringify(result, null, 2));

    // Exit with error code if the command failed
    if (result.success === false) {
      process.exit(1);
    }
  } catch (error) {
    console.error(JSON.stringify({
      error: 'Command execution failed',
      message: error.message,
      stack: error.stack
    }, null, 2));
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error(JSON.stringify({
      error: 'Fatal error',
      message: error.message,
      stack: error.stack
    }, null, 2));
    process.exit(1);
  });
}

module.exports = { commands, makeRequest };
