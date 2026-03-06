# Changelog

All notable changes to the Personal Genomics skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0] - 2026-02-07

### Added

#### Interactive Web Dashboard
- New `dashboard/index.html` - self-contained HTML/CSS/JS visualization
- Auto-generated `dashboard.html` with every analysis run
- Sections: Overview, Pharmacogenomics, Health Risks (PRS), Traits, Ancestry, Carrier Status, Sleep Profile, Athletic Profile, UV/Skin, Dietary Interactions
- Dark mode toggle with persistence
- Mobile responsive design
- Collapsible sections for easy navigation
- Search/filter functionality for tables and traits
- Export to PDF via print functionality
- Drag & drop JSON loading for standalone use
- Zero external dependencies - works completely offline
- Inline CSS/JS for single-file distribution

#### Code Quality Improvements
- Complete type hints for all public functions
- TypedDict definitions for complex return types (GenotypeData, MarkerInfo, AnalysisResult, APOEResult, PRSResult)
- Google-style docstrings for all public functions
- Added `py.typed` PEP 561 marker file
- Module-level docstrings explaining purpose

#### Defensive Programming
- Input validation for all public functions
- `validate_rsid()` - validates rsID format
- `validate_genotype()` - validates genotype format
- `validate_filepath()` - validates and resolves file paths
- `sanitize_genotype()` - cleans and normalizes genotype strings
- Graceful handling of missing/malformed genotype data
- Informative error messages with suggested fixes
- Logging for warnings and recoverable issues

#### API Improvements
- New `analyze_dna_file()` function as main entry point for programmatic usage
- New `generate_dashboard()` function for standalone dashboard generation
- `--open` CLI flag to auto-open dashboard in browser
- `--no-dashboard` CLI flag to skip dashboard generation
- Better separation of CLI and library usage

#### Testing
- 30 new edge case tests in `tests/test_edge_cases.py`
- Input validation tests
- Empty input handling tests
- Malformed data tests
- Encoding handling tests (UTF-8, Latin-1)
- APOE edge case tests
- PRS edge case tests
- Report generation tests
- Dashboard generation tests
- Integration tests
- Total: 200 tests, all passing

### Changed
- Updated version to 4.2.0
- Improved error handling throughout codebase
- Better type safety with explicit type annotations
- More defensive code patterns
- Cleaner separation of concerns

### Fixed
- Better handling of edge cases in file loading
- Improved encoding error handling
- Fixed potential issues with missing marker data

## [4.1.0] - 2026-02-06

### Added
- Medication Interaction Checker with brand/generic name support
- Sleep Optimization Profile (chronotype, caffeine metabolism)
- Dietary Interaction Matrix (caffeine, alcohol, lactose, gluten, etc.)
- Athletic Performance Profiling (power vs endurance, recovery, injury risk)
- UV Sensitivity Calculator (skin type, SPF recommendations)
- Natural Language Explanations for all findings
- Telomere Length Estimation
- Research Variant Flagging
- Extended PRS markers
- Extended carrier status markers
- Extended pharmacogenomics markers

## [4.0.0] - 2026-02-06

### Added
- Haplogroup Analysis (mtDNA and Y-DNA)
- Ancestry Composition with population comparisons
- Expanded Hereditary Cancer Panel (BRCA1/2, Lynch syndrome, etc.)
- Autoimmune HLA Associations
- Pain Sensitivity markers
- PDF Report Generation
- Data Quality Metrics
- Integration & Export formats

## [3.0.0] - Initial Release

### Added
- Core genetic analysis with 1600+ markers
- Pharmacogenomics (CPIC Level 1A)
- Polygenic Risk Scores for 10+ conditions
- Carrier Status screening
- Health Risks assessment
- Traits analysis
- Nutrition markers
- Fitness markers
- Neurogenetics markers
- Longevity markers
- Immunity markers
- Rare Diseases panel
- Mental Health markers
- Dermatology markers
- Vision & Hearing markers
- Fertility markers
- Agent-friendly JSON output
- Human-readable text reports
- Multi-format support (23andMe, AncestryDNA, VCF, etc.)
