#!/usr/bin/env python3
"""
Heatmap Examples - matplotlib and seaborn
Usage: python heatmap.py
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
sns.set_theme(style="white")

# Example 1: Simple heatmap
def simple_heatmap():
    data = np.random.rand(10, 12) * 100
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(data, annot=True, fmt='.1f', cmap='YlOrRd', 
                linewidths=0.5, cbar_kws={'label': 'Value'})
    plt.title('Monthly Sales Heatmap', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Product', fontsize=12)
    plt.tight_layout()
    plt.savefig('heatmap_simple.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: heatmap_simple.png")

# Example 2: Correlation matrix
def correlation_heatmap():
    # Generate sample data
    np.random.seed(42)
    df = pd.DataFrame({
        'Revenue': np.random.randn(100) * 10 + 50,
        'Costs': np.random.randn(100) * 8 + 30,
        'Marketing': np.random.randn(100) * 5 + 20,
        'Employees': np.random.randn(100) * 3 + 15,
        'Satisfaction': np.random.randn(100) * 2 + 8
    })
    
    # Compute correlation matrix
    corr = df.corr()
    
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))  # Mask upper triangle
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', 
                cmap='coolwarm', center=0, 
                square=True, linewidths=1, 
                cbar_kws={'shrink': 0.8, 'label': 'Correlation'})
    plt.title('Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('heatmap_correlation.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: heatmap_correlation.png")

# Example 3: Custom labeled heatmap
def labeled_heatmap():
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = [f'{h:02d}:00' for h in range(0, 24, 2)]
    
    # Generate sample activity data
    np.random.seed(42)
    data = np.random.rand(len(hours), len(days)) * 100
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, xticklabels=days, yticklabels=hours,
                cmap='Blues', cbar_kws={'label': 'Activity Level'},
                linewidths=0.5, linecolor='gray')
    plt.title('Weekly Activity Heatmap', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Day of Week', fontsize=12)
    plt.ylabel('Time of Day', fontsize=12)
    plt.tight_layout()
    plt.savefig('heatmap_labeled.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: heatmap_labeled.png")

# Example 4: Diverging heatmap
def diverging_heatmap():
    # Generate data with positive and negative values
    np.random.seed(42)
    data = np.random.randn(8, 10) * 50
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(data, annot=True, fmt='.0f', 
                cmap='RdBu_r', center=0,
                linewidths=1, linecolor='white',
                cbar_kws={'label': 'Change (%)'})
    plt.title('Year-over-Year Change (%)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Region', fontsize=12)
    plt.ylabel('Quarter', fontsize=12)
    plt.tight_layout()
    plt.savefig('heatmap_diverging.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: heatmap_diverging.png")

if __name__ == '__main__':
    simple_heatmap()
    correlation_heatmap()
    labeled_heatmap()
    diverging_heatmap()
    print("\n✓ All heatmaps generated successfully!")
