#!/usr/bin/env python3
"""
Session data manager for FileWave skill.

Tracks all queries executed in a session with full server context to prevent
data confusion when working with multiple FileWave servers.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict


@dataclass
class QueryResult:
    """Represents a single query execution."""
    
    id: int
    timestamp: str
    server: str
    profile: str
    query_id: int
    device_count: int
    devices: List[Dict[str, Any]] = field(default_factory=list)
    reference: str = ""
    filter_description: str = ""  # e.g., "last_seen > 30 days"
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    def __str__(self):
        return f"[{self.reference}] {self.server}: {self.device_count} devices"


@dataclass
class ComparisonResult:
    """Result of comparing two query result sets."""
    
    query1_ref: str
    query2_ref: str
    query1_count: int
    query2_count: int
    difference: int
    comparison_timestamp: str
    
    def __str__(self):
        q1_desc = f"{self.query1_ref} ({self.query1_count})"
        q2_desc = f"{self.query2_ref} ({self.query2_count})"
        
        if self.difference > 0:
            return f"{q2_desc} has {abs(self.difference)} more than {q1_desc}"
        elif self.difference < 0:
            return f"{q1_desc} has {abs(self.difference)} more than {q2_desc}"
        else:
            return f"{q1_desc} and {q2_desc} are equal"


class SessionDataManager:
    """Manage query data across a session with server context tracking."""
    
    def __init__(self):
        self.queries: List[QueryResult] = []
        self.result_index: Dict[str, QueryResult] = {}
        self.comparisons: List[ComparisonResult] = []
        self.bulk_updates: List[Dict[str, Any]] = []
        self.session_start = datetime.now(timezone.utc).isoformat()
    
    def record_query(
        self,
        server: str,
        profile: str,
        query_id: int,
        devices: List[Dict[str, Any]],
        reference: Optional[str] = None,
        filter_description: str = ""
    ) -> QueryResult:
        """Record a query result with full context.
        
        Args:
            server: Server URL or hostname
            profile: Profile name used (lab, production, test, etc.)
            query_id: FileWave Inventory Query ID
            devices: List of device objects returned
            reference: User-friendly reference name (auto-generated if not provided)
            filter_description: Description of any filters applied
        
        Returns:
            QueryResult object
        """
        query_num = len(self.queries) + 1
        
        # Generate reference if not provided
        if not reference:
            reference = f"query_{query_num}_{profile}"
        
        result = QueryResult(
            id=query_num,
            timestamp=datetime.now(timezone.utc).isoformat(),
            server=server,
            profile=profile,
            query_id=query_id,
            device_count=len(devices),
            devices=devices,
            reference=reference,
            filter_description=filter_description
        )
        
        self.queries.append(result)
        self.result_index[reference] = result
        
        return result
    
    def get_reference(self, ref: str) -> Optional[QueryResult]:
        """Retrieve query result by reference name."""
        return self.result_index.get(ref)
    
    def list_references(self) -> List[str]:
        """List all recorded reference names."""
        return list(self.result_index.keys())
    
    def list_queries(self, server: Optional[str] = None) -> List[QueryResult]:
        """List all queries in session, optionally filtered by server."""
        if server:
            return [q for q in self.queries if q.server == server or q.profile == server]
        return self.queries
    
    def print_query_log(self, server: Optional[str] = None):
        """Print formatted query log."""
        queries = self.list_queries(server)
        
        if not queries:
            print("No queries recorded in session.")
            return
        
        print("\n=== Session Query Log ===\n")
        for q in queries:
            filter_info = f" (filter: {q.filter_description})" if q.filter_description else ""
            print(f"[{q.reference}]")
            print(f"  Server: {q.server} (profile: {q.profile})")
            print(f"  Query ID: {q.query_id}")
            print(f"  Devices: {q.device_count}{filter_info}")
            print(f"  Time: {q.timestamp}")
            print()
    
    def compare(self, ref1: str, ref2: str) -> Optional[ComparisonResult]:
        """Compare two result sets with full context.
        
        Returns ComparisonResult or None if references not found.
        """
        q1 = self.result_index.get(ref1)
        q2 = self.result_index.get(ref2)
        
        if not (q1 and q2):
            missing = []
            if not q1:
                missing.append(ref1)
            if not q2:
                missing.append(ref2)
            print(f"ERROR: Reference(s) not found: {', '.join(missing)}")
            return None
        
        # Warn if comparing same server
        if q1.server == q2.server:
            print(f"⚠️  Warning: Both queries from {q1.server}")
            print(f"   Comparing [{ref1}] vs [{ref2}] from same server")
        
        result = ComparisonResult(
            query1_ref=ref1,
            query2_ref=ref2,
            query1_count=q1.device_count,
            query2_count=q2.device_count,
            difference=q2.device_count - q1.device_count,
            comparison_timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.comparisons.append(result)
        return result
    
    def get_servers(self) -> List[str]:
        """Get list of unique servers queried in session."""
        return sorted(set(q.server for q in self.queries))
    
    def get_profiles(self) -> List[str]:
        """Get list of unique profiles used in session."""
        return sorted(set(q.profile for q in self.queries))
    
    def record_bulk_update(
        self,
        server: str,
        profile: str,
        csv_file: str,
        device_count: int,
        successful: int,
        failed: int
    ):
        """Record a bulk device update operation."""
        update_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": server,
            "profile": profile,
            "csv_file": csv_file,
            "device_count": device_count,
            "successful": successful,
            "failed": failed
        }
        self.bulk_updates.append(update_record)
    
    def aggregate_by_server(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate query statistics by server."""
        stats = {}
        
        for query in self.queries:
            if query.server not in stats:
                stats[query.server] = {
                    "server": query.server,
                    "profiles": set(),
                    "total_devices": 0,
                    "query_count": 0,
                    "queries": []
                }
            
            stats[query.server]["profiles"].add(query.profile)
            stats[query.server]["total_devices"] += query.device_count
            stats[query.server]["query_count"] += 1
            stats[query.server]["queries"].append(query.reference)
        
        # Convert sets to lists for JSON serialization
        for server in stats:
            stats[server]["profiles"] = sorted(stats[server]["profiles"])
        
        return stats
    
    def export_session(self) -> Dict[str, Any]:
        """Export session data as dictionary (for JSON serialization)."""
        return {
            "session_start": self.session_start,
            "queries": [q.to_dict() for q in self.queries],
            "comparisons": [asdict(c) for c in self.comparisons],
            "bulk_updates": self.bulk_updates,
            "servers": self.get_servers(),
            "profiles": self.get_profiles(),
            "summary": self.aggregate_by_server()
        }
    
    def export_json(self, filepath: str):
        """Export session data to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.export_session(), f, indent=2)
        print(f"Session exported to: {filepath}")
    
    def print_summary(self):
        """Print session summary."""
        print("\n=== Session Summary ===\n")
        print(f"Start time: {self.session_start}")
        print(f"Total queries: {len(self.queries)}")
        print(f"Total comparisons: {len(self.comparisons)}")
        print(f"Bulk updates: {len(self.bulk_updates)}")
        print(f"Servers queried: {', '.join(self.get_servers())}")
        print(f"Profiles used: {', '.join(self.get_profiles())}")
        print()
        
        # Per-server stats
        stats = self.aggregate_by_server()
        for server, data in stats.items():
            print(f"{server}:")
            print(f"  Profiles: {', '.join(data['profiles'])}")
            print(f"  Queries: {data['query_count']}")
            print(f"  Total devices: {data['total_devices']}")
        
        # Bulk updates summary
        if self.bulk_updates:
            print("\nBulk Updates:")
            for update in self.bulk_updates:
                print(f"  {update['timestamp']}: {update['profile']} ({update['successful']}/{update['device_count']})")


# Example usage
if __name__ == "__main__":
    mgr = SessionDataManager()
    
    # Simulate queries
    lab_devices = [
        {"name": "Device1", "os": "macOS"},
        {"name": "Device2", "os": "macOS"},
        {"name": "Device3", "os": "iOS"}
    ]
    
    prod_devices = [
        {"name": "ProdDevice1", "os": "macOS"},
        {"name": "ProdDevice2", "os": "macOS"},
        {"name": "ProdDevice3", "os": "macOS"},
        {"name": "ProdDevice4", "os": "iOS"},
        {"name": "ProdDevice5", "os": "iOS"}
    ]
    
    # Record queries
    lab_result = mgr.record_query(
        server="filewave.company.com",
        profile="lab",
        query_id=1,
        devices=lab_devices,
        reference="lab_macos"
    )
    
    prod_result = mgr.record_query(
        server="filewave.company.com",
        profile="production",
        query_id=1,
        devices=prod_devices,
        reference="prod_macos"
    )
    
    print("Recorded queries:")
    print(f"  {lab_result}")
    print(f"  {prod_result}")
    
    # Compare
    comparison = mgr.compare("lab_macos", "prod_macos")
    print(f"\nComparison: {comparison}")
    
    # Print logs
    mgr.print_query_log()
    mgr.print_summary()
