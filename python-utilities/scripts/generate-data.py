#!/usr/bin/env python
"""
Generate Data
Convenience script to generate sample data
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_pipeline.generate_sample_data import generate_sample_data


def main():
    """Generate sample data"""
    print("=" * 70)
    print("POWER BI SAMPLE DATA GENERATOR")
    print("=" * 70)

    config_file = "../../config/data-generation-config.json"

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
        print("\n✓ Sample data generation complete!")
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
