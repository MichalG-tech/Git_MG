# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

- Remaining documentation files (COMMON_ERRORS.md, DEPLOYMENT_GUIDE.md, TABULAR_EDITOR_GUIDE.md, RUNBOOK.md, FEATURE_WORKFLOW.md, IMPLEMENTATION_GUIDE.md)
- Design integration — Power BI background images, color palette standards
- End-to-end XMLA deployment testing against live Power BI workspaces
- GitHub issue templates

---

## [2.0.0] - 2026-04-23

Major feature release delivering the full technical implementation of the PoC: two complete semantic models, all Python automation modules, five GitHub Actions workflows, redesigned data schema, and the core documentation suite.

### Added — Semantic Models

**Sales Analytics** (`semantic-models/sales-analytics/`)
- Full TMDL structure: `definition/`, `tables/`, `relationships/`, `roles/`, `cultures/`, `metadata/`
- 7 tables: DimDate (17 columns, April fiscal calendar), DimCustomer (9 columns), DimProduct (8 columns), DimRegion (5 columns), FactSales (11 columns), FactReturns (9 columns), FactInventory (7 columns)
- 12 relationships: 4 active (FactSales → all dimensions), 8 inactive (FactReturns and FactInventory with USERELATIONSHIP() pattern)
- 63 DAX measures in `_Measures.tmdl` across 9 groups:
  - Sales Performance (12): Total Sales, Gross Profit, Gross Margin %, Order Count, AOV, Discount Rate %
  - Time Intelligence Period Totals (8): MTD, QTD, YTD, Prior Month/Quarter/Year, Rolling 3M/12M
  - Time Intelligence Growth (7): MoM/QoQ/YoY Growth %, YTD vs Prior YTD %
  - Returns Analytics (5): Return Amount, Return Rate %, Net Sales, YoY Return Rate Change
  - Customer Analytics (10): Active Customers 90d, New Customers, Retention Rate %, Repeat Rate %, Top 10 Concentration %
  - Product Analytics (8): Product Contribution %, Price Realization %, Category Sales Rank
  - Inventory Analytics (5): Days of Supply, Stockout Products
  - Geography (4): Region Sales %, Target Attainment %
  - Ranking & Intelligence (7): % of Total Sales, Cumulative Sales %, Sales Velocity, Weekend/Weekday Sales
- Row-level security: `SalesManager.tmdl` (full access), `RegionalAnalyst.tmdl` (DimRegion filter)
- `en-US.tmdl` localisation culture
- `model-metadata.json` schema documentation

**Finance Reporting** (`semantic-models/finance-reporting/`)
- Full TMDL structure across `definition/`, `tables/`, `relationships/`, `roles/`, `metadata/`
- 6 tables: DimAccount (12 hardcoded P&L accounts), DimDepartment (12 departments), DimPeriod (M-generated 2021–2026 monthly, April fiscal), DimEntity (5 entities with currency codes), FactActuals (simulated 5,000 rows), FactBudget (simulated 3,000 rows with BudgetVersion column)
- 8 relationships: FactActuals → all 4 dims (active), FactBudget → all 4 dims (inactive)
- 20 DAX measures in `_FinanceMeasures.tmdl`: Actuals, Budget, Variance, YTD pairs, Prior Year comparisons, full income statement (Revenue → Net Income, EBITDA, EBITDA Margin %)
- `FinanceViewer.tmdl` security role

### Added — Python Utilities

- `python-utilities/src/deployers/__init__.py` — Full implementation skeleton for all 4 environments with structured return dicts; documents msal + Tabular Editor CLI requirements for production wiring
- `python-utilities/src/tabular_editor/__init__.py` — `TabularEditorCLI` class: `validate()`, `deploy()`, `run_bpa()`; subprocess wrapper with timeout and error handling
- `python-utilities/src/git_helpers/__init__.py` — `get_changed_files()`, `get_current_branch()`, `get_current_commit_sha()`, `create_release_tag()`, `get_commits_since_tag()`, `assert_clean_working_tree()`
- `python-utilities/src/utils/__init__.py` — `get_logger()` (ISO timestamps), `load_config()` (with required key validation), `get_env()`, `find_tmdl_files()`, `find_model_directories()`, `format_result()`, `print_summary()`

