# TMDL Standards & Conventions

Standards for authoring and maintaining TMDL semantic model files in this repository.

---

## File Organisation

Each semantic model lives under `semantic-models/<model-name>/` with this structure:

```
semantic-models/<model-name>/
├── definition/
│   ├── model.tmdl          — model-level settings, shared expressions (parameters)
│   └── database.tmdl       — compatibility level
├── tables/
│   ├── DimDate.tmdl        — date dimension (one file per table)
│   ├── DimCustomer.tmdl
│   ├── FactSales.tmdl
│   └── _Measures.tmdl      — all measures (hidden utility table)
├── relationships/
│   └── relationships.tmdl  — all relationship definitions
├── roles/
│   └── SalesManager.tmdl   — one file per RLS role
├── cultures/
│   └── en-US.tmdl          — language/localisation
└── metadata/
    └── model-metadata.json — model documentation and schema reference
```

---

## Naming Conventions

### Tables

| Pattern | Example | Notes |
|---------|---------|-------|
| `DimXxx` | `DimDate`, `DimCustomer` | Dimension tables |
| `FactXxx` | `FactSales`, `FactReturns` | Fact tables |
| `_Xxx` | `_Measures`, `_Parameters` | Hidden utility tables |

Never: `tbl_`, `dim_`, `fact_` (underscore prefix is reserved for hidden utility tables).

### Columns

- PascalCase, no spaces: `CustomerID`, `TotalAmount`, `IsWeekend`
- Foreign key columns: match the primary key name in the target table
- Hidden FK columns: same name + `isHidden` property
- Boolean columns: `Is`, `Has`, `Can` prefix — `IsActive`, `HasDiscount`

### Measures

- Title Case with spaces: `Total Sales`, `Gross Margin %`, `YoY Sales Growth %`
- No prefix required (measures live in `_Measures` table, already namespaced)
- Use `%` suffix for percentage measures: `Gross Margin %`
- Use currency symbol in formatString, not in the name

### Roles

- Title Case: `Sales Manager`, `Regional Analyst`, `Finance Viewer`

---

## Measure Quality Standards

Every measure must have:

1. **`description:`** — explains what the measure calculates, what it's used for, and any caveats
2. **`formatString:`** — always explicit; never leave default
3. **`lineageTag:`** — unique GUID (copy from existing + increment)

```tmdl
measure 'Total Sales' = SUM(FactSales[TotalAmount])
    formatString: $ #,##0
    lineageTag: me000008-0101-0000-0000-000000000001
    description: Total gross sales revenue from the pre-computed TotalAmount column.
```

### Format String Reference

| Data type | Format string |
|-----------|--------------|
| Currency (whole) | `$ #,##0` |
| Currency (2dp) | `$ #,##0.00` |
| Percentage (1dp) | `0.0%` |
| Percentage with sign | `+0.0%;-0.0%;0.0%` |
| Integer count | `#,##0` |
| Decimal | `#,##0.0` |

---

## DAX Best Practices

### Always use DIVIDE() for division

```dax
// CORRECT — handles divide-by-zero gracefully
Gross Margin % = DIVIDE([Gross Profit], [Total Sales])

// WRONG — crashes on zero denominator
Gross Margin % = [Gross Profit] / [Total Sales]
```

### Use CALCULATE sparingly and purposefully

```dax
// CORRECT — clear filter modification with named function
Sales YTD = CALCULATE([Total Sales], DATESYTD(DimDate[Date]))

// AVOID — deeply nested CALCULATE calls without clear intent
```

### Prefer SUM over SUMX for simple aggregations

```dax
// CORRECT — fast, simple
Total Sales = SUM(FactSales[TotalAmount])

// ONLY when row context is needed
Total Cost = SUMX(FactSales, RELATED(DimProduct[CostPrice]) * FactSales[Quantity])
```

### Use RELATED() for dimension lookups in fact table context

```dax
// Access a dimension attribute from a fact table measure
Total Cost = SUMX(FactSales, RELATED(DimProduct[CostPrice]) * FactSales[Quantity])
```

---

## Star Schema Rules

1. **Every fact table column** that is a foreign key must be `isHidden`
2. **All measures** go in the `_Measures` (or `_FinanceMeasures`) hidden utility table — never in fact or dimension tables
3. **Dimension tables** have no measures, only columns
4. **`_Measures` table** has no columns, only measures and an empty M partition
5. **Date table** (DimDate) must be explicitly marked as a date table for time intelligence

---

## Required Descriptions Checklist

Before committing any TMDL file, verify:

- [ ] Table has a `description:` property
- [ ] Every visible column has a `description:` property
- [ ] Every measure has a `description:` property
- [ ] Hidden FK columns have a `description:` explaining the relationship target
- [ ] The model.tmdl has a top-level `description:`

Run `py python-utilities/scripts/run-all-checks.py` to validate automatically.
