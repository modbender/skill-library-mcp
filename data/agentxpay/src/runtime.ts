import { AgentXPayClient } from "@agentxpay/sdk";
import { ethers } from "ethers";
import type {
  AgentXPaySkillConfig,
  DiscoverServicesParams,
  DiscoverServicesResult,
  PayAndCallParams,
  PayAndCallResult,
  ManageWalletParams,
  WalletInfo,
  SubscribeServiceParams,
  SubscribeResult,
  CreateEscrowParams,
  EscrowResult,
  SmartCallParams,
  SmartCallResult,
  ServiceInfo,
} from "./types";

export class AgentXPaySkill {
  private client: AgentXPayClient;
  private provider: ethers.JsonRpcProvider;
  private wallet: ethers.Wallet;

  constructor(config: AgentXPaySkillConfig) {
    this.provider = new ethers.JsonRpcProvider(config.rpcUrl);
    this.wallet = new ethers.Wallet(config.privateKey, this.provider);
    this.client = new AgentXPayClient({
      rpcUrl: config.rpcUrl,
      privateKey: config.privateKey,
      contracts: config.contracts,
      network: config.network || "testnet",
    });
  }

  // ─── Tool 1: Discover Services ─────────────────────────────

  async discoverServices(
    params: DiscoverServicesParams
  ): Promise<DiscoverServicesResult> {
    const filter: { category?: string; maxPrice?: bigint } = {};

    if (params.category) {
      filter.category = params.category;
    }
    if (params.maxPrice) {
      filter.maxPrice = ethers.parseEther(params.maxPrice);
    }

    const services = await this.client.discoverServices(filter);

    const mapped: ServiceInfo[] = services.map((svc) => ({
      id: svc.id.toString(),
      provider: svc.provider,
      name: svc.name,
      description: svc.description,
      endpoint: svc.endpoint,
      category: svc.category,
      pricePerCall: ethers.formatEther(svc.pricePerCall),
      isActive: svc.isActive,
    }));

    return {
      services: mapped,
      totalCount: mapped.length,
    };
  }

  // ─── Tool 2: Pay & Call (x402 Core) ────────────────────────

  async payAndCall(params: PayAndCallParams): Promise<PayAndCallResult> {
    const startTime = Date.now();

    const fetchOptions: RequestInit & {
      autoPayment: boolean;
      maxRetries?: number;
      serviceId?: string;
      pricePerCall?: string;
    } = {
      method: params.method,
      headers: {
        "Content-Type": "application/json",
        ...(params.headers || {}),
      },
      autoPayment: true,
    };

    // Pass on-chain serviceId and pricePerCall to SDK for validation (mismatch throws error)
    if (params.serviceId) {
      fetchOptions.serviceId = params.serviceId;
    }
    if (params.pricePerCall) {
      fetchOptions.pricePerCall = params.pricePerCall;
    }

    if (params.body) {
      fetchOptions.body = JSON.stringify(params.body);
    }

    const response = await this.client.fetch(params.url, fetchOptions);
    const latencyMs = Date.now() - startTime;

    let data: unknown;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    let payment: PayAndCallResult["payment"] = null;
    if (typeof data === "object" && data !== null && "payment" in data) {
      const paymentData = (data as Record<string, unknown>).payment as
        | Record<string, unknown>
        | undefined;
      if (paymentData?.txHash) {
        payment = {
          txHash: String(paymentData.txHash),
          amount: String(paymentData.amount || ""),
          serviceId: String(paymentData.serviceId || ""),
        };
      }
    }

    return {
      status: response.status,
      data,
      payment,
      latencyMs,
    };
  }

  // ─── Tool 3: Manage Agent Wallet ───────────────────────────

