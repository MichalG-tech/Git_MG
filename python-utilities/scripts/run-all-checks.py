#!/usr/bin/env python
"""
Run All Checks
Runs the complete validation suite against all semantic models.
"""

import sys
import os
import subprocess
from pathlib import Path

# Fix Windows encoding before any output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Resolve paths relative to this script, not the working directory
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT   = SCRIPT_DIR.parent.parent
MODELS_DIR  = REPO_ROOT / "semantic-models"

# Add src to path for imports
sys.path.insert(0, str(SCRIPT_DIR.parent / "src"))

from validators.tmdl_validator import validate_tmdl_directory
from validators.best_practices_checker import check_file


def run_tmdl_validation(model_path: Path) -> tuple:
    """Returns (passed: bool, message: str)."""
    try:
        result = validate_tmdl_directory(str(model_path))
        if result['total_errors'] == 0:
            return True, f"[OK] {model_path.name}: {result['files_checked']} files, {result['total_warnings']} warnings"
        else:
            return False, f"[ERROR] {model_path.name}: {result['total_errors']} errors found"
    except Exception as exc:
        return False, f"[ERROR] {model_path.name}: {exc}"


def run_best_practices(model_path: Path) -> tuple:
    """Returns (passed: bool, message: str)."""
    try:
        tmdl_files = list(model_path.glob("**/*.tmdl"))
        if not tmdl_files:
            return True, f"[OK] {model_path.name}: no TMDL files found"

        violations = 0
        errors = 0
        for f in tmdl_files:
            result = check_file(str(f))
            violations += result['warning_count']
            errors     += result['error_count']

        if errors == 0 and violations == 0:
            return True, f"[OK] {model_path.name}: {len(tmdl_files)} files, no violations"
        elif errors > 0:
            return False, f"[ERROR] {model_path.name}: {errors} errors, {violations} warnings"
        else:
            return False, f"[WARN] {model_path.name}: {violations} best practice violations"
    except Exception as exc:
        return False, f"[ERROR] {model_path.name}: {exc}"


def main():
    print("=" * 70)
    print("POWER BI ENTERPRISE POC - COMPLETE VALIDATION SUITE")
    print("=" * 70)

    all_passed = True

    # Discover semantic models
    model_dirs = sorted([d for d in MODELS_DIR.iterdir() if d.is_dir()]) if MODELS_DIR.exists() else []

    # ------------------------------------------------------------------ #
    #  Check 1: TMDL Syntax Validation                                    #
    # ------------------------------------------------------------------ #
    print("\n[1/3] TMDL Syntax Validation")
    print("-" * 70)

    if not model_dirs:
        print("  [SKIP] No semantic model directories found")
    else:
        for model_path in model_dirs:
            passed, msg = run_tmdl_validation(model_path)
            print(f"  {msg}")
            if not passed:
                all_passed = False

    # ------------------------------------------------------------------ #
    #  Check 2: Best Practices                                            #
    # ------------------------------------------------------------------ #
    print("\n[2/3] Best Practices Check")
    print("-" * 70)

    if not model_dirs:
        print("  [SKIP] No semantic model directories found")
    else:
        for model_path in model_dirs:
            passed, msg = run_best_practices(model_path)
            print(f"  {msg}")
            if not passed:
                all_passed = False

    # ------------------------------------------------------------------ #
    #  Check 3: Python Unit Tests                                         #
    # ------------------------------------------------------------------ #
    print("\n[3/3] Python Unit Tests")
    print("-" * 70)

    tests_dir = SCRIPT_DIR.parent / "tests"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_dir), "-v", "--tb=short"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode == 0:
            print("  [OK] All unit tests passed")
        else:
            print("  [FAIL] Some unit tests failed")
            # Print the last 20 lines of pytest output for context
            lines = (result.stdout + result.stderr).splitlines()
            for line in lines[-20:]:
                print(f"    {line}")
            all_passed = False
    except Exception as exc:
        print(f"  [SKIP] Could not run pytest: {exc}")

    # ------------------------------------------------------------------ #
    #  Summary                                                            #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    if all_passed:
        print("[OK] ALL CHECKS PASSED - ready to commit and deploy")
        return 0
    else:
        print("[FAIL] SOME CHECKS FAILED - fix errors before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
