# CAT Implementation Guide

Practical patterns for building computerized adaptive test systems.

## Architecture Overview

**Core components:**

1. **Item bank** — Database of calibrated items with IRT parameters
2. **CAT engine** — Selects items, estimates ability, applies stopping rule
3. **Session manager** — Tracks student progress, handles state
4. **Reporting** — Ability estimate, confidence interval, recommendations

**Data flow:**
```
Student → Answer → Update θ estimate → Select next item → Present item
                          ↓
                   Check stopping rule → End test → Report
```

## Technology Stack Options

### Python (Recommended for Startups)

**Pros:** Fast development, good IRT libraries, easy integration
**Cons:** Slower than compiled languages (not usually a problem)

**Core libraries:**
- `catsim` — Full CAT simulation framework
- `girth` — Fast IRT parameter estimation
- `numpy/scipy` — Numerical computation
- `fastapi` — API layer
- `sqlalchemy` — Database ORM

**Example stack:**
- Backend: FastAPI + PostgreSQL
- CAT logic: catsim
- Frontend: Next.js/React
- Deployment: Railway, Fly.io, or Render

### R (Best for Psychometrics Research)

**Pros:** Mature IRT ecosystem, publication-ready  
**Cons:** Harder to productionize

**Core libraries:**
- `catR` — CAT simulation
- `mirt` — IRT parameter estimation
- `shiny` — Web interface (if needed)

**Use when:** Building research prototypes, not production systems

### JavaScript/TypeScript (For Full-Stack Teams)

**Pros:** Single language across stack, browser-based CAT possible  
**Cons:** Limited IRT library support

