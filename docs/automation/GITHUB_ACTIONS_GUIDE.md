# GitHub Actions Guide

Reference for the 5 CI/CD workflows in this repository.

---

## Licence Requirements

The five workflows split into two categories:

| Workflow | Requires Premium? | Notes |
|----------|------------------|-------|
| `pr-validation.yml` | **No** | Runs Python validators and unit tests — works with any GitHub plan |
| `deploy-dev.yml` | **Yes** | Deploys to a Power BI workspace via XMLA — requires Premium or PPU |
| `deploy-test.yml` | **Yes** | Same |
| `deploy-staging.yml` | **Yes** | Same |
| `deploy-prod.yml` | **Yes** | Same |

**Desktop-only users**: the PR validation workflow runs fully on every push and pull request. The deploy workflows are included to demonstrate the enterprise CI/CD architecture — they are wired and ready to execute the moment Power BI Premium workspaces are configured.

---

## Pipeline Overview

```
Developer pushes code
        │
        ▼
┌─────────────────┐
│ PR Validation   │  ← Runs on every PR to main/develop
│ (pr-validation) │    TMDL + Python + unit tests
└────────┬────────┘
         │ PR merged to develop
         ▼
┌─────────────────┐
│ Deploy to Dev   │  ← Auto-deploys on push to develop
│ (deploy-dev)    │    No approval required
└────────┬────────┘
         │ Release candidate tag (v*.*.*-rc*)
         ▼
┌─────────────────┐
│ Deploy to Test  │  ← Deploys pre-release builds
│ (deploy-test)   │    QA validation window
└────────┬────────┘
         │ Stable release tag (v*.*.*)
         ▼
┌─────────────────┐
│ Deploy to       │  ← Requires maintainer approval
│ Staging         │    Production mirror
└────────┬────────┘
         │ Workflow dispatch (manual)
         ▼
┌─────────────────┐
│ Deploy to       │  ← Requires CONFIRM input + approval
│ Production      │    Full audit trail written
└─────────────────┘
```

---

## Workflow Details

### 1. PR Validation (`pr-validation.yml`)

**Triggers**: Pull requests targeting `main` or `develop`  
**Purpose**: Prevent broken TMDL from being merged

Checks performed:
1. **TMDL syntax** — balanced brackets, required keywords, Dim/Fact naming
2. **Best practices** — descriptions, forbidden patterns, naming conventions
3. **Unit tests** — validates the Python utilities themselves
4. **CHANGELOG check** — warns (non-blocking) if model files changed without a CHANGELOG entry

**What to do if it fails:**
- Run `py python-utilities/scripts/run-all-checks.py` locally first
- Fix reported errors in the TMDL files
- Update CHANGELOG.md with your change description

---

### 2. Deploy to Dev (`deploy-dev.yml`)

**Triggers**: Push to `develop` branch (model or data changes only)  
**Purpose**: Continuous deployment for the development team  
**Approval**: None required

The workflow:
1. Checks out the branch
2. Runs pre-deployment validation
3. Deploys to the Dev Power BI workspace via XMLA
4. Writes a deployment summary to the GitHub Actions job

**Required GitHub Secret**: `DEV_WORKSPACE_ID`

---

### 3. Deploy to Test (`deploy-test.yml`)

**Triggers**: GitHub pre-release created (tag pattern `v*.*.*-rc*`)  
**Purpose**: Provide QA with a stable, versioned snapshot  
**Approval**: None (but pre-release tag creation is itself controlled)

How to create a release candidate:
```bash
git tag v1.1.0-rc1 -m "Release candidate 1 for v1.1.0"
git push origin v1.1.0-rc1
# Or create a pre-release in GitHub Releases UI
```

**Required GitHub Secret**: `TEST_WORKSPACE_ID`

---

### 4. Deploy to Staging (`deploy-staging.yml`)

**Triggers**: GitHub stable release created (tag pattern `v*.*.*`)  
**Purpose**: Final validation before production  
**Approval**: Required — repo maintainer must approve in GitHub Actions UI

The `staging` environment has a required reviewer configured. GitHub will pause the deployment and notify the reviewer. The reviewer must click **Approve** in the workflow run UI before deployment proceeds.

**Required GitHub Secret**: `STAGING_WORKSPACE_ID`

---

### 5. Deploy to Production (`deploy-prod.yml`)

**Triggers**: Manual only (`workflow_dispatch`)  
**Purpose**: Controlled production releases with full audit trail  
**Approval**: Required — senior maintainer must approve

Required inputs:
- `version` — exact release version (must match a tested Staging version)
- `change_ticket` — change management reference (CHG-XXXX)
- `confirmed` — must type `CONFIRM` exactly

Every production deployment writes a line to `deployment/change-log/releases/deployment-log.txt` and commits it automatically.

**Required GitHub Secret**: `PROD_WORKSPACE_ID`

---

## Configuring GitHub Environments

1. Go to **GitHub → Settings → Environments**
2. Create environments: `dev`, `test`, `staging`, `production`
3. For `staging` and `production`: add **Required reviewers**
4. For `production`: optionally add **Deployment branches** (restrict to `main`)

---

## Repository Variables

Set these in **GitHub → Settings → Variables** (not Secrets):

| Variable | Example Value | Used In |
|----------|--------------|---------|
| `DEV_WORKSPACE_URL` | `https://app.powerbi.com/groups/...` | deploy-dev summary |

---

## Debugging Failed Workflows

1. Click the failed workflow run in the **Actions** tab
2. Expand the failed step to see the full error output
3. For validation failures: run the same checks locally
4. For deployment failures: check the Power BI workspace permissions and XMLA endpoint status

See [COMMON_ERRORS.md](../troubleshooting/COMMON_ERRORS.md) for specific error solutions.