  async manageWallet(params: ManageWalletParams): Promise<WalletInfo> {
    switch (params.action) {
      case "create": {
        const dailyLimit = ethers.parseEther(params.dailyLimit || "1.0");
        const result = await this.client.wallet.createWallet(dailyLimit);

        return {
          walletAddress: result.walletAddress,
          balance: "0.0",
          dailyLimit: params.dailyLimit || "1.0",
          dailySpent: "0.0",
          remainingAllowance: params.dailyLimit || "1.0",
          txHash: result.txHash,
        };
      }

      case "fund": {
        if (!params.walletAddress) {
          throw new Error("walletAddress is required for fund action");
        }
        if (!params.amount) {
          throw new Error("amount is required for fund action");
        }

        const fundTx = await this.wallet.sendTransaction({
          to: params.walletAddress,
          value: ethers.parseEther(params.amount),
        });
        await fundTx.wait();

        const balance = await this.provider.getBalance(params.walletAddress);

        return {
          walletAddress: params.walletAddress,
          balance: ethers.formatEther(balance),
          dailyLimit: "",
          dailySpent: "",
          remainingAllowance: "",
          txHash: fundTx.hash,
        };
      }

      case "get_info": {
        if (!params.walletAddress) {
          throw new Error("walletAddress is required for get_info action");
        }

        const walletClient = this.client.wallet.getWalletInstance(
          params.walletAddress
        );
        const [balance, dailyLimit, dailySpent, remaining] = await Promise.all([
          this.provider.getBalance(params.walletAddress),
          walletClient.getDailySpendingLimit(),
          walletClient.getDailySpent(),
          walletClient.getRemainingDailyAllowance(),
        ]);

        return {
          walletAddress: params.walletAddress,
          balance: ethers.formatEther(balance),
          dailyLimit: ethers.formatEther(dailyLimit),
          dailySpent: ethers.formatEther(dailySpent),
          remainingAllowance: ethers.formatEther(remaining),
        };
      }

      case "set_limit": {
        if (!params.walletAddress) {
          throw new Error("walletAddress is required for set_limit action");
        }
        if (!params.dailyLimit) {
          throw new Error("dailyLimit is required for set_limit action");
        }

        const walletClient = this.client.wallet.getWalletInstance(
          params.walletAddress
        );
        const txHash = await walletClient.setDailySpendingLimit(
          ethers.parseEther(params.dailyLimit)
        );

        return {
          walletAddress: params.walletAddress,
          balance: "",
          dailyLimit: params.dailyLimit,
          dailySpent: "",
          remainingAllowance: "",
          txHash,
        };
      }

      case "authorize_agent": {
        if (!params.walletAddress) {
          throw new Error("walletAddress is required for authorize_agent action");
        }
        if (!params.agentAddress) {
          throw new Error("agentAddress is required for authorize_agent action");
        }

        const authWalletClient = this.client.wallet.getWalletInstance(
          params.walletAddress
        );

        // Pre-check: only wallet owner can authorize agents
        const authCallerAddress = await this.wallet.getAddress();
        const authWalletOwner = await authWalletClient.getOwner();
        if (authWalletOwner.toLowerCase() !== authCallerAddress.toLowerCase()) {
          throw new Error(
            `Only the wallet owner (${authWalletOwner}) can authorize agents. ` +
            `Current caller: ${authCallerAddress}`
          );
        }

        const authTxHash = await authWalletClient.authorizeAgent(params.agentAddress);

        // Verify authorization status
        const isAuthorized = await authWalletClient.isAuthorizedAgent(params.agentAddress);

        return {
          walletAddress: params.walletAddress,
          balance: "",
          dailyLimit: "",
          dailySpent: "",
          remainingAllowance: "",
          txHash: authTxHash,
          agentAddress: params.agentAddress,
          isAuthorized,
        };
      }

      case "revoke_agent": {
        if (!params.walletAddress) {
          throw new Error("walletAddress is required for revoke_agent action");
        }
        if (!params.agentAddress) {
          throw new Error("agentAddress is required for revoke_agent action");
        }

        const revokeWalletClient = this.client.wallet.getWalletInstance(
          params.walletAddress
        );

        // Pre-check: only wallet owner can revoke agents
        const revokeCallerAddress = await this.wallet.getAddress();
        const revokeWalletOwner = await revokeWalletClient.getOwner();
        if (revokeWalletOwner.toLowerCase() !== revokeCallerAddress.toLowerCase()) {
          throw new Error(
            `Only the wallet owner (${revokeWalletOwner}) can revoke agents. ` +
            `Current caller: ${revokeCallerAddress}`
          );
        }

        const revokeTxHash = await revokeWalletClient.revokeAgent(params.agentAddress);

        // Verify revocation
        const stillAuthorized = await revokeWalletClient.isAuthorizedAgent(params.agentAddress);

        return {
          walletAddress: params.walletAddress,
          balance: "",
          dailyLimit: "",
          dailySpent: "",
          remainingAllowance: "",
          txHash: revokeTxHash,
          agentAddress: params.agentAddress,
          isAuthorized: stillAuthorized,
        };
      }

      case "pay": {
        if (!params.walletAddress) {
          throw new Error("walletAddress is required for pay action");
        }
        if (params.serviceId === undefined) {
          throw new Error("serviceId is required for pay action");
        }
        if (!params.amount) {
          throw new Error("amount is required for pay action");
        }

        const payWalletClient = this.client.wallet.getWalletInstance(
          params.walletAddress
        );

        // Verify the caller is authorized to use this wallet
        const callerAddress = await this.wallet.getAddress();
        const callerIsAuthorized = await payWalletClient.isAuthorizedAgent(callerAddress);
        const walletOwner = await payWalletClient.getOwner();
        const isOwner = walletOwner.toLowerCase() === callerAddress.toLowerCase();

        if (!callerIsAuthorized && !isOwner) {
          throw new Error(
            `Agent ${callerAddress} is not authorized to use wallet ${params.walletAddress}. ` +
            `Please authorize this agent first using the 'authorize_agent' action.`
          );
        }

        // Check remaining daily allowance
        const remainingAllowance = await payWalletClient.getRemainingDailyAllowance();
        const payAmount = ethers.parseEther(params.amount);

        if (remainingAllowance < payAmount) {
          throw new Error(
            `Insufficient daily allowance. Remaining: ${ethers.formatEther(remainingAllowance)} MON, ` +
            `Requested: ${params.amount} MON. Adjust daily limit or wait for reset.`
          );
        }

        // Check wallet balance
        const walletBalance = await this.provider.getBalance(params.walletAddress);
        if (walletBalance < payAmount) {
          throw new Error(
            `Insufficient wallet balance. Balance: ${ethers.formatEther(walletBalance)} MON, ` +
            `Requested: ${params.amount} MON. Fund the wallet first.`
          );
        }

        // Encode PaymentManager.payPerUse(serviceId) call data
        const paymentManagerAddress = this.client.payments.getContractAddress();
        const paymentManagerIface = new ethers.Interface([
          "function payPerUse(uint256 serviceId) external payable",
        ]);
        const callData = paymentManagerIface.encodeFunctionData("payPerUse", [
          BigInt(params.serviceId),
        ]);

        // Execute payment through the Agent Wallet
        const payTxHash = await payWalletClient.execute(
          paymentManagerAddress,
          payAmount,
          callData
        );

        // Fetch updated wallet info
        const [updatedBalance, updatedDailySpent, updatedRemaining] = await Promise.all([
          this.provider.getBalance(params.walletAddress),
          payWalletClient.getDailySpent(),
          payWalletClient.getRemainingDailyAllowance(),
        ]);

        return {
          walletAddress: params.walletAddress,
          balance: ethers.formatEther(updatedBalance),
          dailyLimit: "",
          dailySpent: ethers.formatEther(updatedDailySpent),
          remainingAllowance: ethers.formatEther(updatedRemaining),
          txHash: payTxHash,
          paymentServiceId: params.serviceId.toString(),
          paymentAmount: params.amount,
        };
      }

      default:
        throw new Error(`Unknown wallet action: ${params.action}`);
    }
  }