### Added — GitHub Actions Workflows

- `.github/workflows/pr-validation.yml` — TMDL syntax + best practices + pytest + CHANGELOG check; triggers on PRs to `main` or `develop`
- `.github/workflows/deploy-dev.yml` — Auto-deploy on push to `develop`; pre-deployment validation + GitHub Step Summary
- `.github/workflows/deploy-test.yml` — Deploys on pre-release tag (`v*.*.*-rc*`); writes versioned deployment log entry
- `.github/workflows/deploy-staging.yml` — Required reviewer approval gate; version consistency check against `VERSION` file; audit trail commit
- `.github/workflows/deploy-prod.yml` — Three-job pipeline: preflight (CONFIRM validation) → request-approval (environment gate) → deploy; mandatory audit entry on every run including failures

### Added — Documentation

- `docs/getting-started/QUICKSTART.md` — 6-step setup guide
- `docs/getting-started/ENVIRONMENT_SETUP.md` — Python, Git, Tabular Editor 3, GitHub Secrets, Azure AD service principal, GitHub Environments, DataFolderPath configuration
- `docs/semantic-models/TMDL_STANDARDS.md` — File organisation, Dim/Fact/_ naming conventions, measure quality standards (description/formatString/lineageTag requirements), DAX best practices, star schema rules
- `docs/automation/GITHUB_ACTIONS_GUIDE.md` — Pipeline ASCII diagram, all 5 workflow details, environment configuration, debugging guide
- `docs/data/DATA_DICTIONARY.md` — Column-level reference for all 7 tables, measure inventory with 63-measure breakdown by group
- `docs/architecture/DESIGN_DECISIONS.md` — 7 architectural decisions: TMDL+Git, centralised _Measures table, string natural keys, inactive relationships, CSV data source, April fiscal year, 5-environment pipeline

### Changed — Data Schema

- `generate_sample_data.py` complete rewrite with richer star schema:
  - `DimDate`: added QuarterName, MonthName, MonthShortName, YearMonth, YearQuarter, Week, FiscalYear/Quarter/Month (April start); IsWeekend now boolean
  - `DimCustomer`: added RegionID (FK bridge to DimRegion), AcquisitionChannel
  - `DimProduct`: added Subcategory
  - `DimRegion`: added Zone (AMER / EMEA / APAC)
  - `FactSales` (orders.csv): added RegionID, DiscountPct columns
  - `FactReturns` (returns.csv): added CustomerID, ProductID, RegionID for direct dimension slicing
  - `FactInventory`: added RegionID column
- Vectorised Pandas sampling replaces per-row Python loop for generation performance
- April fiscal year helper function (`_fiscal_attrs()`) for consistent FY/FQ/FM calculation

### Changed — Python Validators

- `naming_conventions.json`: removed non-standard `measure_prefix` key; updated table pattern to allow `_` prefix for hidden utility tables; updated measure name pattern to permit `%`, `()`, `#`, `&` for financial notation; added `hidden_table_prefix` and `notes` entries
- `best_practices_checker.py`: complete rewrite using `re` module; distinguishes dim/fact/utility tables in all checks; adds command-line interface

### Fixed

- `generate-data.py` config path resolved to wrong directory (two levels above repo root) — fixed to use `Path(__file__).resolve().parent` for reliable REPO_ROOT detection
- `UnicodeEncodeError` on Windows (cp1252 encoding) in generate-data.py — fixed with `sys.stdout.reconfigure(encoding='utf-8')` and ASCII output symbols

---

## [1.0.0] - 2026-04-22

### Added

- Initial PoC repository structure
- Folder hierarchy for semantic models, Python utilities, documentation
- Git configuration (`.gitignore`, `.gitattributes`)
- README, CONTRIBUTING, and CHANGELOG
- Basic Python utility stubs (validators, deployers, tabular editor, git helpers)
- Sample data generation configuration (`config/data-generation-config.json`)
- Git workflow setup (main/develop branches)

---

**Last Updated**: 2026-04-23  
**Current Version**: v2.0.0
