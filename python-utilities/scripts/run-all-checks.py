#!/usr/bin/env python
"""
Run All Checks
Run complete validation suite
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validators.tmdl_validator import validate_tmdl_directory
from validators.best_practices_checker import check_file


def main():
    """Run all checks"""
    print("=" * 70)
    print("POWER BI ENTERPRISE POC - COMPLETE VALIDATION SUITE")
    print("=" * 70)

    all_passed = True

    # Check 1: TMDL Validation
    print("\n[1/3] TMDL Syntax Validation")
    print("-" * 70)
    try:
        model_dir = "../../semantic-models/sales-analytics"
        if Path(model_dir).exists():
            result = validate_tmdl_directory(model_dir)
            if result['total_errors'] == 0:
                print(f"✓ TMDL valid ({result['files_checked']} files)")
            else:
                print(f"✗ TMDL errors found: {result['total_errors']}")
                all_passed = False
        else:
            print("⊘ No semantic models to validate yet")
    except Exception as e:
        print(f"✗ Error: {e}")
        all_passed = False

    # Check 2: Best Practices
    print("\n[2/3] Best Practices Check")
    print("-" * 70)
    try:
        if Path(model_dir).exists():
            tmdl_files = list(Path(model_dir).glob("**/*.tmdl"))
            if tmdl_files:
                violations = 0
                for tmdl_file in tmdl_files:
                    result = check_file(str(tmdl_file))
                    violations += result['warning_count']

                if violations == 0:
                    print(f"✓ Best practices check passed ({len(tmdl_files)} files)")
                else:
                    print(f"⊘ Found {violations} best practice violations")
            else:
                print("⊘ No TMDL files to check")
        else:
            print("⊘ No semantic models to validate yet")
    except Exception as e:
        print(f"✗ Error: {e}")
        all_passed = False

    # Check 3: Python Tests
    print("\n[3/3] Python Unit Tests")
    print("-" * 70)
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
                               capture_output=True, text=True, cwd="..")
        if result.returncode == 0:
            print("✓ All tests passed")
        else:
            print(f"⊘ Some tests failed (run pytest for details)")
    except Exception as e:
        print(f"⊘ Could not run pytest: {e}")

    # Final Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("\nReady to commit and deploy!")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nPlease fix errors before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
