# Whoop API Reference

## Authentication

Whoop uses OAuth 2.0 for authentication. To get an API token:

1. Go to https://app.whoop.com/
2. Navigate to Settings → Developer
3. Create a new application
4. Complete OAuth flow to get access token
5. Store token in `~/.whoop_token` or set `WHOOP_API_TOKEN` environment variable

Token refresh is required when token expires (check API response for 401 errors).

## API Endpoints

Base URL: `https://api.prod.whoop.com/developer/v2`
Activity Base URL: `https://api.prod.whoop.com/developer/v2/activity`

### Profile
- **GET** `/user/profile/basic` - Get user profile information

### Body Measurement
- **GET** `/user/body_measurement` - ⚠️ Not available in v2 (may be v1-only or deprecated)
- Would return: height, weight, max heart rate

### Recovery
- **GET** `/recovery` - Get recovery scores and metrics (collection)
- **GET** `/recovery/{cycleId}` - ⚠️ Not available in v2 (use collection endpoint instead)
- Query params: `start`, `end`, `limit`
- Returns: Recovery score, HRV, RHR, skin temp, SpO2

### Sleep
- **GET** `/activity/sleep` - Get sleep data (note: under /activity/)
- Query params: `start`, `end`, `limit`
- Returns: Sleep performance, duration, quality, stages, sleep debt

### Cycle
- **GET** `/cycle` - Get physiological cycle data (daily strain)
- Query params: `start`, `end`, `limit`
- Returns: Strain score, calories, avg HR, max HR

### Workout
- **GET** `/activity/workout` - Get workout activities (note: under /activity/)
- Query params: `start`, `end`, `limit`
- Returns: Workout type, strain, duration, HR data, distance

## Data Interpretation

### Recovery Score (0-100%)
- **Green (67-100%)**: Body is well-recovered, ready for high strain
- **Yellow (34-66%)**: Adequate recovery, moderate strain recommended
- **Red (0-33%)**: Body needs rest, prioritize recovery

**Key metrics:**
- **HRV (Heart Rate Variability)**: Higher = better recovery. Baseline varies by individual (30-100ms typical)
- **RHR (Resting Heart Rate)**: Lower = better recovery. Track trends, not absolute values
- **Respiratory Rate**: 12-20 breaths/min typical. Elevated = potential stress/illness
- **Skin Temperature**: Deviation from baseline can indicate illness/stress

### Sleep Performance (0-100%)
- Based on sleep need vs actual sleep duration
- **Debt/Credit**: Running sleep debt reduces performance over time
- **Quality**: REM and SWS (slow-wave sleep) percentage
- **Consistency**: Regular sleep schedule improves recovery

**Optimal sleep:**
- 7-9 hours total
- 20-25% REM sleep
- 15-20% slow-wave sleep (SWS)
- <30 min awake time

### Strain Score (0-21)
- Cumulative cardiovascular load for the day
- **0-9**: Light day (rest/recovery)
- **10-13**: Moderate strain
- **14-17**: High strain
- **18-21**: All-out effort

**Optimal strain:**
- Match strain to recovery (high recovery = can handle high strain)
- Avoid consecutive high-strain days without adequate recovery
- Average 12-15 strain is typical for active individuals

### Trends to Watch

**Positive trends:**
- HRV increasing over weeks
- RHR decreasing or stable
- Consistent sleep schedule
- Recovery matching or exceeding strain

**Warning signs:**
- HRV dropping significantly (>15% below baseline)
- RHR elevated for multiple days
- Sleep debt accumulating
- Low recovery with high strain demands

## Common Use Cases

### Morning Briefing
```python
data = client.get_today_summary()
# Check recovery, sleep, current strain
# Provide recommendations based on metrics
```

### Weekly Analysis
```python
recovery = client.get_recovery(limit=7)
sleep = client.get_sleep(limit=7)
# Analyze trends, identify patterns
# Suggest adjustments to training/sleep
```

### Real-time Alerts
- HRV drops >20% from baseline → Consider rest day
- Sleep performance <50% for 3+ days → Prioritize sleep
- Strain >18 with recovery <33% → Warning about overtraining
