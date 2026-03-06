# Session Data Segregation Strategy

## Problem

In conversational use, when querying multiple FileWave servers in the same session:

```
Me: "Show me all macOS devices"
Kit: [queries lab server, returns 5 devices]

Me: "Compare that to production"
Kit: [queries production server, returns 12 devices]

Me: "Which server has more?"
Kit: ??? [at risk of mixing data]
```

Without explicit segregation, I (Kit) could:
- Forget which data came from which server
- Accidentally compare data from wrong servers
- Return incorrect aggregations

## Solution: Session Data Registry

Keep an **in-session data registry** that tracks:
1. Every query executed
2. Source server for each result
3. Timestamp of each query
4. Query ID used
5. Device count
6. Named references for cross-server comparison

### Data Structure

```python
session_data = {
    "queries": [
        {
            "id": 1,
            "timestamp": "2026-02-12T10:15:00Z",
            "server": "lab",
            "profile": "lab",
            "query_id": 1,
            "device_count": 5,
            "devices": [...],
            "reference": "lab_macos"  # User-friendly name
        },
        {
            "id": 2,
            "timestamp": "2026-02-12T10:16:00Z",
            "server": "production",
            "profile": "production",
            "query_id": 1,
            "device_count": 12,
            "devices": [...],
            "reference": "prod_macos"  # User-friendly name
        }
    ]
}
```

### Session Manager Implementation

```python
class SessionDataManager:
    def __init__(self):
        self.queries = []
        self.result_index = {}  # Reference → query data
    
    def record_query(self, server, profile, query_id, devices, reference=None):
        """Record a query result with full context."""
        query_result = {
            "id": len(self.queries) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "server": server,
            "profile": profile,
            "query_id": query_id,
            "device_count": len(devices),
            "devices": devices,
            "reference": reference or f"query_{len(self.queries)+1}"
        }
        self.queries.append(query_result)
        self.result_index[query_result["reference"]] = query_result
        return query_result
    
    def get_reference(self, ref):
        """Retrieve data by reference name."""
        return self.result_index.get(ref)
    
    def list_queries(self):
        """Show all queries in this session."""
        for q in self.queries:
            print(f"[{q['id']}] {q['reference']}: {q['device_count']} devices from {q['server']}")
    
    def compare(self, ref1, ref2):
        """Compare two result sets with source context."""
        q1 = self.result_index.get(ref1)
        q2 = self.result_index.get(ref2)
        
        if not (q1 and q2):
            return None
        
        return {
            "query1": {"reference": ref1, "server": q1["server"], "count": q1["device_count"]},
            "query2": {"reference": ref2, "server": q2["server"], "count": q2["device_count"]},
            "difference": q2["device_count"] - q1["device_count"]
        }
```

## Response Format with Server Context

### Single Server Query

```
Query: [lab] Inventory Query #1
Timestamp: 2026-02-12 10:15:00 UTC
Result Reference: lab_query

Found 5 devices (from lab):
  • Device1
  • Device2
  ...
```

### Multi-Server Comparison

```
Comparing production vs lab:

Lab [lab_query]:
  - Query ID: 1
  - Devices: 5
  - Last updated: 2026-02-12 10:15:00 UTC

Production [prod_query]:
  - Query ID: 1
  - Devices: 12
  - Last updated: 2026-02-12 10:16:00 UTC

Difference: Production has 7 more devices than lab
```

## Conversation Flow Example

**With explicit data segregation:**

```
Me: "Show macOS devices from lab"

Kit: Recording query [lab_macos]
     Querying lab server...
     
     ✓ Lab Inventory (lab_macos): 5 macOS devices
       • Device1 (Monterey)
       • Device2 (Sonoma)
       • Device3 (Sequoia)
       • Device4 (Tahoe)
       • Device5 (Monterey)

Me: "Now check production"

Kit: Recording query [prod_macos]
     Querying production server...
     
     ✓ Production Inventory (prod_macos): 12 macOS devices
       • DeviceA (Sonoma)
       • DeviceB (Sequoia)
       ... (10 more)

Me: "Which server has more devices?"

Kit: Comparing [lab_macos] vs [prod_macos]
     
     Lab:        5 devices
     Production: 12 devices
     
     Production has 7 more macOS devices.
     
     (Using explicitly tracked data from queries recorded above)

Me: "Show me stale devices (not seen in 30 days) from both"

Kit: Querying both servers...
     
     Lab stale (30+ days) [lab_stale]:
       • OldDevice1 (last seen 45 days ago)
       • OldDevice2 (last seen 60 days ago)
     
     Production stale (30+ days) [prod_stale]:
       • OldProdDevice1 (last seen 50 days ago)
       • OldProdDevice2 (last seen 35 days ago)
       • OldProdDevice3 (last seen 90 days ago)
     
     Stale device summary:
       Lab:        2 stale devices
       Production: 3 stale devices
       
       (Tracked via [lab_stale] and [prod_stale])
```

