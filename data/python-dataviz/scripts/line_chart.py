#!/usr/bin/env python3
"""
Line Chart Examples - matplotlib and seaborn
Usage: python line_chart.py
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
sns.set_theme(style="whitegrid")

# Example 1: Simple line chart
def simple_line():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue = [45000, 52000, 48000, 61000, 58000, 67000]
    
    plt.figure(figsize=(10, 6))
    plt.plot(months, revenue, marker='o', linewidth=2.5, markersize=8, color='#667eea')
    plt.title('Monthly Revenue', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Revenue ($)', fontsize=12)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('line_simple.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: line_simple.png")

# Example 2: Multiple lines
def multiple_lines():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    product_a = [45, 52, 48, 61, 58, 67]
    product_b = [38, 42, 51, 49, 56, 62]
    product_c = [25, 28, 32, 35, 41, 45]
    
    plt.figure(figsize=(12, 6))
    plt.plot(months, product_a, marker='o', linewidth=2.5, label='Product A', color='#667eea')
    plt.plot(months, product_b, marker='s', linewidth=2.5, label='Product B', color='#f6ad55')
    plt.plot(months, product_c, marker='^', linewidth=2.5, label='Product C', color='#4299e1')
    
    plt.title('Product Sales Comparison', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Sales (thousands)', fontsize=12)
    plt.legend(frameon=True, shadow=True, fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('line_multiple.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: line_multiple.png")

# Example 3: Time series with pandas
def time_series():
    dates = pd.date_range('2024-01-01', periods=180, freq='D')
    values = np.cumsum(np.random.randn(180)) + 100
    
    df = pd.DataFrame({'Date': dates, 'Value': values})
    
    plt.figure(figsize=(14, 6))
    plt.plot(df['Date'], df['Value'], linewidth=2, color='#667eea', alpha=0.7)
    plt.fill_between(df['Date'], df['Value'], alpha=0.2, color='#667eea')
    
    plt.title('Stock Price Over Time', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('line_timeseries.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: line_timeseries.png")

# Example 4: Line with confidence interval
def confidence_interval():
    x = np.linspace(0, 10, 50)
    y = 2 * x + 1 + np.random.randn(50) * 2
    
    # Calculate rolling mean and std
    df = pd.DataFrame({'x': x, 'y': y})
    df = df.sort_values('x')
    df['y_smooth'] = df['y'].rolling(window=5, center=True).mean()
    df['y_std'] = df['y'].rolling(window=5, center=True).std()
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['x'], df['y'], 'o', alpha=0.3, label='Data points', color='#718096')
    plt.plot(df['x'], df['y_smooth'], linewidth=2.5, label='Trend', color='#667eea')
    plt.fill_between(df['x'], 
                     df['y_smooth'] - df['y_std'], 
                     df['y_smooth'] + df['y_std'],
                     alpha=0.2, color='#667eea', label='±1 SD')
    
    plt.title('Trend with Confidence Interval', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('X', fontsize=12)
    plt.ylabel('Y', fontsize=12)
    plt.legend(frameon=True, shadow=True)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('line_confidence.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: line_confidence.png")

if __name__ == '__main__':
    simple_line()
    multiple_lines()
    time_series()
    confidence_interval()
    print("\n✓ All line charts generated successfully!")
