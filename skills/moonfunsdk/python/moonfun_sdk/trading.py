"""
Trading Client
Handles token buy/sell operations (preserved from pre_sdk)
"""
from web3 import Web3
from typing import Dict, Any
from .blockchain import BlockchainClient
from .constants import WBNB_ADDRESS, ERC20_ABI
from .exceptions import TransactionFailedError


class TradingClient:
    """
    Client for token trading operations
    
    Features:
        - Buy tokens with BNB
        - Sell tokens for BNB
        - Price queries
        - Slippage protection
    """
    
    def __init__(self, blockchain_client: BlockchainClient):
        """
        Initialize trading client
        
        Args:
            blockchain_client: Blockchain client instance
        """
        self.blockchain = blockchain_client
        self.w3 = blockchain_client.w3
        self.router = blockchain_client.router
        self.auth = blockchain_client.auth
    
    def get_amount_out(
        self,
        token_in: str,
        amount_in: int,
        token_out: str
    ) -> int:
        """
        Calculate expected output amount for a swap
        
        Args:
            token_in: Input token address (WBNB or token)
            amount_in: Input amount in wei
            token_out: Output token address
        
        Returns:
            Expected output amount in wei
        """
        return self.router.functions.getAmountOut(
            Web3.to_checksum_address(token_in),
            amount_in,
            Web3.to_checksum_address(token_out)
        ).call()
    
    def buy_token(
        self,
        token_address: str,
        bnb_amount: float,
        slippage: float = 0.1,
        source: int = 0
    ) -> Dict[str, Any]:
        """
        Buy tokens with BNB
        
        Args:
            token_address: Token contract address
            bnb_amount: Amount of BNB to spend
            slippage: Slippage tolerance (0.1 = 10%)
            source: Source identifier
        
        Returns:
            Dictionary containing:
                - success: True if transaction succeeded
                - tx_hash: Transaction hash
                - gas_used: Gas consumed
        
        Raises:
            TransactionFailedError: If transaction fails
        """
        try:
            # Convert BNB to wei
            amount_in_wei = self.w3.to_wei(bnb_amount, 'ether')
            
            # Get expected output (for new tokens with no liquidity, this may fail)
            try:
                expected_out = self.get_amount_out(
                    WBNB_ADDRESS,
                    amount_in_wei,
                    token_address
                )
                # Calculate minimum received with slippage
                min_received = int(expected_out * (1 - slippage))
            except Exception as e:
                # For new tokens (holders=0), getAmountOut fails
                # Fallback to min_received=0 to allow first purchase
                print(f"⚠️  getAmountOut failed (new token?): {e}")
                print(f"   Setting min_received=0 to allow first purchase")
                min_received = 0
            
            # Get nonce and gas price
            nonce = self.w3.eth.get_transaction_count(self.auth.address)
            gas_price = int(self.w3.eth.gas_price * 1.2)
            
            # Estimate gas dynamically
            try:
                gas_estimate = self.router.functions.buy(
                    Web3.to_checksum_address(token_address),
                    min_received,
                    source
                ).estimate_gas({
                    'from': self.auth.address,
                    'value': amount_in_wei
                })
                gas_limit = int(gas_estimate * 1.2)  # 20% buffer
            except Exception:
                # Fallback to default gas limit if estimation fails
                gas_limit = 300000
            
            # Build transaction
            tx = self.router.functions.buy(
                Web3.to_checksum_address(token_address),
                min_received,
                source
            ).build_transaction({
                'from': self.auth.address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'value': amount_in_wei,
                'chainId': self.w3.eth.chain_id
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(
                tx,
                self.auth.private_key
            )
            
            # Compatibility: support both old and new web3.py versions
            raw_tx = getattr(signed_tx, 'raw_transaction', None) or \
                     getattr(signed_tx, 'rawTransaction', None)
            if raw_tx is None:
                raise TransactionFailedError(
                    "Unable to get raw transaction from signed transaction"
                )
            
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] != 1:
                raise TransactionFailedError(
                    f"Buy transaction failed: {tx_hash.hex()}"
                )
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'gas_used': receipt['gasUsed']
            }
        
        except Exception as e:
            if isinstance(e, TransactionFailedError):
                raise
            raise TransactionFailedError(f"Buy failed: {str(e)}")
    
    def sell_token(
        self,
        token_address: str,
        amount: int,
        slippage: float = 0.1,
        source: int = 0
    ) -> Dict[str, Any]:
        """
        Sell tokens for BNB
        
        Args:
            token_address: Token contract address
            amount: Amount of tokens to sell (in wei)
            slippage: Slippage tolerance (0.1 = 10%)
            source: Source identifier
        
        Returns:
            Dictionary containing:
                - success: True if transaction succeeded
                - tx_hash: Transaction hash
                - gas_used: Gas consumed
        
        Raises:
            TransactionFailedError: If transaction fails
        """
        try:
            token_checksum = Web3.to_checksum_address(token_address)
            
            # Step 1: Approve router to spend tokens
            token_contract = self.w3.eth.contract(
                address=token_checksum,
                abi=ERC20_ABI
            )
            
            nonce = self.w3.eth.get_transaction_count(self.auth.address)
            
            approve_tx = token_contract.functions.approve(
                Web3.to_checksum_address(self.router.address),
                amount
            ).build_transaction({
                'from': self.auth.address,
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': int(self.w3.eth.gas_price * 1.2),
                'chainId': self.w3.eth.chain_id
            })
            
            signed = self.w3.eth.account.sign_transaction(
                approve_tx,
                self.auth.private_key
            )
            
            # Compatibility: support both old and new web3.py versions
            raw_approve = getattr(signed, 'raw_transaction', None) or \
                          getattr(signed, 'rawTransaction', None)
            if raw_approve is None:
                raise TransactionFailedError(
                    "Unable to get raw transaction from signed approve transaction"
                )
            
            # Send approve transaction and wait for confirmation
            approve_hash = self.w3.eth.send_raw_transaction(raw_approve)
            approve_receipt = self.w3.eth.wait_for_transaction_receipt(approve_hash, timeout=60)
            
            if approve_receipt['status'] != 1:
                raise TransactionFailedError(
                    f"Approve transaction failed: {approve_hash.hex()}"
                )
            
            # Step 2: Get expected output (may fail for new tokens)
            try:
                expected_out = self.get_amount_out(
                    token_checksum,
                    amount,
                    WBNB_ADDRESS
                )
                min_received = int(expected_out * (1 - slippage))
            except Exception as e:
                # For tokens with low liquidity, getAmountOut may fail
                # Fallback to min_received=0 to allow selling
                print(f"⚠️  getAmountOut failed (low liquidity?): {e}")
                print(f"   Setting min_received=0 to allow sell")
                min_received = 0
            
            # Step 3: Sell tokens
            nonce = self.w3.eth.get_transaction_count(self.auth.address)
            
            # Estimate gas dynamically
            try:
                gas_estimate = self.router.functions.sell(
                    token_checksum,
                    amount,
                    min_received,
                    source
                ).estimate_gas({'from': self.auth.address})
                gas_limit = int(gas_estimate * 1.2)  # 20% buffer
            except Exception:
                # Fallback to default gas limit if estimation fails
                gas_limit = 300000
            
            tx = self.router.functions.sell(
                token_checksum,
                amount,
                min_received,
                source
            ).build_transaction({
                'from': self.auth.address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': int(self.w3.eth.gas_price * 1.2),
                'chainId': self.w3.eth.chain_id
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(
                tx,
                self.auth.private_key
            )
            
            # Compatibility: support both old and new web3.py versions
            raw_tx = getattr(signed_tx, 'raw_transaction', None) or \
                     getattr(signed_tx, 'rawTransaction', None)
            if raw_tx is None:
                raise TransactionFailedError(
                    "Unable to get raw transaction from signed transaction"
                )
            
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] != 1:
                raise TransactionFailedError(
                    f"Sell transaction failed: {tx_hash.hex()}"
                )
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'gas_used': receipt['gasUsed']
            }
        
        except Exception as e:
            if isinstance(e, TransactionFailedError):
                raise
            raise TransactionFailedError(f"Sell failed: {str(e)}")
