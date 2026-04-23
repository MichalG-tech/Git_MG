# Debug Guide

How to diagnose and fix issues systematically across Python, TMDL, GitHub Actions, and Power BI.

---

## Debugging Principles

1. **Read the error message completely** before searching for solutions — most error messages tell you exactly what's wrong and where
2. **Reproduce locally first** — if a GitHub Actions check fails, run the same command locally before pushing a fix
3. **Isolate the change** — if something broke after a commit, run `git diff HEAD~1` to see exactly what changed
4. **Check the audit log** — for deployment issues, check `deployment/change-log/releases/deployment-log.txt`

---

## Python Debugging

### Getting a full traceback

By default some scripts suppress stack traces. For full output:

```bash
py -u python-utilities/scripts/generate-data.py 2>&1
py -u python-utilities/scripts/run-all-checks.py 2>&1
```

The `-u` flag disables output buffering, which helps on Windows when output gets swallowed.

### Testing a single validator in isolation

```bash
py -c "
from python_utilities.src.validators.best_practices_checker import BestPracticesChecker
checker = BestPracticesChecker()
results = checker.check('semantic-models/sales-analytics/')
for r in results:
    print(r)
"
```

### Running a single test file

```bash
py -m pytest python-utilities/tests/test_validators.py -v
py -m pytest python-utilities/tests/test_validators.py::TestNamingConventions::test_measure_title_case -v
```

### Debugging data generation

If CSVs are generated but the row counts look wrong, add verbose output:

```bash
py -c "
import json, pathlib
config = json.loads(pathlib.Path('config/data-generation-config.json').read_text())
print(json.dumps(config, indent=2))
"
```

Compare the config values to the expected row counts in [DATA_DICTIONARY.md](../data/DATA_DICTIONARY.md).

---

## TMDL Debugging

### Finding the exact line causing a validation failure

The validator reports table and measure names. To find the measure in the file:

```bash
grep -n "measure 'Total Sales'" semantic-models/sales-analytics/tables/_Measures.tmdl
```

On Windows (PowerShell):
```powershell
Select-String -Path "semantic-models\sales-analytics\tables\_Measures.tmdl" -Pattern "measure 'Total Sales'"
```

### Checking for duplicate lineageTags

Each measure must have a unique `lineageTag`. To check for duplicates:

```bash
grep -h "lineageTag:" semantic-models/sales-analytics/tables/*.tmdl | sort | uniq -d
```

Any output means there are duplicates — change the hex prefix on the newer measure.

### Checking descriptions are present

```bash
grep -c "description:" semantic-models/sales-analytics/tables/_Measures.tmdl
```

This should equal the number of measures in the file. If it's lower, some measures are missing descriptions.

### Validating bracket balance

TMDL uses indentation rather than brackets for nesting, but curly braces appear in M queries. To check for unbalanced braces in an M partition:

Open the file in VS Code — the editor's bracket matching highlights any unbalanced pairs.

### Relationship debugging

If a measure returns wrong results and you suspect a relationship issue, check `relationships.tmdl`:

1. Confirm the relationship `fromColumn` and `toColumn` match the actual column names in the respective TMDL files
2. Confirm `isActive` is set correctly (only FactSales relationships should be active)
3. Confirm measures that use USERELATIONSHIP() reference the correct relationship tables and columns

---

## GitHub Actions Debugging

### Reading the Actions log

1. Go to **GitHub → Actions**
2. Click the failed workflow run (red X)
3. Click the failed job
4. Expand the failed step — the full error message is in the collapsible section

### Reproducing CI checks locally

The PR validation workflow runs these commands — run them in order locally:

```bash
# Step 1: TMDL syntax check
py -c "
import sys
sys.path.insert(0, 'python-utilities')
from src.validators.tmdl_validator import TmdlValidator
v = TmdlValidator()
results = v.validate_all('semantic-models/')
for r in results: print(r)
"

# Step 2: Best practices
py python-utilities/scripts/run-all-checks.py

# Step 3: Unit tests
py -m pytest python-utilities/tests/ -v

# Step 4: CHANGELOG check (did model files change without a CHANGELOG update?)
git diff --name-only HEAD~1 | grep "semantic-models/"
git diff --name-only HEAD~1 | grep "CHANGELOG.md"
```

### Debugging secret-related failures

If a deployment fails with a 401 or 403 error, the service principal credentials are likely wrong or expired:

1. Go to **GitHub → Settings → Secrets → POWERBI_CLIENT_SECRET**
2. Confirm the secret value matches what's in the Azure portal
3. In Azure AD → App registrations → the service principal → Certificates & secrets — check the expiry date
4. If expired, generate a new secret and update the GitHub secret

### Debugging environment approval issues

If the workflow is stuck and no notification was sent to the reviewer:

1. Confirm the reviewer is configured: **GitHub → Settings → Environments → staging → Required reviewers**
2. The reviewer must be a repository collaborator with at least Write access
3. The reviewer must have GitHub notifications enabled for this repository

---

## Power BI Desktop Debugging

### Diagnosing DAX errors in measures

When a measure shows `[Error]` in a visual:
1. Open Power BI Desktop
2. **Modeling → New measure** (temporary)
3. Write: `= <MeasureName>` and check what error appears in the formula bar
4. Or use **Performance Analyzer** (View menu) to capture the DAX query and run it in DAX Studio

### Debugging time intelligence measures

Time intelligence measures (MTD, YTD, rolling) require:
1. DimDate marked as date table (right-click → Mark as date table → select `Date` column)
2. The visual's date axis or slicer must use `DimDate[Date]`, not a fact table date column
3. The DimDate range must cover the dates in your data

To test a time intelligence measure in isolation:
1. Create a table visual with `DimDate[Year]`, `DimDate[Month]`, and the measure
2. Check whether values roll over correctly at year boundaries

### Debugging inactive relationships (Returns and Inventory)

Measures using `USERELATIONSHIP()` for returns/inventory require the slicer or axis to come from the correct dimension:

- Returns by date → slicer must use `DimDate[Date]` (DimDate → FactReturns[DateID] inactive relationship)
- Returns by product → slicer must use `DimProduct[ProductName]` (DimProduct → FactReturns[ProductID] inactive relationship)

If the measure returns BLANK, check that:
1. The slicer field matches the relationship columns in `relationships.tmdl`
2. The `USERELATIONSHIP()` call references exactly the same column names as in the relationship definition
3. The inactive relationship exists in `relationships.tmdl` (check `isActive: false` is set)

---

## Data Quality Debugging

### Verifying referential integrity

After generating data, check that FK columns in fact tables have matching keys in dimension tables:

```python
import pandas as pd

orders = pd.read_csv('data/raw/orders.csv')
customers = pd.read_csv('data/raw/customers.csv')

orphaned = orders[~orders['CustomerID'].isin(customers['CustomerID'])]
print(f"Orphaned CustomerIDs in orders: {len(orphaned)}")
```

Run similar checks for ProductID, RegionID, and DateID. The generator produces clean data but this is useful after manual edits to the config.

### Checking date range coverage

DimDate covers 2021-01-01 to 2026-04-22. If FactSales has orders outside this range, DateID joins will return BLANK:

```python
import pandas as pd
dates = pd.read_csv('data/raw/date_dimension.csv')
orders = pd.read_csv('data/raw/orders.csv')

unmatched = orders[~orders['DateID'].isin(dates['DateID'])]
print(f"Orders with unmatched DateID: {len(unmatched)}")
```

If `config/data-generation-config.json` date_range extends beyond the DimDate coverage, regenerate both files.
