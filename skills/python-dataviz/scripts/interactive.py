#!/usr/bin/env python3
"""
Interactive Plotly Examples
Usage: python interactive.py
Output: HTML files that can be opened in a browser
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Example 1: Interactive scatter plot
def interactive_scatter():
    np.random.seed(42)
    df = pd.DataFrame({
        'Hours Studied': np.random.randn(100) * 10 + 50,
        'Test Score': np.random.randn(100) * 15 + 75,
        'Student': [f'Student {i}' for i in range(1, 101)],
        'Class': np.random.choice(['A', 'B', 'C'], 100)
    })
    
    fig = px.scatter(df, x='Hours Studied', y='Test Score', 
                    color='Class', hover_data=['Student'],
                    title='Interactive Scatter: Hover for Details',
                    template='plotly_white')
    
    fig.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='white')))
    fig.write_html('interactive_scatter.html')
    print("✓ Saved: interactive_scatter.html")

# Example 2: Interactive line chart
def interactive_line():
    dates = pd.date_range('2024-01-01', periods=365, freq='D')
    np.random.seed(42)
    
    df = pd.DataFrame({
        'Date': dates,
        'Product A': np.cumsum(np.random.randn(365)) + 100,
        'Product B': np.cumsum(np.random.randn(365)) + 120,
        'Product C': np.cumsum(np.random.randn(365)) + 90
    })
    
    fig = go.Figure()
    
    for col in ['Product A', 'Product B', 'Product C']:
        fig.add_trace(go.Scatter(x=df['Date'], y=df[col], 
                                mode='lines', name=col,
                                line=dict(width=2)))
    
    fig.update_layout(
        title='Interactive Time Series (Click legend to toggle)',
        xaxis_title='Date',
        yaxis_title='Sales',
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.write_html('interactive_line.html')
    print("✓ Saved: interactive_line.html")

# Example 3: Interactive bar chart
def interactive_bar():
    categories = ['Q1', 'Q2', 'Q3', 'Q4']
    df = pd.DataFrame({
        'Quarter': categories * 3,
        'Product': ['A']*4 + ['B']*4 + ['C']*4,
        'Sales': [45, 52, 58, 61, 38, 42, 51, 49, 25, 28, 32, 35]
    })
    
    fig = px.bar(df, x='Quarter', y='Sales', color='Product',
                barmode='group', title='Interactive Grouped Bar Chart',
                template='plotly_white')
    
    fig.update_traces(marker_line_color='white', marker_line_width=1.5)
    fig.write_html('interactive_bar.html')
    print("✓ Saved: interactive_bar.html")

# Example 4: Interactive heatmap
def interactive_heatmap():
    np.random.seed(42)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = [f'{h:02d}:00' for h in range(0, 24, 2)]
    data = np.random.rand(len(hours), len(days)) * 100
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=days,
        y=hours,
        colorscale='Viridis',
        hoverongaps=False,
        colorbar=dict(title='Activity')
    ))
    
    fig.update_layout(
        title='Interactive Activity Heatmap (Hover for values)',
        xaxis_title='Day',
        yaxis_title='Time',
        template='plotly_white'
    )
    
    fig.write_html('interactive_heatmap.html')
    print("✓ Saved: interactive_heatmap.html")

# Example 5: 3D scatter plot
def interactive_3d():
    np.random.seed(42)
    df = pd.DataFrame({
        'X': np.random.randn(200) * 10,
        'Y': np.random.randn(200) * 10,
        'Z': np.random.randn(200) * 10,
        'Category': np.random.choice(['A', 'B', 'C'], 200)
    })
    
    fig = px.scatter_3d(df, x='X', y='Y', z='Z', color='Category',
                       title='Interactive 3D Scatter (Drag to rotate)',
                       template='plotly_white')
    
    fig.update_traces(marker=dict(size=5, opacity=0.8, line=dict(width=0.5, color='white')))
    fig.write_html('interactive_3d.html')
    print("✓ Saved: interactive_3d.html")

# Example 6: Interactive pie chart
def interactive_pie():
    data = {
        'Category': ['Product A', 'Product B', 'Product C', 'Product D'],
        'Sales': [45, 62, 38, 71]
    }
    df = pd.DataFrame(data)
    
    fig = px.pie(df, values='Sales', names='Category',
                title='Interactive Pie Chart (Click slices)',
                template='plotly_white',
                hole=0.3)  # Donut chart
    
    fig.update_traces(textposition='inside', textinfo='percent+label',
                     marker=dict(line=dict(color='white', width=2)))
    fig.write_html('interactive_pie.html')
    print("✓ Saved: interactive_pie.html")

if __name__ == '__main__':
    interactive_scatter()
    interactive_line()
    interactive_bar()
    interactive_heatmap()
    interactive_3d()
    interactive_pie()
    print("\n✓ All interactive charts generated successfully!")
    print("\nOpen the HTML files in your browser to interact with the charts.")
