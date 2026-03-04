---
name: kefir-batch-manager
description: Comprehensive kéfir batch management system with cycle tracking, intelligent reminders, grain health monitoring, and recipe management. Use when managing kéfir fermentation cycles, tracking grain health, calculating ratios, scheduling reminders, or maintaining fermentation records.
---

# Kéfir Batch Manager

Complete management system for kéfir de fruits fermentation cycles, grain maintenance, and production tracking.

## When to Use

- Starting new fermentation batches
- Tracking active fermentation cycles
- Managing grain health and stock
- Calculating ingredient ratios
- Setting intelligent reminders based on temperature/season
- Recording tasting notes and batch quality
- Planning production schedules
- Troubleshooting fermentation issues

## Core Features

### 1. Batch Cycle Management

**Start New Batch:**
```
- Record start time, ingredients, ratios
- Calculate optimal fermentation duration based on temperature
- Set adaptive reminders (faster in summer, slower in winter)
- Photo documentation (before fermentation)
```

**Track Active Batches:**
```
- Monitor fermentation progress
- Adjust timing based on environmental conditions
- Log observations and changes
- Alert when ready for tasting/bottling
```

**Complete Batch:**
```
- Record end time and actual duration
- Document results, taste notes, quality rating
- Calculate yield and efficiency
- Photo documentation (final product)
```

### 2. Intelligent Reminders

Temperature-adaptive scheduling:
- **Summer (>25°C)**: 18-24 hours first fermentation
- **Spring/Autumn (20-25°C)**: 24-36 hours
- **Winter (<20°C)**: 36-48 hours

Maintenance reminders:
- **Weekly**: Check active batches
- **Monthly**: Refresh mother grains
- **Seasonal**: Deep clean equipment

### 3. Grain Management

**Health Monitoring:**
```
- Visual inspection checklist
- Color, firmness, multiplication rate tracking
- Problem diagnosis (mold, softness, inactivity)
- Stock management (mother + active portions)
```

**Stock Tracking:**
```
- Mother grain reserve (typically 200g)
- Active batch portions
- Grain multiplication calculations
- Sharing/backup planning
```

### 4. Recipe Database

**Base Recipes:**
- Classic water kéfir (sugar ratios)
- Fruit variations (seasonal recommendations)
- Milk kéfir adaptations
- Flavoring combinations (spices, herbs)

**Personalization:**
- Save favorite recipes
- Seasonal ingredient optimization
- Success rate tracking per recipe
- Custom ratio calculations

### 5. Production Dashboard

**Calendar View:**
- Batch timeline visualization
- Optimal start dates planning
- Holiday/vacation scheduling
- Production frequency analysis

**Statistics:**
- Success rates by season/temperature
- Favorite recipes and variations
- Grain multiplication trends
- Production consistency metrics

## Usage Workflows

### Daily Check-in
```
1. Review active batches status
2. Check temperature for timing adjustments
3. Update fermentation progress notes
4. Set next reminder if needed
```

### Weekly Planning
```
1. Plan new batches based on consumption
2. Check grain health and stock levels
3. Review upcoming events/travel
4. Adjust production schedule
```

### Monthly Maintenance
```
1. Refresh mother grain batch
2. Deep clean all equipment
3. Review month's production statistics
4. Plan seasonal recipe transitions
```

## Specialized Knowledge

### Paris Water Considerations
- Chlorine removal techniques (24h standing, filtration)
- Mineral content impacts on fermentation
- Seasonal water quality variations

### Double Fermentation Technique
- Primary: 24-48h depending on temperature
- Secondary: 12-24h in bottle for carbonation
- Timing optimization for best results

### Troubleshooting Guide
See [troubleshooting.md](references/troubleshooting.md) for complete diagnostic guide.

## Implementation Scripts

- `batch_tracker.py`: Core batch lifecycle management
- `ratio_calculator.py`: Ingredient calculations
- `reminder_scheduler.py`: Intelligent timing alerts
- `grain_health.py`: Health monitoring and diagnostics

## Templates and Assets

- `batch_template.json`: Standard batch record format
- `grain_health_guide.png`: Visual health assessment guide
- `recipe_templates/`: Collection of proven recipes

## Getting Started

1. **Initialize your setup**: Document current grain stock and equipment
2. **Start tracking**: Begin with your next batch using the batch tracker
3. **Set preferences**: Configure your temperature zone and timing preferences
4. **Build history**: Record several batches to establish baselines

The skill learns from your specific environment and preferences to provide increasingly accurate timing and recommendations.