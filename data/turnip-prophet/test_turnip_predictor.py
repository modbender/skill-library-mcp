#!/usr/bin/env python3
"""
Test script for the turnip price predictor
Demonstrates the exact algorithm functionality
Run from skill root directory: python3 test_turnip_predictor.py
"""

import json
import subprocess
import sys
import os

def test_predictor(test_name, input_data):
    """Test the predictor with given input"""
    print(f"\n=== {test_name} ===")
    print(f"Input: {input_data}")
    
    try:
        # Determine script path relative to this test file
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(skill_dir, 'scripts')
        
        # Run the predictor
        process = subprocess.Popen(
            ['python3', 'turnip_predict.py'],
            cwd=scripts_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=json.dumps(input_data))
        
        if process.returncode != 0:
            print(f"Error: {stderr}")
            return
        
        result = json.loads(stdout)
        
        # Display key results
        print(f"\nPattern Probabilities:")
        for pattern, prob in result['pattern_probabilities'].items():
            print(f"  {pattern}: {prob:.3f}")
        
        print(f"\nRecommendation: {result['recommended_action']}")
        
        # Show some future price predictions
        future_predictions = []
        for i, pred in enumerate(result['predictions']):
            if input_data['prices'][i] is None and pred['min'] > 0:
                future_predictions.append(f"  Period {i+1}: {pred['min']}-{pred['max']} bells")
        
        if future_predictions:
            print(f"\nFuture Price Ranges:")
            for pred in future_predictions[:5]:  # Show first 5
                print(pred)
    
    except Exception as e:
        print(f"Test failed: {e}")

def main():
    """Run comprehensive tests"""
    
    # Test 1: No known prices - should show all patterns possible
    test_predictor("Test 1: No Known Prices", {
        "buy_price": 100,
        "prices": [None] * 12,
        "previous_pattern": None
    })
    
    # Test 2: Clear decreasing pattern
    test_predictor("Test 2: Decreasing Pattern", {
        "buy_price": 100,
        "prices": [85, 80, 75, 70, 65, 60, 55, 50] + [None] * 4,
        "previous_pattern": None
    })
    
    # Test 3: Large spike detected
    test_predictor("Test 3: Large Spike Pattern", {
        "buy_price": 90,
        "prices": [None, None, None, None, None, None, 450, None, None, None, None, None],
        "previous_pattern": None
    })
    
    # Test 4: Small spike pattern
    test_predictor("Test 4: Small Spike Pattern", {
        "buy_price": 100,
        "prices": [88, 85, 82, 78, None, None, None, None, None, None, None, None],
        "previous_pattern": None
    })
    
    # Test 5: With previous pattern knowledge
    test_predictor("Test 5: With Previous Pattern (Large Spike)", {
        "buy_price": 95,
        "prices": [None] * 12,
        "previous_pattern": 1  # Previous was large spike
    })

if __name__ == '__main__':
    main()