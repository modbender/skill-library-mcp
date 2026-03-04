---
name: "open-data-integrator"
description: "Integrate open construction datasets. Combine open data sources for enhanced analysis"
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🌐", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Open Data Integrator

## Overview

Based on DDC methodology (Chapter 2.2), this skill integrates open construction datasets from various sources like government databases, industry benchmarks, weather services, and geospatial data.

**Book Reference:** "Доминирование открытых данных" / "Open Data Dominance"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, date
import json
import requests
from abc import ABC, abstractmethod

class DataSourceType(Enum):
    """Types of open data sources"""
    GOVERNMENT = "government"           # Government statistics
    INDUSTRY_BENCHMARK = "benchmark"    # Industry benchmarks
    WEATHER = "weather"                 # Weather data
    GEOSPATIAL = "geospatial"           # Geographic data
    MATERIAL_PRICES = "material_prices" # Material cost indices
    LABOR_RATES = "labor_rates"         # Labor cost data
    BUILDING_PERMITS = "permits"        # Permit data
    ENERGY = "energy"                   # Energy prices/data
    ECONOMIC = "economic"               # Economic indicators

class UpdateFrequency(Enum):
    """Data update frequency"""
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

@dataclass
class OpenDataSource:
    """Definition of an open data source"""
    id: str
    name: str
    source_type: DataSourceType
    url: str
    api_key_required: bool = False
    update_frequency: UpdateFrequency = UpdateFrequency.DAILY
    format: str = "json"
    license: str = "open"
    description: Optional[str] = None
    fields: List[str] = field(default_factory=list)

@dataclass
class DataRecord:
    """A single data record from a source"""
    source_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationResult:
    """Result of data integration"""
    source: str
    records_fetched: int
    records_processed: int
    errors: List[str]
    last_updated: datetime
    sample_data: List[Dict]

@dataclass
class EnrichedData:
    """Data enriched with open data"""
    original_data: Dict[str, Any]
    enrichments: Dict[str, Any]
    sources_used: List[str]
    confidence: float


class OpenDataConnector(ABC):
    """Base class for open data connectors"""

    @abstractmethod
    def fetch(self, params: Dict) -> List[DataRecord]:
        pass

    @abstractmethod
    def get_metadata(self) -> Dict:
        pass


