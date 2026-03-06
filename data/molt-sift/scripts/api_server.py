"""
API Server - HTTP bounty endpoint for external agents
Provides REST API for posting and processing bounties.
"""

import json
import sys
from typing import Dict, Any, Tuple
from datetime import datetime

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("[APIServer] Error: Flask not installed. Run: pip install flask")
    sys.exit(1)

try:
    from sifter import Sifter
    from solana_payment import SolanaPaymentHandler
    from payaclaw_client import PayAClawClient
except ImportError:
    print("[APIServer] Error: Missing required modules")
    sys.exit(1)


class BountyAPIServer:
    """REST API server for bounty operations."""
    
    def __init__(self, port: int = 8000):
        """
        Initialize API server.
        
        Args:
            port: Port to run server on
        """
        self.port = port
        self.app = Flask(__name__)
        self.payment_handler = SolanaPaymentHandler()
        self.payaclaw_client = PayAClawClient()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        
        @self.app.route('/bounty', methods=['POST'])
        def post_bounty():
            """
            POST /bounty - Submit validation bounty
            
            Payload:
            {
                "raw_data": {...},
                "schema": {...},
                "validation_rules": "crypto",
                "amount_usdc": 5.00,
                "payout_address": "SOLANA_ADDR"
            }
            
            Response:
            {
                "status": "validated",
                "score": 0.87,
                "clean_data": {...},
                "issues": [...],
                "payment_txn": "..."
            }
            """
            return self._handle_bounty_request()
        
        @self.app.route('/bounty/<job_id>', methods=['GET'])
        def get_bounty_status(job_id: str):
            """Get bounty job status."""
            job = self.payaclaw_client.get_job(job_id)
            if not job:
                return jsonify({
                    "status": "error",
                    "message": f"Job {job_id} not found"
                }), 404
            
            return jsonify({
                "status": "success",
                "job": job
            })
        
        @self.app.route('/payment/<txn_signature>', methods=['GET'])
        def get_payment_status(txn_signature: str):
            """Get payment status."""
            status = self.payment_handler.get_payment_status(txn_signature)
            return jsonify(status)
        
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Get API statistics."""
            return jsonify({
                "status": "success",
                "total_bounties": len(self.payaclaw_client.list_bounties()),
                "total_payments": len(self.payment_handler.payments),
                "confirmed_payments": len(self.payment_handler.confirmed_txns),
                "total_volume_usdc": sum(p["amount_usdc"] for p in self.payment_handler.payments),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    
    def _handle_bounty_request(self) -> Tuple[Dict[str, Any], int]:
        """Handle POST /bounty request."""
        try:
            # Parse request
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Request body must be JSON"
                }), 400
            
            # Validate required fields
            required = ["raw_data", "amount_usdc", "payout_address"]
            missing = [f for f in required if f not in data]
            
            if missing:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing)}"
                }), 400
            
            raw_data = data["raw_data"]
            schema = data.get("schema")
            rules = data.get("validation_rules", "json-strict")
            amount_usdc = data["amount_usdc"]
            payout_address = data["payout_address"]
            
            # Validate amount
            if not isinstance(amount_usdc, (int, float)) or amount_usdc <= 0:
                return jsonify({
                    "status": "error",
                    "message": "amount_usdc must be a positive number"
                }), 400
            
            # Validate address
            if not self.payment_handler._is_valid_solana_address(payout_address):
                return jsonify({
                    "status": "error",
                    "message": f"Invalid Solana address: {payout_address}"
                }), 400
            
            # Run validation
            print(f"[APIServer] Processing bounty: {rules} validation for ${amount_usdc} USDC")
            sifter = Sifter(rules=rules)
            validation_result = sifter.validate(raw_data, schema)
            
            # Trigger payment
            payment_result = self.payment_handler.send_payment(
                amount_usdc=amount_usdc,
                recipient_address=payout_address,
                job_id=f"bounty_{int(datetime.utcnow().timestamp())}"
            )
            
            # Return result
            return jsonify({
                "status": "validated",
                "validation_score": validation_result["score"],
                "clean_data": validation_result["clean_data"],
                "issues": validation_result["issues"],
                "payment_status": payment_result["status"],
                "payment_txn": payment_result.get("txn_signature"),
                "amount_paid_usdc": amount_usdc,
                "explorer_url": payment_result.get("explorer_url"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }), 200
        
        except Exception as e:
            print(f"[APIServer] Error processing bounty: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    def run(self, debug: bool = False) -> None:
        """
        Start the API server.
        
        Args:
            debug: Enable Flask debug mode
        """
        print(f"[APIServer] [SIFT] Starting Molt Sift API Server")
        print(f"[APIServer] Listening on http://0.0.0.0:{self.port}")
        print(f"[APIServer] Endpoints:")
        print(f"  - GET  /health              (health check)")
        print(f"  - POST /bounty              (submit validation bounty)")
        print(f"  - GET  /bounty/<job_id>     (get job status)")
        print(f"  - GET  /payment/<txn_sig>   (get payment status)")
        print(f"  - GET  /stats               (API statistics)")
        print(f"[APIServer] Ready to process bounties!\n")
        
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)


def start_api_server(port: int = 8000, debug: bool = False) -> None:
    """
    Start HTTP API server with /bounty endpoint.
    
    Args:
        port: Port to run server on
        debug: Enable debug mode
    """
    server = BountyAPIServer(port=port)
    server.run(debug=debug)
