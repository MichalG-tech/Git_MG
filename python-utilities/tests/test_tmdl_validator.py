"""
Tests for TMDL Validator
"""

import pytest
import tempfile
import os
from pathlib import Path
from validators.tmdl_validator import TMDLValidator, validate_tmdl_file


class TestTMDLValidator:
    """Test TMDL validation"""

    def test_valid_tmdl_file(self):
        """Test validating a valid TMDL file"""
        content = """
table DimCustomer
    lineageTag: 12345

    column CustomerID
        dataType: string
        isKey: true

    column CustomerName
        dataType: string
        description: "Customer name"

measure Customer_Count = COUNTROWS(DimCustomer)
    description: "Total customers"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tmdl', delete=False) as f:
            f.write(content)
            f.flush()

            validator = TMDLValidator()
            result = validator.validate_file(f.name)

            assert result['valid'] == True
            assert result['error_count'] == 0

            os.unlink(f.name)

    def test_empty_file(self):
        """Test validating empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tmdl', delete=False) as f:
            f.write("")
            f.flush()

            validator = TMDLValidator()
            result = validator.validate_file(f.name)

            assert 'empty' in ' '.join(result['warnings']).lower()

            os.unlink(f.name)

    def test_unbalanced_braces(self):
        """Test detecting unbalanced braces"""
        content = "table DimCustomer { column Name { dataType: string"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.tmdl', delete=False) as f:
            f.write(content)
            f.flush()

            validator = TMDLValidator()
            result = validator.validate_file(f.name)

            assert result['valid'] == False
            assert result['error_count'] > 0

            os.unlink(f.name)

    def test_missing_descriptions(self):
        """Test warning for missing descriptions"""
        content = """
table DimProduct
    column ProductID
        dataType: string
        isKey: true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tmdl', delete=False) as f:
            f.write(content)
            f.flush()

            validator = TMDLValidator()
            result = validator.validate_file(f.name)

            assert result['warning_count'] > 0

            os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
