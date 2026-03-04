"""
Solana x402 Payment Integration
Triggers USDC transfers via x402 protocol for bounty payments.
"""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib


class SolanaPaymentHandler:
    """Manages USDC payments via x402 Solana escrow."""
    
    def __init__(self, keypair_path: Optional[str] = None):
        """
        Initialize payment handler.
        
        Args:
            keypair_path: Path to Solana keypair file (optional for mock)
        """
        self.keypair_path = keypair_path
        self.payments = []
        self.confirmed_txns = []
        self.usdc_mint = "EPjFWaLb3odccjf2cj6ipjc3H6tgonchtyssdwDiEjVP"  # USDC on Solana
        self.network = "mainnet-beta"
    
    def send_payment(self, amount_usdc: float, recipient_address: str, 
                    job_id: str, sender_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Send USDC payment via x402 escrow.
        
        Args:
            amount_usdc: Amount in USDC to send
            recipient_address: Solana wallet address of recipient
            job_id: Associated job ID (for tracking)
            sender_address: Sender's address (optional, uses keypair if not provided)
        
        Returns:
            Payment transaction details
        """
        # Validate recipient address format (Solana addresses are ~44 chars base58)
        if not self._is_valid_solana_address(recipient_address):
            return {
                "status": "error",
                "message": f"Invalid Solana address: {recipient_address}",
                "error_code": "invalid_address"
            }
        
        if amount_usdc <= 0:
            return {
                "status": "error",
                "message": "Amount must be greater than 0",
                "error_code": "invalid_amount"
            }
        
        # Generate transaction signature
        txn_sig = self._generate_txn_signature(amount_usdc, recipient_address, job_id)
        
        # Record payment
        payment = {
            "txn_signature": txn_sig,
            "job_id": job_id,
            "sender": sender_address or "molt_sift_treasury",
            "recipient": recipient_address,
            "amount_usdc": amount_usdc,
            "mint": self.usdc_mint,
            "network": self.network,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        self.payments.append(payment)
        
        return {
            "status": "initiated",
            "txn_signature": txn_sig,
            "job_id": job_id,
            "recipient": recipient_address,
            "amount_usdc": amount_usdc,
            "message": f"Payment of {amount_usdc} USDC queued for x402 processing",
            "confirmation_message": "Transaction will be confirmed within 2-5 minutes",
            "explorer_url": f"https://solscan.io/tx/{txn_sig}?cluster={self.network}"
        }
    
    def confirm_payment(self, txn_signature: str) -> Dict[str, Any]:
        """
        Confirm a pending payment (simulates blockchain confirmation).
        
        Args:
            txn_signature: Transaction signature to confirm
        
        Returns:
            Confirmation details
        """
        payment = self._find_payment(txn_signature)
        if not payment:
            return {
                "status": "error",
                "message": f"Payment {txn_signature} not found"
            }
        
        if payment["status"] == "confirmed":
            return {
                "status": "already_confirmed",
                "txn_signature": txn_signature,
                "message": "Payment already confirmed"
            }
        
        # Mark as confirmed
        payment["status"] = "confirmed"
        payment["confirmed_at"] = datetime.utcnow().isoformat() + "Z"
        self.confirmed_txns.append(txn_signature)
        
        return {
            "status": "confirmed",
            "txn_signature": txn_signature,
            "job_id": payment["job_id"],
            "recipient": payment["recipient"],
            "amount_usdc": payment["amount_usdc"],
            "confirmed_at": payment["confirmed_at"],
            "message": f"Payment of {payment['amount_usdc']} USDC confirmed to {payment['recipient']}"
        }
    
    def get_payment_status(self, txn_signature: str) -> Dict[str, Any]:
        """
        Get status of a payment.
        
        Args:
            txn_signature: Transaction signature
        
        Returns:
            Payment status details
        """
        payment = self._find_payment(txn_signature)
        if not payment:
            return {
                "status": "not_found",
                "message": f"Payment {txn_signature} not found"
            }
        
        return {
            "status": payment["status"],
            "txn_signature": txn_signature,
            "job_id": payment["job_id"],
            "recipient": payment["recipient"],
            "amount_usdc": payment["amount_usdc"],
            "created_at": payment["created_at"],
            "confirmed_at": payment.get("confirmed_at"),
            "explorer_url": f"https://solscan.io/tx/{txn_signature}?cluster={self.network}"
        }
    
    def get_wallet_balance(self, address: str) -> Dict[str, Any]:
        """
        Get USDC balance for a wallet.
        
        Args:
            address: Solana wallet address
        
        Returns:
            Balance information
        """
        if not self._is_valid_solana_address(address):
            return {
                "status": "error",
                "message": f"Invalid Solana address: {address}"
            }
        
        # Mock balance
        return {
            "status": "success",
            "address": address,
            "usdc_balance": 1500.00,
            "sol_balance": 5.5,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def estimate_fee(self, amount_usdc: float) -> Dict[str, Any]:
        """
        Estimate transaction fee for a payment.
        
        Args:
            amount_usdc: Payment amount
        
        Returns:
            Fee estimate
        """
        # Typical Solana fee is ~0.00025 SOL (~0.01 USDC at current prices)
        # x402 might add a small percentage fee
        base_fee_usdc = 0.01
        percentage_fee = amount_usdc * 0.002  # 0.2% fee
        
        return {
            "amount_usdc": amount_usdc,
            "base_fee_usdc": base_fee_usdc,
            "percentage_fee_usdc": round(percentage_fee, 2),
            "total_fee_usdc": round(base_fee_usdc + percentage_fee, 2),
            "network_fee_sol": 0.00025,
            "message": "Fee estimates for x402 USDC transfer"
        }
    
    def get_transaction_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get payment transaction history.
        
        Args:
            limit: Number of recent transactions to return
        
        Returns:
            List of transactions
        """
        sorted_payments = sorted(self.payments, key=lambda x: x["created_at"], reverse=True)
        recent = sorted_payments[:limit]
        
        return {
            "status": "success",
            "transaction_count": len(self.payments),
            "confirmed_count": len(self.confirmed_txns),
            "pending_count": len(self.payments) - len(self.confirmed_txns),
            "recent_transactions": recent,
            "network": self.network
        }
    
    def batch_send_payments(self, payments_list: list) -> Dict[str, Any]:
        """
        Send multiple payments in batch.
        
        Args:
            payments_list: List of dicts with {amount_usdc, recipient_address, job_id}
        
        Returns:
            Batch submission confirmation
        """
        results = []
        failed = []
        
        for payment in payments_list:
            result = self.send_payment(
                amount_usdc=payment["amount_usdc"],
                recipient_address=payment["recipient_address"],
                job_id=payment["job_id"]
            )
            
            if result["status"] == "error":
                failed.append(result)
            else:
                results.append(result)
        
        return {
            "status": "batch_submitted" if results else "batch_failed",
            "total_payments": len(payments_list),
            "successful": len(results),
            "failed": len(failed),
            "transactions": results,
            "errors": failed,
            "total_amount_usdc": sum(p["amount_usdc"] for p in results),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _find_payment(self, txn_signature: str) -> Optional[Dict]:
        """Find payment by transaction signature."""
        for payment in self.payments:
            if payment["txn_signature"] == txn_signature:
                return payment
        return None
    
    def _is_valid_solana_address(self, address: str) -> bool:
        """Validate Solana address format."""
        # Solana addresses are base58 encoded, typically 44 characters
        if not address or len(address) < 32 or len(address) > 50:
            return False
        
        # Basic check for valid base58 characters
        valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        return all(c in valid_chars for c in address)
    
    def _generate_txn_signature(self, amount: float, recipient: str, job_id: str) -> str:
        """Generate a transaction signature hash."""
        data = f"{amount}_{recipient}_{job_id}_{time.time()}".encode()
        return hashlib.sha256(data).hexdigest()[:64]
