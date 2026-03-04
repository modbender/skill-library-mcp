# Statistical Visualizations

## Distribution Analysis

### Histogram vs KDE
```python
# Histogram: exact counts
sns.histplot(data, bins=30, kde=False)

# KDE: smooth density estimate
sns.kdeplot(data, fill=True)

# Combined: best of both
sns.histplot(data, bins=30, kde=True)
```

### Box Plot vs Violin Plot
```python
# Box plot: quartiles + outliers (compact)
sns.boxplot(data=df, x='category', y='value')

# Violin plot: full distribution shape (more info)
sns.violinplot(data=df, x='category', y='value')

# Combine: box inside violin
sns.violinplot(data=df, x='category', y='value', inner='box')
```

## Relationship Analysis

### Scatter with Regression
```python
# Simple linear regression
sns.regplot(x='x', y='y', data=df)

# Polynomial regression (order=2 for quadratic)
sns.regplot(x='x', y='y', data=df, order=2)

# Lowess smoother (non-parametric)
sns.regplot(x='x', y='y', data=df, lowess=True)
```

### Correlation Matrices
```python
# Compute correlation
corr = df.corr()

# Visualize
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)

# Mask upper triangle (avoid duplication)
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm', center=0)
```

## Categorical Comparisons

### Count Plot
```python
# Bar chart of value counts
sns.countplot(data=df, x='category', order=df['category'].value_counts().index)
```

### Point Plot (Mean + CI)
```python
# Shows mean with confidence interval
sns.pointplot(data=df, x='category', y='value', ci=95)
```

### Strip Plot + Box Plot
```python
# Show individual points + distribution
sns.boxplot(data=df, x='category', y='value', color='lightgray')
sns.stripplot(data=df, x='category', y='value', color='black', alpha=0.5)
```

## Multi-Variable Analysis

### Pair Plot (Scatter Matrix)
```python
# All pairwise relationships
sns.pairplot(df, hue='category')
```

### Joint Plot (Bivariate)
```python
# Scatter + marginal distributions
sns.jointplot(data=df, x='var1', y='var2', kind='scatter')
sns.jointplot(data=df, x='var1', y='var2', kind='hex')    # Hexbin
sns.jointplot(data=df, x='var1', y='var2', kind='kde')    # 2D KDE
sns.jointplot(data=df, x='var1', y='var2', kind='reg')    # With regression
```

### Facet Grid (Small Multiples)
```python
# Multiple subplots by category
g = sns.FacetGrid(df, col='category', row='subcategory', height=4)
g.map(sns.histplot, 'value')
g.add_legend()
```

## Time Series

### Trend Lines
```python
# Rolling average
df['rolling_mean'] = df['value'].rolling(window=7).mean()
plt.plot(df['date'], df['value'], alpha=0.3, label='Raw')
plt.plot(df['date'], df['rolling_mean'], linewidth=2, label='7-day avg')
```

### Confidence Intervals
```python
# Compute stats
mean = df.groupby('date')['value'].mean()
std = df.groupby('date')['value'].std()

# Plot
plt.plot(mean.index, mean.values, linewidth=2)
plt.fill_between(mean.index, mean - std, mean + std, alpha=0.2)
```

## Statistical Annotations

### Significance Stars
```python
from scipy import stats

# T-test
t_stat, p_value = stats.ttest_ind(group1, group2)

# Annotate
if p_value < 0.001:
    sig = '***'
elif p_value < 0.01:
    sig = '**'
elif p_value < 0.05:
    sig = '*'
else:
    sig = 'ns'

plt.text(x, y, sig, fontsize=16)
```

### Summary Statistics
```python
# Add text box with stats
from matplotlib.patches import Rectangle

stats_text = f"Mean: {data.mean():.2f}\nSD: {data.std():.2f}\nN: {len(data)}"
plt.text(0.95, 0.95, stats_text, transform=plt.gca().transAxes,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
```

## Best Practices

1. **Show uncertainty**: Include confidence intervals or error bars
2. **Report sample size**: Indicate n in title or legend
3. **Test assumptions**: Check normality before parametric tests
4. **Multiple comparisons**: Adjust p-values (Bonferroni, FDR)
5. **Effect size**: Report Cohen's d, not just p-values
6. **Raw data**: Show points when n < 100

## Common Pitfalls

❌ **Bar charts for means**: Use box/violin plots instead (show distribution)
❌ **Pie charts for >5 categories**: Use bar chart
❌ **Dual y-axes**: Misleading, avoid when possible
❌ **3D charts**: Harder to read, stick to 2D
❌ **Truncated y-axis**: Can exaggerate differences (use with caution)
