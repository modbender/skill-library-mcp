"""
MoonfunSDK - Unified SDK for Meme Platform

A secure, production-ready SDK for creating and trading Meme tokens on BSC.

Features:
    - One-click Meme creation with AI-generated images
    - Triple-lock security (Signature + Timestamp + Balance)
    - Token trading (buy/sell)
    - Comprehensive error handling

Example:
    >>> from moonfun_sdk import MoonfunSDK
    >>> sdk = MoonfunSDK(
    ...     private_key="0x...",
    ...     image_api_url="https://api.example.com"
    ... )
    >>> result = sdk.create_meme("A funny cat")
    >>> print(result['token_address'])

Security:
    - All API requests are cryptographically signed
    - Timestamp-bound to prevent replay attacks
    - Balance-gated to prevent Sybil attacks
    - Private keys never leave the SDK

Author: Meme Platform Team
Version: 1.0.6
License: MIT
"""

from .client import MoonfunSDK
from .constants import (
    ROUTER_ADDRESS,
    WBNB_ADDRESS,
    CHAIN_ID,
    CREATE_FEE_BNB,
    PLATFORM_BASE_URL,
    DEFAULT_CHAIN,
    DEFAULT_RPC_URL
)
from .exceptions import (
    MoonfunSDKError,
    AuthenticationError,
    InvalidSignatureError,
    ExpiredTimestampError,
    InsufficientBalanceError,
    RateLimitError,
    NetworkError,
    RPCConnectionError,
    APIConnectionError,
    PlatformError,
    LoginError,
    UploadError,
    MetadataCreationError,
    BlockchainError,
    TransactionFailedError,
    InsufficientGasError,
    ContractError
)

__version__ = "1.0.6"
__author__ = "Meme Platform Team"
__all__ = [
    "MoonfunSDK",
    "ROUTER_ADDRESS",
    "WBNB_ADDRESS",
    "CHAIN_ID",
    "CREATE_FEE_BNB",
    "PLATFORM_BASE_URL",
    "DEFAULT_CHAIN",
    "DEFAULT_RPC_URL",
    "MoonfunSDKError",
    "AuthenticationError",
    "InvalidSignatureError",
    "ExpiredTimestampError",
    "InsufficientBalanceError",
    "RateLimitError",
    "NetworkError",
    "RPCConnectionError",
    "APIConnectionError",
    "PlatformError",
    "LoginError",
    "UploadError",
    "MetadataCreationError",
    "BlockchainError",
    "TransactionFailedError",
    "InsufficientGasError",
    "ContractError",
]
