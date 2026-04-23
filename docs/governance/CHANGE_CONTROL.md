# Change Control Guide

Governance procedures for managing changes to Power BI semantic models in production.

---

## Why Change Control Matters

Power BI semantic models used by decision-makers are business-critical assets. A broken measure, an incorrect relationship, or an accidentally removed column can affect reports used for executive decisions, financial reporting, or operational planning.

Change control ensures:
- Every production change is reviewed and approved before deployment
- Every deployment is documented with a change ticket reference
- The audit trail supports compliance, incident investigation, and rollback
- No single person can deploy to production without a second approver

---

## Change Categories

| Category | Examples | Pipeline Path |
|----------|---------|---------------|
| **Standard change** | Add a measure, add a column, update a description | Full pipeline (Dev → Test → Staging → Prod) |
| **Minor change** | Fix a description typo, update a format string | Full pipeline — no shortcuts even for minor changes |
| **Hotfix** | Fix a broken measure in production causing report errors | Fast-tracked but still requires approval (see Hotfix procedure) |
| **Major change** | Add a new fact table, restructure relationships, add a new model | Full pipeline with extended QA window in Test |

All changes, regardless of category, require:
1. A pull request with automated CI passing
2. A CHANGELOG.md entry
3. A change ticket reference for Staging and Production deployments

---

## The Change Ticket

Every Staging and Production deployment requires a change ticket reference in the `change_ticket` input field of the deployment workflow. Format: `CHG-XXXX`.

The change ticket should document:
- **What** is changing (reference the PR or release)
- **Why** the change is needed (business reason or incident reference)
- **Who** approved the change (the reviewer who approved the production deployment)
- **When** the change was deployed (written automatically to the audit log)
- **Rollback plan** (which version to redeploy if the change causes issues)

If your organisation uses ServiceNow, JIRA, or a similar ITSM tool, create the ticket there and use its reference number. If no ITSM tool is in use, track in GitHub Issues and use the issue number (`GH-42`).

---

## Approval Matrix

| Environment | Who Can Approve |
|-------------|----------------|
| Dev | None required (automatic on merge to `develop`) |
| Test | None required (tag creation is the gate) |
| Staging | Repo maintainer (configured as required reviewer in GitHub Environments) |
| Production | Senior maintainer (configured as required reviewer in GitHub Environments) |

A person cannot approve their own deployment. The approver must be different from the person who triggered the workflow.

---

## The Production Deployment Checklist

Before triggering a production deployment:

- [ ] The same version has been deployed to Staging and validated
- [ ] A change ticket exists with business sign-off
- [ ] The deployment window has been agreed with stakeholders (avoid month-end close, board reporting periods)
- [ ] A rollback plan is documented (which previous version to redeploy)
- [ ] The production workspace admin has been notified
- [ ] Post-deployment verification steps are ready

---

## Audit Trail

Every Staging and Production deployment automatically appends an entry to:
```
deployment/change-log/releases/deployment-log.txt
```

This file is committed to Git, making the audit trail immutable and version-controlled.

Entry format:
```
[2026-04-23T14:32:00Z] v1.1.0 → production | CHG-0042 | approver: @MichalG-tech | status: success
[2026-04-23T15:01:00Z] v1.1.0 → production | CHG-ROLLBACK-01 | approver: @MichalG-tech | status: success (rollback from v1.2.0)
```

Failed deployments are also logged — the audit trail captures what was attempted, not just what succeeded.

---

## Hotfix Procedure

For urgent production issues, the standard pipeline can be fast-tracked — but not bypassed.

1. Create a `hotfix/*` branch from `main` (not `develop`)
2. Apply the minimal fix
3. Open a PR targeting `main` — request expedited review
4. On merge, immediately deploy to production via manual workflow dispatch
5. After the production hotfix deploys, merge `main` back into `develop`
6. Tag the hotfix as a patch release (`v1.1.1`)

Even for hotfixes, the production deployment requires a change ticket and an approver. If the normal approver is unavailable, escalate to the next available senior maintainer.

---

## Change Freeze Periods

Coordinate with stakeholders to define change freeze windows. Typical examples:

- **Month-end close** (last 3 business days of the month): no production deployments
- **Quarter-end reporting** (last week of the quarter): standard changes blocked, hotfixes only
- **Board preparation** (48 hours before board meetings): freeze all model changes

Change freezes should be communicated by opening a GitHub Issue and labelling it `change-freeze`. Link the issue in any PRs that are ready to merge but must wait.

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

| Type | When to increment | Example |
|------|------------------|---------|
| **Patch** (x.y.**Z**) | Bug fixes, description corrections, format string changes | 1.1.0 → 1.1.1 |
| **Minor** (x.**Y**.0) | New measures, new columns, new roles — backward compatible | 1.1.0 → 1.2.0 |
| **Major** (**X**.0.0) | Breaking changes: table renames, relationship restructure, column removal | 1.1.0 → 2.0.0 |

A change is **breaking** if it would cause existing reports or DAX queries to return errors or different results without modification.

Update `VERSION` and `CHANGELOG.md` as part of every release commit.

---

## Compliance Evidence Package

For engagements with formal compliance requirements (ISO 27001, SOC 2, internal audit), the following evidence can be produced from this repository:

| Evidence | Source |
|---------|--------|
| Change log | `deployment/change-log/releases/deployment-log.txt` |
| Approved change requests | GitHub pull request approval history |
| Deployment approvers | GitHub Actions workflow run approval history |
| Code review records | GitHub PR review comments and approvals |
| Test evidence | GitHub Actions PR validation run logs |
| Version history | `git log --oneline --tags` |
| Current version | `VERSION` file |
