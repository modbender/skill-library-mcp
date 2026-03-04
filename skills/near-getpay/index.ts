import { PaymentOrchestrator } from './scripts/payment-orchestrator';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables
dotenv.config({ path: path.join(__dirname, '.env') });

/**
 * Main entry point for NEAR PingPay skill
 * Integrates with NEAR Intents skill to enable Web2 invoice payments using any crypto token
 */

export interface PayInvoiceParams {
  invoiceId: string;
  nearAccount: string;
  sourceToken?: string; // Default: "NEAR"
  nearIntentsSkillPath?: string; // Path to near-intents skill
}

export interface ListInvoicesParams {
  status?: 'pending' | 'paid' | 'expired' | 'cancelled';
}

export interface CreateTestInvoiceParams {
  amount: number;
  recipientAddress: string;
  description?: string;
}

/**
 * Pay a PingPay invoice using any token from NEAR wallet
 */
export async function payInvoice(params: PayInvoiceParams): Promise<any> {
  const apiKey = process.env.PINGPAY_API_KEY;
  if (!apiKey) {
    throw new Error('PINGPAY_API_KEY not configured in .env');
  }

  const orchestrator = new PaymentOrchestrator(apiKey);
  
  // Import NEAR Intents skill
  const nearIntentsPath = params.nearIntentsSkillPath || '../near-intents';
  const { executeIntent } = await import(nearIntentsPath);

  // Create NEAR Intents executor wrapper
  const nearIntentsExecutor = async (intentParams: {
    fromToken: string;
    toToken: string;
    amount: string;
    fromChain: string;
    toChain: string;
    toAddress: string;
  }) => {
    // Two-step execution for reliability:
    // Step 1: Swap to USDC on NEAR
    const swapResult = await executeIntent({
      operation: 'swap',
      fromToken: intentParams.fromToken,
      toToken: 'USDC',
      amount: intentParams.amount,
      chain: 'NEAR',
      nearAccount: params.nearAccount
    });

    // Step 2: Bridge USDC to Base
    const bridgeResult = await executeIntent({
      operation: 'withdraw',
      token: 'USDC',
      amount: intentParams.amount,
      fromChain: 'NEAR',
      toChain: 'Base',
      toAddress: intentParams.toAddress,
      nearAccount: params.nearAccount
    });

    return {
      swapTxHash: swapResult.txHash,
      bridgeTxHash: bridgeResult.txHash
    };
  };

  return orchestrator.payInvoice({
    invoiceId: params.invoiceId,
    nearAccount: params.nearAccount,
    sourceToken: params.sourceToken || 'NEAR',
    nearIntentsExecutor
  });
}

/**
 * List invoices by status
 */
export async function listInvoices(params?: ListInvoicesParams): Promise<any> {
  const apiKey = process.env.PINGPAY_API_KEY;
  if (!apiKey) {
    throw new Error('PINGPAY_API_KEY not configured in .env');
  }

  const orchestrator = new PaymentOrchestrator(apiKey);
  
  if (params?.status === 'pending') {
    return orchestrator.getPendingInvoices();
  }

  // For other statuses, use the PingPay client directly
  const { PingPayClient } = await import('./scripts/pingpay-client');
  const client = new PingPayClient(apiKey);
  return client.listInvoices({ status: params?.status });
}

/**
 * Create a test invoice (for development/testing)
 */
export async function createTestInvoice(params: CreateTestInvoiceParams): Promise<any> {
  const apiKey = process.env.PINGPAY_API_KEY;
  if (!apiKey) {
    throw new Error('PINGPAY_API_KEY not configured in .env');
  }

  const orchestrator = new PaymentOrchestrator(apiKey);
  return orchestrator.createTestInvoice({
    amount: params.amount,
    recipient_address: params.recipientAddress,
    description: params.description
  });
}

// For CLI usage
if (require.main === module) {
  const command = process.argv[2];
  
  switch (command) {
    case 'pay':
      const invoiceId = process.argv[3];
      const nearAccount = process.argv[4];
      const sourceToken = process.argv[5] || 'NEAR';
      
      if (!invoiceId || !nearAccount) {
        console.error('Usage: ts-node index.ts pay <invoice_id> <near_account> [source_token]');
        process.exit(1);
      }
      
      payInvoice({ invoiceId, nearAccount, sourceToken })
        .then(result => {
          console.log('\n✅ Payment Result:');
          console.log(JSON.stringify(result, null, 2));
        })
        .catch(error => {
          console.error('❌ Error:', error.message);
          process.exit(1);
        });
      break;

    case 'list':
      const status = process.argv[3] as any;
      listInvoices({ status })
        .then(invoices => {
          console.log('\n📄 Invoices:');
          console.log(JSON.stringify(invoices, null, 2));
        })
        .catch(error => {
          console.error('❌ Error:', error.message);
          process.exit(1);
        });
      break;

    case 'create-test':
      const amount = parseFloat(process.argv[3]);
      const recipientAddress = process.argv[4];
      const description = process.argv[5];
      
      if (!amount || !recipientAddress) {
        console.error('Usage: ts-node index.ts create-test <amount> <recipient_address> [description]');
        process.exit(1);
      }
      
      createTestInvoice({ amount, recipientAddress, description })
        .then(invoice => {
          console.log('\n✅ Test Invoice Created:');
          console.log(JSON.stringify(invoice, null, 2));
        })
        .catch(error => {
          console.error('❌ Error:', error.message);
          process.exit(1);
        });
      break;

    default:
      console.log(`
NEAR PingPay - Pay Web2 invoices with any crypto token

Commands:
  pay <invoice_id> <near_account> [source_token]
    Pay a PingPay invoice using tokens from your NEAR wallet
    Example: ts-node index.ts pay INV123 cuongdcdev.near PEPE

  list [status]
    List invoices (status: pending|paid|expired|cancelled)
    Example: ts-node index.ts list pending

  create-test <amount> <recipient_address> [description]
    Create a test invoice for development
    Example: ts-node index.ts create-test 10 0x30FE694284a082a5D1adfF6D25C0B9B6bF61F77D

Configuration:
  Create .env file with:
    PINGPAY_API_KEY=your_api_key_here
    NEAR_ACCOUNT_ID=your_account.near
    NEAR_PRIVATE_KEY=ed25519:...
      `);
  }
}
