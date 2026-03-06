"""
PayAClaw API Client - Integration with PayAClaw bounty system
Handles job fetching, claiming, and result submission.
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


class PayAClawClient:
    """Manages PayAClaw API interactions for bounty jobs."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://api.payaclaw.ai"):
        """
        Initialize PayAClaw client.
        
        Args:
            api_key: Optional API key for authentication
            api_url: PayAClaw API endpoint
        """
        self.api_key = api_key
        self.api_url = api_url
        self.session_id = self._generate_session_id()
        self.jobs_claimed = []
        self.results_submitted = []
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for this agent."""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def list_bounties(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        List available bounty jobs.
        
        Args:
            filters: Optional filters like {"job_type": "sift", "min_amount": 1.0}
        
        Returns:
            List of bounty job objects
        """
        # Mock implementation - would call actual API
        mock_jobs = [
            {
                "job_id": "molt_sift_001",
                "job_type": "sift",
                "title": "Validate crypto data",
                "description": "Validate price feed data against crypto schema",
                "raw_data": {
                    "symbol": "BTC",
                    "price": "invalid_price",
                    "volume": 1500000000,
                    "timestamp": "2026-02-25T12:00:00Z"
                },
                "schema": {
                    "type": "object",
                    "required": ["symbol", "price"],
                    "properties": {
                        "symbol": {"type": "string"},
                        "price": {"type": "number"},
                        "volume": {"type": "number"}
                    }
                },
                "validation_rules": "crypto",
                "amount_usdc": 5.0,
                "payout_address": "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7",
                "deadline": "2026-02-26T12:00:00Z",
                "created_at": "2026-02-25T12:00:00Z",
                "status": "open"
            },
            {
                "job_id": "molt_sift_002",
                "job_type": "sift",
                "title": "Validate trading order",
                "description": "Validate order execution logs",
                "raw_data": {
                    "order_id": "ord_987654",
                    "symbol": "ETH/USDT",
                    "side": "sell",
                    "price": 2450.00,
                    "quantity": 1.5
                },
                "validation_rules": "trading",
                "amount_usdc": 3.0,
                "payout_address": "7pf1C3qf6kWJ8DH5LqYw5mRzJqHVQR6xkfYpSEJvCsF7",
                "deadline": "2026-02-26T18:00:00Z",
                "created_at": "2026-02-25T11:30:00Z",
                "status": "open"
            }
        ]
        
        # Apply filters
        if filters:
            filtered = mock_jobs
            if "job_type" in filters:
                filtered = [j for j in filtered if j.get("job_type") == filters["job_type"]]
            if "min_amount" in filters:
                min_amount = float(filters["min_amount"])
                filtered = [j for j in filtered if j.get("amount_usdc", 0) >= min_amount]
            return filtered
        
        return mock_jobs
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch details for a specific job.
        
        Args:
            job_id: Job ID to fetch
        
        Returns:
            Job details or None if not found
        """
        jobs = self.list_bounties()
        for job in jobs:
            if job["job_id"] == job_id:
                return job
        return None
    
    def claim_job(self, job_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Claim a bounty job.
        
        Args:
            job_id: Job ID to claim
            agent_id: Identifier for claiming agent
        
        Returns:
            Claim confirmation with job details
        """
        job = self.get_job(job_id)
        if not job:
            return {
                "status": "error",
                "message": f"Job {job_id} not found"
            }
        
        if job["status"] != "open":
            return {
                "status": "error",
                "message": f"Job {job_id} is already claimed or closed"
            }
        
        # Record claim
        self.jobs_claimed.append({
            "job_id": job_id,
            "agent_id": agent_id,
            "claimed_at": datetime.utcnow().isoformat() + "Z",
            "session_id": self.session_id
        })
        
        return {
            "status": "claimed",
            "job_id": job_id,
            "job_type": job["job_type"],
            "title": job["title"],
            "raw_data": job["raw_data"],
            "schema": job.get("schema"),
            "validation_rules": job.get("validation_rules", "json-strict"),
            "amount_usdc": job["amount_usdc"],
            "payout_address": job["payout_address"],
            "message": f"Job claimed successfully. Process data and submit results."
        }
    
    def submit_result(self, job_id: str, validation_result: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """
        Submit validation result for a claimed job.
        
        Args:
            job_id: Job ID for the result
            validation_result: Result from Sifter.validate()
            agent_id: Identifier for the agent
        
        Returns:
            Submission confirmation with payment details
        """
        job = self.get_job(job_id)
        if not job:
            return {
                "status": "error",
                "message": f"Job {job_id} not found"
            }
        
        # Verify this agent claimed the job
        claimed = any(c["job_id"] == job_id and c["agent_id"] == agent_id 
                     for c in self.jobs_claimed)
        if not claimed:
            return {
                "status": "error",
                "message": f"Job {job_id} not claimed by agent {agent_id}"
            }
        
        # Record submission
        submission = {
            "job_id": job_id,
            "agent_id": agent_id,
            "validation_result": validation_result,
            "submitted_at": datetime.utcnow().isoformat() + "Z",
            "session_id": self.session_id
        }
        self.results_submitted.append(submission)
        
        return {
            "status": "submitted",
            "job_id": job_id,
            "message": "Result submitted successfully",
            "validation_score": validation_result.get("score"),
            "result_id": job_id + "_result_" + self.session_id,
            "ready_for_payment": True
        }
    
    def trigger_payment(self, job_id: str, agent_id: str, amount_usdc: float, 
                       payout_address: str) -> Dict[str, Any]:
        """
        Trigger payment for a completed job.
        
        Args:
            job_id: Job ID for payment
            agent_id: Agent to receive payment
            amount_usdc: Amount in USDC
            payout_address: Solana wallet address for payment
        
        Returns:
            Payment confirmation
        """
        # In real implementation, this would call x402 payment trigger
        return {
            "status": "payment_initiated",
            "job_id": job_id,
            "agent_id": agent_id,
            "amount_usdc": amount_usdc,
            "payout_address": payout_address,
            "message": "Payment queued for x402 processing",
            "expected_confirmation": "within 2 minutes"
        }
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get statistics for an agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent statistics
        """
        claimed_by_agent = [j for j in self.jobs_claimed if j["agent_id"] == agent_id]
        submitted_by_agent = [j for j in self.results_submitted if j["agent_id"] == agent_id]
        
        total_earned = sum(
            self.get_job(s["job_id"]).get("amount_usdc", 0)
            for s in submitted_by_agent
            if self.get_job(s["job_id"])
        )
        
        return {
            "agent_id": agent_id,
            "jobs_claimed": len(claimed_by_agent),
            "jobs_completed": len(submitted_by_agent),
            "total_earned_usdc": total_earned,
            "completion_rate": (len(submitted_by_agent) / len(claimed_by_agent) 
                               if claimed_by_agent else 0),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def is_healthy(self) -> bool:
        """Check API health."""
        # In real implementation, would ping API endpoint
        return True
    
    def get_session_id(self) -> str:
        """Get current session ID."""
        return self.session_id
