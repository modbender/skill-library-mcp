#!/usr/bin/env python3
"""
Generate turnip price chart using matplotlib
Usage: generate_chart.py <buy> <known_json> <mins_json> <maxs_json> <output_path>
"""
import sys
import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

def main():
    if len(sys.argv) != 6:
        print("Usage: generate_chart.py <buy> <known_json> <mins_json> <maxs_json> <output_path>", file=sys.stderr)
        sys.exit(1)
    
    buy_price = int(sys.argv[1])
    known = json.loads(sys.argv[2])
    mins = json.loads(sys.argv[3])
    maxs = json.loads(sys.argv[4])
    output_path = sys.argv[5]
    
    # Labels for the 12 time slots
    labels = ['Mon AM', 'Mon PM', 'Tue AM', 'Tue PM', 'Wed AM', 'Wed PM',
              'Thu AM', 'Thu PM', 'Fri AM', 'Fri PM', 'Sat AM', 'Sat PM']
    
    x = np.arange(len(labels))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot min-max range as shaded area
    ax.fill_between(x, mins, maxs, alpha=0.3, color='#4a90e2', label='Possible range')
    
    # Plot known prices as line with markers
    known_x = []
    known_y = []
    for i, price in enumerate(known):
        if price is not None:
            known_x.append(i)
            known_y.append(price)
    
    if known_x:
        ax.plot(known_x, known_y, 'o-', color='#e74c3c', linewidth=2, 
                markersize=8, label='Actual prices', zorder=5)
    
    # Add buy price reference line
    ax.axhline(y=buy_price, color='#95a5a6', linestyle='--', linewidth=1.5, 
               label=f'Buy price ({buy_price})', alpha=0.7)
    
    # Styling
    ax.set_xlabel('Time', fontsize=11, fontweight='bold')
    ax.set_ylabel('Price (bells)', fontsize=11, fontweight='bold')
    ax.set_title(f'Turnip Price Prediction (Buy: {buy_price} bells)', 
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', framealpha=0.9)
    
    # Set y-axis to start at 0
    ax.set_ylim(bottom=0)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

if __name__ == '__main__':
    main()