  // ─── Tool 4: Subscribe to Service ─────────────────────────

  async subscribeService(
    params: SubscribeServiceParams
  ): Promise<SubscribeResult> {
    const serviceId = BigInt(params.serviceId);

    // Get subscription plans
    const plans = await this.client.services.getSubscriptionPlans(serviceId);
    if (plans.length === 0) {
      throw new Error(
        `No subscription plans available for service #${params.serviceId}`
      );
    }

    // Select plan
    const plan =
      params.planId !== undefined
        ? plans.find((p) => p.planId === BigInt(params.planId!))
        : plans[0];

    if (!plan) {
      throw new Error(`Plan #${params.planId} not found`);
    }

    // Subscribe
    const result = await this.client.subscribe(serviceId, plan.planId, plan.price);

    // Verify access
    const signerAddress = await this.wallet.getAddress();
    const hasAccess = await this.client.subscriptions.checkAccess(
      signerAddress,
      serviceId
    );

    return {
      subscriptionId: result.subscriptionId.toString(),
      serviceId: params.serviceId.toString(),
      planName: plan.name,
      price: ethers.formatEther(plan.price),
      txHash: result.txHash,
      hasAccess,
    };
  }

  // ─── Tool 5: Create Escrow ────────────────────────────────

  async createEscrow(params: CreateEscrowParams): Promise<EscrowResult> {
    const serviceId = BigInt(params.serviceId);
    const amount = ethers.parseEther(params.amount);
    const deadlineTimestamp = BigInt(
      Math.floor(Date.now() / 1000) + params.deadlineDays * 24 * 3600
    );

    // Get service to find provider address
    const service = await this.client.services.getServiceDetails(serviceId);

    const result = await this.client.escrow.createEscrow(
      serviceId,
      service.provider,
      deadlineTimestamp,
      params.description,
      amount
    );

    const deadlineDate = new Date(
      Number(deadlineTimestamp) * 1000
    ).toISOString();

    return {
      escrowId: result.escrowId.toString(),
      serviceId: params.serviceId.toString(),
      amount: params.amount,
      deadline: deadlineDate,
      txHash: result.txHash,
    };
  }

