# Tabular Editor 3 Guide

How to use Tabular Editor 3 (TE3) with the TMDL semantic models in this repository.

---

## Why Tabular Editor 3

Power BI Desktop cannot open TMDL folders directly. Tabular Editor 3 is the primary authoring and editing tool for TMDL-based models:

- Opens `semantic-models/<model-name>/` folders natively
- Saves changes directly back to `.tmdl` files
- Validates model integrity (circular dependencies, broken relationships)
- Deploys to Power BI workspaces via XMLA endpoint
- Runs Best Practice Analyser (BPA) rules

**Tabular Editor 2** (free, open-source) supports TMDL in read mode only. Authoring and deployment require **Tabular Editor 3** (commercial licence).

---

## Installation

1. Download from [tabulareditor.com](https://tabulareditor.com/)
2. Install to the default location: `C:\Program Files\Tabular Editor 3\`
3. Add to PATH so the CLI is accessible:
   ```powershell
   $env:PATH += ";C:\Program Files\Tabular Editor 3\"
   ```
4. Verify CLI access:
   ```bash
   TabularEditor3.exe --help
   ```

---

## Opening a Model

1. Launch Tabular Editor 3
2. **File → Open → From File**
3. Navigate to `semantic-models/sales-analytics/` and select the folder (not a specific file)
4. TE3 loads all `.tmdl` files and reconstructs the full model in memory

---

## Configuring DataFolderPath

The Sales Analytics model uses a `DataFolderPath` parameter to locate CSV files. After opening the model:

1. In the left panel, expand **Shared Expressions**
2. Double-click **DataFolderPath**
3. Update the M expression to your local path:
   ```m
   "C:/Users/yourname/GitFolder/data/raw/" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
   ```
4. **File → Save** — this writes the change to `definition/model.tmdl`

Note: Use forward slashes in the path even on Windows.

---

## Editing Measures

### In the TE3 UI

1. Expand **Tables → _Measures** in the left panel
2. Click a measure to open it in the expression editor
3. Edit the DAX, description, or formatString in the Properties pane
4. **File → Save** when done

### Directly in VS Code

`.tmdl` files are plain text. You can edit `tables/_Measures.tmdl` in VS Code and TE3 will reflect the changes when you reopen the model.

Measure template:
```tmdl
measure 'Measure Name' = <DAX expression>
    formatString: $ #,##0
    lineageTag: meXXXXXX-0101-0000-0000-000000000001
    description: What this measure calculates and any caveats.
```

Requirements:
- `lineageTag` must be unique across the entire model — increment the hex prefix for each new measure
- `description` is mandatory — the CI validator rejects measures without one
- `formatString` is mandatory — never leave the default

---

## Validating with the CLI

The `python-utilities/src/tabular_editor/__init__.py` module wraps the TE3 CLI. You can also call it directly:

```bash
# Validate model structure (checks for broken references, circular dependencies)
TabularEditor3.exe semantic-models/sales-analytics/ -V

# Run Best Practice Analyser with default rules
TabularEditor3.exe semantic-models/sales-analytics/ -BPA
```

The Python validation script (`run-all-checks.py`) runs the text-based TMDL checks. TE3 CLI validation adds a deeper structural check (requires TE3 installed and on PATH).

---

## Deploying via XMLA

Deploying to a Power BI workspace requires:
1. A Power BI Premium or PPU workspace with XMLA endpoint enabled
2. An Azure AD service principal with workspace Member or Admin access
3. The workspace XMLA endpoint URL (format: `powerbi://api.powerbi.com/v1.0/myorg/<workspace-name>`)

```bash
# Deploy to a workspace
TabularEditor3.exe semantic-models/sales-analytics/ \
  -D "powerbi://api.powerbi.com/v1.0/myorg/Dev-Workspace" \
  "sales-analytics" \
  -O \
  -U "<client-id>" \
  -P "<client-secret>"
```

In practice, this command is invoked by the GitHub Actions deployment workflows rather than run manually. See [DEPLOYMENT_GUIDE.md](../deployment/DEPLOYMENT_GUIDE.md) for the full deployment pipeline.

---

## Best Practice Analyser (BPA)

TE3's BPA runs a configurable set of quality rules against the model. To use custom rules:

1. Place a `BPA.json` file in the model folder
2. Run: `TabularEditor3.exe semantic-models/sales-analytics/ -BPA BPA.json`

The Python BPA wrapper (`python-utilities/src/tabular_editor/__init__.py`) supports passing a custom rules file via `run_bpa(model_path, rules_file="BPA.json")`.

---

## Saving and Committing

TE3 saves all changes back to the `.tmdl` files in the model folder. After saving in TE3:

```bash
# Check what changed
git diff semantic-models/

# Stage and commit
git add semantic-models/sales-analytics/
git commit -m "feat(sales-model): Add customer lifetime value measure"
```

TMDL diffs are human-readable — reviewers can see exactly which measure was added or changed in the pull request without loading the model.

---

## Relationship Management

To add or modify a relationship in TE3:
1. Open the **Relationships** view (**Model → Relationships**)
2. Drag from the foreign key column to the primary key column
3. Set Active/Inactive, Cardinality, and Cross-filter direction in the Properties pane

All relationships are stored in `relationships/relationships.tmdl`. The standard for this model:
- `isActive: true` for FactSales → all dimension relationships
- `isActive: false` for FactReturns and FactInventory relationships (use USERELATIONSHIP() in DAX)
- Cardinality: always `manyToOne` (fact → dimension)
- Cross-filter: `singleDirection` (dimension filters fact, not the reverse)

---

## Troubleshooting TE3 Issues

### Model loads but all measures show `[Error]`

Likely `DataFolderPath` points to a directory that doesn't exist on your machine. Update the parameter value (see [Configuring DataFolderPath](#configuring-datafoldepath) above) and generate the data files first:
```bash
py python-utilities/scripts/generate-data.py
```

### `TabularEditor3.exe` not found in CLI

Add the TE3 installation directory to your PATH:
```powershell
$env:PATH += ";C:\Program Files\Tabular Editor 3\"
```

Or use the full path in scripts:
```bash
"C:/Program Files/Tabular Editor 3/TabularEditor3.exe" semantic-models/sales-analytics/ -V
```

### XMLA deployment fails with 403 Forbidden

The service principal does not have sufficient permissions on the workspace. In Power BI Admin portal:
1. **Tenant settings → Developer settings → Service principals can use Power BI APIs** — must be enabled
2. Workspace settings → Add the service principal as Member or Admin
