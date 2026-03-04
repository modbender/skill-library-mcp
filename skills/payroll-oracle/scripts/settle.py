import sys

def calculate_payout(total_amount):
    # Your 1% Revenue Logic
    protocol_fee = total_amount * 0.01
    worker_payout = total_amount - protocol_fee
    
    return worker_payout, protocol_fee

if __name__ == "__main__":
    # Example: Genesis passes $100.00 to the script
    amount = float(sys.argv[1])
    worker, fee = calculate_payout(amount)
    
    print(f"Settling: ${worker} to Worker | ${fee} to your Trust Wallet")
    # In a real run, the x402 facilitator handles the actual on-chain move.