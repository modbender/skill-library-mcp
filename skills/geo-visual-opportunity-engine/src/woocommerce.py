"""
WooCommerce / WordPress Integration Module
Author: Tim (sales@dageno.ai)

This module handles WooCommerce REST API integration for:
- Creating products
- Uploading product images
- Setting price, inventory, SKU
- Managing product categories and tags
"""

import os
import json
import uuid
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from requests.auth import OAuth1
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class WooCommerceIntegration:
    """
    WooCommerce REST API Integration
    Handles product creation and management via WooCommerce REST API
    """

    def __init__(
        self,
        store_url: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None
    ):
        """
        Initialize WooCommerce integration

        Args:
            store_url: WooCommerce store URL (e.g., "https://mystore.com")
            consumer_key: WooCommerce API consumer key
            consumer_secret: WooCommerce API consumer secret
        """
        self.store_url = store_url or os.environ.get("WOOCOMMERCE_STORE_URL", "")
        self.consumer_key = consumer_key or os.environ.get("WOOCOMMERCE_CONSUMER_KEY", "")
        self.consumer_secret = consumer_secret or os.environ.get("WOOCOMMERCE_CONSUMER_SECRET", "")

        # Ensure URL doesn't have trailing slash
        self.store_url = self.store_url.rstrip('/')

        # Setup OAuth1 authentication
        self.auth = None
        self.connected = False

        if self.consumer_key and self.consumer_secret:
            try:
                self.auth = OAuth1(
                    self.consumer_key,
                    client_secret=self.consumer_secret,
                    signature_method="HMAC-SHA256",
                    timestamp=str(int(time.time()))
                )
                self.connected = bool(self.store_url)
            except Exception:
                self.connected = False

        self.api_version = "wc/v3"

    def _generate_sku(self, product_name: str) -> str:
        """
        Generate unique SKU for product

        Args:
            product_name: Product name

        Returns:
            SKU string
        """
        # Generate short hash from product name
        hash_obj = hashlib.md5(product_name.encode())
        short_hash = hash_obj.hexdigest()[:6].upper()

        # Generate random suffix
        random_suffix = str(uuid.uuid4())[:4].upper()

        return f"WOO-{short_hash}-{random_suffix}"

    def _get_api_url(self, endpoint: str) -> str:
        """
        Build full API URL

        Args:
            endpoint: API endpoint

        Returns:
            Full URL
        """
        base = f"{self.store_url}/wp-json/{self.api_version}"
        return f"{base}/{endpoint.lstrip('/')}"

    def test_connection(self) -> Dict[str, Any]:
        """
        Test WooCommerce API connection

        Returns:
            Connection status dictionary
        """
        if not self.connected:
            return {
                "connected": False,
                "error": "Missing store_url, consumer_key, or consumer_secret"
            }

        try:
            response = requests.get(
                self._get_api_url("system_status"),
                auth=self.auth,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "connected": True,
                    "site_title": data.get("environment", {}).get("site_title", "Unknown"),
                    "version": data.get("environment", {}).get("version", "")
                }
            else:
                return {
                    "connected": False,
                    "error": f"API error: {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

    def create_product(
        self,
        title: str,
        description: str,
        price: float,
        regular_price: Optional[float] = None,
        sale_price: Optional[float] = None,
        stock_quantity: int = 999,
        sku: Optional[str] = None,
        product_type: str = "simple",
        categories: List[Dict] = None,
        tags: List[Dict] = None,
        images: List[Dict] = None,
        short_description: str = "",
        status: str = "publish",
        manage_stock: bool = True,
        dimensions: Dict = None,
        weight: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new product in WooCommerce

        Args:
            title: Product title
            description: Full product description (HTML supported)
            price: Product price
            regular_price: Regular price (before sale)
            sale_price: Sale price
            stock_quantity: Stock quantity
            sku: Stock keeping unit (auto-generated if not provided)
            product_type: Product type (simple/variable)
            categories: Product categories
            tags: Product tags
            images: Product images
            short_description: Short description
            status: Product status (publish/draft/pending/private)
            manage_stock: Whether to manage stock
            dimensions: Product dimensions (length/width/height)
            weight: Product weight

        Returns:
            Creation result with product ID and details
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to WooCommerce"
            }

        # Generate SKU if not provided
        if not sku:
            sku = self._generate_sku(title)

        # Build product payload
        product_data = {
            "name": title,
            "description": description,
            "short_description": short_description,
            "regular_price": str(regular_price if regular_price else price),
            "price": str(price),
            "sale_price": str(sale_price) if sale_price else "",
            "sku": sku,
            "status": status,
            "manage_stock": manage_stock,
            "stock_quantity": stock_quantity,
            "stock_status": "instock" if stock_quantity > 0 else "outofstock",
            "product_type": product_type,
            "categories": categories or [],
            "tags": tags or [],
            "images": images or [],
            "weight": weight,
            "dimensions": dimensions or {
                "length": "",
                "width": "",
                "height": ""
            }
        }

        # Remove empty values
        product_data = {k: v for k, v in product_data.items() if v}

        try:
            response = requests.post(
                self._get_api_url("products"),
                auth=self.auth,
                json=product_data,
                timeout=30
            )

            if response.status_code in [200, 201]:
                product = response.json()
                return {
                    "success": True,
                    "product_id": product.get("id"),
                    "title": product.get("name"),
                    "sku": product.get("sku"),
                    "permalink": product.get("permalink"),
                    "date_created": product.get("date_created")
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def upload_product_image(
        self,
        product_id: int,
        image_url: str,
        alt_text: str = ""
    ) -> Dict[str, Any]:
        """
        Add image to existing product

        Args:
            product_id: WooCommerce product ID
            image_url: URL of image to upload
            alt_text: Image alt text

        Returns:
            Upload result
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to WooCommerce"
            }

        image_data = {
            "images": [
                {
                    "src": image_url,
                    "alt": alt_text
                }
            ]
        }

        try:
            response = requests.post(
                self._get_api_url(f"products/{product_id}"),
                auth=self.auth,
                json=image_data,
                timeout=30
            )

            if response.status_code == 200:
                product = response.json()
                images = product.get("images", [])
                return {
                    "success": True,
                    "image_id": images[0].get("id") if images else None,
                    "src": images[0].get("src") if images else None
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_stock(
        self,
        product_id: int,
        stock_quantity: int
    ) -> Dict[str, Any]:
        """
        Update product stock

        Args:
            product_id: WooCommerce product ID
            stock_quantity: New stock quantity

        Returns:
            Update result
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to WooCommerce"
            }

        data = {
            "stock_quantity": stock_quantity,
            "manage_stock": True,
            "stock_status": "instock" if stock_quantity > 0 else "outofstock"
        }

        try:
            response = requests.put(
                self._get_api_url(f"products/{product_id}"),
                auth=self.auth,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "product_id": product_id,
                    "stock_quantity": stock_quantity
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """
        Get product details

        Args:
            product_id: WooCommerce product ID

        Returns:
            Product details
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to WooCommerce"
            }

        try:
            response = requests.get(
                self._get_api_url(f"products/{product_id}"),
                auth=self.auth,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "product": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def create_woocommerce_product(
    store_url: str,
    consumer_key: str,
    consumer_secret: str,
    product_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to create a WooCommerce product

    Args:
        store_url: WooCommerce store URL
        consumer_key: API consumer key
        consumer_secret: API consumer secret
        product_data: Product data dictionary

    Returns:
        Creation result
    """
    woo = WooCommerceIntegration(store_url, consumer_key, consumer_secret)
    return woo.create_product(
        title=product_data.get("title", ""),
        description=product_data.get("description", ""),
        price=product_data.get("price", 0),
        regular_price=product_data.get("regular_price"),
        sale_price=product_data.get("sale_price"),
        stock_quantity=product_data.get("stock_quantity", 999),
        sku=product_data.get("sku"),
        product_type=product_data.get("product_type", "simple"),
        categories=product_data.get("categories", []),
        tags=product_data.get("tags", []),
        images=product_data.get("images", []),
        short_description=product_data.get("short_description", ""),
        status=product_data.get("status", "publish")
    )
