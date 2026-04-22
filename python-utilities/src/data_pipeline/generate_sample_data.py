"""
Sample Data Generator
Generates realistic Sales & E-Commerce sample data
"""

import json
import random
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import os


class SampleDataGenerator:
    """Generates realistic sample datasets"""

    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self.output_dir = Path(self.config["output"]["output_location"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.quality_issues = []

    def _load_config(self, config_file: str = None) -> Dict:
        """Load configuration"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}

    def generate_all(self) -> Dict:
        """Generate all sample datasets"""
        print("Starting sample data generation...")

        results = {
            "files_created": [],
            "records_generated": {},
            "quality_report": None,
            "status": "success"
        }

        try:
            # Generate dimensions
            print("  1. Generating DimDate...")
            dates = self._generate_dates()
            date_df = pd.DataFrame(dates)
            date_df.to_csv(self.output_dir / "date_dimension.csv", index=False)
            results["files_created"].append("date_dimension.csv")
            results["records_generated"]["dates"] = len(date_df)
            print(f"     → {len(date_df)} dates")

            print("  2. Generating DimCustomer...")
            customers = self._generate_customers()
            customer_df = pd.DataFrame(customers)
            customer_df.to_csv(self.output_dir / "customers.csv", index=False)
            results["files_created"].append("customers.csv")
            results["records_generated"]["customers"] = len(customer_df)
            print(f"     → {len(customer_df)} customers")

            print("  3. Generating DimProduct...")
            products = self._generate_products()
            product_df = pd.DataFrame(products)
            product_df.to_csv(self.output_dir / "products.csv", index=False)
            results["files_created"].append("products.csv")
            results["records_generated"]["products"] = len(product_df)
            print(f"     → {len(product_df)} products")

            print("  4. Generating DimRegion...")
            regions = self._generate_regions()
            region_df = pd.DataFrame(regions)
            region_df.to_csv(self.output_dir / "regions.csv", index=False)
            results["files_created"].append("regions.csv")
            results["records_generated"]["regions"] = len(region_df)
            print(f"     → {len(region_df)} regions")

            # Generate facts
            print("  5. Generating FactSales...")
            sales = self._generate_sales(customer_df, product_df, date_df)
            sales_df = pd.DataFrame(sales)
            sales_df.to_csv(self.output_dir / "orders.csv", index=False)
            results["files_created"].append("orders.csv")
            results["records_generated"]["sales"] = len(sales_df)
            print(f"     → {len(sales_df)} transactions")

            print("  6. Generating FactReturns...")
            returns = self._generate_returns(sales_df, date_df)
            returns_df = pd.DataFrame(returns)
            returns_df.to_csv(self.output_dir / "returns.csv", index=False)
            results["files_created"].append("returns.csv")
            results["records_generated"]["returns"] = len(returns_df)
            print(f"     → {len(returns_df)} returns")

            print("  7. Generating FactInventory...")
            inventory = self._generate_inventory(product_df, date_df)
            inventory_df = pd.DataFrame(inventory)
            inventory_df.to_csv(self.output_dir / "inventory.csv", index=False)
            results["files_created"].append("inventory.csv")
            results["records_generated"]["inventory"] = len(inventory_df)
            print(f"     → {len(inventory_df)} inventory records")

            results["status"] = "success"
            print("\n✓ Data generation complete!")

        except Exception as e:
            results["status"] = f"error: {str(e)}"
            print(f"\n✗ Error during generation: {e}")

        return results

    def _generate_dates(self) -> List[Dict]:
        """Generate date dimension"""
        start = datetime.strptime(self.config["date_range"]["start_date"], "%Y-%m-%d")
        end = datetime.strptime(self.config["date_range"]["end_date"], "%Y-%m-%d")

        dates = []
        current = start
        date_id = 1

        while current <= end:
            dates.append({
                "DateID": date_id,
                "Date": current.strftime("%Y-%m-%d"),
                "Year": current.year,
                "Month": current.month,
                "Quarter": (current.month - 1) // 3 + 1,
                "Week": current.isocalendar()[1],
                "DayOfWeek": current.weekday() + 1,
                "IsWeekend": 1 if current.weekday() >= 5 else 0,
                "DayName": current.strftime("%A")
            })
            current += timedelta(days=1)
            date_id += 1

        return dates

    def _generate_customers(self) -> List[Dict]:
        """Generate customer dimension"""
        num_customers = self.config["data_volume"]["num_customers"]
        countries = ["USA", "Canada", "UK", "Germany", "France", "Australia", "Japan", "Mexico"]
        segments = ["Premium", "Standard", "Budget"]
        industries = ["Retail", "Technology", "Finance", "Healthcare", "Manufacturing", "Other"]

        customers = []
        for i in range(1, num_customers + 1):
            customers.append({
                "CustomerID": f"CUST{i:06d}",
                "CustomerName": f"Customer {i}",
                "Email": f"customer{i}@example.com",
                "Country": random.choice(countries),
                "City": f"City{random.randint(1, 100)}",
                "JoinDate": (datetime.now() - timedelta(days=random.randint(0, 1825))).strftime("%Y-%m-%d"),
                "Segment": random.choice(segments),
                "Industry": random.choice(industries),
                "LifetimeValue": round(random.uniform(100, 100000), 2)
            })

        return customers

    def _generate_products(self) -> List[Dict]:
        """Generate product dimension"""
        num_products = self.config["data_volume"]["num_products"]
        categories = ["Electronics", "Clothing", "Home", "Sports", "Books", "Food", "Beauty"]
        brands = ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E"]

        products = []
        for i in range(1, num_products + 1):
            products.append({
                "ProductID": f"PROD{i:06d}",
                "ProductName": f"Product {i}",
                "Category": random.choice(categories),
                "Brand": random.choice(brands),
                "UnitPrice": round(random.uniform(10, 5000), 2),
                "CostPrice": round(random.uniform(5, 2500), 2),
                "Status": random.choice(["Active", "Active", "Active", "Discontinued"])
            })

        return products

    def _generate_regions(self) -> List[Dict]:
        """Generate region dimension"""
        num_regions = self.config["data_volume"]["num_regions"]
        continents = ["North America", "Europe", "Asia", "South America", "Africa", "Oceania"]

        regions = []
        for i in range(1, num_regions + 1):
            regions.append({
                "RegionID": i,
                "RegionName": f"Region {i}",
                "Continent": random.choice(continents),
                "SalesTarget": round(random.uniform(100000, 10000000), 2)
            })

        return regions

    def _generate_sales(self, customers_df: pd.DataFrame, products_df: pd.DataFrame,
                       dates_df: pd.DataFrame) -> List[Dict]:
        """Generate sales transactions"""
        target_transactions = self.config["data_volume"]["total_transactions_target"]
        sales = []
        sale_id = 1

        for _ in range(target_transactions):
            customer = customers_df.sample(1).iloc[0]
            product = products_df.sample(1).iloc[0]
            date = dates_df.sample(1).iloc[0]
            quantity = random.randint(1, 50)
            unit_price = product["UnitPrice"]
            discount = random.uniform(0, 0.3)
            amount = quantity * unit_price * (1 - discount)

            sales.append({
                "SalesID": f"SALE{sale_id:08d}",
                "DateID": date["DateID"],
                "CustomerID": customer["CustomerID"],
                "ProductID": product["ProductID"],
                "Quantity": quantity,
                "UnitPrice": round(unit_price, 2),
                "DiscountAmount": round(quantity * unit_price * discount, 2),
                "TotalAmount": round(amount, 2),
                "OrderDate": date["Date"]
            })
            sale_id += 1

        return sales

    def _generate_returns(self, sales_df: pd.DataFrame, dates_df: pd.DataFrame) -> List[Dict]:
        """Generate return transactions"""
        return_rate = self.config["data_volume"]["return_rate"]
        num_returns = int(len(sales_df) * return_rate)
        returns = []
        return_id = 1

        for _ in range(num_returns):
            sale = sales_df.sample(1).iloc[0]
            return_qty = random.randint(1, int(sale["Quantity"]))
            refund = (return_qty / sale["Quantity"]) * sale["TotalAmount"]

            returns.append({
                "ReturnID": f"RET{return_id:07d}",
                "SalesID": sale["SalesID"],
                "DateID": random.choice(dates_df["DateID"]),
                "Quantity": return_qty,
                "RefundAmount": round(refund, 2),
                "ReturnReason": random.choice(["Defective", "Wrong Item", "Not as Described", "Changed Mind"])
            })
            return_id += 1

        return returns

    def _generate_inventory(self, products_df: pd.DataFrame, dates_df: pd.DataFrame) -> List[Dict]:
        """Generate inventory snapshots"""
        inventory = []
        inv_id = 1

        for _, product in products_df.iterrows():
            for _, date in dates_df.sample(min(100, len(dates_df))).iterrows():
                inventory.append({
                    "InventoryID": inv_id,
                    "DateID": date["DateID"],
                    "ProductID": product["ProductID"],
                    "QuantityOnHand": random.randint(0, 10000),
                    "QuantityOnOrder": random.randint(0, 1000),
                    "MonthlyUsage": random.randint(0, 500)
                })
                inv_id += 1

        return inventory


def generate_sample_data(config_file: str = None) -> Dict:
    """Quick generation function"""
    generator = SampleDataGenerator(config_file)
    return generator.generate_all()


if __name__ == "__main__":
    print("Sample Data Generator")
    result = generate_sample_data("../../config/data-generation-config.json")
    print(f"\nResult: {result['status']}")
    print(f"Files: {result['files_created']}")
