"""
DAX Validator
Validates DAX expressions for syntax and best practices
"""

import re
from typing import Dict, List, Tuple


class DAXValidator:
    """Validates DAX expressions for syntax and best practices"""

    # Common DAX anti-patterns
    ANTI_PATTERNS = {
        r'SUM\s*\(\s*IF\s*\(': "Avoid SUM(IF(...)) - use SUMIF or CALCULATE instead",
        r'SUMPRODUCT': "SUMPRODUCT is slow - consider CALCULATE + FILTER",
        r'EVALUATE': "EVALUATE should not be in production measures",
    }

    # Best practices warnings
    BEST_PRACTICES = {
        r'[A-Z].*=.*\n': "Check measure naming convention (should be descriptive)",
    }

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_expression(self, expression: str) -> Dict:
        """
        Validate a DAX expression

        Args:
            expression: DAX expression to validate

        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []
        self.info = []

        if not expression or len(expression.strip()) == 0:
            self.errors.append("Expression is empty")
            return self._format_results(expression)

        # Run validation checks
        self._check_syntax(expression)
        self._check_anti_patterns(expression)
        self._check_best_practices(expression)

        return self._format_results(expression)

    def _check_syntax(self, expression: str) -> None:
        """Check basic DAX syntax"""

        # Check balanced parentheses
        open_parens = expression.count('(')
        close_parens = expression.count(')')
        if open_parens != close_parens:
            self.errors.append(
                f"Unbalanced parentheses: {open_parens} open, {close_parens} close"
            )

        # Check balanced quotes
        double_quotes = expression.count('"')
        if double_quotes % 2 != 0:
            self.errors.append("Unbalanced quotes")

        # Check for common keywords
        dax_keywords = ['CALCULATE', 'FILTER', 'SUM', 'AVERAGE', 'MAX', 'MIN']
        has_function = any(kw in expression.upper() for kw in dax_keywords)
        if not has_function:
            self.warnings.append("Expression has no recognized DAX functions")

        self.info.append(f"Expression length: {len(expression)} characters")

    def _check_anti_patterns(self, expression: str) -> None:
        """Check for DAX anti-patterns"""
        expression_upper = expression.upper()

        for pattern, message in self.ANTI_PATTERNS.items():
            if re.search(pattern, expression_upper, re.IGNORECASE):
                self.warnings.append(message)

    def _check_best_practices(self, expression: str) -> None:
        """Check DAX best practices"""

        # Check for BLANK() handling
        if 'IF(' in expression.upper() and 'BLANK()' not in expression.upper():
            self.warnings.append("Consider using BLANK() instead of 0 in IF statements")

        # Check for multiple nested IFs
        if expression.count('IF(') > 2:
            self.warnings.append("Consider using SWITCH() instead of nested IF()")

        # Check for use of ALL
        if 'ALL(' in expression.upper():
            self.info.append("Using ALL() - ensure this is intentional")

    def _format_results(self, expression: str) -> Dict:
        """Format validation results"""
        return {
            "expression": expression[:100] + "..." if len(expression) > 100 else expression,
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

    def validate_measure(self, name: str, expression: str) -> Dict:
        """
        Validate a complete measure definition

        Args:
            name: Measure name
            expression: Measure DAX expression

        Returns:
            Validation results
        """
        result = self.validate_expression(expression)
        result["measure_name"] = name

        # Additional measure-specific checks
        if not name or len(name.strip()) == 0:
            self.errors.append("Measure name is empty")

        if not name[0].isalpha():
            self.warnings.append("Measure name should start with a letter")

        result["errors"] = self.errors
        result["warnings"] = self.warnings
        result["error_count"] = len(self.errors)
        result["warning_count"] = len(self.warnings)

        return result


def validate_dax(expression: str) -> Dict:
    """Quick validation function"""
    validator = DAXValidator()
    return validator.validate_expression(expression)


def validate_measure(name: str, expression: str) -> Dict:
    """Validate a measure"""
    validator = DAXValidator()
    return validator.validate_measure(name, expression)


if __name__ == "__main__":
    # Example usage
    print("DAX Validator")
    print("Usage: python dax_validator.py")
