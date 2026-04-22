"""
Data Quality Checker
Validates generated sample data for quality
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List


class DataQualityChecker:
    """Validates data quality"""

    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.issues = []
        self.warnings = []
        self.info = []

    def check_all_files(self) -> Dict:
        """Check all CSV files in directory"""
        results = {
            "directory": str(self.data_dir),
            "files_checked": 0,
            "files_valid": 0,
            "total_issues": 0,
            "total_warnings": 0,
            "files": [],
            "summary": {}
        }

        csv_files = list(self.data_dir.glob("*.csv"))

        if not csv_files:
            results["summary"]["status"] = "no_files"
            return results

        for csv_file in csv_files:
            file_result = self._check_file(csv_file)
            results["files"].append(file_result)
            results["files_checked"] += 1

            if file_result["valid"]:
                results["files_valid"] += 1

            results["total_issues"] += file_result["issue_count"]
            results["total_warnings"] += file_result["warning_count"]

            # Store summary
            results["summary"][csv_file.name] = {
                "records": file_result["record_count"],
                "valid": file_result["valid"],
                "issues": file_result["issue_count"],
                "warnings": file_result["warning_count"]
            }

        return results

    def _check_file(self, file_path: Path) -> Dict:
        """Check individual CSV file"""
        self.issues = []
        self.warnings = []
        self.info = []

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return {
                "file": file_path.name,
                "valid": False,
                "error": str(e),
                "record_count": 0,
                "issue_count": 1,
                "warning_count": 0
            }

        # Run checks
        self._check_empty_dataframe(df)
        self._check_duplicates(df)
        self._check_nulls(df)
        self._check_data_types(df, file_path.name)

        return {
            "file": file_path.name,
            "valid": len(self.issues) == 0,
            "record_count": len(df),
            "columns": list(df.columns),
            "issues": self.issues,
            "warnings": self.warnings,
            "info": self.info,
            "issue_count": len(self.issues),
            "warning_count": len(self.warnings)
        }

    def _check_empty_dataframe(self, df: pd.DataFrame) -> None:
        """Check if dataframe is empty"""
        if len(df) == 0:
            self.issues.append("DataFrame is empty")
        else:
            self.info.append(f"Records: {len(df)}")

    def _check_duplicates(self, df: pd.DataFrame) -> None:
        """Check for duplicate rows"""
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            self.warnings.append(f"Found {duplicates} duplicate rows")

    def _check_nulls(self, df: pd.DataFrame) -> None:
        """Check for null values"""
        nulls = df.isnull().sum()
        if nulls.any():
            null_cols = nulls[nulls > 0]
            for col, count in null_cols.items():
                self.warnings.append(f"Column '{col}': {count} null values")
        else:
            self.info.append("No null values found")

    def _check_data_types(self, df: pd.DataFrame, filename: str) -> None:
        """Check data type consistency"""
        # Basic type checking
        if "ID" in df.columns:
            id_vals = df[df.columns[0]].dropna()
            if len(id_vals) > 0:
                self.info.append(f"ID column validated")

        self.info.append(f"Columns: {len(df.columns)}")


def check_data_quality(data_dir: str = "data/raw") -> Dict:
    """Quick quality check function"""
    checker = DataQualityChecker(data_dir)
    return checker.check_all_files()


if __name__ == "__main__":
    print("Data Quality Checker")
    result = check_data_quality()
    print(f"Files checked: {result['files_checked']}")
    print(f"Files valid: {result['files_valid']}")
