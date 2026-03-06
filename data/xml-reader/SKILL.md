---
name: "xml-reader"
description: "Read and parse XML from construction systems - P6 schedules, BSDD exports, IFC-XML, COBie-XML. Convert to pandas DataFrames."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🏷️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# XML Reader for Construction Data

## Overview
XML is used in construction for P6 schedules (XER), IFC-XML, COBie-XML, and buildingSMART Data Dictionary exports. This skill parses XML and converts to structured DataFrames.

## Python Implementation

```python
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class XMLElement:
    """Parsed XML element."""
    tag: str
    attributes: Dict[str, str]
    text: Optional[str]
    children: List['XMLElement']


class ConstructionXMLReader:
    """Parse XML from construction systems."""

    def __init__(self):
        self.namespaces: Dict[str, str] = {}

    def parse_file(self, file_path: str) -> ET.Element:
        """Parse XML file and return root element."""
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract namespaces
        self._extract_namespaces(root)

        return root

    def parse_string(self, xml_string: str) -> ET.Element:
        """Parse XML from string."""
        root = ET.fromstring(xml_string)
        self._extract_namespaces(root)
        return root

    def _extract_namespaces(self, root: ET.Element):
        """Extract namespace mappings."""
        # Find namespace declarations
        for attr, value in root.attrib.items():
            if attr.startswith('{'):
                ns = attr[1:attr.index('}')]
                self.namespaces[root.tag.split('}')[0][1:]] = ns

    def find_elements(self, root: ET.Element,
                      tag: str,
                      namespace: str = None) -> List[ET.Element]:
        """Find all elements with given tag."""
        if namespace:
            tag = f"{{{namespace}}}{tag}"
        return root.findall(f".//{tag}")

    def element_to_dict(self, element: ET.Element,
                        include_children: bool = True) -> Dict[str, Any]:
        """Convert element to dictionary."""
        result = {
            '_tag': element.tag.split('}')[-1] if '}' in element.tag else element.tag,
            '_text': element.text.strip() if element.text else None,
            **element.attrib
        }

        if include_children:
            for child in element:
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

                if child_tag in result:
                    # Multiple children with same tag - make list
                    if not isinstance(result[child_tag], list):
                        result[child_tag] = [result[child_tag]]
                    result[child_tag].append(self.element_to_dict(child))
                else:
                    result[child_tag] = self.element_to_dict(child)

        return result

    def elements_to_dataframe(self, elements: List[ET.Element]) -> pd.DataFrame:
        """Convert list of elements to DataFrame."""
        records = []
        for elem in elements:
            record = {'_tag': elem.tag.split('}')[-1]}
            record.update(elem.attrib)

            # Get direct text content
            if elem.text and elem.text.strip():
                record['_text'] = elem.text.strip()

            # Get child values
            for child in elem:
                child_tag = child.tag.split('}')[-1]
                if child.text and child.text.strip():
                    record[child_tag] = child.text.strip()
                # Also get child attributes
                for attr, val in child.attrib.items():
                    record[f"{child_tag}_{attr}"] = val

            records.append(record)

        return pd.DataFrame(records)

    def flatten_xml(self, root: ET.Element,
                    target_tag: str = None) -> pd.DataFrame:
        """Flatten XML to DataFrame."""
        if target_tag:
            elements = self.find_elements(root, target_tag)
        else:
            elements = list(root)

        return self.elements_to_dataframe(elements)


class P6XMLReader(ConstructionXMLReader):
    """Reader for Primavera P6 XML exports."""

    def parse_activities(self, root: ET.Element) -> pd.DataFrame:
        """Parse activities from P6 XML."""
        activities = self.find_elements(root, 'Activity')
        return self.elements_to_dataframe(activities)

    def parse_resources(self, root: ET.Element) -> pd.DataFrame:
        """Parse resources from P6 XML."""
        resources = self.find_elements(root, 'Resource')
        return self.elements_to_dataframe(resources)

    def parse_wbs(self, root: ET.Element) -> pd.DataFrame:
        """Parse WBS from P6 XML."""
        wbs = self.find_elements(root, 'WBS')
        return self.elements_to_dataframe(wbs)

    def parse_full_schedule(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Parse complete P6 schedule."""
        root = self.parse_file(file_path)
        return {
            'activities': self.parse_activities(root),
            'resources': self.parse_resources(root),
            'wbs': self.parse_wbs(root)
        }


class IFCXMLReader(ConstructionXMLReader):
    """Reader for IFC-XML files."""

    def parse_entities(self, root: ET.Element) -> pd.DataFrame:
        """Parse IFC entities."""
        # Find all Ifc* elements
        all_entities = []
        for elem in root.iter():
            if elem.tag.startswith('Ifc'):
                all_entities.append(elem)
        return self.elements_to_dataframe(all_entities)

    def get_entity_types(self, root: ET.Element) -> Dict[str, int]:
        """Count entity types."""
        counts = {}
        for elem in root.iter():
            tag = elem.tag
            if tag.startswith('Ifc'):
                counts[tag] = counts.get(tag, 0) + 1
        return counts


class COBieXMLReader(ConstructionXMLReader):
    """Reader for COBie XML files."""

    COBIE_SHEETS = ['Facility', 'Floor', 'Space', 'Zone', 'Type',
                    'Component', 'System', 'Assembly', 'Connection',
                    'Spare', 'Resource', 'Job', 'Document', 'Attribute']

    def parse_cobie(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Parse all COBie sheets."""
        root = self.parse_file(file_path)
        result = {}

        for sheet in self.COBIE_SHEETS:
            elements = self.find_elements(root, sheet)
            if elements:
                result[sheet] = self.elements_to_dataframe(elements)

        return result


class BSDDXMLReader(ConstructionXMLReader):
    """Reader for buildingSMART Data Dictionary exports."""

    def parse_classifications(self, root: ET.Element) -> pd.DataFrame:
        """Parse classification items."""
        items = self.find_elements(root, 'Classification')
        return self.elements_to_dataframe(items)

    def parse_properties(self, root: ET.Element) -> pd.DataFrame:
        """Parse property definitions."""
        props = self.find_elements(root, 'Property')
        return self.elements_to_dataframe(props)
```

## Quick Start

```python
reader = ConstructionXMLReader()

# Parse XML file
root = reader.parse_file("schedule.xml")

# Find specific elements
activities = reader.find_elements(root, "Activity")
print(f"Found {len(activities)} activities")

# Convert to DataFrame
df = reader.elements_to_dataframe(activities)
```

## Common Use Cases

### 1. P6 Schedule Import
```python
p6_reader = P6XMLReader()
schedule = p6_reader.parse_full_schedule("p6_export.xml")

activities = schedule['activities']
print(f"Activities: {len(activities)}")
```

### 2. COBie Data
```python
cobie_reader = COBieXMLReader()
cobie_data = cobie_reader.parse_cobie("facility_cobie.xml")

components = cobie_data.get('Component', pd.DataFrame())
```

### 3. IFC-XML Analysis
```python
ifc_reader = IFCXMLReader()
root = ifc_reader.parse_file("model.ifcxml")

# Count entity types
types = ifc_reader.get_entity_types(root)
for entity_type, count in sorted(types.items(), key=lambda x: -x[1])[:10]:
    print(f"{entity_type}: {count}")
```

## Resources
- **DDC Book**: Chapter 2.1 - Semi-structured Data
- **IFC-XML**: buildingSMART specification
