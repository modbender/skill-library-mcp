#!/usr/bin/env python3
"""
Scatter Plot Examples - matplotlib and seaborn
Usage: python scatter_plot.py
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
sns.set_theme(style="whitegrid")

# Example 1: Simple scatter plot
def simple_scatter():
    np.random.seed(42)
    x = np.random.randn(100) * 10 + 50
    y = 2 * x + np.random.randn(100) * 20 + 10
    
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.6, s=80, color='#667eea', edgecolors='white', linewidth=0.5)
    plt.title('Simple Scatter Plot', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('X Variable', fontsize=12)
    plt.ylabel('Y Variable', fontsize=12)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('scatter_simple.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: scatter_simple.png")

# Example 2: Scatter with regression line
def scatter_with_regression():
    np.random.seed(42)
    x = np.random.randn(100) * 10 + 50
    y = 2 * x + np.random.randn(100) * 20 + 10
    
    df = pd.DataFrame({'Hours Studied': x, 'Test Score': y})
    
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='Hours Studied', y='Test Score', 
                scatter_kws={'alpha': 0.6, 's': 80, 'edgecolor': 'white', 'linewidth': 0.5},
                line_kws={'color': '#fc8181', 'linewidth': 2.5},
                color='#667eea')
    plt.title('Study Hours vs Test Score', fontsize=16, fontweight='bold', pad=20)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('scatter_regression.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: scatter_regression.png")

# Example 3: Colored by category
def scatter_by_category():
    np.random.seed(42)
    categories = ['Group A', 'Group B', 'Group C']
    data = []
    
    for i, cat in enumerate(categories):
        n = 50
        x = np.random.randn(n) * 10 + (i * 20 + 20)
        y = np.random.randn(n) * 10 + (i * 15 + 30)
        data.extend([{'x': xi, 'y': yi, 'category': cat} for xi, yi in zip(x, y)])
    
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='x', y='y', hue='category', 
                   s=100, alpha=0.7, palette='husl', 
                   edgecolor='white', linewidth=0.5)
    plt.title('Scatter Plot by Category', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('X Variable', fontsize=12)
    plt.ylabel('Y Variable', fontsize=12)
    plt.legend(title='Category', frameon=True, shadow=True)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('scatter_category.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: scatter_category.png")

# Example 4: Bubble chart (size variation)
def bubble_chart():
    np.random.seed(42)
    n = 50
    x = np.random.randn(n) * 10 + 50
    y = np.random.randn(n) * 15 + 60
    sizes = np.random.randint(100, 1000, n)
    colors = np.random.rand(n)
    
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(x, y, s=sizes, c=colors, alpha=0.6, 
                         cmap='viridis', edgecolors='white', linewidth=1)
    plt.colorbar(scatter, label='Value')
    plt.title('Bubble Chart', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('X Variable', fontsize=12)
    plt.ylabel('Y Variable', fontsize=12)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('scatter_bubble.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: scatter_bubble.png")

if __name__ == '__main__':
    simple_scatter()
    scatter_with_regression()
    scatter_by_category()
    bubble_chart()
    print("\n✓ All scatter plots generated successfully!")