## Visual Segregation in Chat

### Color/Badge Approach (if supported)

```
🏷️ [lab] macOS inventory
   Devices: 5
   • Device1 (Monterey)
   • Device2 (Sonoma)

🏷️ [production] macOS inventory
   Devices: 12
   • DeviceA (Sonoma)
   • DeviceB (Sequoia)

⚖️ Comparison: Production has 7 more
```

### Plain Text Approach (Signal safe)

```
=== Lab Server (lab_macos) ===
Devices: 5
• Device1 (Monterey)
• Device2 (Sonoma)

=== Production Server (prod_macos) ===
Devices: 12
• DeviceA (Sonoma)
• DeviceB (Sequoia)

--- Comparison ---
Production: +7 devices
```

## Query Reference Naming

Automatic generation helps track queries:

```
[lab_macos]
[prod_macos]
[lab_stale_30days]
[prod_stale_30days]
[lab_vs_prod_compliance]
```

Or user-provided names:

```
Me: "Check iOS devices on lab (call it lab_ios_fleet)"

Kit: Recording query [lab_ios_fleet]
     ...
```

## Preventing Confusion

### Explicit Query Log

At any point, I can show what's been tracked:

```
Me: "What have we queried so far?"

Kit: Session Query Log:
     [1] lab_macos        → Lab, 5 devices (2026-02-12 10:15:00)
     [2] prod_macos       → Production, 12 devices (2026-02-12 10:16:00)
     [3] lab_stale_30days → Lab, 2 devices (2026-02-12 10:17:00)
```

### Validation Before Cross-Server Operations

Before comparing or aggregating:

```
# Pseudocode in Python
def compare_results(ref1, ref2):
    q1 = session.get_reference(ref1)
    q2 = session.get_reference(ref2)
    
    # Validation
    if q1["server"] == q2["server"]:
        print(f"Warning: Both queries from {q1['server']}")
        print("Comparing data from same server. Did you mean different servers?")
    
    # Proceed with explicit source tracking
    return {
        "source1": q1["server"],
        "source2": q2["server"],
        "comparison": ...
    }
```

## Implementation Plan

### Phase 1: Session Registry
- [ ] SessionDataManager class
- [ ] Record all queries with metadata
- [ ] Provide query history
- [ ] Reference tracking

### Phase 2: Response Formatting
- [ ] Include server context in all responses
- [ ] Named references for queries
- [ ] Visual separation in chat

### Phase 3: Cross-Server Operations
- [ ] Compare function with validation
- [ ] Aggregation across servers (with source tracking)
- [ ] Safe multi-server analysis

## Benefits

✅ **No confusion** — Always know which server data came from  
✅ **Traceable** — Full history of queries in session  
✅ **Safe comparisons** — Validate before cross-server operations  
✅ **Referenceable** — Can refer back to earlier queries  
✅ **Explicit** — User and Kit both see server context  
✅ **Scalable** — Works with 1 server or 10 servers  

## Example Session Log

```
Session: 2026-02-12_10-15-00
User: Josh Levitsky
Server Profiles Available: [lab, production, test]

Query #1 [lab_macos]
  Time: 10:15:00
  Server: lab
  QueryID: 1
  Result: 5 devices
  
Query #2 [prod_macos]
  Time: 10:16:00
  Server: production
  QueryID: 1
  Result: 12 devices

Comparison #1 [lab_vs_prod_macos]
  Query1: [lab_macos] (lab, 5)
  Query2: [prod_macos] (production, 12)
  Result: Production +7 devices

Query #3 [lab_stale]
  Time: 10:17:00
  Server: lab
  QueryID: 2
  Filter: last_seen > 30 days
  Result: 2 devices

Summary:
  Total queries: 3
  Servers queried: lab (2), production (1)
  Data operations: 1 comparison
```

## Notes

- **Not a database** — Session data lives in memory, cleared when session ends
- **For conversation** — Designed for interactive Q&A with Kit
- **Prevents accidents** — Explicit tracking prevents mixing data
- **Audit trail** — Full history in session for verification