class WeatherDataConnector(OpenDataConnector):
    """Connector for weather data (e.g., OpenWeatherMap)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def fetch(
        self,
        params: Dict
    ) -> List[DataRecord]:
        """Fetch weather data for location"""
        lat = params.get("lat")
        lon = params.get("lon")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        # Simulate API call (in production, use actual API)
        records = []

        # Generate sample historical data
        current = start_date
        while current <= end_date:
            records.append(DataRecord(
                source_id="openweathermap",
                timestamp=datetime.combine(current, datetime.min.time()),
                data={
                    "date": current.isoformat(),
                    "temp_max": 25.0,
                    "temp_min": 15.0,
                    "precipitation": 0.0,
                    "wind_speed": 10.0,
                    "weather_code": "clear"
                },
                metadata={"lat": lat, "lon": lon}
            ))
            current = date(current.year, current.month, current.day + 1) if current.day < 28 else date(current.year, current.month + 1 if current.month < 12 else 1, 1)

        return records[:30]  # Limit for demo

    def get_metadata(self) -> Dict:
        return {
            "source": "OpenWeatherMap",
            "type": DataSourceType.WEATHER.value,
            "frequency": UpdateFrequency.HOURLY.value,
            "fields": ["temp_max", "temp_min", "precipitation", "wind_speed"]
        }


class MaterialPriceConnector(OpenDataConnector):
    """Connector for material price indices"""

    def __init__(self, region: str = "US"):
        self.region = region
        self.price_indices = self._load_indices()

    def _load_indices(self) -> Dict[str, Dict]:
        """Load material price indices"""
        return {
            "concrete": {"base": 100, "current": 125, "trend": "up"},
            "steel": {"base": 100, "current": 145, "trend": "up"},
            "lumber": {"base": 100, "current": 180, "trend": "stable"},
            "copper": {"base": 100, "current": 135, "trend": "up"},
            "asphalt": {"base": 100, "current": 115, "trend": "stable"},
            "gypsum": {"base": 100, "current": 110, "trend": "stable"},
            "glass": {"base": 100, "current": 105, "trend": "down"},
            "cement": {"base": 100, "current": 120, "trend": "up"},
        }

    def fetch(self, params: Dict) -> List[DataRecord]:
        """Fetch material price data"""
        materials = params.get("materials", list(self.price_indices.keys()))

        records = []
        for material in materials:
            if material in self.price_indices:
                records.append(DataRecord(
                    source_id="material_prices",
                    timestamp=datetime.now(),
                    data={
                        "material": material,
                        "region": self.region,
                        **self.price_indices[material]
                    }
                ))
        return records

    def get_metadata(self) -> Dict:
        return {
            "source": "Material Price Index",
            "type": DataSourceType.MATERIAL_PRICES.value,
            "frequency": UpdateFrequency.MONTHLY.value,
            "materials": list(self.price_indices.keys())
        }


class LaborRateConnector(OpenDataConnector):
    """Connector for labor rate data"""

    def __init__(self, region: str = "US"):
        self.region = region
        self.labor_rates = self._load_rates()

    def _load_rates(self) -> Dict[str, Dict]:
        """Load labor rates by trade"""
        return {
            "carpenter": {"hourly": 45.00, "burden_rate": 1.35},
            "electrician": {"hourly": 55.00, "burden_rate": 1.40},
            "plumber": {"hourly": 52.00, "burden_rate": 1.38},
            "ironworker": {"hourly": 58.00, "burden_rate": 1.42},
            "laborer": {"hourly": 32.00, "burden_rate": 1.30},
            "operator": {"hourly": 48.00, "burden_rate": 1.35},
            "mason": {"hourly": 50.00, "burden_rate": 1.36},
            "painter": {"hourly": 38.00, "burden_rate": 1.32},
            "hvac_tech": {"hourly": 54.00, "burden_rate": 1.38},
            "welder": {"hourly": 52.00, "burden_rate": 1.40},
        }

    def fetch(self, params: Dict) -> List[DataRecord]:
        """Fetch labor rate data"""
        trades = params.get("trades", list(self.labor_rates.keys()))

        records = []
        for trade in trades:
            if trade in self.labor_rates:
                rate_data = self.labor_rates[trade]
                records.append(DataRecord(
                    source_id="labor_rates",
                    timestamp=datetime.now(),
                    data={
                        "trade": trade,
                        "region": self.region,
                        "hourly_rate": rate_data["hourly"],
                        "burden_rate": rate_data["burden_rate"],
                        "fully_loaded": rate_data["hourly"] * rate_data["burden_rate"]
                    }
                ))
        return records

    def get_metadata(self) -> Dict:
        return {
            "source": "Labor Rate Database",
            "type": DataSourceType.LABOR_RATES.value,
            "frequency": UpdateFrequency.QUARTERLY.value,
            "trades": list(self.labor_rates.keys())
        }


class BuildingPermitConnector(OpenDataConnector):
    """Connector for building permit data"""

    def __init__(self, jurisdiction: str = "default"):
        self.jurisdiction = jurisdiction

    def fetch(self, params: Dict) -> List[DataRecord]:
        """Fetch permit data"""
        # Simulate permit data
        permit_types = ["new_construction", "renovation", "addition", "demolition"]

        records = []
        for ptype in permit_types:
            records.append(DataRecord(
                source_id="building_permits",
                timestamp=datetime.now(),
                data={
                    "permit_type": ptype,
                    "jurisdiction": self.jurisdiction,
                    "count_ytd": 150,
                    "total_value": 25000000,
                    "avg_processing_days": 21
                }
            ))
        return records

    def get_metadata(self) -> Dict:
        return {
            "source": "Building Permit Database",
            "type": DataSourceType.BUILDING_PERMITS.value,
            "frequency": UpdateFrequency.DAILY.value
        }


class OpenDataIntegrator:
    """
    Integrate open construction datasets.
    Based on DDC methodology Chapter 2.2.
    """

    def __init__(self, region: str = "US"):
        self.region = region
        self.connectors: Dict[str, OpenDataConnector] = {}
        self.cache: Dict[str, List[DataRecord]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        self._register_default_connectors()

    def _register_default_connectors(self):
        """Register default data connectors"""
        self.register_connector("weather", WeatherDataConnector())
        self.register_connector("material_prices", MaterialPriceConnector(self.region))
        self.register_connector("labor_rates", LaborRateConnector(self.region))
        self.register_connector("permits", BuildingPermitConnector())

    def register_connector(
        self,
        name: str,
        connector: OpenDataConnector
    ):
        """Register a data connector"""
        self.connectors[name] = connector

    def fetch_data(
        self,
        source: str,
        params: Optional[Dict] = None,
        use_cache: bool = True
    ) -> IntegrationResult:
        """
        Fetch data from a source.

        Args:
            source: Name of the data source
            params: Query parameters
            use_cache: Whether to use cached data

        Returns:
            Integration result with fetched data
        """
        if source not in self.connectors:
            return IntegrationResult(
                source=source,
                records_fetched=0,
                records_processed=0,
                errors=[f"Unknown source: {source}"],
                last_updated=datetime.now(),
                sample_data=[]
            )

        # Check cache
        cache_key = f"{source}_{json.dumps(params or {}, sort_keys=True)}"
        if use_cache and cache_key in self.cache:
            expiry = self.cache_expiry.get(cache_key)
            if expiry and expiry > datetime.now():
                cached = self.cache[cache_key]
                return IntegrationResult(
                    source=source,
                    records_fetched=len(cached),
                    records_processed=len(cached),
                    errors=[],
                    last_updated=expiry,
                    sample_data=[r.data for r in cached[:5]]
                )

        # Fetch fresh data
        connector = self.connectors[source]
        errors = []

        try:
            records = connector.fetch(params or {})

            # Cache the results
            self.cache[cache_key] = records
            self.cache_expiry[cache_key] = datetime.now()

            return IntegrationResult(
                source=source,
                records_fetched=len(records),
                records_processed=len(records),
                errors=errors,
                last_updated=datetime.now(),
                sample_data=[r.data for r in records[:5]]
            )

        except Exception as e:
            errors.append(str(e))
            return IntegrationResult(
                source=source,
                records_fetched=0,
                records_processed=0,
                errors=errors,
                last_updated=datetime.now(),
                sample_data=[]
            )

    def enrich_project_data(
        self,
        project_data: Dict[str, Any],
        enrichment_sources: Optional[List[str]] = None
    ) -> EnrichedData:
        """
        Enrich project data with open data.

        Args:
            project_data: Original project data
            enrichment_sources: Sources to use for enrichment

        Returns:
            Enriched data
        """
        sources = enrichment_sources or ["material_prices", "labor_rates", "weather"]
        enrichments = {}
        sources_used = []

        # Material price enrichment
        if "material_prices" in sources and "materials" in project_data:
            materials = project_data["materials"]
            result = self.fetch_data("material_prices", {"materials": materials})
            if result.records_fetched > 0:
                enrichments["material_price_indices"] = result.sample_data
                sources_used.append("material_prices")

        # Labor rate enrichment
        if "labor_rates" in sources and "trades" in project_data:
            trades = project_data["trades"]
            result = self.fetch_data("labor_rates", {"trades": trades})
            if result.records_fetched > 0:
                enrichments["labor_rates"] = result.sample_data
                sources_used.append("labor_rates")

        # Weather enrichment
        if "weather" in sources and "location" in project_data:
            loc = project_data["location"]
            params = {
                "lat": loc.get("lat"),
                "lon": loc.get("lon"),
                "start_date": project_data.get("start_date", date.today()),
                "end_date": project_data.get("end_date", date.today())
            }
            result = self.fetch_data("weather", params)
            if result.records_fetched > 0:
                enrichments["weather_forecast"] = result.sample_data
                sources_used.append("weather")

        # Calculate confidence based on enrichment success
        confidence = len(sources_used) / len(sources) if sources else 0

        return EnrichedData(
            original_data=project_data,
            enrichments=enrichments,
            sources_used=sources_used,
            confidence=confidence
        )

    def get_cost_indices(
        self,
        materials: Optional[List[str]] = None,
        trades: Optional[List[str]] = None
    ) -> Dict:
        """Get current cost indices"""
        indices = {
            "timestamp": datetime.now().isoformat(),
            "region": self.region
        }

        if materials:
            result = self.fetch_data("material_prices", {"materials": materials})
            indices["materials"] = result.sample_data

        if trades:
            result = self.fetch_data("labor_rates", {"trades": trades})
            indices["labor"] = result.sample_data

        return indices

    def get_weather_risk(
        self,
        lat: float,
        lon: float,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Assess weather risk for project period"""
        result = self.fetch_data("weather", {
            "lat": lat,
            "lon": lon,
            "start_date": start_date,
            "end_date": end_date
        })

        if result.records_fetched == 0:
            return {"error": "No weather data available"}

        # Calculate risk metrics
        rain_days = sum(1 for d in result.sample_data
                       if d.get("precipitation", 0) > 5)
        extreme_temp_days = sum(1 for d in result.sample_data
                               if d.get("temp_max", 0) > 35 or d.get("temp_min", 0) < 0)

        total_days = len(result.sample_data)
        risk_score = (rain_days + extreme_temp_days) / total_days if total_days > 0 else 0

        return {
            "total_days": total_days,
            "rain_days": rain_days,
            "extreme_temperature_days": extreme_temp_days,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 0.3 else "medium" if risk_score > 0.1 else "low"
        }

    def list_sources(self) -> List[Dict]:
        """List all available data sources"""
        sources = []
        for name, connector in self.connectors.items():
            meta = connector.get_metadata()
            sources.append({
                "name": name,
                **meta
            })
        return sources

    def generate_report(self) -> str:
        """Generate data availability report"""
        output = """
# Open Data Integration Report

## Available Sources
"""
        for source in self.list_sources():
            output += f"""
### {source['name'].title()}
- **Type:** {source['type']}
- **Update Frequency:** {source['frequency']}
"""

        output += """
## Cache Status
"""
        for key, expiry in self.cache_expiry.items():
            status = "valid" if expiry > datetime.now() else "expired"
            output += f"- {key}: {status}\n"

        return output
