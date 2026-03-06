#!/usr/bin/env python3
"""
Quick test script for Molt Sift core functionality
"""

import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from sifter import Sifter


def test_crypto_validation():
    """Test crypto data validation."""
    print("\n=== Test 1: Crypto Validation ===")
    
    data = {
        "symbol": "BTC",
        "price": 42850.50,
        "volume": 1500000000,
        "change_pct": 3.25,
        "timestamp": "2026-02-25T12:00:00Z"
    }
    
    sifter = Sifter(rules="crypto")
    result = sifter.validate(data)
    
    print(json.dumps(result, indent=2))
    assert result["status"] == "validated", "Crypto validation should pass"
    assert result["score"] >= 0.7, "Score should be valid"
    print("[PASS] Crypto validation test passed")


def test_invalid_data():
    """Test with invalid data."""
    print("\n=== Test 2: Invalid Data ===")
    
    data = {
        "symbol": "BTC",
        "price": "not_a_number"  # Invalid price
    }
    
    sifter = Sifter(rules="crypto")
    result = sifter.validate(data)
    
    print(json.dumps(result, indent=2))
    assert result["status"] == "failed", "Invalid data should fail"
    assert len(result["issues"]) > 0, "Should have issues"
    print("[PASS] Invalid data test passed")


def test_sifting():
    """Test signal sifting."""
    print("\n=== Test 3: Signal Sifting ===")
    
    data = [
        {"symbol": "BTC", "price": 42850, "volume": 1000000000},
        {"symbol": "ETH", "price": 2450, "volume": 500000000},
        {"symbol": "SOL", "price": 95, "volume": 200000000}
    ]
    
    sifter = Sifter(rules="crypto")
    result = sifter.sift(data)
    
    print(json.dumps(result, indent=2))
    assert result["status"] == "sifted", "Should return sifted status"
    assert len(result["clean_data"]) > 0, "Should have sifted entries"
    print("[PASS] Sifting test passed")


def test_trading_validation():
    """Test trading order validation."""
    print("\n=== Test 4: Trading Order Validation ===")
    
    data = {
        "order_id": "ord_123456",
        "symbol": "BTC/USDT",
        "side": "buy",
        "price": 42850.00,
        "quantity": 0.5,
        "timestamp": "2026-02-25T12:00:00Z"
    }
    
    sifter = Sifter(rules="trading")
    result = sifter.validate(data)
    
    print(json.dumps(result, indent=2))
    assert result["status"] == "validated", "Trading validation should pass"
    print("[PASS] Trading validation test passed")


def test_missing_fields():
    """Test detection of missing required fields."""
    print("\n=== Test 5: Missing Required Fields ===")
    
    data = {
        "symbol": "BTC"
        # Missing 'price' field
    }
    
    sifter = Sifter(rules="crypto")
    result = sifter.validate(data)
    
    print(json.dumps(result, indent=2))
    assert result["status"] == "failed", "Should fail with missing fields"
    assert any("missing" in str(i).lower() for i in result["issues"]), "Should report missing field"
    print("[PASS] Missing fields test passed")


def main():
    """Run all tests."""
    print("[Molt Sift] Running tests...")
    
    try:
        test_crypto_validation()
        test_invalid_data()
        test_sifting()
        test_trading_validation()
        test_missing_fields()
        
        print("\n" + "="*50)
        print("[SUCCESS] All tests passed!")
        print("="*50)
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
