"""
Tabular Editor Integration
Python wrapper for Tabular Editor 3 CLI operations.

Tabular Editor CLI (TabularEditor3.exe) is used to:
  - Validate TMDL model files without loading Power BI Desktop
  - Deploy models to Analysis Services / Power BI Premium XMLA endpoints
  - Run C# scripts against the model object model (BPA, transformations)
  - Extract and compare model schemas for change tracking

Installation:
  Tabular Editor 3 is available at https://tabulareditor.com/
  Free Community Edition supports all features used in this PoC.

CLI reference: https://docs.tabulareditor.com/te3/other/command-line-options.html
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional


__all__ = [
    "TabularEditorCLI",
    "validate_model",
    "deploy_model",
]


class TabularEditorCLI:
    """Wrapper for Tabular Editor 3 CLI operations."""

    def __init__(self, executable_path: str = "TabularEditor3.exe"):
        self.executable = executable_path

    def _run(self, args: List[str], timeout: int = 120) -> Dict:
        """Execute a Tabular Editor CLI command and return structured output."""
        cmd = [self.executable] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {
                "returncode": result.returncode,
                "stdout":     result.stdout,
                "stderr":     result.stderr,
                "success":    result.returncode == 0,
            }
        except FileNotFoundError:
            return {
                "returncode": -1,
                "stdout":     "",
                "stderr":     f"Tabular Editor CLI not found at: {self.executable}",
                "success":    False,
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -2,
                "stdout":     "",
                "stderr":     f"Timed out after {timeout}s",
                "success":    False,
            }

    def validate(self, model_path: str) -> Dict:
        """Validate a TMDL model folder using Tabular Editor's built-in checks.

        Catches DAX syntax errors, relationship cardinality issues, and other
        problems that the Python TMDL validator cannot detect.
        """
        result = self._run([model_path, "-V"])
        return {
            "success":    result["success"],
            "errors":     [result["stderr"]] if not result["success"] else [],
            "raw_output": result["stdout"],
        }

    def deploy(self, model_path: str, connection_string: str,
               dataset_name: str, overwrite: bool = True) -> Dict:
        """Deploy a TMDL model to an XMLA endpoint via Tabular Editor CLI."""
        args = [model_path, "-D", connection_string, dataset_name]
        if overwrite:
            args.append("-O")
        result = self._run(args, timeout=300)
        return {
            "success": result["success"],
            "message": result["stdout"] if result["success"] else result["stderr"],
        }

    def run_bpa(self, model_path: str, rules_file: Optional[str] = None) -> Dict:
        """Run Best Practice Analyser rules against the model."""
        args = [model_path, "-A"]
        if rules_file:
            args += ["-R", rules_file]
        result = self._run(args)
        return {
            "success":    result["success"],
            "violations": result["stderr"].splitlines() if not result["success"] else [],
            "summary":    result["stdout"],
        }


def validate_model(model_path: str,
                   executable: str = "TabularEditor3.exe") -> Dict:
    """Convenience: validate a TMDL model with Tabular Editor CLI."""
    return TabularEditorCLI(executable).validate(model_path)


def deploy_model(model_path: str, connection_string: str,
                 dataset_name: str,
                 executable: str = "TabularEditor3.exe") -> Dict:
    """Convenience: deploy a TMDL model via Tabular Editor CLI."""
    return TabularEditorCLI(executable).deploy(model_path, connection_string, dataset_name)
