"""
TMDL Validator
Validates TMDL file syntax and structure
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple


class TMDLValidator:
    """Validates TMDL files for syntax and structure"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_file(self, file_path: str) -> Dict:
        """
        Validate a single TMDL file

        Args:
            file_path: Path to TMDL file

        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []
        self.info = []

        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return self._format_results(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Cannot read file: {str(e)}")
            return self._format_results(file_path)

        # Basic validation checks
        self._check_syntax(content, file_path)
        self._check_structure(content, file_path)
        self._check_naming_conventions(content, file_path)

        return self._format_results(file_path)

    def _check_syntax(self, content: str, file_path: str) -> None:
        """Check basic TMDL syntax"""
        lines = content.split('\n')

        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            self.errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

        # Check for balanced brackets
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        if open_brackets != close_brackets:
            self.errors.append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")

        # Check for empty file
        if len(content.strip()) == 0:
            self.warnings.append("File is empty")

        self.info.append(f"Checked {len(lines)} lines")

    def _check_structure(self, content: str, file_path: str) -> None:
        """Check TMDL structure"""
        # Check for required sections
        if 'table' not in content.lower() and 'measure' not in content.lower():
            self.warnings.append("No tables or measures found in file")

        # Check for descriptions
        if 'description:' not in content.lower():
            self.warnings.append("No descriptions found - consider adding descriptions")

    def _check_naming_conventions(self, content: str, file_path: str) -> None:
        """Check naming conventions"""
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Check measure naming
            if 'measure' in line.lower() and '=' in line:
                if not any(x in line for x in ['measure_', ' [', 'Measure']):
                    self.warnings.append(f"Line {i}: Measure might not follow naming convention")

            # Check table naming
            if line.strip().startswith('table'):
                if not any(x in line for x in ['Dim', 'Fact']):
                    self.warnings.append(f"Line {i}: Table should start with 'Dim' or 'Fact'")

    def _format_results(self, file_path: str) -> Dict:
        """Format validation results"""
        return {
            "file": file_path,
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

    def validate_directory(self, directory: str) -> Dict:
        """
        Validate all TMDL files in directory

        Args:
            directory: Path to directory containing TMDL files

        Returns:
            Dictionary with validation results for all files
        """
        results = {
            "directory": directory,
            "files_checked": 0,
            "files_valid": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "files": []
        }

        tmdl_files = Path(directory).glob("**/*.tmdl")

        for tmdl_file in tmdl_files:
            file_result = self.validate_file(str(tmdl_file))
            results["files"].append(file_result)
            results["files_checked"] += 1

            if file_result["valid"]:
                results["files_valid"] += 1

            results["total_errors"] += file_result["error_count"]
            results["total_warnings"] += file_result["warning_count"]

        return results


def validate_tmdl_file(file_path: str) -> Dict:
    """Quick validation function"""
    validator = TMDLValidator()
    return validator.validate_file(file_path)


def validate_tmdl_directory(directory: str) -> Dict:
    """Quick directory validation function"""
    validator = TMDLValidator()
    return validator.validate_directory(directory)


if __name__ == "__main__":
    # Example usage
    print("TMDL Validator")
    print("Usage: python tmdl_validator.py <file_or_directory>")
