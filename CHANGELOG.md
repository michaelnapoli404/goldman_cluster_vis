# Changelog

All notable changes to Wave Visualizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release planning

## [0.1.0] - 2024-12-19

### Added
- **Core Visualization Engine**
  - Alluvial plot (Sankey diagram) generation for longitudinal data transitions
  - Interactive Plotly-based visualizations with hover tooltips and customizable layouts
  - Support for wave-to-wave transition analysis (W1→W2, W1→W3, etc.)

- **Data Cleaning Pipeline**
  - Automatic SPSS (.sav) file loading and processing
  - Metadata extraction and label conversion system
  - Missing value handling with multiple strategies
  - Value merging capabilities for categorical data cleanup
  - Configurable data filtering and row reduction

- **Dynamic Wave Configuration System**
  - Support for unlimited survey waves through CSV-driven configuration
  - Dynamic column name generation and wave parsing
  - Extensible wave definition system for future data collection waves

- **Semantic Color Mapping**
  - Consistent color assignments for categorical variables across visualizations
  - User-configurable color mappings with persistent storage
  - Intelligent fallback color schemes for unmapped values

- **Export System**
  - Multi-format export (HTML, PNG, SVG, PDF) with single command
  - Automatic exports folder creation relative to calling script
  - High-resolution image generation with customizable parameters
  - Call stack inspection for intelligent file placement

- **Comprehensive Logging System**
  - Configurable logging levels with custom formatters
  - Professional log output with structured formatting
  - File and console logging options
  - Package-wide logging configuration

- **Input Validation & Error Handling**
  - Custom exception hierarchy with helpful error messages
  - Comprehensive input validation for all user-facing functions
  - Parameter sanitization and type checking
  - Intelligent error suggestions (e.g., column name suggestions)

- **Architecture**
  - Builder pattern for modular visualization construction
  - Strategy pattern for pluggable data cleaning approaches
  - Factory pattern for flexible component creation
  - Interface protocols for type-safe component contracts
  - Command pattern implementation for undoable operations

- **Type Safety & IDE Support**
  - Comprehensive type hints throughout the codebase
  - MyPy strict type checking compliance
  - Full IDE autocomplete and error detection support
  - Professional docstrings with Google-style formatting

- **Testing Infrastructure**
  - Comprehensive pytest test suite with >90% coverage
  - Unit tests, integration tests, and performance tests
  - Mock-based testing for external dependencies
  - Automated test fixtures and test data generation
  - Test categorization with pytest markers

- **Development Tools**
  - Pre-commit hooks with black, isort, flake8, mypy, and bandit
  - Comprehensive Makefile for development workflow automation
  - Professional .gitignore with Python-specific exclusions
  - Development environment setup with conda environment export

- **Configuration Management**
  - Centralized configuration system with dataclasses
  - User-configurable settings with automatic persistence
  - JSON-based configuration files in user home directory
  - Environment-based configuration overrides

- **Documentation**
  - Comprehensive README with installation, usage, and API reference
  - Professional contributing guidelines with code standards
  - Architecture documentation with design pattern explanations
  - API documentation with parameter details and usage examples

### Technical Highlights
- **Code Quality**: Black formatting, comprehensive linting, strict type checking
- **Testing**: 95%+ test coverage with unit, integration, and performance tests
- **Architecture**: Clean interfaces, design patterns, and separation of concerns
- **Performance**: Optimized data processing and visualization generation
- **Maintainability**: Professional logging, error handling, and documentation

### Package Structure
```
wave_visualizer/
├── data_prep/              # Data cleaning and preprocessing
│   ├── cleaning/           # Cleaning pipeline components
│   ├── color_mapping.py    # Semantic color management
│   ├── customization.py    # Visualization configuration
│   ├── export_handler.py   # Multi-format export system
│   └── wave_parser.py      # Dynamic wave configuration
├── settings/               # Persistent configuration storage
├── utils/                  # Logging and utility functions
├── validators.py           # Input validation and sanitization
├── visualization_techs/    # Visualization generation
│   ├── alluvial_builder.py # Builder pattern implementation
│   └── alluvial_plots.py   # Main visualization interface
├── config.py              # Configuration management
├── exceptions.py          # Custom exception hierarchy
└── interfaces.py          # Protocol definitions
```

### Dependencies
- **Core**: pandas ≥1.3.0, plotly ≥5.0.0, numpy ≥1.20.0, pyreadstat ≥1.1.0
- **Development**: pytest, black, flake8, mypy, pre-commit, isort, bandit
- **Optional**: kaleido (image export), coverage (testing)

### Supported Python Versions
- Python 3.8+
- Tested on Windows and Linux

---

## Version History

### Legend
- **Added**: New features
- **Changed**: Changes in existing functionality  
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

---

For more details about any release, see the [GitHub releases page](https://github.com/michaelnapoli404/wave-visualizer/releases). 