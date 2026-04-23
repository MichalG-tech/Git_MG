# Frequently Asked Questions

---

## Setup and Configuration

**Q: Do I need a Power BI Premium licence to use this repository?**

For local development with Tabular Editor 3 — no. You can open, edit, and validate the TMDL models without any Premium licence.

For deployment via XMLA endpoint — yes. Power BI Premium Per User (PPU) is the most cost-effective option. It's a per-user monthly licence and provides XMLA read/write access.

For the PoC demonstration itself (showing the models to a client in Power BI Desktop): no Premium required. Connect Power BI Desktop to the semantic model via Tabular Editor's local Analysis Services instance.

---

**Q: Why do I need Tabular Editor 3 and not just Power BI Desktop?**

Power BI Desktop cannot open TMDL folders. It works with `.pbix` files (binary), which cannot be meaningfully version-controlled or code-reviewed.

Tabular Editor 3 is the authoring tool for TMDL. It saves changes as text files that Git can diff, merge, and review. This is the entire basis of the governance story.

---

**Q: Can I use Tabular Editor 2 (the free version)?**

Tabular Editor 2 supports TMDL in read mode only. You can inspect the model but cannot save changes back to TMDL format. You need Tabular Editor 3 for authoring and deployment.

---

**Q: Where do I put the CSV data files?**

Generate them:
```bash
py python-utilities/scripts/generate-data.py
```

They go into `data/raw/` automatically. The `DataFolderPath` parameter in the semantic model must point to this folder's absolute path on your machine.

---

**Q: Why aren't the CSV files in Git?**

Large data files don't belong in Git — they bloat the repository, make cloning slow, and can't be meaningfully diffed. Each developer generates their own local copy from the same deterministic script. For a production system, the CSVs would be replaced by direct warehouse connections.

---

## DAX and Measures

**Q: Why are all measures in `_Measures.tmdl` instead of in the fact tables?**

This is Power BI best practice. The `_Measures` hidden utility table:
- Keeps fact tables focused on data columns only
- Makes all measures easy to find in the Fields pane (one place to look)
- Simplifies automated extraction and documentation
- Follows the convention established by the broader Power BI community

See [DESIGN_DECISIONS.md](../architecture/DESIGN_DECISIONS.md) for the full rationale.

---

**Q: Some measures return BLANK in certain filters. Is that a bug?**

Usually not. Measures that use `USERELATIONSHIP()` (returns and inventory measures) only return values when the filter context comes from the correct dimension column. Make sure slicers reference DimDate, DimProduct, or DimRegion — not the fact table's raw date/ID columns.

If a measure that should never return BLANK does so, check whether the relationship between the relevant fact and dimension tables is active or inactive in `relationships.tmdl`.

---

**Q: Time intelligence measures (MTD, YTD) return unexpected values. What's wrong?**

Most likely DimDate hasn't been marked as the date table. In Power BI Desktop:
- Right-click DimDate in the Fields pane → **Mark as date table** → select the `Date` column

Also check that your report's date slicer is using `DimDate[Date]`, not a raw date column from a fact table. Time intelligence functions require the marked date table.

---

**Q: What's the difference between `Total Sales` and `Net Sales`?**

- `Total Sales` — gross revenue: `SUM(FactSales[TotalAmount])`. Already accounts for discounts (TotalAmount = Quantity × UnitPrice × (1 − DiscountPct)).
- `Net Sales` — revenue after returns: `[Total Sales] - [Return Amount]`.

Use `Total Sales` for top-line revenue reporting. Use `Net Sales` when returns need to be reflected.

---

**Q: Why does `Gross Margin %` look different from the list price margin?**

The Sales Analytics model uses the actual selling price (`FactSales[UnitPrice]`), which may differ from the list price (`DimProduct[UnitPrice]`). The difference is captured in `Price Realization %` which shows how close to list price the actual sales were.

---

## GitHub Actions

**Q: The PR validation workflow failed. Where do I look?**

1. Open **GitHub → Actions → PR Validation** and click the failed run
2. Expand the failed step — the error message is in the output
3. Run the same check locally first: `py python-utilities/scripts/run-all-checks.py`
4. Fix the reported issues and push again — the workflow re-runs automatically

Common causes and fixes are in [COMMON_ERRORS.md](COMMON_ERRORS.md).

---

**Q: Can I skip the PR validation checks for a quick fix?**

No. The validation checks exist to protect the model from breaking changes. Even small fixes can introduce issues (a missing description, a naming convention violation, a divide-by-zero). The checks run fast (under 2 minutes) and running them locally before pushing is even faster.

---

**Q: The deployment workflow is stuck at "Waiting for approval". What do I do?**

This is normal for Staging and Production deployments. A designated reviewer must:
1. Open the workflow run in GitHub Actions
2. Click **Review deployments**
3. Approve or reject

If the reviewer isn't available, escalate to the next available approver. Do not bypass the approval gate.

---

**Q: How do I force a Dev deployment without changing any model files?**

Go to **GitHub → Actions → Deploy to Dev → Run workflow**. The manual trigger (workflow_dispatch) bypasses the path filter.

---

## Finance Reporting Model

**Q: Why does the Finance Reporting model use hardcoded data instead of CSVs?**

The Finance Reporting model demonstrates an in-memory M-generated data pattern that's useful for:
- Chart of accounts that rarely change (DimAccount, DimDepartment, DimEntity)
- PoC scenarios where a live finance data source isn't available

In a production engagement, these tables would connect to the client's ERP system (SAP, Oracle, Dynamics 365).

---

**Q: What does "April fiscal year" mean for the Finance model?**

FY2023 = April 2022 to March 2023. This is common for UK companies, Indian companies, and many multinationals. The `DimPeriod` table has both calendar and fiscal year attributes so reports can be built using either convention.

---

**Q: What's the difference between FactActuals and FactBudget?**

- `FactActuals` — recorded financial transactions (revenue recognised, costs incurred)
- `FactBudget` — planned figures, available in three versions: Original Budget, Revised Budget, Latest Forecast

The key measures (`Variance`, `Variance %`, `Budget Attainment %`) compare Actuals against the appropriate Budget version using `CALCULATE()` with a `BudgetVersion` filter.

---

## Contributing

**Q: I want to add a new measure. What's the right process?**

See [FEATURE_WORKFLOW.md](../development/FEATURE_WORKFLOW.md) for the full workflow. The short version:
1. Create a feature branch
2. Add the measure to `_Measures.tmdl` with a description, formatString, and unique lineageTag
3. Run `py python-utilities/scripts/run-all-checks.py`
4. Update CHANGELOG.md
5. Open a PR targeting `develop`

---

**Q: Can I change the data generation parameters (number of customers, products, etc.)?**

Yes. Edit `config/data-generation-config.json` and re-run `py python-utilities/scripts/generate-data.py`. Keep in mind that changing row counts may affect performance tests and any expected-value assertions in unit tests.
