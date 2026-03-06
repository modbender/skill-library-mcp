---
name: pest-disease-tracker
description: "Track garden pests and diseases with treatments. Identify
  problems, track treatments, and monitor effectiveness. Use when dealing with
  garden pests, plant diseases, or treatment planning. Security: file exports
  restricted to safe directories. Perfect for home gardeners and small farmers
  managing plant health."
---


# Pest & Disease Tracker

Track and manage garden pests and diseases with treatment tracking.

## Quick Start

### Add a pest or disease
```bash
pest_tracker.py add --type "pest" --name "aphids" --plants "tomatoes,peppers"
```

### Record treatment
```bash
pest_tracker.py treat "<id>" --method "<method>" --product "<product>" --notes "<notes>"
```

### List all issues
```bash
pest_tracker.py list
```

### Show problem details
```bash
pest_tracker.py show "<id>"
```

### Search issues
```bash
pest_tracker.py search "<query>"
```

### Get treatment recommendations
```bash
pest_tracker.py recommend "<problem>"
```

### Export data
```bash
pest_tracker.py export "<output_file>"
```

## Usage Patterns

### For pest identification and tracking
```bash
# Add pest sightings
pest_tracker.py add --type "pest" --name "aphids" --plants "tomatoes" --severity "moderate"
pest_tracker.py add --type "pest" --name "slugs" --plants "lettuce,hostas" --severity "high"

# Get treatment recommendations
pest_tracker.py recommend "aphids"
# Output: Neem oil, insecticidal soap, ladybugs

# Record treatments
pest_tracker.py treat <id> --method "spray" --product "neem oil" --notes "Apply in evening, reapply in 7 days"
pest_tracker.py treat <id> --method "natural" --product "ladybugs" --notes "Released 100 ladybugs"
```

### For disease management
```bash
# Add diseases
pest_tracker.py add --type "disease" --name "early blight" --plants "tomatoes" --severity "critical"
pest_tracker.py add --type "disease" --name "powdery mildew" --plants "squash" --severity "moderate"

# Get treatment options
pest_tracker.py recommend "early blight"
# Output: Copper fungicide, remove affected leaves, improve air circulation

# Track treatment effectiveness
pest_tracker.py treat <id> --method "remove" --product "fungicide" --status "effective"
```

### For preventive planning
```bash
# Document common issues in your garden
pest_tracker.py add --type "pest" --name "cucumber beetles" --plants "cucumbers,melons" --severity "low" --notes "Prevent with row covers"

# Set up prevention schedule
pest_tracker.py recommend "cucumber beetles"
# Output: Row covers, beneficial nematodes, crop rotation
```

## Problem Types

### Common Pests
- **Aphids** - Small sap-suckers, distort new growth
- **Slugs** - Eat leaves, leave slime trails
- **Caterpillars** - Eat foliage and fruit
- **Cucumber Beetles** - Chew leaves, spread wilt disease
- **Japanese Beetles** - Skeletonize leaves
- **Squash Bugs** - Pierce stems, cause wilting
- **Spider Mites** - Webbing, yellow stippling
- **Thrips** - Scarring, distorted growth
- **Whiteflies** - Yellow leaves, sticky honeydew

### Common Diseases
- **Early Blight** - Dark spots on tomatoes
- **Late Blight** - White fuzzy growth
- **Powdery Mildew** - White powdery coating
- **Downy Mildew** - Yellow patches, purple growth
- **Blossom End Rot** - Blossoms fall off
- **Verticillium Wilt** - Plants wilt and die
- **Bacterial Spot** - Water-soaked spots
- **Anthracnose** - Sunken lesions

## Treatment Recommendations

### Organic/Natural Treatments
- **Neem Oil** - Broad-spectrum insecticide, safe for beneficials
- **Insecticidal Soap** - Kills soft-bodied insects on contact
- **Diatomaceous Earth** - Mechanical insect control
- **Bacillus thuringiensis** - Bt for caterpillars
- **Copper Fungicide** - Organic disease control
- **Sulfur Fungicide** - Powdery mildew control
- **Compost Tea** - Boosts plant immunity
- **Beneficial Insects** - Ladybugs, lacewings, parasitic wasps
- **Barriers** - Row covers, collars, netting