  // ─── Composite Tool: Smart Call ───────────────────────────

  async smartCall(params: SmartCallParams): Promise<SmartCallResult> {
    const startTime = Date.now();

    // 1. Discover matching services
    const { services } = await this.discoverServices({
      category: params.category,
      maxPrice: params.maxBudget,
    });

    if (services.length === 0) {
      throw new Error(
        `No matching services found${params.category ? ` in category "${params.category}"` : ""}${params.maxBudget ? ` within budget ${params.maxBudget} MON` : ""}`
      );
    }

    // 2. Select optimal service
    let selected: ServiceInfo;
    if (params.preferCheapest) {
      selected = [...services].sort(
        (a, b) => parseFloat(a.pricePerCall) - parseFloat(b.pricePerCall)
      )[0];
    } else {
      selected = services[0];
    }

    // 3. x402 auto-pay call (pass on-chain serviceId and pricePerCall for validation)
    const result = await this.payAndCall({
      url: selected.endpoint,
      method: "POST",
      body: { prompt: params.task },
      serviceId: selected.id,
      pricePerCall: ethers.parseEther(selected.pricePerCall).toString(),
    });

    const latencyMs = Date.now() - startTime;

    return {
      selectedService: {
        id: selected.id,
        name: selected.name,
        price: selected.pricePerCall,
        category: selected.category,
      },
      response: result.data,
      payment: result.payment,
      latencyMs,
    };
  }

  // ─── Utility: Get Agent Info ──────────────────────────────

  async getAgentInfo(): Promise<{
    address: string;
    balance: string;
    network: string;
  }> {
    const address = await this.wallet.getAddress();
    const balance = await this.provider.getBalance(address);
    const network = await this.provider.getNetwork();

    return {
      address,
      balance: ethers.formatEther(balance),
      network: network.chainId.toString(),
    };
  }

  /** Expose underlying AgentXPayClient for advanced usage */
  getClient(): AgentXPayClient {
    return this.client;
  }
}
