#!/usr/bin/env python3
"""
Kéfir Batch Tracker
Manages complete lifecycle of kéfir fermentation batches
"""

import json
import datetime
from typing import Dict, List, Optional
import os

class KefirBatch:
    def __init__(self, batch_id: str = None):
        self.batch_id = batch_id or self._generate_batch_id()
        self.start_time = None
        self.end_time = None
        self.ingredients = {}
        self.ratios = {}
        self.temperature = None
        self.notes = []
        self.photos = []
        self.quality_rating = None
        self.taste_notes = ""
        self.status = "planned"  # planned, active, complete

    def _generate_batch_id(self) -> str:
        """Generate unique batch ID based on timestamp"""
        return f"batch_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"

    def start_batch(self, ingredients: Dict[str, float], temperature: float = 22.0):
        """Start a new fermentation batch"""
        self.start_time = datetime.datetime.now()
        self.ingredients = ingredients
        self.temperature = temperature
        self.status = "active"
        
        # Calculate ratios
        water_volume = ingredients.get('water_ml', 1500)
        self.ratios = {
            'grains_per_liter': (ingredients.get('grains_g', 80) / water_volume) * 1000,
            'sugar_per_liter': (ingredients.get('sugar_g', 80) / water_volume) * 1000
        }
        
        # Estimate completion time based on temperature
        base_hours = 36
        if temperature > 25:
            estimated_hours = max(18, base_hours - (temperature - 22) * 2)
        elif temperature < 20:
            estimated_hours = base_hours + (22 - temperature) * 2
        else:
            estimated_hours = base_hours
            
        self.estimated_completion = self.start_time + datetime.timedelta(hours=estimated_hours)
        
        return {
            'batch_id': self.batch_id,
            'started': self.start_time.isoformat(),
            'estimated_ready': self.estimated_completion.isoformat(),
            'ratios': self.ratios
        }

    def add_note(self, note: str, photo_path: str = None):
        """Add observation note and optional photo"""
        entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'note': note
        }
        if photo_path:
            entry['photo'] = photo_path
            self.photos.append(photo_path)
        self.notes.append(entry)

    def complete_batch(self, quality_rating: int, taste_notes: str = ""):
        """Complete the batch with final assessment"""
        self.end_time = datetime.datetime.now()
        self.status = "complete"
        self.quality_rating = quality_rating
        self.taste_notes = taste_notes
        
        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        
        return {
            'batch_id': self.batch_id,
            'duration_hours': round(duration_hours, 1),
            'quality_rating': quality_rating,
            'completed': self.end_time.isoformat()
        }

    def to_dict(self) -> Dict:
        """Export batch data as dictionary"""
        return {
            'batch_id': self.batch_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'ingredients': self.ingredients,
            'ratios': self.ratios,
            'temperature': self.temperature,
            'notes': self.notes,
            'photos': self.photos,
            'quality_rating': self.quality_rating,
            'taste_notes': self.taste_notes,
            'status': self.status
        }

def load_batch_history(data_file: str = "kefir_batches.json") -> List[Dict]:
    """Load batch history from JSON file"""
    if not os.path.exists(data_file):
        return []
    
    with open(data_file, 'r') as f:
        return json.load(f)

def save_batch(batch: KefirBatch, data_file: str = "kefir_batches.json"):
    """Save batch to history file"""
    history = load_batch_history(data_file)
    
    # Update existing batch or add new one
    batch_dict = batch.to_dict()
    for i, existing in enumerate(history):
        if existing['batch_id'] == batch.batch_id:
            history[i] = batch_dict
            break
    else:
        history.append(batch_dict)
    
    with open(data_file, 'w') as f:
        json.dump(history, f, indent=2)

def get_active_batches(data_file: str = "kefir_batches.json") -> List[Dict]:
    """Get all currently active batches"""
    history = load_batch_history(data_file)
    return [batch for batch in history if batch['status'] == 'active']

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_tracker.py <command> [args]")
        print("Commands: start, note, complete, active, history")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        # Example: python batch_tracker.py start 80 1500 80 22
        if len(sys.argv) < 6:
            print("Usage: python batch_tracker.py start <grains_g> <water_ml> <sugar_g> <temp_c>")
            sys.exit(1)
        
        batch = KefirBatch()
        ingredients = {
            'grains_g': float(sys.argv[2]),
            'water_ml': float(sys.argv[3]),
            'sugar_g': float(sys.argv[4])
        }
        temperature = float(sys.argv[5])
        
        result = batch.start_batch(ingredients, temperature)
        save_batch(batch)
        print(f"Started batch {result['batch_id']}")
        print(f"Estimated ready: {result['estimated_ready']}")
        print(f"Ratios: {result['ratios']}")
    
    elif command == "active":
        active = get_active_batches()
        if not active:
            print("No active batches")
        else:
            for batch in active:
                print(f"Batch {batch['batch_id']}: {batch['status']}")
                if batch['start_time']:
                    start = datetime.datetime.fromisoformat(batch['start_time'])
                    elapsed = datetime.datetime.now() - start
                    print(f"  Running for: {elapsed}")
    
    elif command == "history":
        history = load_batch_history()
        print(f"Total batches: {len(history)}")
        for batch in history[-5:]:  # Show last 5
            status = batch['status']
            quality = batch.get('quality_rating', 'N/A')
            print(f"  {batch['batch_id']}: {status} (Quality: {quality})")