"""
Best Practices Checker
Validates TMDL files against Power BI semantic model best practices.

Rules enforced:
  - Measure names: max length, no forbidden patterns
  - Table names: Dim/Fact prefix for data tables; _ prefix for hidden utility tables
  - Descriptions required on all objects
  - Forbidden development-phase patterns detected
"""

import json
import re
from pathlib import Path
from typing import Dict, List


class BestPracticesChecker:
    """Validates a TMDL file against configured Power BI best practice rules."""

    def __init__(self, config_file: str = None):
        self.errors:   List[str] = []
        self.warnings: List[str] = []
        self.info:     List[str] = []
        self.config = self._load_config(config_file)

    # ------------------------------------------------------------------ #
    #  Config                                                              #
    # ------------------------------------------------------------------ #

    def _load_config(self, config_file: str = None) -> Dict:
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except Exception as exc:
                print(f"Warning: Could not load config file: {exc}")

        return {
            "naming_convention": {
                "measures": r"^[A-Z][a-zA-Z0-9 %()/#&+\-]*$",
                "columns":  r"^[A-Z][a-zA-Z0-9_]*$",
                "tables":   r"^(Dim|Fact|_)[a-zA-Z][a-zA-Z0-9_]*$",
                "roles":    r"^[A-Za-z][A-Za-z0-9 _-]*$",
            },
            "hidden_table_prefix": "_",
            "forbidden_patterns": ["temp", "tmp", "xxx", "delete", "debug", "hack", "fixme"],
            "required_descriptions": True,
            "max_measure_name_length": 100,
            "max_column_name_length": 80,
            "max_table_name_length": 80,
        }

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def check_file(self, file_path: str) -> Dict:
        """Run all checks on a single TMDL file and return a results dict."""
        self.errors   = []
        self.warnings = []
        self.info     = []

        path = Path(file_path)
        if not path.exists():
            self.errors.append(f"File not found: {file_path}")
            return self._format_results(file_path)

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            self.errors.append(f"Cannot read file: {exc}")
            return self._format_results(file_path)

        self._check_naming_conventions(content, file_path)
        self._check_forbidden_patterns(content)
        self._check_descriptions(content)
        self._check_table_organisation(content)

        return self._format_results(file_path)

    # ------------------------------------------------------------------ #
    #  Check implementations                                              #
    # ------------------------------------------------------------------ #

    def _check_naming_conventions(self, content: str, file_path: str) -> None:
        """Validate measure name length and table naming conventions."""
        max_measure_len = self.config.get("max_measure_name_length", 100)
        hidden_prefix   = self.config.get("hidden_table_prefix", "_")

        for i, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()

            # --- Measure name length ---
            if re.search(r"\bmeasure\b", stripped, re.IGNORECASE) and "=" in stripped:
                # Extract the name between 'measure' and '='
                m = re.match(r"measure\s+['\"]?([^'\"=]+)['\"]?\s*=", stripped, re.IGNORECASE)
                if m:
                    name = m.group(1).strip()
                    if len(name) > max_measure_len:
                        self.warnings.append(
                            f"Line {i}: Measure name too long ({len(name)} chars): '{name}'"
                        )

            # --- Table naming convention ---
            if re.match(r"^table\s+\S+", stripped):
                table_name = stripped.split()[1].strip()
                # Hidden utility tables (_Measures, _Parameters, etc.) are exempt
                if table_name.startswith(hidden_prefix):
                    self.info.append(f"Line {i}: Hidden utility table detected: '{table_name}'")
                elif not re.match(r"^(Dim|Fact)[A-Za-z]", table_name):
                    self.warnings.append(
                        f"Line {i}: Table '{table_name}' should start with 'Dim' or 'Fact' "
                        f"(or '{hidden_prefix}' for hidden utility tables)"
                    )

        self.info.append("Naming conventions checked")

    def _check_forbidden_patterns(self, content: str) -> None:
        """Detect development-phase placeholder strings that must not ship to production."""
        content_lower = content.lower()
        forbidden     = self.config.get("forbidden_patterns", [])

        for pattern in forbidden:
            if pattern in content_lower:
                count = content_lower.count(pattern)
                self.warnings.append(
                    f"Found '{pattern}' {count} time(s) — remove before production"
                )

    def _check_descriptions(self, content: str) -> None:
        """Verify that descriptions are present on table objects."""
        if not self.config.get("required_descriptions", True):
            return

        # Only apply description checks to files that actually define tables,
        # columns, or measures. Relationship/culture/definition files have no
        # description properties — skip them to avoid false positives.
        has_table   = bool(re.search(r"^\s*table\s+\S+",   content, re.MULTILINE))
        has_measure = bool(re.search(r"^\s*measure\s+",    content, re.MULTILINE))
        has_column  = bool(re.search(r"^\s*column\s+\S+",  content, re.MULTILINE))

        if not (has_table or has_measure or has_column):
            return

        description_count = content.lower().count("description:")
        table_count       = len(re.findall(r"^\s*table\s+\S+", content, re.MULTILINE | re.IGNORECASE))

        if description_count == 0:
            self.warnings.append(
                "No descriptions found — add 'description:' to table, column, and measure objects"
            )
        elif table_count > 0 and description_count < table_count:
            self.warnings.append(
                f"Found {table_count} table(s) but only {description_count} description(s) — check all objects are described"
            )

    def _check_table_organisation(self, content: str) -> None:
        """Report dimension/fact table counts for star schema validation."""
        dim_count  = len(re.findall(r"^\s*table\s+Dim\w+", content, re.MULTILINE))
        fact_count = len(re.findall(r"^\s*table\s+Fact\w+", content, re.MULTILINE))
        util_count = len(re.findall(r"^\s*table\s+_\w+",   content, re.MULTILINE))

        if dim_count == 0 and fact_count == 0 and util_count == 0:
            self.info.append("No standard Dim/Fact/_ tables found in this file")
        else:
            parts = []
            if dim_count:  parts.append(f"{dim_count} dimension(s)")
            if fact_count: parts.append(f"{fact_count} fact(s)")
            if util_count: parts.append(f"{util_count} utility table(s)")
            self.info.append(f"Found {', '.join(parts)}")

    # ------------------------------------------------------------------ #
    #  Result formatting                                                   #
    # ------------------------------------------------------------------ #

    def _format_results(self, file_path: str) -> Dict:
        return {
            "file":          file_path,
            "passed":        len(self.errors) == 0 and len(self.warnings) == 0,
            "errors":        self.errors,
            "warnings":      self.warnings,
            "info":          self.info,
            "error_count":   len(self.errors),
            "warning_count": len(self.warnings),
        }


def check_file(file_path: str) -> Dict:
    """Convenience function for single-file checks."""
    return BestPracticesChecker().check_file(file_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python best_practices_checker.py <tmdl_file>")
        sys.exit(1)

    result = check_file(sys.argv[1])
    status = "[PASS]" if result["passed"] else "[FAIL]"
    print(f"{status} {result['file']}")
    for e in result["errors"]:   print(f"  ERROR:   {e}")
    for w in result["warnings"]: print(f"  WARNING: {w}")
    for i in result["info"]:     print(f"  INFO:    {i}")
