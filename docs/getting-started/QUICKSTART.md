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

## Step 5 — Open the model in Tabular Editor 3

1. Open **Tabular Editor 3**
2. **File → Open → From File** — select the `semantic-models/sales-analytics/` folder
3. In the left panel: expand **Shared Expressions → DataFolderPath**
4. Update the M value to your absolute `data/raw/` path:
   ```
   "C:/Users/yourname/GitFolder/data/raw/"
   ```
5. **File → Save** — writes the change back to the TMDL files

---

## Step 6 — Preview in Power BI Desktop (Desktop-only, no Premium needed)

Power BI Desktop cannot open TMDL folders directly, but Tabular Editor 3 can deploy the model to Desktop's embedded Analysis Services engine:

1. Open **Power BI Desktop** → create a new blank report (this starts the local AS engine)
2. Back in **Tabular Editor 3** — with the model still open, click **File → Deploy**
3. TE3 detects the running Power BI Desktop instance automatically — select it from the list
4. Enter a database name (e.g. `sales-analytics`) and click **Deploy**
5. In Power BI Desktop: the model fields now appear in the **Fields** pane
6. Build visuals — slicers, charts, tables — using the 63 pre-built measures

> Power BI Desktop also shows **Tabular Editor 3** in its **External Tools** ribbon once TE3 is installed, which opens TE3 already connected to the local model.

---

## What you now have

- **Sales Analytics model**: 7 tables, 63 measures, 2 RLS roles — live in Power BI Desktop
- **Finance Reporting model**: 6 tables, 20 measures, 1 role — ready to deploy the same way
- **500,000+ transactions** of realistic sample data
- **Validated** TMDL files passing all automated checks

**Next step**: See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for full configuration including GitHub Actions and (optionally) Power BI Service deployment.
