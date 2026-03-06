#!/usr/bin/env python3
"""
Kéfir Ratio Calculator
Calculates optimal ingredient ratios for different batch sizes and conditions
"""

import math
from typing import Dict, Tuple, Optional

class KefirRatioCalculator:
    """Calculate optimal ratios for kéfir fermentation"""
    
    # Standard ratios per liter
    STANDARD_RATIOS = {
        'grains_g_per_l': 50,      # 50g grains per liter
        'sugar_g_per_l': 50,       # 50g sugar per liter
        'salt_g_per_l': 1,         # 1g salt per liter (optional)
        'lemon_ml_per_l': 15       # 15ml lemon juice per liter
    }
    
    # Seasonal adjustments
    SEASONAL_FACTORS = {
        'winter': {'grains': 1.1, 'fermentation_hours': 48},
        'spring': {'grains': 1.0, 'fermentation_hours': 36},
        'summer': {'grains': 0.9, 'fermentation_hours': 24},
        'autumn': {'grains': 1.0, 'fermentation_hours': 36}
    }

    def __init__(self):
        self.temperature_factors = self._calculate_temperature_factors()

    def _calculate_temperature_factors(self) -> Dict[int, float]:
        """Calculate fermentation speed factors for different temperatures"""
        factors = {}
        for temp in range(15, 35):
            # Optimal temperature is 22°C, factor decreases as we move away
            if temp <= 22:
                factors[temp] = 1.0 + (22 - temp) * 0.15  # Slower at lower temps
            else:
                factors[temp] = max(0.5, 1.0 - (temp - 22) * 0.1)  # Faster at higher temps
        return factors

    def calculate_ingredients(self, 
                            volume_ml: float, 
                            temperature: float = 22,
                            season: str = 'spring',
                            strength: str = 'normal') -> Dict[str, float]:
        """
        Calculate ingredient amounts for given volume and conditions
        
        Args:
            volume_ml: Total water volume in milliliters
            temperature: Fermentation temperature in Celsius
            season: Current season (winter/spring/summer/autumn)
            strength: Desired strength (light/normal/strong)
        """
        volume_l = volume_ml / 1000
        
        # Base ratios
        base_grains = self.STANDARD_RATIOS['grains_g_per_l'] * volume_l
        base_sugar = self.STANDARD_RATIOS['sugar_g_per_l'] * volume_l
        
        # Seasonal adjustment
        seasonal_factor = self.SEASONAL_FACTORS.get(season, self.SEASONAL_FACTORS['spring'])
        grains_adjustment = seasonal_factor['grains']
        
        # Strength adjustment
        strength_factors = {
            'light': 0.8,
            'normal': 1.0,
            'strong': 1.3
        }
        strength_factor = strength_factors.get(strength, 1.0)
        
        # Temperature adjustment for fermentation time
        temp_factor = self.temperature_factors.get(int(temperature), 1.0)
        
        # Final calculations
        grains_g = base_grains * grains_adjustment * strength_factor
        sugar_g = base_sugar * strength_factor
        salt_g = self.STANDARD_RATIOS['salt_g_per_l'] * volume_l
        lemon_ml = self.STANDARD_RATIOS['lemon_ml_per_l'] * volume_l
        
        # Estimated fermentation time
        base_hours = seasonal_factor['fermentation_hours']
        estimated_hours = base_hours / temp_factor
        
        return {
            'water_ml': volume_ml,
            'grains_g': round(grains_g, 1),
            'sugar_g': round(sugar_g, 1),
            'salt_g': round(salt_g, 1),
            'lemon_ml': round(lemon_ml, 1),
            'estimated_fermentation_hours': round(estimated_hours, 1),
            'ratios_per_liter': {
                'grains': round(grains_g / volume_l, 1),
                'sugar': round(sugar_g / volume_l, 1)
            }
        }

    def scale_recipe(self, original_recipe: Dict, new_volume_ml: float) -> Dict:
        """Scale existing recipe to new volume"""
        original_volume = original_recipe.get('water_ml', 1500)
        scale_factor = new_volume_ml / original_volume
        
        scaled = {}
        for ingredient, amount in original_recipe.items():
            if ingredient == 'water_ml':
                scaled[ingredient] = new_volume_ml
            elif isinstance(amount, (int, float)):
                scaled[ingredient] = round(amount * scale_factor, 1)
            else:
                scaled[ingredient] = amount
        
        return scaled

    def calculate_grain_multiplication(self, 
                                    initial_weight: float,
                                    days_active: int,
                                    batches_per_week: int = 2) -> Dict:
        """
        Estimate grain multiplication over time
        
        Args:
            initial_weight: Starting grain weight in grams
            days_active: Number of days grains have been active
            batches_per_week: How many batches per week
        """
        weeks = days_active / 7
        
        # Grains typically multiply 10-20% per week when actively used
        base_multiplication_rate = 0.15  # 15% per week
        
        # More frequent use = faster multiplication
        frequency_factor = min(1.5, batches_per_week / 2)
        
        final_weight = initial_weight * (1 + base_multiplication_rate * frequency_factor) ** weeks
        total_growth = final_weight - initial_weight
        
        return {
            'initial_weight_g': initial_weight,
            'estimated_current_weight_g': round(final_weight, 1),
            'total_growth_g': round(total_growth, 1),
            'growth_percentage': round((total_growth / initial_weight) * 100, 1),
            'weeks_active': round(weeks, 1)
        }

    def optimize_for_conditions(self, 
                               target_volume_ml: float,
                               available_grains_g: float,
                               temperature: float,
                               desired_strength: str = 'normal') -> Dict:
        """Optimize recipe based on available grains and conditions"""
        
        # Calculate what volume we can make with available grains
        volume_l = target_volume_ml / 1000
        optimal_grains_needed = self.STANDARD_RATIOS['grains_g_per_l'] * volume_l
        
        if available_grains_g < optimal_grains_needed * 0.6:
            # Not enough grains, suggest smaller batch
            max_volume_l = available_grains_g / (self.STANDARD_RATIOS['grains_g_per_l'] * 0.6)
            suggested_volume_ml = max_volume_l * 1000
            
            return {
                'warning': 'Insufficient grains for target volume',
                'suggested_volume_ml': round(suggested_volume_ml, 0),
                'grains_needed_g': round(optimal_grains_needed, 1),
                'grains_available_g': available_grains_g
            }
        
        # Calculate optimal recipe
        recipe = self.calculate_ingredients(
            target_volume_ml, 
            temperature, 
            strength=desired_strength
        )
        
        # Adjust for available grains
        if available_grains_g != recipe['grains_g']:
            recipe['grains_g'] = available_grains_g
            recipe['note'] = f"Using available grains ({available_grains_g}g) instead of optimal ({recipe['grains_g']}g)"
        
        return recipe

