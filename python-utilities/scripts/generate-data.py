#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate Data
Convenience script to generate sample data
"""

import sys
import os
from pathlib import Path

# Force UTF-8 output so Unicode symbols render correctly on all platforms
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / 'src'))

from data_pipeline.generate_sample_data import generate_sample_data

# Config is relative to the repo root (two levels above this script)
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_CONFIG = str(REPO_ROOT / "config" / "data-generation-config.json")


def main():
    """Generate sample data"""
    print("=" * 70)
    print("POWER BI SAMPLE DATA GENERATOR")
    print("=" * 70)

    config_file = DEFAULT_CONFIG

    print(f"\nConfiguration: {config_file}")
    print("-" * 70)

    try:
        result = generate_sample_data(config_file)

        print("\nGeneration Summary:")
        print("-" * 70)
        print(f"Status: {result['status']}")
        print(f"Files created: {len(result['files_created'])}")

        if result['records_generated']:
            print("\nRecords generated:")
            for data_type, count in result['records_generated'].items():
                print(f"  {data_type:20s}: {count:>10,}")

        print("\nFiles location: data/raw/")
        print("\n[OK] Sample data generation complete!")
        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
