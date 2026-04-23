"""
Sample Data Generator
Generates realistic Sales & E-Commerce sample data for the Power BI Enterprise PoC.

Schema produces a proper star schema:
  - DimDate:     date_dimension.csv   — enriched date dimension with fiscal calendar
  - DimCustomer: customers.csv        — customer master with region assignment
  - DimProduct:  products.csv         — product master with cost and price
  - DimRegion:   regions.csv          — geographic hierarchy
  - FactSales:   orders.csv           — transactional sales fact
  - FactReturns: returns.csv          — return transactions (customer + product FKs)
  - FactInventory: inventory.csv      — periodic inventory snapshots
"""

import json
import random
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
MONTH_SHORT = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]
QUARTER_NAMES = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}

# Fiscal year starts in April (common enterprise standard)
FISCAL_YEAR_START_MONTH = 4


def _fiscal_attrs(dt: datetime) -> Dict:
    """Compute fiscal year/quarter/month for a given date (April fiscal year start)."""
    fmonth = ((dt.month - FISCAL_YEAR_START_MONTH) % 12) + 1
    fquarter = (fmonth - 1) // 3 + 1
    # Fiscal year label: April 2022 belongs to FY2023
    fyear = dt.year + 1 if dt.month >= FISCAL_YEAR_START_MONTH else dt.year
    return {"FiscalYear": fyear, "FiscalQuarter": fquarter, "FiscalMonth": fmonth}


