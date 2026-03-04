"""
Sifter - Core validation and signal extraction engine
"""

import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime


class Sifter:
    """Validates and extracts signals from data."""
    
    def __init__(self, rules: str = "json-strict"):
        self.rules = rules
        self.rule_sets = self._load_rule_sets()
    
    def _load_rule_sets(self) -> Dict[str, Dict]:
        """Load validation rule definitions."""
        return {
            "json-strict": {
                "name": "JSON Strict",
                "checks": ["structure", "types", "required_fields"],
            },
            "crypto": {
                "name": "Crypto Data",
                "checks": ["structure", "types", "required_fields", "crypto_fields", "price_validity"],
                "required_fields": ["symbol", "price"],
                "numeric_fields": ["price", "volume", "change_pct"],
            },
            "trading": {
                "name": "Trading Data",
                "checks": ["structure", "types", "required_fields", "trading_fields", "order_validity"],
                "required_fields": ["order_id", "symbol", "side", "price", "quantity"],
            },
            "sentiment": {
                "name": "Sentiment Data",
                "checks": ["structure", "required_fields", "text_fields", "score_validity"],
                "required_fields": ["text", "score"],
            },
        }
    
    def validate(self, data: Any, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Validate data against schema or rules.
        
        Returns:
        {
            "status": "validated|failed",
            "score": 0.0-1.0,
            "clean_data": {...},
            "issues": [...],
            "metadata": {...}
        }
        """
        start_time = time.time()
        issues = []
        clean_data = data.copy() if isinstance(data, dict) else data
        
        try:
            # Basic structure check
            if not isinstance(data, (dict, list)):
                issues.append({
                    "issue": "data_not_json",
                    "severity": "error",
                    "description": "Data must be dict or list"
                })
                return self._result("failed", 0.0, clean_data, issues, start_time)
            
            # Get rule set
            rule_set = self.rule_sets.get(self.rules, self.rule_sets["json-strict"])
            
            # Run checks
            for check in rule_set.get("checks", []):
                check_issues = self._run_check(check, data, rule_set)
                issues.extend(check_issues)
            
            # If user provided schema, validate against it
            if schema:
                schema_issues = self._validate_against_schema(data, schema)
                issues.extend(schema_issues)
            
            # Calculate score
            score = self._calculate_score(data, issues)
            status = "validated" if score > 0.7 else "failed"
            
            return self._result(status, score, clean_data, issues, start_time)
        
        except Exception as e:
            issues.append({
                "issue": "validation_error",
                "severity": "error",
                "description": str(e)
            })
            return self._result("failed", 0.0, clean_data, issues, start_time)
    
    def sift(self, data: Any) -> Dict[str, Any]:
        """
        Sift data for high-confidence signals.
        Filters and scores entries based on signal strength.
        """
        start_time = time.time()
        
        if not isinstance(data, (list, dict)):
            return self._result("failed", 0.0, [], [], start_time)
        
        entries = data if isinstance(data, list) else [data]
        sifted = []
        
        for entry in entries:
            if isinstance(entry, dict):
                score = self._signal_score(entry)
                if score > 0.5:  # Keep entries with 50%+ signal strength
                    sifted.append({
                        "data": entry,
                        "signal_score": score
                    })
        
        # Sort by signal score descending
        sifted.sort(key=lambda x: x["signal_score"], reverse=True)
        
        return self._result("sifted", len(sifted) / len(entries) if entries else 0, sifted, [], start_time)
    
    def _run_check(self, check: str, data: Any, rule_set: Dict) -> List[Dict]:
        """Run a specific validation check."""
        issues = []
        
        if check == "structure":
            if not isinstance(data, (dict, list)):
                issues.append({
                    "field": "_root",
                    "issue": "invalid_structure",
                    "severity": "error"
                })
        
        elif check == "types":
            if isinstance(data, dict):
                for key, value in data.items():
                    if value is None:
                        issues.append({
                            "field": key,
                            "issue": "null_value",
                            "severity": "warning"
                        })
        
        elif check == "required_fields":
            required = rule_set.get("required_fields", [])
            if isinstance(data, dict) and required:
                for field in required:
                    if field not in data or data.get(field) is None:
                        issues.append({
                            "field": field,
                            "issue": "missing_required_field",
                            "severity": "error"
                        })
        
        elif check == "crypto_fields":
            if isinstance(data, dict):
                if "price" in data:
                    try:
                        float(data["price"])
                    except (ValueError, TypeError):
                        issues.append({
                            "field": "price",
                            "issue": "invalid_price_format",
                            "severity": "error"
                        })
        
        elif check == "price_validity":
            if isinstance(data, dict) and "price" in data:
                try:
                    price = float(data["price"])
                    if price < 0:
                        issues.append({
                            "field": "price",
                            "issue": "negative_price",
                            "severity": "error"
                        })
                except (ValueError, TypeError):
                    pass
        
        elif check == "trading_fields":
            if isinstance(data, dict):
                required = ["order_id", "symbol", "side", "price", "quantity"]
                for field in required:
                    if field not in data:
                        issues.append({
                            "field": field,
                            "issue": "missing_trading_field",
                            "severity": "error"
                        })
        
        elif check == "text_fields":
            if isinstance(data, dict):
                if "text" in data and not isinstance(data["text"], str):
                    issues.append({
                        "field": "text",
                        "issue": "text_not_string",
                        "severity": "error"
                    })
        
        elif check == "score_validity":
            if isinstance(data, dict) and "score" in data:
                try:
                    score = float(data["score"])
                    if not 0 <= score <= 1:
                        issues.append({
                            "field": "score",
                            "issue": "score_out_of_range",
                            "severity": "warning"
                        })
                except (ValueError, TypeError):
                    pass
        
        return issues
    
    def _validate_against_schema(self, data: Any, schema: Dict) -> List[Dict]:
        """Validate data against a JSON schema."""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        # Check required fields
        for field in schema.get("required", []):
            if field not in data:
                issues.append({
                    "field": field,
                    "issue": "missing_required_field",
                    "severity": "error"
                })
        
        # Check field types
        properties = schema.get("properties", {})
        for field, field_schema in properties.items():
            if field in data:
                expected_type = field_schema.get("type")
                if expected_type:
                    actual_type = type(data[field]).__name__
                    # Map Python types to JSON types
                    type_map = {
                        "str": "string",
                        "int": "integer",
                        "float": "number",
                        "bool": "boolean",
                        "dict": "object",
                        "list": "array",
                    }
                    if type_map.get(actual_type) != expected_type:
                        issues.append({
                            "field": field,
                            "issue": f"type_mismatch",
                            "expected": expected_type,
                            "actual": type_map.get(actual_type),
                            "severity": "error"
                        })
        
        return issues
    
    def _signal_score(self, entry: Dict) -> float:
        """Calculate signal strength (0-1) for an entry."""
        if not isinstance(entry, dict):
            return 0.0
        
        score = 0.5  # Base score
        
        # Bonus for data completeness
        if len(entry) > 2:
            score += 0.2
        
        # Bonus for numeric data quality
        numeric_fields = [v for v in entry.values() if isinstance(v, (int, float))]
        if numeric_fields:
            score += 0.2
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _calculate_score(self, data: Any, issues: List[Dict]) -> float:
        """Calculate validation score (0-1)."""
        if not issues:
            return 1.0
        
        # Count error severity
        errors = len([i for i in issues if i.get("severity") == "error"])
        warnings = len([i for i in issues if i.get("severity") == "warning"])
        
        # Deduct points
        score = 1.0
        score -= errors * 0.3
        score -= warnings * 0.05
        
        return max(score, 0.0)
    
    def _result(self, status: str, score: float, data: Any, issues: List[Dict], start_time: float) -> Dict:
        """Format result."""
        return {
            "status": status,
            "score": round(score, 2),
            "clean_data": data,
            "issues": issues,
            "metadata": {
                "rule_set": self.rules,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "processing_ms": int((time.time() - start_time) * 1000),
            }
        }
