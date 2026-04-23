# Common Errors & Solutions

Fixes for the most frequently encountered issues in this repository.

---

## Python & Data Generation

### `ModuleNotFoundError: No module named 'pandas'`

**Cause**: Dependencies not installed.

```bash
py -m pip install -r python-utilities/requirements.txt
```

Verify:
```bash
py -c "import pandas; print(pandas.__version__)"
```

---

### `UnicodeEncodeError: 'charmap' codec can't encode character`

**Cause**: Windows console uses cp1252 by default; some Python scripts print UTF-8 symbols.

**Fix**: Run with UTF-8 mode or update your terminal:
```bash
py -X utf8 python-utilities/scripts/generate-data.py
```

Or set the environment variable permanently:
```powershell
[System.Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
```

---

### `KeyError: 'output'` or `FileNotFoundError` in generate-data.py

**Cause**: Script resolves config path relative to the current working directory, not the script location.

**Fix**: Always run scripts from the repository root:
```bash
cd C:\Users\yourname\GitFolder
py python-utilities/scripts/generate-data.py
```

---

### Data generator produces empty CSV files

**Cause**: Config row counts are zero, or a date range mismatch prevents join keys from aligning.

**Fix**: Check `config/data-generation-config.json` — verify `num_customers`, `num_products`, `num_orders` are non-zero and the `date_range` spans at least one full year.

---

## TMDL Validation

### `PR Validation` fails — "Missing description on table"

**Cause**: A new TMDL table or column was added without a `description:` property.

**Fix**: Add descriptions before committing. Run locally first:
```bash
py python-utilities/scripts/run-all-checks.py
```

Every table, every visible column, and every measure must have a `description:` property. See [TMDL_STANDARDS.md](../semantic-models/TMDL_STANDARDS.md).

---

### `PR Validation` fails — "Forbidden pattern: DIVIDE not used"

**Cause**: A measure uses `/` for division instead of `DIVIDE()`.

```dax
// Wrong
Margin % = [Profit] / [Revenue]

// Correct
Margin % = DIVIDE([Profit], [Revenue])
```

---

### `PR Validation` fails — "Table naming violation"

**Cause**: Table name uses an unsupported prefix (e.g., `tbl_Sales` or `dim_Date`).

Allowed patterns per [TMDL_STANDARDS.md](../semantic-models/TMDL_STANDARDS.md):
- Dimension tables: `DimXxx` (e.g., `DimDate`, `DimCustomer`)
- Fact tables: `FactXxx` (e.g., `FactSales`, `FactReturns`)
- Hidden utility tables: `_Xxx` (e.g., `_Measures`, `_Parameters`)

---

### Tabular Editor 3 — `File not found` when opening TMDL folder

**Cause**: Power BI Desktop cannot open TMDL folders directly. Only Tabular Editor 3 supports TMDL.

**Fix**: Open Tabular Editor 3, then use **File → Open → From File** and select the model folder (e.g., `semantic-models/sales-analytics/`).

---

### Tabular Editor 3 — Model loads but relationships show errors

**Cause**: The CSV data files haven't been generated yet, so M queries can't resolve the `DataFolderPath` parameter.

**Fix**:
1. Generate data: `py python-utilities/scripts/generate-data.py`
2. Update `DataFolderPath` in TE3: **Model → Shared Expressions → DataFolderPath**
3. Set the value to your absolute `data/raw/` path: `"C:/Users/yourname/GitFolder/data/raw/"`

---

## GitHub Actions

### PR validation fails — Python version mismatch

**Cause**: Workflow specifies Python 3.11 but a package requires a newer version.

**Fix**: Raise the version in the workflow file:
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.12'
```

---

### `deploy-dev.yml` skips — no model files changed

**Cause**: The workflow path filter only triggers on changes inside `semantic-models/**` or `data/**`. A commit that only touches docs or Python scripts will not trigger a deployment.

This is intentional — avoids unnecessary deploys. To force a deploy, use **Actions → deploy-dev → Run workflow**.

---

### `DEV_WORKSPACE_ID` secret not found

**Cause**: GitHub Secrets haven't been configured yet.

**Fix**: Go to **GitHub → Settings → Secrets and variables → Actions → New repository secret**.

Required secrets: `POWERBI_CLIENT_ID`, `POWERBI_TENANT_ID`, `POWERBI_CLIENT_SECRET`, plus one workspace ID per environment. See [ENVIRONMENT_SETUP.md](../getting-started/ENVIRONMENT_SETUP.md).

---

### Staging / Production deployment stuck at "Waiting for approval"

This is expected behaviour — both environments require a required reviewer to approve before deployment proceeds.

**Fix**: The reviewer must open the workflow run in the GitHub Actions UI and click **Review deployments → Approve**.

---

### Production deployment rejected — `confirmed` input was wrong

**Cause**: The `confirmed` input must be exactly `CONFIRM` (uppercase, no spaces). Any other value causes the preflight job to fail before requesting approval.

---

## Power BI Desktop

### `DataFolderPath` prompt appears on open

**Cause**: The parameter value stored in the TMDL uses a path that doesn't exist on your machine.

**Fix**: When prompted, enter your absolute `data/raw/` path. Or update it permanently in Power BI Desktop:
**Home → Transform data → Edit parameters → DataFolderPath**

---

### Time intelligence measures return BLANK

**Cause**: DimDate has not been marked as the date table.

**Fix**: Right-click **DimDate** in the Fields pane → **Mark as date table** → select the `Date` column.

---

### Inactive relationship measures return wrong results

**Cause**: Measures that use USERELATIONSHIP() only work when the filter context is set correctly. Placing them inside the wrong visual or slicer type can suppress the relationship activation.

**Fix**: Ensure the slicer or axis field comes from DimDate, not from the fact table's `OrderDate` / `ReturnDate` columns. Only DimDate participates in the active/inactive relationship chain.

---

## Git

### `git push` rejected — branch protection

**Cause**: Direct pushes to `main` are blocked by branch protection rules.

**Fix**: Always push to a feature branch and open a pull request:
```bash
git checkout -b feature/my-change
git push origin feature/my-change
# Open PR → target: develop
```

---

### Merge conflict in a TMDL file

TMDL files are text — conflicts can be resolved in any text editor. Key rules:
1. Never duplicate a `lineageTag` — each must be unique across the model
2. Measure order within `_Measures.tmdl` doesn't affect model behaviour; keep alphabetical or grouped by category
3. After resolving, run `py python-utilities/scripts/run-all-checks.py` before committing

---

If the issue isn't listed here, check the [GitHub Actions run log](../../.github/workflows/) for the exact error message, or open an issue on the repository.