**Approach:** Implement IRT math directly (it's not that complex), or port Python logic

### Commercial Platforms

- **FastTest** — White-label CAT platform
- **TAO** — Open-source testing platform (supports IRT)
- **AdaptiveTest.io** — SaaS CAT for K-12

**Use when:** Time-to-market matters more than customization

## Implementation Pattern (Python)

### 1. Item Bank Schema

```python
# models.py
from sqlalchemy import Column, Integer, Float, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)  # Question text
    content_area = Column(String)  # e.g., 'algebra', 'geometry'
    
    # IRT parameters
    discrimination = Column(Float)  # a parameter
    difficulty = Column(Float)      # b parameter
    guessing = Column(Float)        # c parameter (optional)
    
    # Operational stats
    times_used = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    
    # Metadata
    author = Column(String)
    created_at = Column(DateTime)
    reviewed = Column(Boolean, default=False)
```

### 2. CAT Engine Core

```python
# cat_engine.py
import numpy as np
from scipy.stats import norm
from scipy.optimize import fmin

class CATEngine:
    def __init__(self, item_bank, config):
        self.item_bank = item_bank
        self.config = config
        self.ability_estimate = 0.0  # Start at population mean
        self.se = 999  # Large initial SE
        self.items_used = []
        self.responses = []
        
    def probability(self, ability, item):
        """3PL model: P(correct | ability, a, b, c)"""
        a, b, c = item.discrimination, item.difficulty, item.guessing
        return c + (1 - c) / (1 + np.exp(-a * (ability - b)))
    
    def information(self, ability, item):
        """Fisher information at given ability"""
        p = self.probability(ability, item)
        a = item.discrimination
        c = item.guessing
        
        if c == 0:  # 2PL
            return a**2 * p * (1 - p)
        else:  # 3PL
            return a**2 * ((p - c)**2 / ((1 - c)**2 * p * (1 - p)))
    
    def estimate_ability_mle(self):
        """Maximum Likelihood Estimation"""
        def neg_log_likelihood(ability):
            ll = 0
            for item, response in zip(self.items_used, self.responses):
                p = self.probability(ability, item)
                ll += response * np.log(p) + (1 - response) * np.log(1 - p)
            return -ll
        
        # Optimize
        result = fmin(neg_log_likelihood, self.ability_estimate, disp=False)
        return float(result[0])
    
    def estimate_ability_eap(self):
        """Expected A Posteriori (better for extreme scores)"""
        # Prior: N(0, 1)
        theta_range = np.linspace(-4, 4, 100)
        prior = norm.pdf(theta_range, 0, 1)
        
        # Likelihood
        likelihood = np.ones_like(theta_range)
        for item, response in zip(self.items_used, self.responses):
            p = np.array([self.probability(t, item) for t in theta_range])
            likelihood *= p if response else (1 - p)
        
        # Posterior
        posterior = likelihood * prior
        posterior /= posterior.sum()
        
        # Expected value
        return np.sum(theta_range * posterior)
    
    def standard_error(self):
        """SE = 1 / sqrt(information)"""
        total_info = sum(self.information(self.ability_estimate, item) 
                        for item in self.items_used)
        return 1 / np.sqrt(total_info) if total_info > 0 else 999
    
    def select_next_item(self):
        """Randomesque: MFI from top 5"""
        # Filter unused items
        available = [item for item in self.item_bank 
                    if item.id not in [i.id for i in self.items_used]]
        
        if not available:
            return None
        
        # Compute information for each item
        info_scores = [(item, self.information(self.ability_estimate, item)) 
                      for item in available]
        
        # Sort by information, take top N
        info_scores.sort(key=lambda x: x[1], reverse=True)
        top_n = info_scores[:self.config['randomesque_n']]
        
        # Random selection from top N
        selected = np.random.choice([item for item, _ in top_n])
        return selected
    
    def should_stop(self):
        """Combined stopping rule"""
        n = len(self.responses)
        min_items = self.config['min_items']
        max_items = self.config['max_items']
        target_se = self.config['target_se']
        
        # Must answer at least min_items
        if n < min_items:
            return False
        
        # Stop if max_items reached
        if n >= max_items:
            return True
        
        # Stop if SE below target
        if self.se < target_se:
            return True
        
        return False
    
    def administer_item(self, item, response):
        """Process student response"""
        self.items_used.append(item)
        self.responses.append(response)
        
        # Update ability estimate
        if len(self.responses) >= 2:
            self.ability_estimate = self.estimate_ability_eap()
            self.se = self.standard_error()
        
        # Update item exposure tracking
        item.times_used += 1
        if response:
            item.times_correct += 1
```

### 3. API Endpoints

```python
# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class StartTestRequest(BaseModel):
    student_id: str
    test_type: str

class SubmitAnswerRequest(BaseModel):
    session_id: str
    item_id: int
    response: bool  # True = correct, False = incorrect

@app.post("/api/test/start")
async def start_test(req: StartTestRequest):
    # Load item bank
    item_bank = load_item_bank(req.test_type)
    
    # Initialize CAT engine
    config = {
        'min_items': 10,
        'max_items': 30,
        'target_se': 0.3,
        'randomesque_n': 5
    }
    engine = CATEngine(item_bank, config)
    
    # Create session
    session = create_session(req.student_id, engine)
    
    # Select first item
    first_item = engine.select_next_item()
    
    return {
        'session_id': session.id,
        'item': serialize_item(first_item)
    }

@app.post("/api/test/answer")
async def submit_answer(req: SubmitAnswerRequest):
    # Load session
    session = get_session(req.session_id)
    engine = session.engine
    
    # Get item
    item = get_item(req.item_id)
    
    # Process response
    engine.administer_item(item, req.response)
    
    # Check stopping rule
    if engine.should_stop():
        return {
            'finished': True,
            'ability': engine.ability_estimate,
            'se': engine.se,
            'items_used': len(engine.responses)
        }
    
    # Select next item
    next_item = engine.select_next_item()
    
    return {
        'finished': False,
        'item': serialize_item(next_item),
        'current_ability': engine.ability_estimate,
        'current_se': engine.se
    }
```

### 4. Content Balancing Extension

```python
def select_next_item_with_content_balance(self):
    """Select item that balances both information and content coverage"""
    # Track content area usage
    content_counts = {}
    for item in self.items_used:
        content_counts[item.content_area] = content_counts.get(item.content_area, 0) + 1
    
    # Target proportions (from test blueprint)
    target_props = self.config['content_balance']  # e.g., {'algebra': 0.4, 'geometry': 0.3, ...}
    
    # Available items
    available = [item for item in self.item_bank 
                if item.id not in [i.id for i in self.items_used]]
    
    # Score each item
    scored_items = []
    for item in available:
        # Information score
        info = self.information(self.ability_estimate, item)
        
        # Content penalty (if overused)
        current_prop = content_counts.get(item.content_area, 0) / len(self.items_used)
        target_prop = target_props.get(item.content_area, 0.25)
        content_penalty = max(0, current_prop - target_prop)
        
        # Combined score
        score = info * (1 - content_penalty)
        scored_items.append((item, score))
    
    # Select from top N
    scored_items.sort(key=lambda x: x[1], reverse=True)
    top_n = scored_items[:self.config['randomesque_n']]
    
    return np.random.choice([item for item, _ in top_n])
```

## Performance Optimization

### Database Indexing

```sql
-- Essential indexes
CREATE INDEX idx_items_difficulty ON items(difficulty);
CREATE INDEX idx_items_content ON items(content_area);
CREATE INDEX idx_items_exposure ON items(times_used);

-- Composite for content-balanced selection
CREATE INDEX idx_items_content_difficulty ON items(content_area, difficulty);
```

### Caching Item Bank

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def load_item_bank(test_type):
    """Cache item bank in memory"""
    return db.query(Item).filter_by(test_type=test_type).all()
```

### Pre-compute Information

Store information function values for grid of abilities:

```python
# During calibration
ability_grid = np.linspace(-3, 3, 61)  # 0.1 increments
for item in items:
    item.info_table = [information(theta, item) for theta in ability_grid]
    
# During CAT
def fast_information(ability, item):
    """Interpolate from pre-computed table"""
    idx = int((ability + 3) / 0.1)
    return item.info_table[idx]
```

## Testing & Validation

### Unit Tests

```python
def test_probability_function():
    """Test 3PL probability calculation"""
    item = Item(discrimination=1.0, difficulty=0.0, guessing=0.25)
    engine = CATEngine([item], {})
    
    # At ability = difficulty, P should be midpoint between c and 1
    p = engine.probability(0.0, item)
    expected = 0.25 + (1 - 0.25) * 0.5
    assert abs(p - expected) < 0.01

def test_stopping_rule():
    """Test that stopping rule triggers correctly"""
    # ... create mock engine with known SE
    # ... verify should_stop() behavior
```

### Simulation Testing

```python
def simulate_cat_session(true_ability, item_bank, config):
    """Simulate a CAT session with known ability"""
    engine = CATEngine(item_bank, config)
    
    while not engine.should_stop():
        item = engine.select_next_item()
        
        # Simulate response based on true ability
        p_correct = engine.probability(true_ability, item)
        response = np.random.random() < p_correct
        
        engine.administer_item(item, response)
    
    return {
        'true_ability': true_ability,
        'estimated_ability': engine.ability_estimate,
        'se': engine.se,
        'items_used': len(engine.responses),
        'error': abs(true_ability - engine.ability_estimate)
    }

# Run 1000 simulations
results = [simulate_cat_session(np.random.normal(0, 1), item_bank, config) 
           for _ in range(1000)]

# Analyze
print(f"Mean error: {np.mean([r['error'] for r in results]):.3f}")
print(f"Mean SE: {np.mean([r['se'] for r in results]):.3f}")
print(f"Mean length: {np.mean([r['items_used'] for r in results]):.1f}")
```

## Deployment Checklist

- [ ] Item bank loaded and indexed
- [ ] IRT parameters validated (no negative a, extreme b)
- [ ] Content balance targets configured
- [ ] Stopping rules tested across ability range
- [ ] Session persistence (DB or Redis)
- [ ] Exposure tracking enabled
- [ ] Simulation results acceptable (bias < 0.1, RMSE < 0.3)
- [ ] API rate limiting configured
- [ ] Monitoring: test length, SE distribution, item exposure
- [ ] Backup/recovery for live sessions

## Common Issues

**Problem:** Test too long for some students  
**Fix:** Lower target SE or add max items cap

**Problem:** Some items never used  
**Fix:** Check if b parameters are outside typical ability range

**Problem:** Ability estimates jump wildly  
**Fix:** Use EAP instead of MLE, especially early in test

**Problem:** Same items appear frequently  
**Fix:** Increase randomesque N, add exposure control

**Problem:** Content imbalance  
**Fix:** Implement content-weighted selection (see above)

## Resources

- **catsim documentation:** https://douglasrizzo.github.io/catsim/
- **IRT in Python tutorial:** https://irt.psychometricsociety.org/
- **FastAPI:** https://fastapi.tiangolo.com/
