#!/usr/bin/env python3
"""
Distribution Plot Examples - matplotlib and seaborn
Usage: python distribution.py
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
sns.set_theme(style="whitegrid")

# Example 1: Histogram
def histogram():
    np.random.seed(42)
    data = np.random.randn(1000) * 15 + 100
    
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=30, color='#667eea', alpha=0.7, edgecolor='white', linewidth=1.2)
    plt.axvline(data.mean(), color='#fc8181', linestyle='--', linewidth=2, label=f'Mean: {data.mean():.1f}')
    plt.axvline(np.median(data), color='#4299e1', linestyle='--', linewidth=2, label=f'Median: {np.median(data):.1f}')
    
    plt.title('Score Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend(frameon=True, shadow=True)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('dist_histogram.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: dist_histogram.png")

# Example 2: KDE (Kernel Density Estimation)
def kde_plot():
    np.random.seed(42)
    data1 = np.random.randn(1000) * 15 + 100
    data2 = np.random.randn(1000) * 20 + 110
    
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=data1, fill=True, alpha=0.6, linewidth=2, label='Group A', color='#667eea')
    sns.kdeplot(data=data2, fill=True, alpha=0.6, linewidth=2, label='Group B', color='#f6ad55')
    
    plt.title('Distribution Comparison (KDE)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Value', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend(frameon=True, shadow=True)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('dist_kde.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: dist_kde.png")

# Example 3: Box plot
def box_plot():
    np.random.seed(42)
    categories = ['Group A', 'Group B', 'Group C', 'Group D']
    data = [np.random.randn(100) * 10 + (i * 5 + 50) for i in range(4)]
    
    df_data = []
    for cat, values in zip(categories, data):
        df_data.extend([{'Category': cat, 'Value': v} for v in values])
    df = pd.DataFrame(df_data)
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Category', y='Value', palette='Set2', 
                linewidth=2, fliersize=5)
    plt.title('Distribution by Category (Box Plot)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('dist_boxplot.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: dist_boxplot.png")

# Example 4: Violin plot
def violin_plot():
    np.random.seed(42)
    categories = ['Q1', 'Q2', 'Q3', 'Q4']
    data = []
    
    for i, cat in enumerate(categories):
        values = np.random.randn(100) * 12 + (i * 8 + 60)
        data.extend([{'Quarter': cat, 'Sales': v} for v in values])
    
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(12, 6))
    sns.violinplot(data=df, x='Quarter', y='Sales', palette='muted',
                  inner='box', linewidth=1.5)
    plt.title('Sales Distribution by Quarter (Violin Plot)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Quarter', fontsize=12)
    plt.ylabel('Sales (thousands)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('dist_violin.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: dist_violin.png")

# Example 5: Combined histogram + KDE
def hist_kde_combo():
    np.random.seed(42)
    data = np.random.randn(1000) * 15 + 100
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=30, kde=True, color='#667eea', 
                alpha=0.6, edgecolor='white', linewidth=1.2,
                line_kws={'linewidth': 2.5})
    
    plt.title('Distribution with Histogram + KDE', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Value', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('dist_hist_kde.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: dist_hist_kde.png")

if __name__ == '__main__':
    histogram()
    kde_plot()
    box_plot()
    violin_plot()
    hist_kde_combo()
    print("\n✓ All distribution plots generated successfully!")
