---
name: sap-integration
description: SAP system integration, data extraction, and automation for ABAP, HANA, S/4HANA environments. Use when working with SAP systems for: (1) Data extraction and reporting, (2) RFC/BAPI calls, (3) SAP API integration, (4) ABAP code generation, (5) SAP table analysis, (6) Workflow automation, (7) S/4HANA migration tasks, or any SAP-related development and integration work.
---

# SAP Integration Skill

Enterprise SAP system integration and automation capability built by SAPCONET experts.

## Core Capabilities

### Data Operations
- **Extract SAP data** via RFC, BAPI, or OData services
- **Generate reports** from SAP tables with proper joins and filters
- **Export to Excel/CSV** with formatting and pivot analysis
- **Real-time data sync** between SAP and external systems

### Development Support
- **ABAP code generation** for common patterns (ALV reports, BAPIs, enhancements)
- **SAP table analysis** with field descriptions and relationships
- **Custom transaction creation** with proper authorization checks
- **Performance optimization** queries and recommendations

### Integration Patterns
- **REST API wrappers** for SAP functions
- **Middleware connectivity** via PI/PO or CPI
- **Cloud integration** with SAP Business Technology Platform
- **Legacy system bridging** for modernization projects

## Quick Start Examples

### Data Extraction
```abap
" Extract customer master data
SELECT kunnr, name1, ort01, land1 
FROM kna1 
INTO TABLE lt_customers 
WHERE erdat >= sy-datum - 30.
```

### BAPI Integration
```python
# Python RFC connection
import pyrfc
conn = pyrfc.Connection(...)
result = conn.call('BAPI_CUSTOMER_GETDETAIL2', 
                  CUSTOMERNO='0000001000')
```

## Advanced Workflows

### SAP HANA Integration
For complex analytics and real-time processing:
- See [references/hana-integration.md](references/hana-integration.md)

### S/4HANA Migration Support  
For brownfield and greenfield transitions:
- See [references/s4hana-migration.md](references/s4hana-migration.md)

### Custom Enhancement Framework
For user exits, BADIs, and enhancement spots:
- See [references/enhancement-framework.md](references/enhancement-framework.md)

## Authentication & Security

All SAP connections require proper authentication:
- **Username/password** for basic RFC
- **X.509 certificates** for secure connections  
- **OAuth 2.0** for cloud API access
- **SSO integration** via SAML/Kerberos

Security best practices enforced:
- Minimal authorization principle
- Encrypted data transmission
- Audit trail logging
- No hardcoded credentials

## Scripts Available

Execute common SAP operations without manual coding:

- `scripts/sap_data_extractor.py` - Generic table data extraction
- `scripts/rfc_function_caller.py` - Execute any RFC function module
- `scripts/sap_report_generator.py` - Generate formatted Excel reports
- `scripts/table_analyzer.py` - Analyze SAP table structure and relationships

## Support Matrix

| SAP Product | Supported | Integration Method |
|-------------|-----------|-------------------|
| SAP ECC 6.0+ | ✅ | RFC, BAPI, IDoc |
| S/4HANA Cloud | ✅ | OData, REST API |
| S/4HANA On-Premise | ✅ | RFC, OData, BAPI |
| SAP BW/4HANA | ✅ | MDX, OData, RFC |
| SAP Ariba | ✅ | REST API |
| SAP SuccessFactors | ✅ | OData, SOAP |
| SAP Concur | ✅ | REST API |

Built with enterprise-grade reliability by SAPCONET - South Africa's leading SAP automation specialists.