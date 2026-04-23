# Data Dictionary

Reference for all tables and columns in the Sales Analytics semantic model.

---

## FactSales (`data/raw/orders.csv`)

Grain: One row per sales transaction. ~500,000 rows.

| Column | Type | Description |
|--------|------|-------------|
| SalesID | text | Natural key (SALE00000001). Used in DISTINCTCOUNT for order count measures. |
| DateID | int | FK → DimDate[DateID]. Hidden. |
| CustomerID | text | FK → DimCustomer[CustomerID]. Hidden. |
| ProductID | text | FK → DimProduct[ProductID]. Hidden. |
| RegionID | int | FK → DimRegion[RegionID]. Hidden. Derived from the purchasing customer's region. |
| Quantity | int | Units sold (1–50). |
| UnitPrice | decimal | Actual selling price per unit (may differ from DimProduct[UnitPrice] list price). |
| DiscountPct | decimal | Discount percentage applied (0.00–0.30). |
| DiscountAmount | decimal | Total discount in currency (Quantity × UnitPrice × DiscountPct). |
| TotalAmount | decimal | Net sales amount (Quantity × UnitPrice × (1 − DiscountPct)). Foundation for Total Sales measure. |
| OrderDate | date | Transaction date. DimDate is used for time intelligence — this column is for row context only. |

---

## FactReturns (`data/raw/returns.csv`)

Grain: One row per return transaction. ~25,000 rows (≈5% of FactSales).

| Column | Type | Description |
|--------|------|-------------|
| ReturnID | text | Natural key (RET0000001). |
| SalesID | text | Reference to FactSales[SalesID]. Not a formal relationship — traceability only. |
| DateID | int | FK → DimDate[DateID] (return date). Inactive relationship. |
| CustomerID | text | FK → DimCustomer[CustomerID]. Inactive relationship. |
| ProductID | text | FK → DimProduct[ProductID]. Inactive relationship. |
| RegionID | int | FK → DimRegion[RegionID]. Inactive relationship. |
| Quantity | int | Units returned (≤ original sale quantity). |
| RefundAmount | decimal | Prorated refund amount. |
| ReturnReason | text | Reason category (Defective, Wrong Item, Not as Described, Changed Mind, Duplicate Order). |

---

## FactInventory (`data/raw/inventory.csv`)

Grain: One row per product per region per snapshot date. ~90,000 rows.

| Column | Type | Description |
|--------|------|-------------|
| InventoryID | int | Surrogate key. |
| DateID | int | FK → DimDate[DateID] (snapshot date). Inactive relationship. |
| ProductID | text | FK → DimProduct[ProductID]. Inactive relationship. |
| RegionID | int | FK → DimRegion[RegionID]. Inactive relationship. |
| QuantityOnHand | int | Units in stock at snapshot date. 0 = stockout. |
| QuantityOnOrder | int | Units on open purchase orders. |
| MonthlyUsage | int | Average monthly demand (units). Used in Days of Supply calculation. |

---

## DimDate (`data/raw/date_dimension.csv`)

Grain: One row per calendar day. 1,938 rows (2021-01-01 to 2026-04-22).

**Mark as date table** in Power BI Desktop using the `Date` column.

| Column | Type | Description |
|--------|------|-------------|
| DateID | int | Surrogate key (sequential from 1). Relationship key. |
| Date | date | Calendar date. Primary date column for time intelligence. |
| Year | int | Calendar year (2021–2026). |
| Quarter | int | Quarter number (1–4). |
| QuarterName | text | "Q1"–"Q4". Sort by Quarter. |
| Month | int | Month number (1–12). |
| MonthName | text | "January"–"December". Sort by Month. |
| MonthShortName | text | "Jan"–"Dec". Sort by Month. |
| YearMonth | text | "YYYY-MM". Sort by DateID. |
| YearQuarter | text | "YYYY Q#". Sort by DateID. |
| Week | int | ISO week number (1–53). |
| DayOfWeek | int | Day of week (1=Monday, 7=Sunday). |
| DayName | text | "Monday"–"Sunday". Sort by DayOfWeek. |
| IsWeekend | bool | True for Saturday/Sunday. |
| FiscalYear | int | Fiscal year (April start). April 2022 = FY2023. |
| FiscalQuarter | int | Fiscal quarter (1–4, Q1 starts April). |
| FiscalMonth | int | Fiscal month (1–12, 1=April). |

---

## DimCustomer (`data/raw/customers.csv`)

Grain: One row per customer. 5,000 rows.

| Column | Type | Description |
|--------|------|-------------|
| CustomerID | text | Natural key (CUST000001). Relationship key. |
| CustomerName | text | Display name. |
| Country | text | Customer country (8 countries). |
| City | text | Customer city. |
| JoinDate | date | Customer acquisition date. Used in New Customers measure. |
| Segment | text | Value segment: Premium, Standard, Budget. |
| Industry | text | Industry vertical (6 industries). |
| AcquisitionChannel | text | How acquired: Online, Direct Sales, Partner, Inbound. |
| RegionID | int | FK → DimRegion[RegionID]. Hidden. Bridges customer to region dimension. |

---

## DimProduct (`data/raw/products.csv`)

Grain: One row per product. 1,500 rows.

| Column | Type | Description |
|--------|------|-------------|
| ProductID | text | Natural key (PROD000001). Relationship key. |
| ProductName | text | Display name. |
| Category | text | Top-level category (7 categories). |
| Subcategory | text | Sub-level within Category (4 per category). |
| Brand | text | Brand name (Brand A–E). |
| UnitPrice | decimal | Standard list price. Compare to FactSales[UnitPrice] for Price Realization %. |
| CostPrice | decimal | Standard cost. Used via RELATED() in Total Cost and Gross Profit measures. |
| Status | text | Active or Discontinued. |

---

## DimRegion (`data/raw/regions.csv`)

Grain: One row per region. 50 rows.

| Column | Type | Description |
|--------|------|-------------|
| RegionID | int | Surrogate key. Relationship key. |
| RegionName | text | "Region 1"–"Region 50". |
| Continent | text | Geographic continent (6 values). |
| Zone | text | Global zone: AMER, EMEA, APAC. |
| SalesTarget | decimal | Annual sales target. Used in Target Attainment % measure. |

---

## Measure Inventory

See [_Measures.tmdl](../../semantic-models/sales-analytics/tables/_Measures.tmdl) for the complete measure definitions.

| Group | Count | Key Measures |
|-------|-------|-------------|
| Sales Performance | 12 | Total Sales, Gross Profit, Gross Margin % |
| Time Intelligence (totals) | 8 | Sales MTD/QTD/YTD, Rolling 3M/12M |
| Time Intelligence (growth) | 7 | YoY/MoM/QoQ Growth %, YTD vs Prior YTD % |
| Returns | 5 | Return Amount, Return Rate %, Net Sales |
| Customer Analytics | 10 | Active Customers (90d), Repeat Rate %, Top 10 Concentration % |
| Product Analytics | 8 | Product Contribution %, Price Realization %, Category Rank |
| Inventory | 5 | Days of Supply, Stockout Products |
| Geography | 4 | Region Sales %, Target Attainment % |
| Ranking & Intelligence | 7 | Product Rank, % of Total Sales, Cumulative Sales % |
| **Total** | **63** | |