def main():
    """Command line interface for ratio calculator"""
    import sys
    
    if len(sys.argv) < 2:
        print("Kéfir Ratio Calculator")
        print("Usage:")
        print("  python ratio_calculator.py calculate <volume_ml> [temperature] [season] [strength]")
        print("  python ratio_calculator.py multiply <initial_weight_g> <days_active> [batches_per_week]")
        print("  python ratio_calculator.py optimize <volume_ml> <available_grains_g> <temperature>")
        sys.exit(1)
    
    calc = KefirRatioCalculator()
    command = sys.argv[1]
    
    if command == "calculate":
        volume_ml = float(sys.argv[2])
        temperature = float(sys.argv[3]) if len(sys.argv) > 3 else 22
        season = sys.argv[4] if len(sys.argv) > 4 else 'spring'
        strength = sys.argv[5] if len(sys.argv) > 5 else 'normal'
        
        result = calc.calculate_ingredients(volume_ml, temperature, season, strength)
        print(f"Recipe for {volume_ml}ml at {temperature}°C:")
        for ingredient, amount in result.items():
            if isinstance(amount, dict):
                continue
            unit = 'ml' if 'ml' in ingredient else ('g' if 'g' in ingredient else ('hours' if 'hours' in ingredient else ''))
            print(f"  {ingredient}: {amount} {unit}")
    
    elif command == "multiply":
        initial_weight = float(sys.argv[2])
        days_active = int(sys.argv[3])
        batches_per_week = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        
        result = calc.calculate_grain_multiplication(initial_weight, days_active, batches_per_week)
        print("Grain multiplication estimate:")
        for key, value in result.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()