"""
Shopify Integration Module
Author: Tim (sales@dageno.ai)

This module handles Shopify Admin API integration for:
- Creating products
- Uploading product images
- Setting price, inventory, SKU
- Managing variants
"""

import os
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ShopifyIntegration:
    """
    Shopify Admin API Integration
    Handles product creation and management via Shopify Admin API
    """

    def __init__(
        self,
        store_url: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        """
        Initialize Shopify integration

        Args:
            store_url: Shopify store URL (e.g., "mystore.myshopify.com")
            access_token: Shopify Admin API access token
        """
        self.store_url = store_url or os.environ.get("SHOPIFY_STORE_URL", "")
        self.access_token = access_token or os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
        self.api_version = "2024-01"
        self.base_url = f"https://{self.store_url}/admin/api/{self.api_version}"

        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        } if self.access_token else {}

        self.connected = bool(self.store_url and self.access_token)

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

        return f"SHOP-{short_hash}-{random_suffix}"

    def test_connection(self) -> Dict[str, Any]:
        """
        Test Shopify API connection

        Returns:
            Connection status dictionary
        """
        if not self.connected:
            return {
                "connected": False,
                "error": "Missing store_url or access_token"
            }

        try:
            response = requests.get(
                f"{self.base_url}/shop.json",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                shop_data = response.json().get("shop", {})
                return {
                    "connected": True,
                    "shop_name": shop_data.get("name", "Unknown"),
                    "domain": shop_data.get("domain", "")
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
        compare_at_price: Optional[float] = None,
        inventory_quantity: int = 999,
        sku: Optional[str] = None,
        product_type: str = "",
        vendor: str = "",
        tags: List[str] = None,
        image_url: Optional[str] = None,
        status: str = "active"
    ) -> Dict[str, Any]:
        """
        Create a new product in Shopify

        Args:
            title: Product title
            description: Product description (HTML supported)
            price: Product price
            compare_at_price: Compare at price (for sales)
            inventory_quantity: Inventory quantity
            sku: Stock keeping unit (auto-generated if not provided)
            product_type: Product type
            vendor: Product vendor
            tags: Product tags
            image_url: URL of product image
            status: Product status (active/draft/archived)

        Returns:
            Creation result with product ID and details
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to Shopify"
            }

        # Generate SKU if not provided
        if not sku:
            sku = self._generate_sku(title)

        # Build product payload
        product_data = {
            "product": {
                "title": title,
                "body_html": description,
                "vendor": vendor,
                "product_type": product_type,
                "status": status,
                "tags": tags or [],
                "variants": [
                    {
                        "price": str(price),
                        "compare_at_price": str(compare_at_price) if compare_at_price else None,
                        "sku": sku,
                        "inventory_quantity": inventory_quantity,
                        "inventory_policy": "deny",
                        "fulfillment_service": "manual"
                    }
                ]
            }
        }

        try:
            # Create product
            response = requests.post(
                f"{self.base_url}/products.json",
                headers=self.headers,
                json=product_data,
                timeout=30
            )

            if response.status_code == 201:
                product = response.json().get("product", {})
                product_id = product.get("id")

                result = {
                    "success": True,
                    "product_id": product_id,
                    "title": product.get("title"),
                    "sku": sku,
                    "handle": product.get("handle"),
                    "created_at": product.get("created_at")
                }

                # Upload image if provided
                if image_url and product_id:
                    image_result = self.upload_product_image(product_id, image_url)
                    result["image_uploaded"] = image_result.get("success", False)

                return result
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
        position: int = 1
    ) -> Dict[str, Any]:
        """
        Upload product image from URL

        Args:
            product_id: Shopify product ID
            image_url: URL of image to upload
            position: Image position (1 = first)

        Returns:
            Upload result
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to Shopify"
            }

        image_data = {
            "image": {
                "src": image_url,
                "position": position
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/products/{product_id}/images.json",
                headers=self.headers,
                json=image_data,
                timeout=30
            )

            if response.status_code == 201:
                image = response.json().get("image", {})
                return {
                    "success": True,
                    "image_id": image.get("id"),
                    "src": image.get("src")
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

    def update_variant_inventory(
        self,
        variant_id: int,
        inventory_quantity: int,
        location_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update variant inventory

        Args:
            variant_id: Shopify variant ID
            inventory_quantity: New quantity
            location_id: Shopify location ID (required for inventory updates)

        Returns:
            Update result
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to Shopify"
            }

        # For simplified inventory, just update variant directly
        variant_data = {
            "variant": {
                "inventory_quantity": inventory_quantity
            }
        }

        try:
            response = requests.put(
                f"{self.base_url}/variants/{variant_id}.json",
                headers=self.headers,
                json=variant_data,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "variant_id": variant_id,
                    "inventory_quantity": inventory_quantity
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
            product_id: Shopify product ID

        Returns:
            Product details
        """
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to Shopify"
            }

        try:
            response = requests.get(
                f"{self.base_url}/products/{product_id}.json",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "product": response.json().get("product", {})
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


def create_shopify_product(
    store_url: str,
    access_token: str,
    product_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to create a Shopify product

    Args:
        store_url: Shopify store URL
        access_token: Admin API access token
        product_data: Product data dictionary

    Returns:
        Creation result
    """
    shopify = ShopifyIntegration(store_url, access_token)
    return shopify.create_product(
        title=product_data.get("title", ""),
        description=product_data.get("description", ""),
        price=product_data.get("price", 0),
        compare_at_price=product_data.get("compare_at_price"),
        inventory_quantity=product_data.get("inventory_quantity", 999),
        sku=product_data.get("sku"),
        product_type=product_data.get("product_type", ""),
        vendor=product_data.get("vendor", ""),
        tags=product_data.get("tags", []),
        image_url=product_data.get("image_url"),
        status=product_data.get("status", "active")
    )
