#!/usr/bin/env python3
"""
BlindOracle OpenClaw Skill Handler (Brand A: Privacy-First)

Sanitized terminology wrapper around the core BlindOracle capability handlers.
Maps Brand A capability names to internal Brand B handlers via a translation
layer. All external-facing language uses privacy/fintech vocabulary -- no
cryptocurrency-specific terms (BTC, sats, Lightning, etc.).

Routes incoming OpenClaw Gateway requests through:
  1. Brand A -> Brand B capability name translation
  2. Brand A -> Brand B parameter name translation
  3. Core handler execution (shared with Brand B)
  4. Brand B -> Brand A response translation

Uses the /v2 API routes on the x402 gateway.

@author: Craig M. Brown
@version: 1.0.0
@date: 2026-03-01

Copyright (c) 2025 Craig M. Brown. All rights reserved.
"""

import sys
import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Add parent directories to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from security.blindoracle_security_gateway import (
    BlindOracleSecurityGateway,
    SecurityConfig,
    SecurityRequest,
    SecurityLevel,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("blindoracle.openclaw_skill_brand_a")


# ============================================================================
# BRAND A <-> BRAND B TRANSLATION MAPS
# ============================================================================

# Brand A (sanitized) -> Brand B (internal) capability mapping
CAPABILITY_MAP_A_TO_B = {
    # Forecasting (Brand A) -> Prediction Markets (Brand B)
    "create_forecast": "create_market",
    "submit_position": "place_prediction",
    "resolve_forecast": "settle_market",
    # Credentials (Brand A) -> Identity (Brand B)
    "verify_credential": "verify_identity",
    "mint_credential": "mint_badge",
    # Account (Brand A) -> Payments (Brand B)
    "check_account": "check_balance",
    "create_settlement_request": "create_invoice",
    # Transfers (Brand A) -> Swaps (Brand B)
    "transfer_cross_rail": "swap_btc_eth",
    "convert_private_to_stable": "swap_ecash_usdc",
    "get_transfer_quote": "get_quote",
    # Settlement (Brand A) -> Withdrawals (Brand B)
    "settle_instant": "withdraw_lightning",
    "settle_onchain": "withdraw_ethereum",
}

# Reverse map for response translation
CAPABILITY_MAP_B_TO_A = {v: k for k, v in CAPABILITY_MAP_A_TO_B.items()}

# Parameter name translations (Brand A -> Brand B)
PARAM_MAP_A_TO_B = {
    # Forecasting parameters
    "forecast_question": "question",
    "forecast_deadline": "deadline",
    "initial_stake_units": "initial_liquidity_sats",
    "forecast_id": "market_id",
    "stance": "position",
    "stake_units": "amount_sats",
    "outcome_evidence_url": "evidence_url",
    "resolution_oracle": "resolution_source",
    # Credential parameters
    "agent_public_key": "agent_pubkey",
    "credential_type": "proof_type",
    "credential_metadata": "metadata",
    "attestors": "witnesses",
    "attestor_signatures": "witness_signatures",
    # Transfer parameters
    "transfer_units": "amount_sats",
    "destination": "destination_address",
    "receiving_address": "eth_address",
    "settlement_invoice": "bolt11_invoice",
    "target_address": "base_address",
    "asset_pair": "pair",
    "transfer_amount": "amount",
    # Account parameters
    "account_rail": "rail",
    "request_units": "amount_sats",
    "request_description": "description",
    "expiry": "expiry_seconds",
}

# Response field translations (Brand B -> Brand A)
RESPONSE_MAP_B_TO_A = {
    "market_id": "forecast_id",
    "prediction_id": "position_id",
    "amount_sats": "stake_units",
    "initial_liquidity_sats": "initial_stake_units",
    "agent_pubkey": "agent_public_key",
    "proof_types": "credential_types",
    "bolt11_invoice": "settlement_invoice",
    "swap_id": "transfer_id",
    "fee_amount": "transfer_fee",
}

# Terms to scrub from any string values in responses
SCRUB_TERMS = {
    "Bitcoin": "digital value",
    "bitcoin": "digital value",
    "BTC": "DV",
    "btc": "dv",
    "Ethereum": "settlement network",
    "ethereum": "settlement network",
    "ETH": "SN",
    "Lightning": "instant rail",
    "lightning": "instant rail",
    "Lightning Network": "instant settlement rail",
    "sats": "units",
    "satoshi": "unit",
    "satoshis": "units",
    "cryptocurrency": "digital asset",
    "crypto": "digital",
    "blockchain": "distributed ledger",
    "mining": "validation",
    "miner": "validator",
    "wallet": "account",
    "token": "credential",
    "prediction market": "forecast platform",
    "prediction": "forecast position",
}


# ============================================================================
# PRICING CONFIGURATION (Brand A terminology)
# ============================================================================

CAPABILITY_PRICING = {
    "create_forecast": {"base_fee": 0.001, "currency": "USDC"},
    "submit_position": {"base_fee": 0.0005, "percentage": 0.001, "currency": "USDC"},
    "resolve_forecast": {"base_fee": 0.002, "currency": "USDC"},
    "verify_credential": {"base_fee": 0.0002, "currency": "USDC"},
    "mint_credential": {"base_fee": 0.001, "currency": "USDC"},
    "check_account": {"base_fee": 0.0, "currency": "USDC"},
    "create_settlement_request": {"base_fee": 0.0001, "currency": "USDC"},
    "transfer_cross_rail": {"base_fee": 0.001, "percentage": 0.001, "currency": "USDC"},
    "convert_private_to_stable": {"base_fee": 0.0005, "percentage": 0.0005, "currency": "USDC"},
    "get_transfer_quote": {"base_fee": 0.0, "currency": "USDC"},
    "settle_instant": {"base_fee": 0.0005, "percentage": 0.001, "currency": "USDC"},
    "settle_onchain": {"base_fee": 0.001, "percentage": 0.0005, "currency": "USDC"},
}


# ============================================================================
# TRANSLATION HELPERS
# ============================================================================

def _translate_params_a_to_b(params: Dict[str, Any]) -> Dict[str, Any]:
    """Translate Brand A parameter names to Brand B."""
    translated = {}
    for key, value in params.items():
        brand_b_key = PARAM_MAP_A_TO_B.get(key, key)
        translated[brand_b_key] = value
    return translated


def _translate_response_b_to_a(response: Dict[str, Any]) -> Dict[str, Any]:
    """Translate Brand B response fields to Brand A and scrub crypto terms."""
    if not isinstance(response, dict):
        return response

    translated = {}
    for key, value in response.items():
        # Translate key name
        new_key = RESPONSE_MAP_B_TO_A.get(key, key)

        # Recursively translate nested dicts
        if isinstance(value, dict):
            translated[new_key] = _translate_response_b_to_a(value)
        elif isinstance(value, list):
            translated[new_key] = [
                _translate_response_b_to_a(item) if isinstance(item, dict)
                else _scrub_string(item) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, str):
            translated[new_key] = _scrub_string(value)
        else:
            translated[new_key] = value

    return translated


def _scrub_string(text: str) -> str:
    """Remove cryptocurrency-specific terms from a string."""
    result = text
    for crypto_term, sanitized_term in SCRUB_TERMS.items():
        result = result.replace(crypto_term, sanitized_term)
    return result


# ============================================================================
# ERROR RESPONSE HELPERS
# ============================================================================

def error_response(code: int, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": _scrub_string(message),
        }
    }
    if details:
        response["error"]["details"] = _translate_response_b_to_a(details)
    return response


