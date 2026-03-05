# Color Theory & Palettes

## Built-in Color Palettes

### Seaborn Palettes
```python
import seaborn as sns

# Qualitative (categorical data)
sns.set_palette("deep")      # Bold, saturated
sns.set_palette("muted")     # Soft, less saturated
sns.set_palette("bright")    # Vibrant
sns.set_palette("pastel")    # Light, washed
sns.set_palette("dark")      # Dark, muted

# Sequential (ordered data, low to high)
sns.color_palette("Blues")
sns.color_palette("Greens")
sns.color_palette("rocket")  # Modern gradient

# Diverging (data with meaningful center)
sns.color_palette("coolwarm")  # Blue-white-red
sns.color_palette("RdBu_r")    # Red-blue reversed
sns.color_palette("vlag")      # Modern diverging
```

### Matplotlib Colormaps
```python
plt.imshow(data, cmap='viridis')  # Default, colorblind-safe
plt.imshow(data, cmap='plasma')   # Purple-orange
plt.imshow(data, cmap='magma')    # Black-white
plt.imshow(data, cmap='cividis')  # Colorblind-optimized
```

## Custom Color Schemes

### Brand Colors
```python
# Define palette
brand_colors = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'accent': '#f6ad55',
    'success': '#48bb78',
    'warning': '#ed8936',
    'danger': '#fc8181'
}

# Use in plots
plt.plot(x, y, color=brand_colors['primary'])
sns.set_palette(list(brand_colors.values()))
```

### Gradients
```python
# Linear gradient
from matplotlib.colors import LinearSegmentedColormap

colors = ['#667eea', '#764ba2', '#f093fb']
n_bins = 100
cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

plt.imshow(data, cmap=cmap)
```

## Accessibility

### Colorblind-Safe Palettes
```python
# Recommended palettes
sns.set_palette("colorblind")  # Safe for most color blindness
sns.color_palette("crest")     # Sequential, accessible
sns.color_palette("icefire")   # Diverging, accessible

# Avoid: red-green combinations
# Use: blue-orange, purple-green instead
```

### High Contrast
```python
# For presentations/dashboards
high_contrast = ['#000000', '#E69F00', '#56B4E9', '#009E73', 
                '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
sns.set_palette(high_contrast)
```

## Color Psychology

- **Blue** (#4299e1): Trust, stability, data (most common in dataviz)
- **Green** (#48bb78): Growth, success, positive
- **Red** (#fc8181): Warning, danger, negative
- **Orange** (#ed8936): Energy, attention
- **Purple** (#9f7aea): Creativity, luxury
- **Yellow** (#f6e05e): Optimism, caution (hard to read, use sparingly)

## Best Practices

1. **Limit colors**: 3-5 for categorical data
2. **Meaningful colors**: Red for negative, green for positive
3. **Consistency**: Same color = same category across charts
4. **Contrast**: Ensure readability against background
5. **Print-safe**: Test in grayscale if printing

## Quick Reference

```python
# Categorical (distinct items)
sns.set_palette("husl", n_colors=8)  # Evenly spaced hues

# Sequential (ordered intensity)
sns.color_palette("YlOrRd", as_cmap=True)

# Diverging (centered around zero)
sns.color_palette("RdBu_r", as_cmap=True)

# Custom hex codes
custom = ['#667eea', '#764ba2', '#f6ad55', '#4299e1']
sns.set_palette(custom)
```
