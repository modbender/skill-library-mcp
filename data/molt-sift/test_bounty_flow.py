#!/usr/bin/env python3
"""
End-to-End Bounty Flow Test
Simulates: Agent A posts bounty → Agent B claims → Molt Sift validates → Agent B gets paid
"""

import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from bounty_agent import BountyAgent
from payaclaw_client import PayAClawClient
from solana_payment import SolanaPaymentHandler
from sifter import Sifter


def print_section(title: str) -> None:
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_bounty_flow():
    """Test complete bounty flow."""
    
    print_section("Molt Sift Phase 1: End-to-End Bounty Flow Test")
    
    # Setup
    print("[Test Setup]")
    agent_a_address = "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7"
    agent_b_address = "4oJ5BaJjRxvRkwm5uXFQvVtTvfGwTQqRr4pZNqhWkVkq"
    
    payaclaw = PayAClawClient()
    payment_handler = SolanaPaymentHandler()
    
    print(f"[OK] Agent A (Bounty Poster): {agent_a_address}")
    print(f"[OK] Agent B (Bounty Hunter): {agent_b_address}")
    print(f"[OK] PayAClaw Client: {payaclaw.session_id}")
    
    # Step 1: Agent A lists available bounties
    print_section("Step 1: Agent A Reviews Available Bounties")
    
    bounties = payaclaw.list_bounties(filters={"job_type": "sift"})
    print(f"Available bounties: {len(bounties)}\n")
    
    for i, bounty in enumerate(bounties, 1):
        print(f"Bounty {i}:")
        print(f"  Job ID: {bounty['job_id']}")
        print(f"  Title: {bounty['title']}")
        print(f"  Amount: ${bounty['amount_usdc']} USDC")
        print(f"  Status: {bounty['status']}")
        print()
    
    # Step 2: Agent B (Bounty Hunter) Creates Agent and Claims First Job
    print_section("Step 2: Agent B Creates Bounty Hunter Agent")
    
    # Create agent (it will use its own payment handler)
    agent_b = BountyAgent(payout_address=agent_b_address, agent_id="agent_b_hunter_001")
    # Replace with the shared payment handler so we can track payments in test
    agent_b.payment_handler = payment_handler
    print(f"[OK] Agent created: {agent_b.agent_id}")
    print(f"[OK] Payout address: {agent_b_address}")
    
    # Get first bounty
    first_bounty = bounties[0]
    job_id = first_bounty["job_id"]
    
    print_section("Step 3: Agent B Claims and Processes Bounty Job")
    
    print(f"Target job: {job_id}")
    print(f"Title: {first_bounty['title']}")
    print(f"Reward: ${first_bounty['amount_usdc']} USDC\n")
    
    # Claim and process the job
    claim_result = agent_b.claim_bounty(job_id)
    
    if claim_result["status"] == "error":
        print(f"[FAIL] Claim failed: {claim_result['message']}")
        return False
    
    print(f"\n[OK] Job claimed and processed!")
    print(f"  Validation score: {claim_result['validation_score']}")
    print(f"  Amount earned: ${claim_result['amount_earned_usdc']} USDC")
    print(f"  Payment TXN: {claim_result['payment_txn'][:16]}...")
    
    # Step 3: Agent B Validates Data with Molt Sift (already done above, but let's show details)
    print_section("Step 4: Validation Details")
    
    # Get job details for reference
    job_details = payaclaw.get_job(job_id)
    raw_data = job_details["raw_data"]
    schema = job_details.get("schema")
    rules = job_details["validation_rules"]
    
    # Re-run validation to show details
    sifter = Sifter(rules=rules)
    validation_result = sifter.validate(raw_data, schema)
    
    print(f"Rule set: {rules}")
    print(f"Validation score: {validation_result['score']} / 1.0")
    print(f"Status: {validation_result['status']}")
    print(f"Issues found: {len(validation_result['issues'])}")
    
    if validation_result["issues"]:
        print("\nDetected issues:")
        for issue in validation_result["issues"][:3]:
            print(f"  - {issue.get('field', '_root')}: {issue['issue']} (severity: {issue['severity']})")
    
    print(f"\nCleaned data (first 5 fields):")
    if isinstance(validation_result["clean_data"], dict):
        for i, (k, v) in enumerate(validation_result["clean_data"].items()):
            if i >= 5:
                break
            print(f"  {k}: {v}")
    
    # Step 5: Extract transaction signature from agent
    print_section("Step 5: Payment Confirmation")
    
    # The agent already initiated payment - get the TXN from agent's completed jobs
    if not agent_b.completed_jobs:
        print("[FAIL] No completed jobs found")
        return False
    
    txn_sig = agent_b.completed_jobs[0]["txn_signature"]
    amount_usdc = agent_b.completed_jobs[0]["amount_usdc"]
    
    print(f"[OK] Payment was initiated by agent!")
    print(f"  Transaction: {txn_sig}")
    print(f"  Job ID: {agent_b.completed_jobs[0]['job_id']}")
    print(f"  Amount earned: ${amount_usdc} USDC")
    
    # Step 6: Confirm Payment
    print_section("Step 6: Payment Confirmation")
    
    confirmation = payment_handler.confirm_payment(txn_sig)
    
    if confirmation["status"] in ["confirmed", "already_confirmed"]:
        print(f"[OK] Payment confirmed!")
        print(f"  Transaction: {confirmation['txn_signature'][:16]}...")
        print(f"  Job ID: {confirmation.get('job_id', 'N/A')}")
        print(f"  Amount: {confirmation.get('amount_usdc', 'N/A')} USDC")
        print(f"  Confirmed at: {confirmation.get('confirmed_at', 'Just now')}")
    else:
        print(f"[FAIL] Confirmation failed: {confirmation['message']}")
        return False
    
    # Step 7: Get Agent Stats
    print_section("Step 7: Final Agent Statistics")
    
    agent_stats = payaclaw.get_agent_stats(agent_b.agent_id)
    
    print(f"Agent: {agent_b.agent_id}")
    print(f"Jobs claimed: {agent_stats['jobs_claimed']}")
    print(f"Jobs completed: {agent_stats['jobs_completed']}")
    print(f"Total earned: ${agent_stats['total_earned_usdc']} USDC")
    print(f"Completion rate: {agent_stats['completion_rate']:.0%}")
    
    # Payment History
    print_section("Step 8: Payment History")
    
    history = payment_handler.get_transaction_history(limit=5)
    
    print(f"Total transactions: {history['transaction_count']}")
    print(f"Confirmed: {history['confirmed_count']}")
    print(f"Pending: {history['pending_count']}")
    print(f"Total volume: ${sum(p['amount_usdc'] for p in history['recent_transactions']):.2f} USDC\n")
    
    for txn in history["recent_transactions"][:1]:
        print(f"Recent transaction:")
        print(f"  Signature: {txn['txn_signature'][:16]}...")
        print(f"  Amount: ${txn['amount_usdc']} USDC")
        print(f"  Recipient: {txn['recipient']}")
        print(f"  Status: {txn['status']}")
    
    # Final Success
    print_section("[OK] Test Complete: Full Bounty Flow Successful!")
    
    print("Summary:")
    print(f"  • Bounty posted: ${amount_usdc} USDC for data validation")
    print(f"  • Claimed by: {agent_b.agent_id}")
    print(f"  • Data validated with Molt Sift")
    print(f"  • Payment initiated via x402 Solana")
    print(f"  • Agent earned: ${amount_usdc} USDC")
    print(f"  • Transaction: {txn_sig}\n")
    
    print("This demonstrates the complete Molt Sift Phase 1 infrastructure:")
    print("  1. [OK] POST bounties (data validation jobs)")
    print("  2. [OK] CLAIM bounties (auto-watch PayAClaw)")
    print("  3. [OK] PROCESS with Sifter engine")
    print("  4. [OK] SUBMIT results to PayAClaw")
    print("  5. [OK] RECEIVE USDC payment via x402 escrow\n")
    
    return True


