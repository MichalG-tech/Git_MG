# Tabular Editor 3 Guide

How to use Tabular Editor 3 (TE3) with the TMDL semantic models in this repository.

---

## Deployment Modes — Desktop vs Service

This PoC supports two deployment targets:

| Mode | Requirement | What it enables |
|------|-------------|----------------|
| **Desktop (local)** | Power BI Desktop + TE3 | Full model authoring and visual building on your machine — no licence beyond Desktop |
| **Service (workspace)** | Power BI Premium or PPU workspace | Shared workspaces, scheduled refresh, row-level security enforcement, GitHub Actions CI/CD |

**If you have Power BI Desktop only** — use the Desktop mode. Everything in the PoC (TMDL authoring, 83 measures, validation, GitHub Actions CI) is fully accessible. The Service deployment workflows are included as architecture demonstrations for clients who do have Premium.

---

## Why Tabular Editor 3

Power BI Desktop cannot open TMDL folders directly. Tabular Editor 3 is the primary authoring and editing tool for TMDL-based models:

- Opens `semantic-models/<model-name>/` folders natively
- Saves changes directly back to `.tmdl` files
- Validates model integrity (circular dependencies, broken relationships)
- Deploys to Power BI Desktop's local engine **or** to a Premium workspace via XMLA
- Runs Best Practice Analyser (BPA) rules

**Tabular Editor 2** (free, open-source) supports TMDL in read mode only. Authoring and deployment require **Tabular Editor 3** (Community tier is free).

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

## Deploying — Desktop (Local, No Premium)

This is the primary workflow for Power BI Desktop users.

**Prerequisites:** Power BI Desktop open with any file (even a blank report).

1. Open **Power BI Desktop** → create a new blank report. Desktop silently starts a local Analysis Services engine on a dynamic port.
2. In **Tabular Editor 3** with the model open: **File → Deploy**
3. TE3 automatically detects running Power BI Desktop instances and lists them in the target dropdown
4. Select the Power BI Desktop instance, enter a database name (e.g. `sales-analytics`), click **Deploy**
5. Switch to Power BI Desktop — all 63 measures and 7 tables appear in the **Fields** pane immediately
6. Build visuals. The model behaves identically to one deployed to a Premium workspace.

> **External Tools shortcut**: If TE3 is installed before Power BI Desktop, it registers itself as an External Tool. Open a blank .pbix in Desktop, then click **External Tools → Tabular Editor 3** — TE3 opens pre-connected to the local model. Editing and saving in TE3 updates the local model in real time.

**Important**: The local AS instance is in-memory only. When you close Power BI Desktop, the deployed model is gone — changes are only persisted in the `.tmdl` files on disk (which TE3 saves separately via **File → Save**).

---

## Deploying — Service (Requires Power BI Premium or PPU)

Deploying to a shared Power BI workspace for multi-user access, scheduled refresh, and RLS enforcement requires:
1. A Power BI Premium or PPU workspace with XMLA read/write enabled
2. An Azure AD service principal with workspace Member or Admin access
3. The workspace XMLA endpoint URL

```bash
# Deploy to a Premium workspace via CLI
TabularEditor3.exe semantic-models/sales-analytics/ \
  -D "powerbi://api.powerbi.com/v1.0/myorg/Dev-Workspace" \
  "sales-analytics" \
  -O \
  -U "<client-id>" \
  -P "<client-secret>"
```

This command is what the GitHub Actions deployment workflows execute automatically. See [DEPLOYMENT_GUIDE.md](../deployment/DEPLOYMENT_GUIDE.md) for the full pipeline setup.

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
