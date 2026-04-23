# Implementation Guide

A client-facing reference explaining what this PoC demonstrates and how to adapt it to a real-world Power BI engagement.

---

## What This PoC Demonstrates

This repository is a working proof of concept for **enterprise-grade Power BI development** — the practices, tooling, and governance that professional delivery teams use on large-scale BI projects.

It answers the question: **"Can BI projects be built and managed with Claude?"**

The answer this PoC gives: yes — and with a higher degree of consistency, documentation, and architectural rigour than most conventional approaches.

---

## The Core Proposition

Traditional Power BI delivery has a governance problem:

- Models live as binary `.pbix` files — opaque, unmerged, undiffable
- There's no meaningful pull request review for model changes
- Deployment is manual: someone drags a file and clicks "Publish"
- There's no audit trail of what changed and who approved it
- Documentation is a Word doc written once and never updated

This PoC shows an alternative: **TMDL + Git + GitHub Actions + Python automation**.

Every change is a pull request. Every deployment is logged. Every measure has a description. Every decision has documented rationale. The whole system is reproducible from a `git clone`.

---

## Architecture Summary

### Semantic Models

Two complete semantic models are included:

**Sales Analytics**
- Star schema: 4 dimensions, 3 fact tables, 12 relationships
- 63 DAX measures covering sales performance, time intelligence, customer analytics, product analytics, inventory, geography, and ranking
- Inactive relationships with `USERELATIONSHIP()` for returns and inventory analysis
- Row-level security (SalesManager, RegionalAnalyst roles)

**Finance Reporting**
- Multi-entity P&L model with budget vs actuals comparison
- April fiscal year calendar
- 20 DAX measures: revenue → EBITDA → Net Income, with YTD and prior year comparisons
- Budget version tracking (Original / Revised / Latest Forecast)

### CI/CD Pipeline

Five-environment pipeline with progressive governance:

| Environment | Trigger | Gate |
|-------------|---------|------|
| Dev | Push to `develop` | None (continuous) |
| Test | Pre-release tag | None (tag creation is the gate) |
| Staging | Stable release tag | Maintainer approval |
| Production | Manual dispatch | Senior maintainer approval + CONFIRM input |

Every production deployment writes a timestamped audit entry. Every PR is validated automatically before merge.

### Python Automation

- TMDL syntax validator
- Naming convention checker (Dim/Fact/_ patterns, Title Case measures)
- Best practices checker (descriptions, `DIVIDE()` usage, star schema rules)
- Sample data generator (500K+ rows, reproducible, April fiscal calendar)
- Tabular Editor 3 CLI wrapper (validate, deploy, BPA)
- Git helpers (branch info, tag creation, clean working tree guard)
- Deployment module skeleton (documents msal + XMLA integration path)

---

## How to Adapt This to a Client Engagement

### Step 1 — Replace sample data with real data sources

The M queries in each TMDL table use a `DataFolderPath` parameter pointing to CSV files. For a production engagement:

1. Replace the CSV M queries with connections to the client's data warehouse (Azure Synapse, Snowflake, SQL Server, Fabric)
2. Update the `DataFolderPath` shared expression with the actual connection string or remove it entirely
3. Parameterise the server name and database using the same pattern

The rest of the model (measures, relationships, roles) requires no changes.

### Step 2 — Configure GitHub Environments

Create four environments in the client's GitHub organisation:

1. `dev` — no approval required
2. `test` — no approval required
3. `staging` — add the client's BI lead as required reviewer
4. `production` — add the client's solution architect as required reviewer

### Step 3 — Set up the Azure AD service principal

Create a single service principal in the client's Azure AD tenant and grant it workspace access across all four Power BI workspaces. Add the `POWERBI_CLIENT_ID`, `POWERBI_TENANT_ID`, `POWERBI_CLIENT_SECRET` secrets to GitHub, plus one workspace ID secret per environment.

Full instructions: [ENVIRONMENT_SETUP.md](../getting-started/ENVIRONMENT_SETUP.md)

### Step 4 — Extend the measure library

Start from the 63 measures in `_Measures.tmdl` and add client-specific KPIs. Every new measure follows the same template:

```tmdl
measure 'Measure Name' = <DAX expression>
    formatString: $ #,##0
    lineageTag: meXXXXXX-0101-0000-0000-000000000001
    description: Clear explanation of what this measures and how to use it.
```

The CI validator enforces descriptions, format strings, and naming conventions automatically.

### Step 5 — Define RLS roles

Replace the placeholder `RegionalAnalyst` role with roles that match the client's access control model. Common patterns:

- By region: `DimRegion[RegionName] = USERPRINCIPALNAME()` with a lookup table
- By department: `DimDepartment[DeptCode] IN VALUES(SecurityTable[AllowedDepts])`
- By entity: `DimEntity[EntityCode] = LOOKUPVALUE(UserAccess[EntityCode], UserAccess[Email], USERPRINCIPALNAME())`

---

## Client Presentation Narrative

When presenting this PoC to clients, the key messages are:

**"Every change is reviewed."**
No model change reaches users without going through a pull request — automated validation, human review, documented rationale.

**"Every deployment is approved and logged."**
Production releases require a senior reviewer's explicit approval and a change ticket. The audit log is permanent and committed to Git.

**"The model is self-documenting."**
Every measure, column, and table has a description. The Data Dictionary is generated from the model. New team members have a complete reference from day one.

**"Claude built this."**
The entire implementation — TMDL models, 83 DAX measures, 5 GitHub Actions workflows, Python automation, and 12+ documentation files — was produced by Claude working in Claude Code. This is what AI-assisted enterprise BI delivery looks like.

---

## What's Not Included in This PoC

This PoC is a demonstration of architecture and governance — not a production deployment. The following items require client-specific implementation:

| Item | Status | Notes |
|------|--------|-------|
| Real data connections | Not included | Replace CSV M queries with warehouse connections |
| Live XMLA deployment | Not wired | Python deployers document the integration path |
| Power BI report layouts (.pbir) | Placeholder | Visual design layer to be built per client |
| Figma report mockups | Placeholder | Design integration planned, not implemented |
| Video walkthroughs | Not included | Available on request |
| User training materials | Not included | Available as a follow-on deliverable |

---

## Frequently Asked Questions from Clients

**"Do we need Power BI Premium?"**
The XMLA endpoint (required for programmatic deployment) requires Premium Per User (PPU) or Premium capacity. PPU is available per user at a predictable monthly cost. For the PoC itself, TMDL authoring with Tabular Editor 3 can be done without a Premium licence.

**"What if our team doesn't know Git?"**
The GitHub Actions automation handles the CI/CD complexity. Most analysts only need to know: create a branch, edit a file, open a PR. The system validates and deploys automatically. Git training is a one-day workshop.

**"Can we keep using Power BI Desktop?"**
Power BI Desktop can connect to the deployed semantic model via the XMLA endpoint for report building. TMDL authoring requires Tabular Editor 3. The two tools are complementary — Tabular Editor owns the model, Power BI Desktop owns the reports.

**"What about Fabric?"**
Microsoft Fabric uses the same TMDL format and the same XMLA deployment mechanism. This PoC is directly compatible with Fabric workspaces.
