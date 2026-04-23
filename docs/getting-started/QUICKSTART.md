# Quickstart Guide

Get the Power BI Enterprise PoC running in 5 minutes.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Git | Any | Repository management |
| Python | 3.11+ | Validation & data generation |
| Power BI Desktop | Latest | Report authoring & model testing |
| Tabular Editor 3 | Community+ | TMDL editing & deployment |

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/MichalG-tech/Git_MG.git
cd Git_MG
git checkout develop
```

---

## Step 2 — Install Python dependencies

```bash
pip install -r python-utilities/requirements.txt
```

---

## Step 3 — Generate sample data

```bash
py python-utilities/scripts/generate-data.py
```

Expected output:
```
[DimDate]     1,938 records -> date_dimension.csv
[DimRegion]      50 records -> regions.csv
[DimCustomer]  5,000 records -> customers.csv
[DimProduct]   1,500 records -> products.csv
[FactSales]  500,000 records -> orders.csv
[FactReturns]  25,000 records -> returns.csv
[FactInventory] 90,000 records -> inventory.csv
```

Data is written to `data/raw/`.

---

## Step 4 — Validate the semantic models

```bash
py python-utilities/scripts/run-all-checks.py
```

All checks should pass. If you see warnings, see [COMMON_ERRORS.md](../troubleshooting/COMMON_ERRORS.md).

---

## Step 5 — Open the model in Tabular Editor

1. Open **Tabular Editor 3**
2. File → Open → **From folder**
3. Select `semantic-models/sales-analytics/`
4. Navigate to **Tables → DimDate → Properties**
5. Set **Mark as Date Table** → Date column = `Date`

---

## Step 6 — Load into Power BI Desktop

1. Open **Power BI Desktop**
2. Home → **Transform data** → **Data source settings**
3. Update the `DataFolderPath` parameter to your `data/raw/` absolute path
4. Click **Refresh**

---

## What you now have

- **Sales Analytics model**: 8 tables, 63 measures, 2 RLS roles
- **Finance Reporting model**: 6 tables, 20 measures, 1 role
- **500,000+ transactions** of realistic sample data
- **Validated** TMDL files passing all automated checks

**Next step**: See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for full environment configuration including GitHub Actions secrets.