def payment_required_response(amount: str, currency: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a 402 Payment Required response."""
    response = {
        "success": False,
        "error": {
            "code": 402,
            "message": "Payment Required",
            "payment": {
                "amount": amount,
                "currency": currency,
            }
        }
    }
    if details:
        # Translate capability name back to Brand A
        if "capability" in details:
            details["capability"] = CAPABILITY_MAP_B_TO_A.get(
                details["capability"], details["capability"]
            )
        response["error"]["payment"].update(details)
    return response


# ============================================================================
# MAIN SKILL HANDLER (Brand A Wrapper)
# ============================================================================

class BlindOracleSkillHandler:
    """
    Brand A handler for BlindOracle OpenClaw skill requests.

    Wraps the core Brand B handlers with terminology translation.
    All external-facing strings are sanitized to remove cryptocurrency
    references for platform compliance.
    """

    def __init__(self, enable_security: bool = True):
        self.enable_security = enable_security
        self.security_gateway = (
            BlindOracleSecurityGateway(SecurityConfig())
            if enable_security else None
        )

        # Import Brand B handlers
        try:
            from distribution.clawhub_skill.handler import CapabilityHandlers
            self.capability_handlers = CapabilityHandlers()
        except ImportError:
            # Fallback: try relative import
            try:
                parent = Path(__file__).parent.parent / "clawhub_skill"
                sys.path.insert(0, str(parent))
                from handler import CapabilityHandlers
                self.capability_handlers = CapabilityHandlers()
            except ImportError:
                logger.warning("Brand B handlers not available, using stub mode")
                self.capability_handlers = None

        logger.info(
            "BlindOracle OpenClaw Skill (Brand A) initialized (security=%s)",
            enable_security,
        )

    def _route_capability(self, brand_a_capability: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Route Brand A capability to Brand B handler with translation."""
        # Translate capability name
        brand_b_capability = CAPABILITY_MAP_A_TO_B.get(brand_a_capability)
        if brand_b_capability is None:
            return error_response(404, f"Unknown capability: {brand_a_capability}")

        # Translate parameters
        brand_b_params = _translate_params_a_to_b(params)

        # Route to Brand B handler
        if self.capability_handlers is None:
            return error_response(503, "Service temporarily unavailable")

        handler_map = {
            "create_market": self.capability_handlers.create_market,
            "place_prediction": self.capability_handlers.place_prediction,
            "settle_market": self.capability_handlers.settle_market,
            "verify_identity": self.capability_handlers.verify_identity,
            "mint_badge": self.capability_handlers.mint_badge,
            "check_balance": self.capability_handlers.check_balance,
            "create_invoice": self.capability_handlers.create_invoice,
            "swap_btc_eth": self.capability_handlers.swap_btc_eth,
            "swap_ecash_usdc": self.capability_handlers.swap_ecash_usdc,
            "get_quote": self.capability_handlers.get_quote,
            "withdraw_lightning": self.capability_handlers.withdraw_lightning,
            "withdraw_ethereum": self.capability_handlers.withdraw_ethereum,
        }

        handler = handler_map.get(brand_b_capability)
        if handler is None:
            return error_response(404, f"Handler not found for: {brand_a_capability}")

        try:
            brand_b_response = handler(brand_b_params)
            # Translate response back to Brand A
            return _translate_response_b_to_a(brand_b_response)
        except Exception as e:
            logger.error(f"Handler error for {brand_a_capability}: {e}", exc_info=True)
            return error_response(500, f"Internal error: {str(e)}")

    def _calculate_payment(self, capability: str, params: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Calculate payment required for capability."""
        pricing = CAPABILITY_PRICING.get(capability, {"base_fee": 0.0, "currency": "USDC"})

        base_fee = pricing["base_fee"]
        currency = pricing["currency"]

        if "percentage" in pricing:
            # Check both Brand A and B param names for amount
            amount = params.get("stake_units", params.get("transfer_units",
                     params.get("request_units", params.get("amount_sats", 0))))
            percentage_fee = amount * pricing["percentage"]
            total = base_fee + percentage_fee
        else:
            total = base_fee

        details = {
            "capability": capability,
            "base_fee": base_fee,
        }
        if "percentage" in pricing:
            details["percentage_fee"] = pricing["percentage"]

        return f"{total:.6f}", currency, details

    def _wrap_security(self, request: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Wrap request in CaMel security gateway."""
        if not self.enable_security or self.security_gateway is None:
            return True, None, None

        try:
            capability = request.get("capability", "")
            agent_id = request.get("agent_id", "unknown")
            params = request.get("params", {})

            # Map Brand A critical ops
            critical_ops = {
                "resolve_forecast", "mint_credential",
                "settle_instant", "settle_onchain",
            }
            security_level = (
                SecurityLevel.CRITICAL if capability in critical_ops
                else SecurityLevel.MEDIUM
            )

            brand_b_capability = CAPABILITY_MAP_A_TO_B.get(capability, capability)
            security_request = SecurityRequest(
                interface="openclaw_skill_brand_a",
                operation=brand_b_capability,
                agent_id=agent_id,
                parameters=_translate_params_a_to_b(params),
                amount_sats=params.get("stake_units", params.get("transfer_units", 0)),
                security_level=security_level,
                metadata={"request_id": request.get("id", "unknown"), "brand": "A"},
            )

            response = self.security_gateway.process_request(security_request)
            if response.approved:
                return True, None, response.to_dict()
            else:
                return False, response.denial_reason, response.to_dict()

        except Exception as e:
            logger.error(f"Security gateway error: {e}", exc_info=True)
            return False, f"Security error: {str(e)}", None

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for OpenClaw Gateway requests (Brand A).

        Args:
            request: JSON-RPC style request with Brand A capability names:
                {
                    "id": "request-id",
                    "capability": "create_forecast",
                    "params": {...},
                    "agent_id": "agent-identifier",
                    "payment_proof": {...} (optional)
                }

        Returns:
            Response with sanitized terminology (no crypto/BTC/sats language).
        """
        try:
            if not isinstance(request, dict):
                return error_response(400, "Invalid request format: expected JSON object")

            if "capability" not in request:
                return error_response(400, "Missing required field: capability")

            capability = request["capability"]
            params = request.get("params", {})
            agent_id = request.get("agent_id", "unknown")

            logger.info(f"[Brand A] Processing: capability={capability}, agent={agent_id}")

            # Validate capability exists
            if capability not in CAPABILITY_MAP_A_TO_B:
                return error_response(404, f"Unknown capability: {capability}")

            # Check if payment is required
            pricing = CAPABILITY_PRICING.get(capability, {"base_fee": 0.0})
            if pricing["base_fee"] > 0 and "payment_proof" not in request:
                amount, currency, details = self._calculate_payment(capability, params)
                logger.info(f"[Brand A] Payment required: {amount} {currency}")
                return payment_required_response(amount, currency, details)

            # Security gateway
            approved, denial_reason, security_details = self._wrap_security(request)
            if not approved:
                logger.warning(f"[Brand A] Security denied: {denial_reason}")
                return error_response(403, f"Security check failed: {denial_reason}")

            # Route to handler with translation
            result = self._route_capability(capability, params)

            if security_details:
                result["security"] = _translate_response_b_to_a(security_details)

            return result

        except Exception as e:
            logger.error(f"[Brand A] Request error: {e}", exc_info=True)
            return error_response(500, f"Internal error: {str(e)}")


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def handle_request(request: Dict[str, Any], enable_security: bool = True) -> Dict[str, Any]:
    """Convenience function for handling Brand A requests."""
    handler = BlindOracleSkillHandler(enable_security=enable_security)
    return handler.handle_request(request)


# ============================================================================
# CLI MODE (for testing)
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BlindOracle OpenClaw Skill (Brand A)")
    parser.add_argument("--test", action="store_true", help="Run test request")
    parser.add_argument("--no-security", action="store_true", help="Disable security")

    args = parser.parse_args()

    if args.test:
        test_request = {
            "id": "test-brand-a-001",
            "capability": "check_account",
            "params": {"account_rail": "all"},
            "agent_id": "test-agent",
        }

        print("BlindOracle OpenClaw Skill (Brand A) - Test")
        print(f"Request: {json.dumps(test_request, indent=2)}")
        print()

        response = handle_request(test_request, enable_security=not args.no_security)
        print(f"Response: {json.dumps(response, indent=2)}")
    else:
        print("BlindOracle OpenClaw Skill (Brand A: Privacy-First)")
        print("Use --test to run a test request")
