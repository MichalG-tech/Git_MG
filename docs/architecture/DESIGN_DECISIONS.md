# Architecture & Design Decisions

Key architectural decisions made in this PoC, including the rationale and trade-offs considered.

---

## Decision 1: TMDL + Git for Semantic Model Version Control

**Decision**: Store semantic models as TMDL (Tabular Model Definition Language) files in Git rather than as binary .pbix files.

**Rationale**:
- TMDL is text-based, human-readable, and diff-friendly — changes are visible in pull request reviews
- Binary .pbix files cannot be meaningfully reviewed, merged, or branched
- TMDL enables automated validation (our Python validators) and CI/CD deployment
- Aligns with software engineering best practices applied to Power BI

**Trade-off**: TMDL requires Tabular Editor 3 for editing (Power BI Desktop cannot open TMDL folders directly). This adds tooling complexity but delivers significant governance and automation benefits.

---

## Decision 2: Centralised Measures Table (_Measures)

**Decision**: Place all DAX measures in a single hidden `_Measures` table rather than distributing them across fact tables.

**Rationale**:
- Keeps fact tables clean and focused on data columns only
- All measures appear in one place in the Fields pane, making them easy to find
- Simplifies automated extraction and documentation of measures
- Follows community-established Power BI best practice

**Trade-off**: Slightly less logical co-location (measures are not next to the data they aggregate). Mitigated by comprehensive descriptions on every measure and a Data Dictionary.

---

## Decision 3: String Natural Keys for Customer and Product Dimensions

**Decision**: Use string natural keys (CUST000001, PROD000001) for DimCustomer and DimProduct, with integer surrogate keys only for DimDate and DimRegion.

**Rationale**:
- The sample data generator produces string-format IDs which are meaningful and human-readable
- For a PoC demonstration, string keys are adequate and avoid unnecessary transformation complexity
- Power BI handles string-type relationships correctly

**Trade-off**: Integer surrogate keys are more storage-efficient and faster for large models. Production implementations connecting to real ERP/CRM data should use integer surrogate keys from a data warehouse.

---

## Decision 4: Inactive Relationships for FactReturns and FactInventory

**Decision**: Mark FactReturns and FactInventory relationships as inactive by default, using USERELATIONSHIP() in measures when needed.

**Rationale**:
- Power BI cannot have multiple active relationships between the same pair of tables (ambiguity)
- FactReturns and FactInventory share dimension tables with FactSales (DimDate, DimProduct, DimRegion)
- Making the FactSales relationships active (the primary model) and others inactive avoids ambiguous filter propagation
- Measures that need to slice returns or inventory by date/customer explicitly activate the relationship via USERELATIONSHIP()

**Trade-off**: DAX authors must be aware of inactive relationships and use USERELATIONSHIP() correctly. Documented in the TMDL Standards guide.

---

## Decision 5: CSV Data Source with DataFolderPath Parameter

**Decision**: Use CSV files as the data source with a user-configurable `DataFolderPath` parameter.

**Rationale**:
- Keeps the PoC self-contained — no database server required
- Makes it easy to generate and update data using the Python generator
- Demonstrates the parameter pattern that clients can replace with actual database connections
- Cross-platform (works on any machine with Python and Power BI Desktop)

**Trade-off**: CSV loading is slower than a columnar database for 500K+ rows. Acceptable for a demonstration; production would connect to Azure Synapse, Snowflake, or SQL Server.

---

## Decision 6: April Fiscal Year for Finance Model

**Decision**: Use an April fiscal year start for the Finance Reporting model (FY2023 = April 2022 to March 2023).

**Rationale**:
- April fiscal year is common in UK, India, and many multinational companies
- Demonstrates that the model supports non-calendar fiscal years — a common client requirement
- Both calendar and fiscal year attributes are included in DimPeriod for flexibility

**Trade-off**: Users must understand the fiscal/calendar year distinction. Documented in the Data Dictionary and DimPeriod column descriptions.

---

## Decision 7: Five-Environment Pipeline (Local → Dev → Test → Staging → Prod)

**Decision**: Implement all five environments with progressive approval gates.

**Rationale**:
- Mirrors enterprise change management processes that clients recognise
- Demonstrates GitHub Environments, required reviewers, and manual gates
- Each environment has a distinct purpose and audience
- The progression (auto → auto → tagged → approved → CONFIRM) shows escalating governance

**Trade-off**: Complexity for a PoC. Justified because the CI/CD architecture is a key demonstration objective, and clients need to see the full governance story.
