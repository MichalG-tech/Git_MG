# Operations Runbook

Procedures for maintaining, monitoring, and operating the Power BI Enterprise PoC in production.

---

## Repository Health Checks

Run these checks regularly to keep the repository in good shape.

### Validate all TMDL models

```bash
py python-utilities/scripts/run-all-checks.py
```

Expected output: all checks pass, zero errors. If warnings appear, review and address before the next release.

### Verify data generation still works

```bash
py python-utilities/scripts/generate-data.py
```

Expected output: 7 CSV files written to `data/raw/` with correct row counts (orders: ~500K, customers: 5K, products: 1.5K, regions: 50, returns: ~25K, inventory: ~90K, date_dimension: ~1,938).

### Check Python dependencies are current

```bash
py -m pip list --outdated
```

Update critical packages (pandas, pytest, msal) in `python-utilities/requirements.txt` when major versions are available. Test after any dependency update:
```bash
py -m pytest python-utilities/tests/ -v
```

---

## Deployment Monitoring

### View recent deployments

The audit log is at:
```
deployment/change-log/releases/deployment-log.txt
```

Format of each entry:
```
[2026-04-23T14:32:00Z] v1.1.0 → production | CHG-0042 | approver: @reviewer | status: success
```

### Check GitHub Actions status

- Open **GitHub → Actions** to see all recent workflow runs
- Filter by workflow name to focus on a specific environment
- A red dot on any completed run means it failed — click to see which step failed

### Verify Power BI workspace health

After any deployment:
1. Open the target Power BI workspace
2. Confirm the semantic model shows the new version number in its description
3. Run a spot-check on 2-3 key measures using **Analyse in Excel** or a test report
4. Check that RLS roles apply correctly by testing with a restricted user account

---

## Adding a New Release

Follow this sequence for every planned release:

1. **Feature complete** — all feature branches merged to `develop`
2. **Local validation** — `py python-utilities/scripts/run-all-checks.py` — zero errors
3. **RC tag** — `git tag v1.2.0-rc1` → auto-deploys to Test
4. **QA sign-off** — business team validates in Test workspace
5. **Stable release** — merge `develop` → `main`, update `VERSION`, tag `v1.2.0`
6. **Staging deployment** — triggered automatically, requires maintainer approval
7. **Staging validation** — final check before production
8. **Production deployment** — manual dispatch with change ticket and CONFIRM input
9. **Post-deployment check** — verify production workspace, confirm with stakeholders

Minimum time between steps 3 and 8 should be one business day to allow proper QA.

---

## Regenerating Sample Data

If the data schema changes (new columns, new tables), regenerate all CSV files:

```bash
py python-utilities/scripts/generate-data.py
```

Data files are excluded from Git (`.gitignore`). Each developer generates their own local copy.

After regeneration, test the semantic model in Tabular Editor 3 to confirm all M queries load correctly and relationships still resolve.

---

## Adding a New Semantic Model

To add a third model (e.g., HR Analytics):

1. Create the folder structure:
   ```
   semantic-models/hr-analytics/
   ├── definition/
   ├── tables/
   ├── relationships/
   ├── roles/
   └── metadata/
   ```

2. Follow the naming conventions in [TMDL_STANDARDS.md](../semantic-models/TMDL_STANDARDS.md)

3. Add a workspace ID secret in GitHub: `HR_WORKSPACE_ID`

4. Copy and adapt an existing deployment workflow:
   ```bash
   cp .github/workflows/deploy-dev.yml .github/workflows/deploy-hr-dev.yml
   ```
   Update the model path and workspace ID references.

5. Add the model to `run-all-checks.py` model discovery (uses `find_model_directories()` from `python-utilities/src/utils/`)

---

## Rotating Secrets

When the Azure AD service principal secret expires or is rotated:

1. Generate a new secret in the Azure portal (Azure AD → App registrations → Certificates & secrets)
2. Update in GitHub: **Settings → Secrets → POWERBI_CLIENT_SECRET → Update**
3. Trigger a test deployment to Dev to verify the new secret works
4. Document the rotation in your organisation's secret management log

Service principal secrets should be rotated at least annually.

---

## Branching Clean-Up

Stale feature branches accumulate over time. Clean them up monthly:

```bash
# List merged branches (safe to delete)
git branch --merged develop

# Delete locally
git branch -d feature/old-feature

# Delete from remote
git push origin --delete feature/old-feature
```

Never delete `main`, `develop`, or any branch with an open PR.

---

## Incident Response

### Production model returns wrong results

1. Identify which measures are affected — check the deployment log for the last change
2. If the change is in the TMDL: revert via a hotfix branch (see [FEATURE_WORKFLOW.md](../development/FEATURE_WORKFLOW.md))
3. If the change is in data: regenerate and redeploy data, then redeploy model
4. Deploy the fix through the normal pipeline — do not bypass approval gates even for urgent fixes
5. Document the incident in the repository's Issues

### GitHub Actions workflow broken

1. Check the Actions tab for the error message
2. Common causes: expired secret, Power BI workspace permissions changed, Python dependency update broke the environment
3. Fixes for common errors: [COMMON_ERRORS.md](../troubleshooting/COMMON_ERRORS.md)
4. For workflow YAML syntax errors: test locally with `act` (GitHub Actions local runner)

### Data generation produces unexpected row counts

Check `config/data-generation-config.json` — someone may have changed the row count parameters. Review git log:
```bash
git log --oneline config/data-generation-config.json
```

---

## Contacts and Escalation

| Role | Responsibility |
|------|---------------|
| Repo maintainer | PR approvals, Staging deployments, branch management |
| Senior maintainer | Production deployment approvals |
| Azure AD admin | Service principal secret rotation, workspace permissions |
| Power BI admin | Tenant settings, workspace creation |
