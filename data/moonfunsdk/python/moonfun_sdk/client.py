"""
MoonfunSDK Main Client
Unified interface for Meme creation and trading
"""
from typing import Dict, Any, Optional
from .auth import AuthManager
from .image_api import ImageAPIClient
from .platform import PlatformClient
from .blockchain import BlockchainClient
from .trading import TradingClient
from .constants import DEFAULT_RPC_URL, PLATFORM_BASE_URL, DEFAULT_CHAIN


class MoonfunSDK:
    """
    Unified SDK for Meme Platform
    
    Features:
        - One-click Meme creation with create_meme()
        - Token trading (buy/sell)
        - Balance queries
        - Triple-lock security for image generation
    
    Example:
        >>> sdk = MoonfunSDK(
        ...     private_key="0x...",
        ...     image_api_url="https://api.example.com"
        ... )
        >>> result = sdk.create_meme("A funny cat")
        >>> print(result['token_address'])
    """
    
    def __init__(
        self,
        private_key: str,
        image_api_url: str = "http://moonfun.site",
        platform_url: str = PLATFORM_BASE_URL,
        chain: str = DEFAULT_CHAIN,
        rpc_url: str = DEFAULT_RPC_URL
    ):
        """
        Initialize MoonfunSDK
        
        Args:
            private_key: Ethereum private key (with or without 0x prefix)
            image_api_url: URL of secured image generation API (default: internal server)
            platform_url: MoonnFun platform URL (default: https://moonn.fun)
            chain: Blockchain name (default: "bsc")
            rpc_url: BSC RPC endpoint (default: public BSC RPC)
        
        Raises:
            ValueError: If private key is invalid
            RPCConnectionError: If unable to connect to RPC
        """
        # Initialize authentication
        self.auth = AuthManager(private_key)
        
        # Initialize components
        self.image_api = ImageAPIClient(image_api_url, self.auth)
        self.platform = PlatformClient(platform_url, chain, self.auth)
        self.blockchain = BlockchainClient(rpc_url, self.auth)
        self.trading = TradingClient(self.blockchain)
        
        # Public properties
        self.address = self.auth.address
        self.chain = chain
    
    def create_meme(
        self,
        prompt: str,
        symbol: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Meme token with one function call
        
        This function orchestrates the entire Meme creation flow:
        1. Generate image and title using AI
        2. Login to platform
        3. Upload image
        4. Create metadata
        5. Call smart contract
        6. Confirm creation
        
        Args:
            prompt: User's Meme description (any language)
            symbol: Token symbol (auto-generated from title if None)
            description: Token description (uses enhanced_prompt if None)
        
        Returns:
            Dictionary containing:
                - success: True
                - token_id: Token ID
                - token_address: Token contract address
                - tx_hash: Creation transaction hash
                - name: Token name (Meme title)
                - symbol: Token symbol
                - image_url: Image URL on platform
                - meme_title: AI-generated title
        
        Raises:
            InsufficientBalanceError: Balance < 0.011 BNB
            AuthenticationError: Signature verification failed
            LoginError: Platform login failed
            UploadError: Image upload failed
            MetadataCreationError: Metadata creation failed
            TransactionFailedError: Contract call failed
        
        Example:
            >>> result = sdk.create_meme("A shocked cat looking at code")
            >>> print(f"Token created: {result['token_address']}")
            >>> print(f"View at: https://moonn.fun/bsc/token/{result['token_address']}")
        """
        print("🎨 Step 1/6: Generating Meme image...")
        
        # Step 1: Generate image and title
        meme_data = self.image_api.generate_meme(prompt)
        
        image_base64 = meme_data['image_base64']
        meme_title = meme_data['meme_title']
        enhanced_prompt = meme_data['enhanced_prompt']
        
        print(f"✅ Generated: {meme_title}")
        
        # Step 2: Login to platform
        print("\n🔐 Step 2/6: Logging in to platform...")
        self.platform.login()
        print("✅ Login successful")
        
        # Step 3: Upload image
        print("\n📤 Step 3/6: Uploading image...")
        image_url = self.platform.upload_image(image_base64)
        print(f"✅ Image uploaded: {image_url}")
        
        # Step 4: Create metadata
        print("\n📝 Step 4/6: Creating token metadata...")
        
        # Auto-generate symbol from title if not provided
        if symbol is None:
            symbol = self._generate_symbol(meme_title)
        
        if description is None:
            description = enhanced_prompt
        
        metadata = self.platform.create_metadata(
            name=meme_title,
            symbol=symbol,
            description=description,
            image_url=image_url
        )
        
        token_id = metadata['id']
        salt = metadata['salt']
        token_address = metadata['address']
        
        print(f"✅ Metadata created (ID: {token_id})")
        
        # Step 5: Call contract
        print("\n⛓️  Step 5/6: Creating token on blockchain...")
        tx_hash = self.blockchain.create_token(
            token_id=token_id,
            name=meme_title,
            symbol=symbol,
            salt=salt
        )
        
        print(f"✅ Transaction confirmed: {tx_hash}")
        
        # Step 6: Confirm creation
        print("\n✅ Step 6/6: Confirming creation...")
        self.platform.confirm_creation(token_id, tx_hash)
        
        print(f"\n🎉 Meme created successfully!")
        print(f"   Token: {token_address}")
        print(f"   View: https://moonn.fun/detail?address={token_address}")
        
        return {
            'success': True,
            'token_id': token_id,
            'token_address': token_address,
            'tx_hash': tx_hash,
            'name': meme_title,
            'symbol': symbol,
            'image_url': image_url,
            'meme_title': meme_title
        }
    
    def buy_token(
        self,
        token_address: str,
        bnb_amount: float,
        slippage: float = 0.1
    ) -> Dict[str, Any]:
        """
        Buy tokens with BNB
        
        Args:
            token_address: Token contract address
            bnb_amount: Amount of BNB to spend
            slippage: Slippage tolerance (0.1 = 10%)
        
        Returns:
            Dictionary containing:
                - success: True if successful
                - tx_hash: Transaction hash
                - gas_used: Gas consumed
        
        Example:
            >>> result = sdk.buy_token("0x...", bnb_amount=0.1)
            >>> print(f"Bought tokens: {result['tx_hash']}")
        """
        return self.trading.buy_token(token_address, bnb_amount, slippage)
    
    def sell_token(
        self,
        token_address: str,
        amount: int,
        slippage: float = 0.1
    ) -> Dict[str, Any]:
        """
        Sell tokens for BNB
        
        Args:
            token_address: Token contract address
            amount: Amount of tokens to sell (in wei)
            slippage: Slippage tolerance (0.1 = 10%)
        
        Returns:
            Dictionary containing:
                - success: True if successful
                - tx_hash: Transaction hash
                - gas_used: Gas consumed
        
        Example:
            >>> balance = sdk.get_token_balance("0x...")
            >>> result = sdk.sell_token("0x...", amount=balance)
            >>> print(f"Sold tokens: {result['tx_hash']}")
        """
        return self.trading.sell_token(token_address, amount, slippage)
    
    def get_balance(self, address: Optional[str] = None) -> float:
        """
        Get BNB balance
        
        Args:
            address: Address to query (defaults to SDK wallet)
        
        Returns:
            Balance in BNB
        
        Example:
            >>> balance = sdk.get_balance()
            >>> print(f"Balance: {balance:.6f} BNB")
        """
        return self.blockchain.get_balance(address)
    
    def get_token_balance(
        self,
        token_address: str,
        address: Optional[str] = None
    ) -> int:
        """
        Get token balance
        
        Args:
            token_address: Token contract address
            address: Address to query (defaults to SDK wallet)
        
        Returns:
            Balance in wei (raw units)
        
        Example:
            >>> balance = sdk.get_token_balance("0x...")
            >>> print(f"Token balance: {balance / 10**18:.2f}")
        """
        return self.blockchain.get_token_balance(token_address, address)
    
    def _generate_symbol(self, title: str) -> str:
        """
        Auto-generate token symbol from title
        
        Args:
            title: Meme title
        
        Returns:
            Symbol (max 6 characters)
        """
        # Take first letters of words, max 6 chars
        words = title.upper().split()
        symbol = ''.join(word[0] for word in words if word.isalnum())[:6]
        return symbol if symbol else "MEME"
