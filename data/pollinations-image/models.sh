#!/bin/sh
# Pollinations Image Models Registry
# This file defines all available models with their metadata

# Format: model_id|display_name|type|cost|speed|quality|description

MODELS_LIST="flux|Flux Schnell|free|0.0002|medium|5|Fast high-quality generation - best default
zimage|Z-Image Turbo|free|0.0002|fast|4|Ultra fast for quick drafts
klein|FLUX.2 Klein 4B|paid|0.008|medium|5|Premium quality with more details
klein-large|FLUX.2 Klein 9B|paid|0.012|slow|6|Maximum quality, slower generation
gptimage|GPT Image 1 Mini|paid|2.0|medium|5|DALL-E style generation"

# Get all model IDs
get_model_ids() {
    echo "$MODELS_LIST" | cut -d'|' -f1
}

# Get model info by ID
# Usage: get_model_info flux display_name
get_model_info() {
    model_id="$1"
    field="$2"
    
    case "$field" in
        id) col=1 ;;
        display_name) col=2 ;;
        type) col=3 ;;
        cost) col=4 ;;
        speed) col=5 ;;
        quality) col=6 ;;
        description) col=7 ;;
        *) echo ""; return ;;
    esac
    
    echo "$MODELS_LIST" | grep "^$model_id|" | cut -d'|' -f"$col"
}

# Check if model is valid
is_valid_model() {
    model_id="$1"
    echo "$MODELS_LIST" | grep -q "^$model_id|"
}

# Get models by type (free/paid)
get_models_by_type() {
    model_type="$1"
    echo "$MODELS_LIST" | grep "|$model_type|" | cut -d'|' -f1
}

# Format model for display
format_model_line() {
    model_id="$1"
    display_name=$(get_model_info "$model_id" display_name)
    type=$(get_model_info "$model_id" type)
    cost=$(get_model_info "$model_id" cost)
    speed=$(get_model_info "$model_id" speed)
    quality=$(get_model_info "$model_id" quality)
    
    # Stars for quality
    stars=""
    i=0
    while [ $i -lt "$quality" ]; do
        stars="${stars}⭐"
        i=$((i + 1))
    done
    
    # Speed indicator
    speed_icon=""
    case "$speed" in
        fast) speed_icon="⚡" ;;
        medium) speed_icon="⚡⚡" ;;
        slow) speed_icon="⚡⚡⚡" ;;
    esac
    
    # Type indicator
    type_indicator=""
    if [ "$type" = "free" ]; then
        type_indicator="🎁 FREE"
    else
        type_indicator="💰 PAID"
    fi
    
    printf "  %-12s %-22s %s %s %s\n" "$model_id" "$display_name" "$stars" "$speed_icon" "$type_indicator"
}

# Print all models in a nice table
print_models_table() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║           POLLINATIONS IMAGE MODELS                              ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  ID          NAME                   QUALITY   SPEED    TYPE      ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    
    # Free models first
    echo "║  🎁 FREE MODELS (5K images/month):                              ║"
    for model in $(get_models_by_type free); do
        line=$(format_model_line "$model")
        printf "║%-66s║\n" "$line"
    done
    
    echo "║                                                                  ║"
    echo "║  💰 PAID MODELS (requires pollen credits):                      ║"
    for model in $(get_models_by_type paid); do
        line=$(format_model_line "$model")
        printf "║%-66s║\n" "$line"
    done
    
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Usage: generate_image.sh --model MODEL_NAME"
    echo "Get pollen: https://enter.pollinations.ai"
    echo ""
}

# Print single model details
print_model_details() {
    model_id="$1"
    
    if ! is_valid_model "$model_id"; then
        echo "Error: Unknown model '$model_id'" >&2
        return 1
    fi
    
    display_name=$(get_model_info "$model_id" display_name)
    type=$(get_model_info "$model_id" type)
    cost=$(get_model_info "$model_id" cost)
    speed=$(get_model_info "$model_id" speed)
    quality=$(get_model_info "$model_id" quality)
    description=$(get_model_info "$model_id" description)
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  MODEL: $display_name"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║  ID:        $model_id"
    echo "║  Type:      $type"
    echo "║  Cost:      ~$cost pollen/img"
    echo "║  Speed:     $speed"
    echo "║  Quality:   $quality/6"
    echo "║"
    echo "║  Description:"
    echo "║  $description"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}
