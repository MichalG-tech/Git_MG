# First Time Guide

Welcome to the Power BI Enterprise PoC. This guide walks you through everything you need to understand, set up, and start contributing — even if you're new to TMDL or Git-based Power BI development.

---

## What This Repository Does

This PoC demonstrates a professional, enterprise-grade approach to Power BI development using:

- **TMDL** (Tabular Model Definition Language) — stores semantic models as readable text files in Git, enabling code review, branching, and automated validation
- **GitHub Actions** — automates validation on every pull request and deploys to five environments (Dev → Test → Staging → Production) with progressive approval gates
- **Python automation** — generates sample data, validates TMDL files, and supports deployment pipelines
- **Star schema design** — follows industry best practices with Dim/Fact table patterns, hidden foreign keys, and a centralised `_Measures` table

The goal is to show clients what a properly governed, engineer-grade Power BI implementation looks like — and to prove that Claude can build it end-to-end.

---

## Mental Model Before You Start

### TMDL is just text

A Power BI semantic model in this repo is a folder of `.tmdl` files — plain text you can read, edit in VS Code, and diff in pull requests. Tabular Editor 3 is the tool that opens, edits, and deploys these files.

### Measures live in one place

All DAX measures are in the `_Measures.tmdl` hidden utility table — not in fact tables or dimension tables. This is by design. See [DESIGN_DECISIONS.md](../architecture/DESIGN_DECISIONS.md).

### The pipeline is progressive

Every code change flows through: Local → Dev (auto) → Test (tag) → Staging (approval) → Production (manual + approval). You cannot skip steps. This mirrors enterprise change management processes.

---

## Step 1 — Prerequisites

Install these before cloning:

| Tool | Version | Download |
|------|---------|----------|
| Git | Latest | https://git-scm.com |
| Python | 3.11+ | https://python.org |
| Power BI Desktop | Latest | Microsoft Store or MSI |
| Tabular Editor 3 | Latest | https://tabulareditor.com |
| VS Code | Latest | https://code.visualstudio.com |

Recommended VS Code extensions:
```
ms-python.python
janisdd.vscode-edit-csv
DavidAnson.vscode-markdownlint
ms-vscode.powershell
```

---

## Step 2 — Clone and Install

```bash
git clone https://github.com/MichalG-tech/Git_MG.git
cd Git_MG

# Install Python dependencies
py -m pip install -r python-utilities/requirements.txt
```

Verify:
```bash
py -m pytest python-utilities/tests/ -v
# Expected: all tests pass
```

---

## Step 3 — Generate Sample Data

The CSV data files are not stored in Git (they're in `.gitignore`). Generate them locally:

```bash
py python-utilities/scripts/generate-data.py
```

This creates 7 CSV files in `data/raw/`:
- `orders.csv` — ~500,000 sales transactions
- `returns.csv` — ~25,000 return transactions
- `inventory.csv` — ~90,000 inventory snapshots
- `customers.csv` — 5,000 customers
- `products.csv` — 1,500 products
- `regions.csv` — 50 regions
- `date_dimension.csv` — daily calendar 2021–2026 with April fiscal calendar

---

## Step 4 — Open the Semantic Model

1. Launch **Tabular Editor 3**
2. **File → Open → From File**
3. Navigate to `semantic-models/sales-analytics/` and open the folder

Once loaded:
1. Go to **Model → Shared Expressions → DataFolderPath**
2. Update the value to your absolute `data/raw/` path:
   ```
   "C:/Users/yourname/GitFolder/data/raw/"
   ```
3. Click **File → Save** (saves back to the TMDL files)

---

## Step 5 — Open in Power BI Desktop

Since Power BI Desktop cannot open TMDL folders directly, you must connect via XMLA (requires Power BI Premium or PPU workspace) or use Tabular Editor as the authoring tool.

For local preview without a workspace:
1. In Tabular Editor 3: **Model → Deploy** to a local Analysis Services instance (if available)
2. Or: use the **External Tools** ribbon in Power BI Desktop to connect to Tabular Editor

---

## Step 6 — Validate Before Committing

Always validate before pushing code:

```bash
py python-utilities/scripts/run-all-checks.py
```

Fix any reported issues. The same checks run automatically in GitHub Actions — failing CI on a PR blocks the merge.

---

## Making a Change — End-to-End

### Add a new measure

1. Create a feature branch:
   ```bash
   git checkout -b feature/add-days-to-close-measure
   ```

2. Open `semantic-models/sales-analytics/tables/_Measures.tmdl` in VS Code or Tabular Editor 3

3. Add the measure following the template in [TMDL_STANDARDS.md](../semantic-models/TMDL_STANDARDS.md):
   ```tmdl
   measure 'Days to Close' = DIVIDE([Order Count], [Active Customers (90d)])
       formatString: #,##0.0
       lineageTag: me000009-0101-0000-0000-000000000001
       description: Average number of orders per active customer.
   ```

4. Validate:
   ```bash
   py python-utilities/scripts/run-all-checks.py
   ```

5. Commit and push:
   ```bash
   git add semantic-models/sales-analytics/tables/_Measures.tmdl
   git commit -m "feat(sales-model): Add days-to-close measure"
   git push origin feature/add-days-to-close-measure
   ```

6. Open a pull request targeting `develop`

7. GitHub Actions validates automatically. Once it passes, request a review. On merge, it auto-deploys to Dev.

---

## Key Files to Know

| File | What it is |
|------|-----------|
| `semantic-models/sales-analytics/tables/_Measures.tmdl` | All 63 DAX measures for Sales Analytics |
| `semantic-models/sales-analytics/relationships/relationships.tmdl` | All 12 relationships (active and inactive) |
| `python-utilities/scripts/run-all-checks.py` | Local validation — run before every commit |
| `python-utilities/scripts/generate-data.py` | Regenerates all 7 CSV data files |
| `config/data-generation-config.json` | Controls row counts for data generation |
| `docs/data/DATA_DICTIONARY.md` | Column-level reference for every table |
| `docs/architecture/DESIGN_DECISIONS.md` | Why the model is designed the way it is |

---

## Asking for Help

If something doesn't work:
1. Check [COMMON_ERRORS.md](../troubleshooting/COMMON_ERRORS.md) first
2. Run `py python-utilities/scripts/run-all-checks.py` — it usually tells you exactly what's wrong
3. Read the error in the GitHub Actions log — expand the failed step for the full output
4. Open an issue on the repository with the error message and the steps to reproduce