### Chemical Treatments
- **Pyrethrin** - Synthetic insecticide
- **Imidacloprid** - Systemic insecticide
- **Chlorothalonil** - Broad-spectrum fungicide
- **Mancozeb** - Multi-site fungicide
- **Captan** - Seed treatment and fungicide

**Always follow label directions and safety precautions.**

## Severity Levels

| Level | Description | Action Timeline |
|-------|-------------|-----------------|
| **low** | Minor annoyance, limited damage | Treat within 7 days |
| **moderate** | Noticeable damage, spreading | Treat within 3-5 days |
| **high** | Significant damage, severe impact | Treat within 1-2 days |
| **critical** | Plant death or total crop loss | Treat immediately |

## Examples

### Aphid outbreak on tomatoes
```bash
# Add the problem
pest_tracker.py add --type "pest" --name "aphids" --plants "tomatoes" --severity "high" \
  --notes "Found on new growth, honeydew present"

# Get treatment options
pest_tracker.py recommend "aphids"
# Output: Neem oil, insecticidal soap, ladybugs, strong water spray

# Apply treatment
pest_tracker.py treat <id> --method "spray" --product "neem oil" \
  --notes "Spray every 2-3 days for 2 weeks, apply in evening"
```

### Early blight on tomatoes
```bash
# Add disease
pest_tracker.py add --type "disease" --name "early blight" --plants "tomatoes" --severity "critical" \
  --notes "Found on lower leaves, rainy weather, needs immediate action"

# Get recommendations
pest_tracker.py recommend "early blight"
# Output: Copper fungicide, remove affected leaves, improve air circulation, avoid overhead watering

# Apply treatment
pest_tracker.py treat <id> --method "remove" --product "copper fungicide" \
  --notes "Applied fungicide, removed worst leaves, spaced plants for airflow"
```

### Slug problem on lettuce
```bash
# Add pest
pest_tracker.py add --type "pest" --name "slugs" --plants "lettuce,hostas" --severity "moderate" \
  --notes "Slime trails visible, holes in leaves"

# Get options
pest_tracker.py recommend "slugs"
# Output: Beer traps, diatomaceous earth, copper tape, beneficial nematodes

# Set up traps
pest_tracker.py treat <id> --method "traps" --product "beer traps" \
  --notes "Set up 5 beer traps around bed, check daily"
```

## Search Features

- Search by problem name
- Filter by type (pest/disease)
- Search by affected plants
- View treatment history
- Track treatment effectiveness

## Security

### Path Validation
The `export` function validates output paths to prevent malicious writes:
- ✅ Allowed: `~/.openclaw/workspace/`, `/tmp/`, and home directory
- ❌ Blocked: System paths (`/etc/`, `/usr/`, `/var/`, etc.)
- ❌ Blocked: Sensitive dotfiles (`~/.bashrc`, `~/.ssh`, etc.)

## Data Storage

- Pest data stored in: `~/.openclaw/workspace/pest_tracker_db.json`
- Each problem tracks: type, name, affected plants, severity, treatments, status
- Treatment history includes: method, product, date, effectiveness, notes
- JSON format makes it easy to backup or migrate

## Best Practices

1. **Identify early** - Treat problems before they spread
2. **Monitor regularly** - Check plants daily during growing season
3. **Use IPM** - Integrated Pest Management combines methods for best results
4. **Document treatments** - Track what worked and what didn't
5. **Prevent first** - Barriers and beneficials reduce need for treatments
6. **Rotate treatments** - Prevent pest resistance
7. **Follow labels** - Chemical treatments need proper application
8. **Improve conditions** - Many problems thrive in stressed plants

## Prevention Tips

### Prevent Pests
- **Crop rotation** - Breaks pest life cycles
- **Barriers** - Row covers, netting, collars
- **Beneficial insects** - Ladybugs, lacewings, praying mantises
- **Clean garden** - Remove debris that harbors pests
- **Companion planting** - Repel pests with specific plants

### Prevent Diseases
- **Water correctly** - Avoid wetting foliage
- **Improve airflow** - Space plants properly, prune regularly
- **Clean tools** - Disinfect between plants
- **Use disease-resistant varieties** - When available
- **Sanitize soil** - Solarization, crop rotation

## Related Skills

- **plant-tracker** - Track individual plants and care schedules
- **seasonal-planting-guide** - What to plant when, by zone
- **garden-layout-planner** - Design gardens with companion planting

Use together for complete garden management!
