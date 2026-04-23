# Feature Development Workflow

End-to-end guide for contributing changes — from branch creation to production deployment.

---

## Branch Strategy

This repository uses a simplified Git Flow:

```
main          — stable, always deployable, tagged releases only
  └── develop — integration branch, auto-deploys to Dev on every push
        └── feature/*    — new features and enhancements
        └── fix/*        — bug fixes
        └── chore/*      — maintenance (config, docs, dependencies)
        └── hotfix/*     — urgent production fixes (branch from main)
```

**Rules:**
- Never commit directly to `main` or `develop`
- All PRs target `develop` (except hotfixes, which target `main`)
- `main` is only updated via merge from `develop` at release time

---

## Commit Message Convention

This repository uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

### Types

| Type | Use for |
|------|---------|
| `feat` | New feature or measure |
| `fix` | Bug fix |
| `chore` | Tooling, config, dependency updates |
| `docs` | Documentation only |
| `refactor` | Code change with no functional effect |
| `test` | Adding or updating tests |
| `ci` | GitHub Actions changes |

### Scopes

| Scope | Use for |
|-------|---------|
| `sales-model` | Sales Analytics TMDL |
| `finance-model` | Finance Reporting TMDL |
| `python` | Python utilities |
| `ci` | GitHub Actions workflows |
| `data` | Data generation scripts or config |
| `docs` | Documentation files |

### Examples

```bash
git commit -m "feat(sales-model): Add customer lifetime value measure"
git commit -m "fix(python): Correct fiscal year calculation for Q4 edge case"
git commit -m "docs(data): Update DATA_DICTIONARY with FactInventory columns"
git commit -m "ci: Add CHANGELOG check to PR validation workflow"
git commit -m "chore(data): Regenerate sample data with updated schema"
```

---

## Standard Feature Workflow

### 1. Start from a clean develop

```bash
git checkout develop
git pull origin develop
```

### 2. Create a feature branch

```bash
git checkout -b feature/your-feature-name
```

Use kebab-case names that describe the change:
- `feature/add-ebitda-margin-measure`
- `feature/regional-analyst-rls-filter`
- `fix/gross-profit-divide-by-zero`

### 3. Make your changes

For TMDL changes, use Tabular Editor 3 or edit the `.tmdl` files directly in VS Code.

Key locations:
- New measures → `semantic-models/sales-analytics/tables/_Measures.tmdl`
- New columns → the relevant `Dim*.tmdl` or `Fact*.tmdl` file
- Relationship changes → `semantic-models/sales-analytics/relationships/relationships.tmdl`
- RLS roles → `semantic-models/sales-analytics/roles/*.tmdl`

### 4. Validate locally

```bash
py python-utilities/scripts/run-all-checks.py
```

Fix all reported issues before committing. The PR will be blocked if this fails in CI.

### 5. Update CHANGELOG.md

Add an entry in the `[Unreleased]` section:

```markdown
## [Unreleased]

### Added
- `feat(sales-model)`: Customer Lifetime Value measure in Sales Analytics
```

### 6. Stage and commit

Stage only the files you intentionally changed:
```bash
git add semantic-models/sales-analytics/tables/_Measures.tmdl
git add CHANGELOG.md
git commit -m "feat(sales-model): Add customer lifetime value measure"
```

Never use `git add .` without reviewing what's staged — data CSVs and `.gitignore`d files must not be committed.

### 7. Push and open a pull request

```bash
git push origin feature/add-customer-lifetime-value-measure
```

Open a PR on GitHub targeting `develop`. The PR title should match the commit message convention.

### 8. Automated CI checks

GitHub Actions (`pr-validation.yml`) runs automatically:
- TMDL syntax validation
- Naming convention compliance
- Best practices checks (descriptions, DIVIDE(), star schema rules)
- Python unit tests
- CHANGELOG check (warns if model files changed without a CHANGELOG entry)

All checks must be green before the PR can be merged.

### 9. Code review

At least one reviewer approves the PR. Reviewers check:
- Does the measure/column do what the description says?
- Is the DAX correct for edge cases (blanks, zero denominators, inactive relationships)?
- Is the `lineageTag` unique?
- Is the `formatString` appropriate for the data type?

### 10. Merge and deploy

On merge to `develop`:
- `deploy-dev.yml` auto-triggers
- The change is deployed to the Dev Power BI workspace within minutes
- Verify in the Dev workspace that the measure appears and returns expected values

---

## Releasing a New Version

### Release candidate (Test environment)

```bash
# Tag a release candidate
git tag v1.2.0-rc1 -m "Release candidate 1 for v1.2.0"
git push origin v1.2.0-rc1

# Create a GitHub pre-release from this tag (UI)
# GitHub Actions auto-deploys to Test
```

### Stable release (Staging + Production)

```bash
# Merge develop to main
git checkout main
git pull origin main
git merge develop
git push origin main

# Update VERSION
echo "1.2.0" > VERSION
git add VERSION
git commit -m "chore(release): bump version to 1.2.0"
git push origin main

# Tag the release
git tag v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Create a GitHub release from this tag (UI, NOT pre-release)
# GitHub Actions deploys to Staging (requires approval)
# Then manually trigger production deployment with change ticket
```

---

## Hotfix Workflow

For urgent production issues:

```bash
# Branch from main (not develop)
git checkout main
git checkout -b hotfix/fix-returns-measure-blank

# Make the fix
# Validate
py python-utilities/scripts/run-all-checks.py

# Commit
git commit -m "fix(sales-model): Correct USERELATIONSHIP activation in returns measure"

# PR to main, get fast approval
# After merge to main, also merge back to develop:
git checkout develop
git merge main
git push origin develop
```

Then follow the release process above to get the hotfix into production via a patch version tag (e.g., `v1.1.1`).

---

## What Happens Where

| Action | Environment Updated |
|--------|-------------------|
| Push to `develop` | Dev (auto) |
| Pre-release tag `v*.*.*-rc*` | Test (auto) |
| Stable release `v*.*.*` | Staging (requires approval) |
| Manual workflow dispatch | Production (requires CONFIRM + approval) |

See [DEPLOYMENT_GUIDE.md](../deployment/DEPLOYMENT_GUIDE.md) for full deployment procedures.
