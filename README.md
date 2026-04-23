# Power BI Enterprise PoC — Professional Implementation

A production-grade proof of concept for managing Power BI semantic models with Git, featuring enterprise automation, governance, and documentation. Built to demonstrate the **Claude + Power BI** development approach to clients.

---

## Overview

This PoC establishes a professional, scalable framework for:

- **Semantic Models** — TMDL-based version control for two complete models (Sales Analytics, Finance Reporting)
- **Data Pipeline** — Realistic sample datasets with 500K+ transactions across a full star schema
- **Automation** — Python validators, deployers, quality checks
- **CI/CD** — GitHub Actions across 5 environments (Local → Dev → Test → Staging → Prod)
- **Tabular Editor** — CLI integration for TMDL management and validation
- **Documentation** — Architecture decisions, data dictionary, standards guides
- **Governance** — Enterprise change control with audit trails

---

## Quick Start

See [QUICKSTART.md](docs/getting-started/QUICKSTART.md) for 5-minute setup.

For detailed configuration: [ENVIRONMENT_SETUP.md](docs/getting-started/ENVIRONMENT_SETUP.md)

---

## Repository Structure

```
semantic-models/          # Power BI TMDL files (version controlled)
  sales-analytics/        #   63 DAX measures, 7 tables, 12 relationships
  finance-reporting/      #   20 DAX measures, 6 tables, 8 relationships
data/                     # Sample datasets (CSV) and generation scripts
python-utilities/         # Validators, deployers, data pipeline, helpers
.github/workflows/        # GitHub Actions CI/CD (5 workflows)
design/                   # Power BI background images (placeholder)
reports/                  # Power BI report files (.pbir)
docs/                     # Architecture, standards, and reference guides
config/                   # Configuration files (JSON)
deployment/               # Deployment tracking and audit logs
```

---

## Key Features

### Version Control
- TMDL semantic models in Git — text-based, diff-friendly, mergeable
- Complete audit trail of all model changes
- Git workflow with branches (main / develop / feature)
- Conventional commits enforced in CI

### Semantic Models

**Sales Analytics** — full star schema
- 7 tables: 4 dimension + 3 fact (FactSales, FactReturns, FactInventory)
- 12 relationships (4 active, 8 inactive with USERELATIONSHIP())
- 63 DAX measures: time intelligence, customer analytics, product analytics, geography, ranking
- Row-level security: SalesManager and RegionalAnalyst roles

**Finance Reporting** — multi-entity income statement model
- 6 tables: 4 dimension + 2 fact (FactActuals, FactBudget)
- 20 DAX measures: actuals vs budget, YTD, prior year, full P&L (Revenue → Net Income)
- April fiscal year support throughout
- FinanceViewer security role

### Automation
- GitHub Actions CI/CD pipeline (5 workflows — see [GITHUB_ACTIONS_GUIDE.md](docs/automation/GITHUB_ACTIONS_GUIDE.md))
- Automated TMDL validation on every pull request
- Progressive deployment with manual approval gates for Staging and Production
- Python validators for TMDL syntax, naming conventions, and best practices

### Data
- 500K+ sales transactions, 5K customers, 1.5K products, 50 regions
- April fiscal year calendar (FY2023 = April 2022 – March 2023)
- Full star schema: RegionID in every fact table, AcquisitionChannel in DimCustomer
- Reproducible generation via `py python-utilities/scripts/generate-data.py`

---

## Workflow Example — Add a New Measure (End-to-End)

```bash
# 1. Create feature branch
git checkout -b feature/add-revenue-targets-measure

# 2. Edit _Measures.tmdl — all measures live in the hidden utility table
#    semantic-models/sales-analytics/tables/_Measures.tmdl

# 3. Validate locally
py python-utilities/scripts/run-all-checks.py

# 4. Commit with conventional message
git commit -m "feat(sales-model): Add revenue targets measure"

# 5. Push and open PR
git push origin feature/add-revenue-targets-measure
```

