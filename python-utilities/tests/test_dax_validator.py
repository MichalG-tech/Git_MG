"""
Tests for DAX Validator
"""

import pytest
from validators.dax_validator import DAXValidator, validate_dax, validate_measure


class TestDAXValidator:
    """Test DAX validation"""

    def test_valid_simple_dax(self):
        """Test validating simple valid DAX"""
        expression = "SUM([Amount])"

        validator = DAXValidator()
        result = validator.validate_expression(expression)

        assert result['valid'] == True
        assert result['error_count'] == 0

    def test_unbalanced_parentheses(self):
        """Test detecting unbalanced parentheses"""
        expression = "SUM([Amount]"

        validator = DAXValidator()
        result = validator.validate_expression(expression)

        assert result['valid'] == False
        assert result['error_count'] > 0

    def test_sum_if_antipattern(self):
        """Test detecting SUM(IF()) anti-pattern"""
        expression = "SUM(IF([Status]=\"Active\",[Amount],0))"

        validator = DAXValidator()
        result = validator.validate_expression(expression)

        assert result['warning_count'] > 0
        assert any('SUM(IF' in w for w in result['warnings'])

    def test_measure_validation(self):
        """Test measure-specific validation"""
        validator = DAXValidator()
        result = validator.validate_measure("Total Revenue", "SUM([Amount])")

        assert result['measure_name'] == "Total Revenue"
        assert result['valid'] == True

    def test_empty_expression(self):
        """Test empty expression validation"""
        validator = DAXValidator()
        result = validator.validate_expression("")

        assert result['valid'] == False
        assert result['error_count'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
