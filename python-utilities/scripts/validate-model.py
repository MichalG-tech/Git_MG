#!/usr/bin/env python
"""
Validate Model
Quick validation script for semantic models
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validators.tmdl_validator import validate_tmdl_directory
from validators.best_practices_checker import check_file


def main():
    """Run all validations"""
    print("=" * 60)
    print("POWER BI MODEL VALIDATOR")
    print("=" * 60)

    # Default directory
    model_dir = "../../semantic-models/sales-analytics"

    if len(sys.argv) > 1:
        model_dir = sys.argv[1]

    if not Path(model_dir).exists():
        print(f"Error: Directory not found: {model_dir}")
        return 1

    print(f"\nValidating: {model_dir}\n")

    # Run TMDL validation
    print("1. TMDL Syntax Validation")
    print("-" * 40)
    tmdl_result = validate_tmdl_directory(model_dir)
    print(f"Files checked: {tmdl_result['files_checked']}")
    print(f"Files valid: {tmdl_result['files_valid']}")
    print(f"Errors: {tmdl_result['total_errors']}")
    print(f"Warnings: {tmdl_result['total_warnings']}")

    # Run best practices check on each file
    print("\n2. Best Practices Check")
    print("-" * 40)
    tmdl_files = Path(model_dir).glob("**/*.tmdl")

    total_warnings = 0
    for tmdl_file in tmdl_files:
        result = check_file(str(tmdl_file))
        if result['warning_count'] > 0:
            print(f"  {tmdl_file.name}: {result['warning_count']} warnings")
            total_warnings += result['warning_count']

    if total_warnings == 0:
        print("  No best practice violations found ✓")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if tmdl_result['total_errors'] == 0:
        print("✓ All validations passed!")
        return 0
    else:
        print(f"✗ Found {tmdl_result['total_errors']} errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
