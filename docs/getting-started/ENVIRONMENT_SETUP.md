# Environment Setup Guide

Full environment configuration for local development and CI/CD deployment.

---

## Local Development Environment

### Python Setup

```bash
# Install Python 3.11+ (https://python.org)
py --version          # Should show Python 3.11.x or higher

# Install dependencies
pip install -r python-utilities/requirements.txt

# Verify installation
py -m pytest python-utilities/tests/ -v
```

### Git Configuration

```bash
# Configure line endings (important on Windows)
git config core.autocrlf false     # Use .gitattributes settings
git config core.eol lf

# Set your identity
git config user.name "Your Name"
git config user.email "your@email.com"
```

### Tabular Editor 3

1. Download from [tabulareditor.com](https://tabulareditor.com/)
2. Install to default location
3. Add to PATH: `C:\Program Files\Tabular Editor 3\`
4. Verify: `TabularEditor3.exe --help`

### Power BI Desktop

1. Download from [Microsoft Store](https://aka.ms/pbidesktopstore) or MSI
2. Enable XMLA endpoint preview features:
   - File → Options → Preview features → ✓ XMLA endpoint

### VS Code Extensions (Recommended)

```
ms-python.python
janisdd.vscode-edit-csv
DavidAnson.vscode-markdownlint
ms-vscode.powershell
```

---

## GitHub Repository Secrets

Configure these secrets in **GitHub → Settings → Secrets and variables → Actions**:

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `POWERBI_CLIENT_ID` | Azure AD app client ID | All environments |
| `POWERBI_TENANT_ID` | Azure AD tenant ID | All environments |
| `POWERBI_CLIENT_SECRET` | Azure AD app secret | All environments |
| `DEV_WORKSPACE_ID` | Dev workspace GUID | deploy-dev.yml |
| `TEST_WORKSPACE_ID` | Test workspace GUID | deploy-test.yml |
| `STAGING_WORKSPACE_ID` | Staging workspace GUID | deploy-staging.yml |
| `PROD_WORKSPACE_ID` | Production workspace GUID | deploy-prod.yml |

### Creating the Azure AD Service Principal

```bash
# Using Azure CLI
az ad sp create-for-rbac \
  --name "PowerBI-PoC-ServicePrincipal" \
  --role "Contributor" \
  --scopes "/subscriptions/{subscription-id}"

# Note the output: appId (CLIENT_ID), password (CLIENT_SECRET), tenant (TENANT_ID)
```

### Granting Power BI Access

1. Power BI Admin portal → Tenant settings → Developer settings
2. Enable **Service principals can use Power BI APIs**
3. Add the service principal to each workspace as **Member** or **Admin**

---

## GitHub Environments

Create these environments in **GitHub → Settings → Environments**:

| Environment | Protection Rule | Secret Override |
|-------------|-----------------|-----------------|
| `dev` | None (auto-deploy) | None |
| `test` | None | None |
| `staging` | Required reviewer: repo maintainer | None |
| `production` | Required reviewer: senior maintainer | None |

---

## DataFolderPath Parameter

The Sales Analytics model uses a `DataFolderPath` parameter to locate CSV files.

**In Tabular Editor:**
1. Model → Shared Expressions → `DataFolderPath`
2. Update value to your absolute `data/raw/` path, e.g.:
   `"C:/Users/yourname/GitFolder/data/raw/"`

**In Power BI Desktop:**
1. Home → Transform data → Edit parameters
2. Update `DataFolderPath` value

---

## Verifying Your Setup

Run this checklist after environment setup:

```bash
# 1. Data generator works
py python-utilities/scripts/generate-data.py
# Expected: 7 CSV files in data/raw/

# 2. Validators pass
py python-utilities/scripts/run-all-checks.py
# Expected: All checks pass

# 3. Unit tests pass
py -m pytest python-utilities/tests/ -v
# Expected: All tests pass

# 4. Git hooks work (if configured)
git commit --allow-empty -m "test: verify hooks"
```

If any step fails, see [COMMON_ERRORS.md](../troubleshooting/COMMON_ERRORS.md).
