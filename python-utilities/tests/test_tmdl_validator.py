"""
Tests for TMDL Validator
"""

import pytest
import tempfile
import os
from pathlib import Path
from validators.tmdl_validator import TMDLValidator, validate_tmdl_file


def _write_temp_tmdl(content: str) -> str:
    """Write content to a temp .tmdl file, close it, return the path."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tmdl', delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name


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
        description: Unique customer identifier.

    column CustomerName
        dataType: string
        description: Customer display name.

measure 'Customer Count' = COUNTROWS(DimCustomer)
    formatString: #,##0
    description: Total number of customer records.
"""
        path = _write_temp_tmdl(content)
        try:
            validator = TMDLValidator()
            result = validator.validate_file(path)
            assert result['valid'] is True
            assert result['error_count'] == 0
        finally:
            os.unlink(path)

    def test_empty_file(self):
        """Test validating empty file"""
        path = _write_temp_tmdl("")
        try:
            validator = TMDLValidator()
            result = validator.validate_file(path)
            assert 'empty' in ' '.join(result['warnings']).lower()
        finally:
            os.unlink(path)

    def test_unbalanced_braces(self):
        """Test detecting unbalanced braces"""
        content = "table DimCustomer { column Name { dataType: string"
        path = _write_temp_tmdl(content)
        try:
            validator = TMDLValidator()
            result = validator.validate_file(path)
            assert result['valid'] is False
            assert result['error_count'] > 0
        finally:
            os.unlink(path)

    def test_missing_descriptions(self):
        """Test warning for missing descriptions"""
        content = """
table DimProduct
    column ProductID
        dataType: string
        isKey: true
"""
        path = _write_temp_tmdl(content)
        try:
            validator = TMDLValidator()
            result = validator.validate_file(path)
            assert result['warning_count'] > 0
        finally:
            os.unlink(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