```

## Common Use Cases

### Fetch Material Prices

```python
integrator = OpenDataIntegrator(region="US")

# Get material price indices
result = integrator.fetch_data("material_prices", {
    "materials": ["concrete", "steel", "lumber"]
})

print(f"Fetched: {result.records_fetched} records")
for record in result.sample_data:
    print(f"  {record['material']}: index={record['current']}, trend={record['trend']}")
```

### Enrich Project Data

```python
project = {
    "name": "Office Building",
    "materials": ["concrete", "steel", "glass"],
    "trades": ["carpenter", "electrician", "plumber"],
    "location": {"lat": 40.7128, "lon": -74.0060},
    "start_date": date(2024, 6, 1),
    "end_date": date(2024, 12, 31)
}

enriched = integrator.enrich_project_data(project)

print(f"Sources used: {enriched.sources_used}")
print(f"Confidence: {enriched.confidence:.0%}")
print(f"Material indices: {enriched.enrichments.get('material_price_indices')}")
```

### Assess Weather Risk

```python
risk = integrator.get_weather_risk(
    lat=40.7128,
    lon=-74.0060,
    start_date=date(2024, 6, 1),
    end_date=date(2024, 8, 31)
)

print(f"Risk Level: {risk['risk_level']}")
print(f"Rain Days: {risk['rain_days']}")
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `OpenDataIntegrator` | Main integration engine |
| `OpenDataConnector` | Base connector class |
| `WeatherDataConnector` | Weather API connector |
| `MaterialPriceConnector` | Material price indices |
| `LaborRateConnector` | Labor rate data |
| `EnrichedData` | Enriched data result |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 2.2
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [ontology-mapper](../ontology-mapper/SKILL.md) for semantic mapping
- Use [cost-prediction](../../Chapter-4.5/cost-prediction/SKILL.md) with indices
- Use [weather-impact-analysis](../../../DDC_Innovative/weather-impact-analysis/SKILL.md) for scheduling
