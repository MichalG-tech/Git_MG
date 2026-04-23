# Deployment Guide

Step-by-step procedures for deploying semantic models across all five environments.

---

## Architecture Overview

```
Developer workstation (Local)
        │ git push → develop
        ▼
    Dev workspace         ← auto-deploy on every merge to develop
        │ git tag v1.0.0-rc1
        ▼
    Test workspace        ← auto-deploy on pre-release tag
        │ git tag v1.0.0
        ▼
    Staging workspace     ← deploy on stable release tag (requires approval)
        │ workflow_dispatch (manual)
        ▼
    Production workspace  ← manual only, CONFIRM input + approval + audit log
```

Each environment maps to a Power BI Premium or PPU workspace. The Tabular Editor 3 CLI performs the actual XMLA endpoint deployment (`TabularEditor3.exe -D` flag).

---

## Environment Reference

| Environment | Trigger | Approval | Audience |
|-------------|---------|----------|---------|
| Dev | Push to `develop` | None | Development team |
| Test | Pre-release tag (`v*.*.*-rc*`) | None | QA team |
| Staging | Stable release tag (`v*.*.*`) | Repo maintainer | Business reviewers |
| Production | Manual dispatch | Senior maintainer | End users |

---

## Deploying to Dev

Dev deployment is fully automatic. No manual steps required.

```bash
# Merge a feature branch to develop
git checkout develop
git merge feature/my-change
git push origin develop
```

GitHub Actions (`deploy-dev.yml`) triggers within seconds. Check status at:
**GitHub → Actions → Deploy to Dev**

If the deployment fails, see [COMMON_ERRORS.md](../troubleshooting/COMMON_ERRORS.md) for XMLA endpoint troubleshooting.

---

## Deploying to Test

Test deployment triggers on a pre-release GitHub tag.

### Create a release candidate

```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Create annotated RC tag
git tag v1.1.0-rc1 -m "Release candidate 1 for v1.1.0"
git push origin v1.1.0-rc1
```

Then go to **GitHub → Releases → Draft a new release**:
- Tag: `v1.1.0-rc1`
- Check **This is a pre-release**
- Click **Publish release**

GitHub Actions (`deploy-test.yml`) deploys to the Test workspace automatically and writes a deployment log entry.

### RC validation checklist

- [ ] Open the Test Power BI workspace and refresh the semantic model
- [ ] Run key measures against known expected values
- [ ] Verify time intelligence returns correct MTD/YTD figures for the current period
- [ ] Test RLS — log in as a RegionalAnalyst user and confirm filter applies
- [ ] Check CHANGELOG for accurate description of changes

---

## Deploying to Staging

Staging deployment triggers on a stable (non-pre-release) GitHub tag and requires maintainer approval.

### Create a stable release

```bash
# Merge develop into main
git checkout main
git merge develop
git push origin main

# Update VERSION file
echo "1.1.0" > VERSION
git add VERSION
git commit -m "chore(release): bump version to 1.1.0"
git push origin main

# Tag the release
git tag v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

Then go to **GitHub → Releases → Draft a new release**:
- Tag: `v1.1.0`
- Do NOT check "This is a pre-release"
- Click **Publish release**

### Approve the staging deployment

1. Open **GitHub → Actions → Deploy to Staging**
2. Find the pending workflow run (yellow dot)
3. Click **Review deployments**
4. Select the `staging` environment and click **Approve and deploy**

The deployment proceeds and writes an audit entry to `deployment/change-log/releases/deployment-log.txt`.

---

## Deploying to Production

Production deployment is manual-only and requires two safeguards: a CONFIRM input and a required reviewer approval.

### Prerequisites

- [ ] Staging deployment completed successfully for the same version
- [ ] Stakeholder sign-off obtained
- [ ] Change ticket raised in your change management system (e.g., ServiceNow: CHG-XXXX)
- [ ] Production deployment window confirmed

### Trigger the production deployment

1. Go to **GitHub → Actions → Deploy to Production**
2. Click **Run workflow**
3. Fill in all required inputs:

| Input | Description | Example |
|-------|-------------|---------|
| `version` | Exact version to deploy (must match a tested Staging version) | `1.1.0` |
| `change_ticket` | Change management reference | `CHG-0042` |
| `confirmed` | Must type exactly `CONFIRM` | `CONFIRM` |
| `rollback_from` | Leave blank for new deployments; fill if this is a rollback | _(blank)_ |

4. Click **Run workflow**

### Approve the production deployment

After the preflight validation passes:

1. The workflow pauses at the `request-approval` job
2. The configured senior maintainer receives a GitHub notification
3. Reviewer opens the workflow run and clicks **Review deployments**
4. Selects `production` environment and clicks **Approve and deploy**

### What happens on deployment

1. `deploy-production` job runs Tabular Editor 3 CLI against the production XMLA endpoint
2. An audit entry is written to `deployment/change-log/releases/deployment-log.txt` — this happens even if the deployment fails
3. The audit entry is automatically committed to the repository
4. The GitHub Step Summary shows version, change ticket, approver, and deployment status

---

## Rollback Procedure

If a production deployment causes issues:

### Option 1 — Re-deploy a previous version

```bash
# Find the last known-good version
git log --tags --simplify-by-decoration --pretty="format:%d %s"

# Trigger production workflow with rollback parameters
# version: 1.0.0 (last good version)
# change_ticket: CHG-ROLLBACK-XXXX
# confirmed: CONFIRM
# rollback_from: 1.1.0 (the broken version)
```

### Option 2 — Revert the TMDL change and re-deploy

```bash
# Identify the breaking commit
git log --oneline semantic-models/

# Revert it
git revert <commit-sha>
git push origin develop

# Fast-track through the pipeline
```

### Important

Every rollback must have its own change ticket. The production deployment audit log records all deployments, including rollbacks. Never skip the change ticket — it's required for compliance audit trails.

---

## Pre-Deployment Validation

The `run-all-checks.py` script runs automatically in every GitHub Actions deployment. To run it locally before pushing:

```bash
py python-utilities/scripts/run-all-checks.py
```

Checks performed:
1. TMDL syntax validation (balanced brackets, required keywords)
2. Naming convention compliance (Dim/Fact/_ patterns, measure Title Case)
3. Best practices (descriptions, DIVIDE() usage, star schema rules)
4. Python unit tests

All checks must pass before any deployment proceeds.

---

## Required GitHub Secrets

See [ENVIRONMENT_SETUP.md](../getting-started/ENVIRONMENT_SETUP.md) for full setup instructions.

| Secret | Required For |
|--------|-------------|
| `POWERBI_CLIENT_ID` | All environments |
| `POWERBI_TENANT_ID` | All environments |
| `POWERBI_CLIENT_SECRET` | All environments |
| `DEV_WORKSPACE_ID` | deploy-dev.yml |
| `TEST_WORKSPACE_ID` | deploy-test.yml |
| `STAGING_WORKSPACE_ID` | deploy-staging.yml |
| `PROD_WORKSPACE_ID` | deploy-prod.yml |

---

## Deployment Log

Every Staging and Production deployment appends to:

```
deployment/change-log/releases/deployment-log.txt
```

Format:
```
[2026-04-23T14:32:00Z] v1.1.0 → production | CHG-0042 | approver: @MichalG-tech | status: success
```

This file is committed automatically and forms the permanent audit trail for change management compliance.