class SampleDataGenerator:
    """Generates realistic sample datasets aligned to the Sales Analytics star schema."""

    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        output_location = self.config.get("output", {}).get("output_location", "data/raw/")
        self.output_dir = Path(output_location)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_file: str = None) -> Dict:
        if config_file and Path(config_file).exists():
            with open(config_file, "r") as f:
                return json.load(f)
        return {}

    # ------------------------------------------------------------------ #
    #  Dimension generators                                                #
    # ------------------------------------------------------------------ #

    def _generate_dates(self) -> List[Dict]:
        """Generate a fully enriched date dimension including fiscal calendar."""
        start = datetime.strptime(self.config["date_range"]["start_date"], "%Y-%m-%d")
        end   = datetime.strptime(self.config["date_range"]["end_date"],   "%Y-%m-%d")

        dates  = []
        date_id = 1
        current = start

        while current <= end:
            month   = current.month
            quarter = (month - 1) // 3 + 1
            fiscal  = _fiscal_attrs(current)

            dates.append({
                "DateID":        date_id,
                "Date":          current.strftime("%Y-%m-%d"),
                "Year":          current.year,
                "Quarter":       quarter,
                "QuarterName":   QUARTER_NAMES[quarter],
                "Month":         month,
                "MonthName":     MONTH_NAMES[month],
                "MonthShortName": MONTH_SHORT[month],
                "YearMonth":     current.strftime("%Y-%m"),
                "YearQuarter":   f"{current.year} {QUARTER_NAMES[quarter]}",
                "Week":          current.isocalendar()[1],
                "DayOfWeek":     current.weekday() + 1,      # 1=Monday
                "DayName":       current.strftime("%A"),
                "IsWeekend":     current.weekday() >= 5,
                "FiscalYear":    fiscal["FiscalYear"],
                "FiscalQuarter": fiscal["FiscalQuarter"],
                "FiscalMonth":   fiscal["FiscalMonth"],
            })
            current += timedelta(days=1)
            date_id += 1

        return dates

    def _generate_regions(self) -> List[Dict]:
        """Generate region dimension. Run before customers so RegionIDs are available."""
        num_regions = self.config["data_volume"]["num_regions"]
        continents  = ["North America", "Europe", "Asia", "South America", "Africa", "Oceania"]
        zones       = {"North America": "AMER", "South America": "AMER",
                       "Europe": "EMEA", "Africa": "EMEA",
                       "Asia": "APAC", "Oceania": "APAC"}

        regions = []
        for i in range(1, num_regions + 1):
            continent = random.choice(continents)
            regions.append({
                "RegionID":    i,
                "RegionName":  f"Region {i}",
                "Continent":   continent,
                "Zone":        zones[continent],
                "SalesTarget": round(random.uniform(100_000, 10_000_000), 2),
            })
        return regions

    def _generate_customers(self, region_ids: List[int]) -> List[Dict]:
        """Generate customer dimension; each customer is assigned to one region."""
        num_customers = self.config["data_volume"]["num_customers"]
        countries     = ["USA", "Canada", "UK", "Germany", "France", "Australia", "Japan", "Mexico"]
        segments      = ["Premium", "Standard", "Budget"]
        industries    = ["Retail", "Technology", "Finance", "Healthcare", "Manufacturing", "Other"]
        channels      = ["Online", "Direct Sales", "Partner", "Inbound"]

        customers = []
        for i in range(1, num_customers + 1):
            customers.append({
                "CustomerID":      f"CUST{i:06d}",
                "CustomerName":    f"Customer {i}",
                "Country":         random.choice(countries),
                "City":            f"City{random.randint(1, 100)}",
                "JoinDate":        (datetime.now() - timedelta(days=random.randint(30, 1825))).strftime("%Y-%m-%d"),
                "Segment":         random.choice(segments),
                "Industry":        random.choice(industries),
                "AcquisitionChannel": random.choice(channels),
                "RegionID":        random.choice(region_ids),
            })
        return customers

    def _generate_products(self) -> List[Dict]:
        """Generate product dimension with cost/price spread to enable margin analysis."""
        num_products = self.config["data_volume"]["num_products"]
        categories   = ["Electronics", "Clothing", "Home", "Sports", "Books", "Food", "Beauty"]
        subcategories = {
            "Electronics": ["Computers", "Mobile", "Audio", "Accessories"],
            "Clothing":    ["Men", "Women", "Kids", "Footwear"],
            "Home":        ["Furniture", "Kitchenware", "Bedding", "Decor"],
            "Sports":      ["Fitness", "Outdoor", "Team Sports", "Water Sports"],
            "Books":       ["Fiction", "Non-Fiction", "Technical", "Education"],
            "Food":        ["Beverages", "Snacks", "Fresh", "Packaged"],
            "Beauty":      ["Skincare", "Haircare", "Makeup", "Fragrance"],
        }
        brands  = ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E"]
        statuses = ["Active", "Active", "Active", "Discontinued"]

        products = []
        for i in range(1, num_products + 1):
            category    = random.choice(categories)
            list_price  = round(random.uniform(10, 5_000), 2)
            cost_price  = round(list_price * random.uniform(0.35, 0.70), 2)
            products.append({
                "ProductID":    f"PROD{i:06d}",
                "ProductName":  f"Product {i}",
                "Category":     category,
                "Subcategory":  random.choice(subcategories[category]),
                "Brand":        random.choice(brands),
                "UnitPrice":    list_price,
                "CostPrice":    cost_price,
                "Status":       random.choice(statuses),
            })
        return products

    # ------------------------------------------------------------------ #
    #  Fact generators                                                     #
    # ------------------------------------------------------------------ #

    def _generate_sales(self,
                        customers_df: pd.DataFrame,
                        products_df:  pd.DataFrame,
                        dates_df:     pd.DataFrame) -> List[Dict]:
        """Generate sales transactions using vectorised sampling for performance."""
        target = self.config["data_volume"]["total_transactions_target"]

        # Vectorised random samples — much faster than Python-level loop
        cust_idx  = customers_df.sample(target, replace=True).reset_index(drop=True)
        prod_idx  = products_df.sample(target, replace=True).reset_index(drop=True)
        date_idx  = dates_df.sample(target, replace=True).reset_index(drop=True)

        quantities = [random.randint(1, 50)           for _ in range(target)]
        discounts  = [round(random.uniform(0, 0.30), 4) for _ in range(target)]

        sales = []
        for i in range(target):
            qty      = quantities[i]
            price    = prod_idx.at[i, "UnitPrice"]
            disc     = discounts[i]
            discount_amt = round(qty * price * disc, 2)
            total_amt    = round(qty * price * (1 - disc), 2)

            sales.append({
                "SalesID":       f"SALE{i + 1:08d}",
                "DateID":        int(date_idx.at[i, "DateID"]),
                "CustomerID":    cust_idx.at[i, "CustomerID"],
                "ProductID":     prod_idx.at[i, "ProductID"],
                "RegionID":      int(cust_idx.at[i, "RegionID"]),
                "Quantity":      qty,
                "UnitPrice":     price,
                "DiscountPct":   disc,
                "DiscountAmount": discount_amt,
                "TotalAmount":   total_amt,
                "OrderDate":     date_idx.at[i, "Date"],
            })
        return sales

    def _generate_returns(self,
                          sales_df: pd.DataFrame,
                          dates_df: pd.DataFrame) -> List[Dict]:
        """Generate returns including CustomerID and ProductID for direct slicing."""
        return_rate = self.config["data_volume"]["return_rate"]
        num_returns = int(len(sales_df) * return_rate)
        sampled     = sales_df.sample(num_returns, replace=False).reset_index(drop=True)
        return_dates = dates_df.sample(num_returns, replace=True).reset_index(drop=True)

        reasons = ["Defective", "Wrong Item", "Not as Described", "Changed Mind", "Duplicate Order"]
        returns = []
        for i in range(num_returns):
            sale      = sampled.iloc[i]
            ret_qty   = random.randint(1, int(sale["Quantity"]))
            refund    = round((ret_qty / sale["Quantity"]) * sale["TotalAmount"], 2)
            returns.append({
                "ReturnID":     f"RET{i + 1:07d}",
                "SalesID":      sale["SalesID"],
                "DateID":       int(return_dates.at[i, "DateID"]),
                "CustomerID":   sale["CustomerID"],
                "ProductID":    sale["ProductID"],
                "RegionID":     int(sale["RegionID"]),
                "Quantity":     ret_qty,
                "RefundAmount": refund,
                "ReturnReason": random.choice(reasons),
            })
        return returns

    def _generate_inventory(self,
                             products_df: pd.DataFrame,
                             dates_df:    pd.DataFrame,
                             region_ids:  List[int]) -> List[Dict]:
        """Generate periodic inventory snapshots by product and region."""
        # Sample ~60 dates to keep inventory table at a manageable size
        sample_dates = dates_df.sample(min(60, len(dates_df))).reset_index(drop=True)
        inventory    = []
        inv_id       = 1

        for _, product in products_df.iterrows():
            for _, date in sample_dates.iterrows():
                inventory.append({
                    "InventoryID":    inv_id,
                    "DateID":         int(date["DateID"]),
                    "ProductID":      product["ProductID"],
                    "RegionID":       random.choice(region_ids),
                    "QuantityOnHand": random.randint(0, 10_000),
                    "QuantityOnOrder": random.randint(0, 1_000),
                    "MonthlyUsage":   random.randint(0, 500),
                })
                inv_id += 1

        return inventory

    # ------------------------------------------------------------------ #
    #  Orchestration                                                       #
    # ------------------------------------------------------------------ #

    def generate_all(self) -> Dict:
        """Generate all datasets in dependency order and write CSV files."""
        print("Starting sample data generation...")

        results: Dict = {
            "files_created":      [],
            "records_generated":  {},
            "status":             "success",
        }

        try:
            def save(name: str, records: List[Dict], label: str) -> pd.DataFrame:
                df = pd.DataFrame(records)
                df.to_csv(self.output_dir / name, index=False, encoding="utf-8")
                results["files_created"].append(name)
                results["records_generated"][label] = len(df)
                print(f"  [{label}] {len(df):,} records -> {name}")
                return df

            print("  Generating dimensions...")
            date_df   = save("date_dimension.csv", self._generate_dates(),             "DimDate")
            region_df = save("regions.csv",        self._generate_regions(),           "DimRegion")
            region_ids = region_df["RegionID"].tolist()
            cust_df   = save("customers.csv",      self._generate_customers(region_ids), "DimCustomer")
            prod_df   = save("products.csv",       self._generate_products(),           "DimProduct")

            print("  Generating facts...")
            sales_df  = save("orders.csv",    self._generate_sales(cust_df, prod_df, date_df),      "FactSales")
            _         = save("returns.csv",   self._generate_returns(sales_df, date_df),            "FactReturns")
            _         = save("inventory.csv", self._generate_inventory(prod_df, date_df, region_ids), "FactInventory")

            print("\n[OK] Data generation complete!")

        except Exception as exc:
            results["status"] = f"error: {exc}"
            print(f"\n[ERROR] {exc}")

        return results


def generate_sample_data(config_file: str = None) -> Dict:
    """Entry point for external callers."""
    return SampleDataGenerator(config_file).generate_all()


if __name__ == "__main__":
    result = generate_sample_data("../../config/data-generation-config.json")
    print(f"Status: {result['status']}")
