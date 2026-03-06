"""
Bounty Agent - Hunts and processes PayAClaw/MoltyGuild bounty jobs
Integrates with x402 Solana escrow for auto-payment
"""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Import local modules
try:
    from payaclaw_client import PayAClawClient
    from solana_payment import SolanaPaymentHandler
    from sifter import Sifter
except ImportError:
    print("[BountyAgent] Error: Missing required modules")
    sys.exit(1)


class BountyAgent:
    """Manages bounty hunting and payment processing."""
    
    def __init__(self, payout_address: str, agent_id: Optional[str] = None):
        """
        Initialize bounty agent.
        
        Args:
            payout_address: Solana wallet address for receiving payments
            agent_id: Unique agent identifier (auto-generated if not provided)
        """
        self.payout_address = payout_address
        self.agent_id = agent_id or f"agent_{int(time.time())}"
        self.jobs_processed = 0
        self.total_earned = 0.0
        self.status = "initialized"
        
        # Initialize API clients
        self.payaclaw = PayAClawClient()
        self.payment_handler = SolanaPaymentHandler()
        
        # Track claimed jobs
        self.claimed_jobs = {}
        self.completed_jobs = []
    
    def watch_and_claim(self, check_interval: int = 30, auto_confirm_payments: bool = True) -> None:
        """
        Watch PayAClaw for bounty jobs and auto-claim.
        
        Args:
            check_interval: Seconds between checks
            auto_confirm_payments: Whether to auto-confirm payments
        """
        print(f"[BountyAgent] [SIFT] Starting bounty agent (watching PayAClaw)...")
        print(f"[BountyAgent] Agent ID: {self.agent_id}")
        print(f"[BountyAgent] Payout address: {self.payout_address}")
        print(f"[BountyAgent] Check interval: {check_interval}s")
        print(f"[BountyAgent] Status: ACTIVE\n")
        
        self.status = "active"
        check_count = 0
        
        try:
            while True:
                check_count += 1
                print(f"[BountyAgent] Check #{check_count} at {datetime.utcnow().isoformat()}Z")
                
                # Check for new bounties
                self._check_payaclaw_bounties()
                
                # Process any pending jobs
                self._process_pending_jobs()
                
                # Confirm payments if needed
                if auto_confirm_payments:
                    self._confirm_pending_payments()
                
                print(f"[BountyAgent] Waiting {check_interval}s until next check...\n")
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n[BountyAgent] [OK] Stopping gracefully...")
            self._print_final_stats()
    
    def claim_bounty(self, job_id: str) -> Dict[str, Any]:
        """
        Claim and process a specific bounty job.
        
        Args:
            job_id: Job ID to claim
        
        Returns:
            Claim and processing result
        """
        print(f"\n[BountyAgent] Claiming bounty {job_id}...")
        
        # Claim job
        claim_result = self.payaclaw.claim_job(job_id, self.agent_id)
        
        if claim_result["status"] == "error":
            print(f"[BountyAgent] [FAIL] Claim failed: {claim_result['message']}")
            return claim_result
        
        print(f"[BountyAgent] [OK] Claimed job {job_id}")
        self.claimed_jobs[job_id] = claim_result
        
        # Process the job
        return self._process_job(job_id, claim_result)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and statistics."""
        return {
            "status": self.status,
            "agent_id": self.agent_id,
            "payout_address": self.payout_address,
            "jobs_claimed": len(self.claimed_jobs),
            "jobs_completed": len(self.completed_jobs),
            "jobs_processed": self.jobs_processed,
            "total_earned_usdc": round(self.total_earned, 2),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _check_payaclaw_bounties(self) -> None:
        """Check PayAClaw for new bounties and auto-claim."""
        try:
            # List available bounties
            bounties = self.payaclaw.list_bounties(filters={"job_type": "sift"})
            
            if not bounties:
                print("[BountyAgent] No new bounties available")
                return
            
            print(f"[BountyAgent] Found {len(bounties)} available bounty(ies)")
            
            # Auto-claim first available job
            for bounty in bounties:
                if bounty["status"] == "open" and bounty["job_id"] not in self.claimed_jobs:
                    print(f"[BountyAgent] Auto-claiming: {bounty['title']} (${bounty['amount_usdc']})")
                    self.claim_bounty(bounty["job_id"])
                    break
        
        except Exception as e:
            print(f"[BountyAgent] Error checking bounties: {e}")
    
    def _process_job(self, job_id: str, job_details: Dict) -> Dict[str, Any]:
        """
        Process a bounty job: validate data and submit result.
        
        Args:
            job_id: Job ID
            job_details: Job details from claim
        
        Returns:
            Processing result with payment info
        """
        print(f"[BountyAgent] Processing job {job_id}...")
        
        try:
            # Extract data and rules
            raw_data = job_details.get("raw_data")
            schema = job_details.get("schema")
            rules = job_details.get("validation_rules", "json-strict")
            amount_usdc = job_details.get("amount_usdc", 0)
            
            # Validate with Sifter
            print(f"[BountyAgent] Validating data with rule set: {rules}")
            sifter = Sifter(rules=rules)
            validation_result = sifter.validate(raw_data, schema)
            
            print(f"[BountyAgent] Validation score: {validation_result['score']}")
            
            # Submit result to PayAClaw
            print(f"[BountyAgent] Submitting validation result...")
            submit_result = self.payaclaw.submit_result(job_id, validation_result, self.agent_id)
            
            if submit_result["status"] == "error":
                print(f"[BountyAgent] [FAIL] Submission failed: {submit_result['message']}")
                return submit_result
            
            print(f"[BountyAgent] [OK] Result submitted")
            
            # Trigger payment
            print(f"[BountyAgent] Triggering payment of ${amount_usdc} USDC...")
            payment_result = self.payment_handler.send_payment(
                amount_usdc=amount_usdc,
                recipient_address=self.payout_address,
                job_id=job_id
            )
            
            if payment_result["status"] == "initiated":
                print(f"[BountyAgent] [OK] Payment initiated")
                print(f"[BountyAgent] Transaction: {payment_result['txn_signature']}")
                
                # Track job completion
                self.jobs_processed += 1
                self.total_earned += amount_usdc
                self.completed_jobs.append({
                    "job_id": job_id,
                    "amount_usdc": amount_usdc,
                    "txn_signature": payment_result["txn_signature"],
                    "completed_at": datetime.utcnow().isoformat() + "Z"
                })
            
            return {
                "status": "completed",
                "job_id": job_id,
                "validation_score": validation_result["score"],
                "amount_earned_usdc": amount_usdc,
                "payment_txn": payment_result.get("txn_signature"),
                "message": f"Job completed and paid ${amount_usdc} USDC"
            }
        
        except Exception as e:
            print(f"[BountyAgent] [FAIL] Job processing error: {e}")
            return {
                "status": "error",
                "job_id": job_id,
                "message": str(e)
            }
    
    def _process_pending_jobs(self) -> None:
        """Process any jobs that haven't been processed yet."""
        unprocessed = [j for j in self.claimed_jobs.keys() 
                      if j not in [c["job_id"] for c in self.completed_jobs]]
        
        if not unprocessed:
            print("[BountyAgent] No pending jobs")
            return
        
        print(f"[BountyAgent] Found {len(unprocessed)} pending job(s)")
    
    def _confirm_pending_payments(self) -> None:
        """Confirm any pending payments."""
        pending_txns = [c["txn_signature"] for c in self.completed_jobs 
                       if self.payment_handler._find_payment(c["txn_signature"]) and 
                          self.payment_handler._find_payment(c["txn_signature"])["status"] == "pending"]
        
        if not pending_txns:
            return
        
        for txn_sig in pending_txns:
            print(f"[BountyAgent] Confirming payment {txn_sig}")
            self.payment_handler.confirm_payment(txn_sig)
    
    def _print_final_stats(self) -> None:
        """Print final statistics."""
        print("\n" + "="*60)
        print("[BountyAgent] Final Statistics")
        print("="*60)
        print(f"Agent ID: {self.agent_id}")
        print(f"Payout address: {self.payout_address}")
        print(f"Jobs claimed: {len(self.claimed_jobs)}")
        print(f"Jobs completed: {len(self.completed_jobs)}")
        print(f"Total earned: ${self.total_earned:.2f} USDC")
        if self.completed_jobs:
            avg_job = self.total_earned / len(self.completed_jobs)
            print(f"Average per job: ${avg_job:.2f} USDC")
        print("="*60 + "\n")
