#!/usr/bin/env python3
"""
Bar Chart Examples - matplotlib and seaborn
Usage: python bar_chart.py
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
sns.set_theme(style="whitegrid")

# Example 1: Simple bar chart
def simple_bar():
    data = {'Product A': 45, 'Product B': 62, 'Product C': 38, 'Product D': 71}
    
    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values(), color='#667eea', alpha=0.8)
    plt.title('Sales by Product', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Product', fontsize=12)
    plt.ylabel('Sales (units)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('bar_simple.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: bar_simple.png")

# Example 2: Grouped bar chart
def grouped_bar():
    df = pd.DataFrame({
        'Product': ['A', 'B', 'C', 'D'] * 3,
        'Quarter': ['Q1']*4 + ['Q2']*4 + ['Q3']*4,
        'Sales': [45, 62, 38, 71, 52, 68, 42, 78, 58, 73, 47, 85]
    })
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='Product', y='Sales', hue='Quarter', palette='husl')
    plt.title('Sales by Product & Quarter', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Product', fontsize=12)
    plt.ylabel('Sales (units)', fontsize=12)
    plt.legend(title='Quarter', frameon=True, shadow=True)
    plt.tight_layout()
    plt.savefig('bar_grouped.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: bar_grouped.png")

# Example 3: Horizontal bar chart
def horizontal_bar():
    data = {
        'Machine Learning': 85,
        'Data Analysis': 72,
        'Cloud Computing': 68,
        'DevOps': 61,
        'Cybersecurity': 58
    }
    
    plt.figure(figsize=(10, 6))
    plt.barh(list(data.keys()), list(data.values()), color='#4299e1', alpha=0.8)
    plt.title('Skills Demand Index', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Demand Score', fontsize=12)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('bar_horizontal.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: bar_horizontal.png")

# Example 4: Stacked bar chart
def stacked_bar():
    categories = ['Q1', 'Q2', 'Q3', 'Q4']
    product_a = [30, 35, 40, 38]
    product_b = [25, 28, 32, 30]
    product_c = [20, 22, 25, 27]
    
    plt.figure(figsize=(10, 6))
    plt.bar(categories, product_a, label='Product A', color='#667eea', alpha=0.8)
    plt.bar(categories, product_b, bottom=product_a, label='Product B', color='#f6ad55', alpha=0.8)
    plt.bar(categories, product_c, bottom=[i+j for i,j in zip(product_a, product_b)], 
            label='Product C', color='#4299e1', alpha=0.8)
    
    plt.title('Quarterly Sales by Product', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Quarter', fontsize=12)
    plt.ylabel('Sales (units)', fontsize=12)
    plt.legend(frameon=True, shadow=True)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('bar_stacked.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: bar_stacked.png")

if __name__ == '__main__':
    simple_bar()
    grouped_bar()
    horizontal_bar()
    stacked_bar()
    print("\n✓ All bar charts generated successfully!")