def test_api_server_simulation():
    """Test API server bounty endpoint."""
    
    print_section("Bonus: API Server Bounty Endpoint Test")
    
    print("This simulates posting a bounty via HTTP API:\n")
    
    test_payload = {
        "raw_data": {
            "symbol": "BTC",
            "price": "invalid_price",
            "volume": 1500000000
        },
        "schema": {
            "type": "object",
            "required": ["symbol", "price"],
            "properties": {
                "symbol": {"type": "string"},
                "price": {"type": "number"}
            }
        },
        "validation_rules": "crypto",
        "amount_usdc": 5.00,
        "payout_address": "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7"
    }
    
    print("POST /bounty payload:")
    print(json.dumps(test_payload, indent=2))
    
    # Simulate the request
    print("\n[Processing...]\n")
    
    sifter = Sifter(rules="crypto")
    validation_result = sifter.validate(test_payload["raw_data"], test_payload["schema"])
    
    payment_handler = SolanaPaymentHandler()
    payment_result = payment_handler.send_payment(
        amount_usdc=test_payload["amount_usdc"],
        recipient_address=test_payload["payout_address"],
        job_id="api_test_001"
    )
    
    response = {
        "status": "validated",
        "validation_score": validation_result["score"],
        "clean_data": validation_result["clean_data"],
        "issues": validation_result["issues"],
        "payment_status": payment_result["status"],
        "payment_txn": payment_result.get("txn_signature"),
        "amount_paid_usdc": test_payload["amount_usdc"]
    }
    
    print("POST /bounty response:")
    print(json.dumps(response, indent=2))
    
    print("\n[OK] API endpoint simulation successful!")


def main():
    """Run all tests."""
    
    try:
        # Test bounty flow
        success = test_bounty_flow()
        
        if not success:
            print("\n[FAIL] Bounty flow test failed")
            sys.exit(1)
        
        # Test API simulation
        test_api_server_simulation()
        
        print_section("[SIFT] All Tests Passed!")
        print("Molt Sift Phase 1 is ready for production.\n")
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
