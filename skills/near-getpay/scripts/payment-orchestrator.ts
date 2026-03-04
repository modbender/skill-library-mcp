import { PingPayClient, PingPayInvoice } from './pingpay-client';
import Decimal from 'decimal.js';

/**
 * Payment orchestrator that integrates NEAR Intents with PingPay
 * Flow: Any Token → USDC (NEAR) → USDC (Base) → PingPay Invoice
 */
export class PaymentOrchestrator {
  private pingpay: PingPayClient;

  constructor(apiKey: string) {
    this.pingpay = new PingPayClient(apiKey);
  }

  /**
   * Pay a PingPay invoice using any token from NEAR wallet
   * 
   * @param invoiceId - PingPay invoice ID
   * @param nearAccount - NEAR account to pay from
   * @param sourceToken - Token to swap from (e.g., "NEAR", "PEPE", "SHIB")
   * @param nearIntentsExecutor - Function to execute NEAR intent (swap + bridge)
   * @returns Payment result with transaction hashes
   */
  async payInvoice(params: {
    invoiceId: string;
    nearAccount: string;
    sourceToken: string;
    nearIntentsExecutor: (params: {
      fromToken: string;
      toToken: string;
      amount: string;
      fromChain: string;
      toChain: string;
      toAddress: string;
    }) => Promise<{ swapTxHash?: string; bridgeTxHash?: string }>;
  }): Promise<{
    success: boolean;
    invoice: PingPayInvoice;
    swapTxHash?: string;
    bridgeTxHash?: string;
    paymentId?: string;
    error?: string;
  }> {
    const { invoiceId, nearAccount, sourceToken, nearIntentsExecutor } = params;

    try {
      // Step 1: Fetch invoice details
      console.log(`📄 Fetching invoice ${invoiceId}...`);
      const invoice = await this.pingpay.getInvoice(invoiceId);

      // Validate invoice
      if (invoice.status !== 'pending') {
        throw new Error(`Invoice status is ${invoice.status}, expected 'pending'`);
      }

      if (invoice.currency.toUpperCase() !== 'USDC') {
        throw new Error(`Invoice currency is ${invoice.currency}, only USDC is supported`);
      }

      const usdcAmount = new Decimal(invoice.amount);
      console.log(`💰 Invoice amount: ${usdcAmount.toString()} USDC`);
      console.log(`📍 Recipient address: ${invoice.recipient_address}`);

      // Step 2: Execute NEAR intent (swap + bridge)
      // Two-step approach for reliability:
      // 1. Swap sourceToken → USDC on NEAR
      // 2. Bridge USDC → Base chain
      console.log(`\n🔄 Executing payment flow: ${sourceToken} → USDC (NEAR) → USDC (Base)...`);
      
      const intentResult = await nearIntentsExecutor({
        fromToken: sourceToken,
        toToken: 'USDC',
        amount: usdcAmount.toString(),
        fromChain: 'NEAR',
        toChain: 'Base',
        toAddress: invoice.recipient_address
      });

      if (!intentResult.bridgeTxHash) {
        throw new Error('Bridge transaction failed - no transaction hash received');
      }

      console.log(`✅ Swap TX: ${intentResult.swapTxHash || 'N/A'}`);
      console.log(`✅ Bridge TX: ${intentResult.bridgeTxHash}`);

      // Step 3: Submit payment proof to PingPay
      console.log(`\n📤 Submitting payment to PingPay...`);
      const paymentResult = await this.pingpay.submitPayment({
        invoice_id: invoiceId,
        tx_hash: intentResult.bridgeTxHash,
        amount: usdcAmount.toNumber(),
        from_address: nearAccount
      });

      console.log(`✅ Payment submitted: ${paymentResult.payment_id}`);
      console.log(`Status: ${paymentResult.status}`);

      return {
        success: true,
        invoice,
        swapTxHash: intentResult.swapTxHash,
        bridgeTxHash: intentResult.bridgeTxHash,
        paymentId: paymentResult.payment_id
      };

    } catch (error: any) {
      console.error(`❌ Payment failed: ${error.message}`);
      return {
        success: false,
        invoice: {} as PingPayInvoice,
        error: error.message
      };
    }
  }

  /**
   * Get pending invoices that need payment
   */
  async getPendingInvoices(): Promise<PingPayInvoice[]> {
    return this.pingpay.listInvoices({ status: 'pending' });
  }

  /**
   * Create a test invoice for development
   */
  async createTestInvoice(params: {
    amount: number;
    recipient_address: string;
    description?: string;
  }): Promise<PingPayInvoice> {
    return this.pingpay.createInvoice({
      amount: params.amount,
      currency: 'USDC',
      recipient_address: params.recipient_address,
      description: params.description || 'Test invoice from NEAR PingPay skill',
      expires_in_hours: 24
    });
  }

  /**
   * Calculate required source token amount for a given USDC invoice
   * (This would integrate with price service to calculate optimal amount)
   */
  async calculateRequiredAmount(params: {
    invoiceAmount: number; // USDC
    sourceToken: string;
    priceService: (token: string) => Promise<number>;
  }): Promise<{
    sourceAmount: string;
    sourceToken: string;
    targetAmount: string;
    estimatedSlippage: string;
  }> {
    const { invoiceAmount, sourceToken, priceService } = params;

    // Get prices
    const usdcPrice = 1; // USDC is pegged to $1
    const sourcePrice = await priceService(sourceToken);

    // Calculate required amount with 1% slippage buffer
    const slippageMultiplier = 1.01;
    const requiredUSD = invoiceAmount * usdcPrice;
    const sourceAmount = (requiredUSD / sourcePrice) * slippageMultiplier;

    return {
      sourceAmount: new Decimal(sourceAmount).toFixed(6),
      sourceToken,
      targetAmount: invoiceAmount.toString(),
      estimatedSlippage: '1%'
    };
  }
}