**Automated from here:**
- PR Validation: TMDL syntax + naming conventions + best practices + unit tests
- Merge to develop → auto-deploy to Dev environment
- RC tag (`v1.1.0-rc1`) → deploy to Test
- Stable release (`v1.1.0`) → approval gate → deploy to Staging
- Manual dispatch → approval gate + CONFIRM input → deploy to Production with audit log

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Semantic Models | TMDL | Git-friendly Power BI model format |
| Python | 3.11+ | Validation, deployment, data generation |
| Data | CSV / Pandas | Sample data and pipeline |
| CI/CD | GitHub Actions | Workflow automation |
| TE Integration | Tabular Editor 3 CLI | Model validation and XMLA deployment |
| Version Control | Git / GitHub | Collaboration and audit trail |

---

## Documentation

| Guide | Category | Purpose |
|-------|----------|---------|
| [QUICKSTART.md](docs/getting-started/QUICKSTART.md) | Getting Started | 6-step setup in under 5 minutes |
| [ENVIRONMENT_SETUP.md](docs/getting-started/ENVIRONMENT_SETUP.md) | Getting Started | Full environment configuration — Python, Git, TE3, GitHub Secrets |
| [FIRST_TIME_GUIDE.md](docs/getting-started/FIRST_TIME_GUIDE.md) | Getting Started | Conceptual overview and end-to-end walkthrough for newcomers |
| [TMDL_STANDARDS.md](docs/semantic-models/TMDL_STANDARDS.md) | Standards | Naming conventions, DAX best practices, star schema rules |
| [DATA_DICTIONARY.md](docs/data/DATA_DICTIONARY.md) | Reference | Column-level reference for all tables and 63-measure inventory |
| [DESIGN_DECISIONS.md](docs/architecture/DESIGN_DECISIONS.md) | Architecture | 7 architectural decisions with rationale and trade-offs |
| [GITHUB_ACTIONS_GUIDE.md](docs/automation/GITHUB_ACTIONS_GUIDE.md) | Automation | CI/CD pipeline reference for all 5 workflows |
| [FEATURE_WORKFLOW.md](docs/development/FEATURE_WORKFLOW.md) | Development | Branch strategy, commit conventions, end-to-end PR workflow |
| [TABULAR_EDITOR_GUIDE.md](docs/tabular-editor/TABULAR_EDITOR_GUIDE.md) | Tools | TE3 setup, TMDL authoring, XMLA deployment, BPA |
| [DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md) | Deployment | Step-by-step deployment procedures for all 5 environments |
| [CHANGE_CONTROL.md](docs/governance/CHANGE_CONTROL.md) | Governance | Approval matrix, change categories, audit trail, compliance evidence |
| [RUNBOOK.md](docs/operations/RUNBOOK.md) | Operations | Health checks, incident response, release procedures |
| [IMPLEMENTATION_GUIDE.md](docs/client-deliverables/IMPLEMENTATION_GUIDE.md) | Client | Client-facing PoC narrative and production adaptation guide |
| [COMMON_ERRORS.md](docs/troubleshooting/COMMON_ERRORS.md) | Troubleshooting | Solutions for common Python, TMDL, CI/CD, and Power BI errors |
| [FAQ.md](docs/troubleshooting/FAQ.md) | Troubleshooting | Frequently asked questions across all areas |
| [DEBUG_GUIDE.md](docs/troubleshooting/DEBUG_GUIDE.md) | Troubleshooting | Systematic diagnostic techniques for all components |

---

## Current Status

- [x] Repository structure and Git configuration
- [x] Python utilities — validators, deployers, git helpers, tabular editor CLI
- [x] Sample data generation — star schema with 500K+ rows
- [x] Semantic models — Sales Analytics (63 measures) and Finance Reporting (20 measures)
- [x] GitHub Actions — all 5 workflows with progressive approval gates
- [x] Documentation suite — 16 reference guides across all areas
- [ ] Design integration (Power BI background images, color palette)
- [ ] End-to-end deployment testing against live Power BI workspaces

---

## Prerequisites

- Git and a GitHub account
- Python 3.11+
- Power BI Desktop
- Tabular Editor 3 (for TMDL editing and CLI validation)

```bash
# Clone and set up
git clone https://github.com/MichalG-tech/Git_MG.git
cd Git_MG
pip install -r python-utilities/requirements.txt
py python-utilities/scripts/generate-data.py
py python-utilities/scripts/run-all-checks.py
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License — See [LICENSE](LICENSE) file

## Author

**Michal Glanowski** — [@MichalG-tech](https://github.com/MichalG-tech/Git_MG)

---

**Version**: v2.0.0  
**Last Updated**: 2026-04-23  
**Status**: Active Development
