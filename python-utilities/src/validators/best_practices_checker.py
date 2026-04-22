"""
Best Practices Checker
Checks for Power BI semantic model best practices
"""

import json
from pathlib import Path
from typing import Dict, List


class BestPracticesChecker:
    """Checks for semantic model best practices"""

    def __init__(self, config_file: str = None):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: str = None) -> Dict:
        """Load configuration from JSON file"""
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")

        # Default configuration
        return {
            "naming_convention": {
                "measures": "^[a-zA-Z][a-zA-Z0-9 _]*$",
                "columns": "^[a-zA-Z][a-zA-Z0-9_]*$",
                "tables": "^(Dim|Fact)[a-zA-Z][a-zA-Z0-9_]*$",
                "roles": "^[A-Za-z ]+$"
            },
            "forbidden_patterns": ["test", "temp", "tmp", "xxx", "delete", "debug"],
            "required_descriptions": True,
            "max_measure_name_length": 100,
            "max_column_name_length": 80,
        }

    def check_file(self, file_path: str) -> Dict:
        """Check a TMDL file for best practices"""
        self.errors = []
        self.warnings = []
        self.info = []

        if not Path(file_path).exists():
            self.errors.append(f"File not found: {file_path}")
            return self._format_results(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Cannot read file: {str(e)}")
            return self._format_results(file_path)

        # Run checks
        self._check_naming_conventions(content, file_path)
        self._check_forbidden_patterns(content, file_path)
        self._check_descriptions(content, file_path)
        self._check_table_organization(content, file_path)

        return self._format_results(file_path)

    def _check_naming_conventions(self, content: str, file_path: str) -> None:
        """Check naming conventions"""
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Check measure names
            if 'measure' in line.lower() and '=' in line:
                # Extract measure name
                parts = line.split('=')
                if len(parts) >= 1:
                    name = parts[0].strip().replace('measure', '').strip()
                    if name and len(name) > self.config["max_measure_name_length"]:
                        self.warnings.append(
                            f"Line {i}: Measure name too long: {len(name)} chars"
                        )

            # Check table names
            if line.strip().startswith('table'):
                if not any(x in line for x in ['Dim', 'Fact']):
                    self.warnings.append(
                        f"Line {i}: Table should start with 'Dim' or 'Fact'"
                    )

        self.info.append("Naming conventions checked")

    def _check_forbidden_patterns(self, content: str, file_path: str) -> None:
        """Check for forbidden patterns"""
        content_lower = content.lower()

        for pattern in self.config["forbidden_patterns"]:
            if pattern in content_lower:
                count = content_lower.count(pattern)
                self.warnings.append(
                    f"Found '{pattern}' {count} times - remove before production"
                )

    def _check_descriptions(self, content: str, file_path: str) -> None:
        """Check for descriptions"""
        if self.config["required_descriptions"]:
            if 'description:' not in content.lower():
                self.warnings.append("No descriptions found - add descriptions to objects")

            # Count objects without descriptions
            tables = content.count('table')
            descriptions = content.count('description:')
            if tables > 0 and descriptions == 0:
                self.warnings.append(
                    f"Found {tables} tables but no descriptions"
                )

    def _check_table_organization(self, content: str, file_path: str) -> None:
        """Check table organization (star schema, etc.)"""
        dim_count = content.count('table Dim')
        fact_count = content.count('table Fact')

        if dim_count == 0 and fact_count == 0:
            self.info.append("No standard dimension/fact tables found")
        else:
            self.info.append(f"Found {dim_count} dimensions and {fact_count} facts")

    def _format_results(self, file_path: str) -> Dict:
        """Format results"""
        return {
            "file": file_path,
            "passed": len(self.errors) == 0 and len(self.warnings) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


def check_file(file_path: str) -> Dict:
    """Quick check function"""
    checker = BestPracticesChecker()
    return checker.check_file(file_path)


if __name__ == "__main__":
    print("Best Practices Checker")
    print("Usage: python best_practices_checker.py <file>")
