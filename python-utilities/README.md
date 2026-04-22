# Python Utilities

Professional automation toolkit for Power BI semantic models.

## What's Inside

### Validators
- **TMDL Validator** (`tmdl_validator.py`) - Validates TMDL file syntax and structure
- **DAX Validator** (`dax_validator.py`) - Validates DAX expressions and best practices
- **Best Practices Checker** (`best_practices_checker.py`) - Enforces naming conventions and standards

### Deployers
- Deploy to Dev, Test, Staging, Production environments
- Deployment logging and audit trails
- Rollback procedures

### Data Pipeline
- Generate realistic sample data
- Transform raw data
- Quality validation and profiling

### Tabular Editor Integration
- CLI wrapper for Tabular Editor
- TMDL export/import
- Advanced model validation

### Git Helpers
- Git operations automation
- Changelog generation
- Semantic versioning

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Quick Start

```bash
# Validate TMDL file
python -m validators.tmdl_validator semantic-models/sales-analytics/

# Validate DAX expression
python -c "from validators.dax_validator import validate_dax; print(validate_dax('SUM([Amount])'))"

# Check best practices
python -m validators.best_practices_checker semantic-models/sales-analytics/tables/FactSales.tmdl
```

## Usage Examples

See `/scripts/` for convenience scripts and examples.

## Testing

```bash
pytest tests/
pytest tests/ -v --cov=src
```

## Project Structure

```
src/
├── validators/          # TMDL, DAX, best practices
├── deployers/           # Deployment automation
├── data_pipeline/       # Data generation & validation
├── tabular_editor/      # TE integration
├── git_helpers/         # Git utilities
└── utils/               # Common utilities

tests/                   # Unit and integration tests
scripts/                 # Convenience scripts
```

## Documentation

See `/docs/` for comprehensive guides:
- `docs/getting-started/` - Setup and first steps
- `docs/development/` - Development workflows
- `docs/semantic-models/` - TMDL best practices
- `docs/deployment/` - Deployment procedures

## Contributing

See `CONTRIBUTING.md` for contribution guidelines.

## License

MIT License - See `LICENSE`
