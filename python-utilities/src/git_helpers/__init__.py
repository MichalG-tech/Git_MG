"""
Git Helpers
Utilities for interacting with the Git repository from Python scripts.

Used by deployment workflows and CI/CD scripts to:
  - Detect which TMDL files changed in a commit or PR
  - Create structured commit messages following conventional commit standard
  - Tag releases with semantic version numbers
  - Assert clean working tree before production deployments
"""

import subprocess
from typing import List, Optional


__all__ = [
    "get_changed_files",
    "get_current_branch",
    "get_current_commit_sha",
    "create_release_tag",
    "get_commits_since_tag",
    "assert_clean_working_tree",
]


def get_changed_files(base_ref: str = "HEAD~1",
                      head_ref: str = "HEAD",
                      filter_extension: str = ".tmdl") -> List[str]:
    """Return files changed between two git refs, optionally filtered by extension.

    Used by CI/CD workflows to scope validation and deployment to only
    the files that actually changed — avoiding full-repository processing.

    Args:
        base_ref: Base git ref (commit SHA, branch name, or tag).
        head_ref: Head git ref to compare against.
        filter_extension: Only return files with this extension. Pass None for all.

    Returns:
        List of relative file paths that changed.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref, head_ref],
        capture_output=True, text=True, check=True,
    )
    files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    if filter_extension:
        files = [f for f in files if f.endswith(filter_extension)]
    return files


def get_current_branch() -> str:
    """Return the name of the currently checked-out git branch."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def get_current_commit_sha(short: bool = True) -> str:
    """Return the SHA of the current HEAD commit."""
    cmd = ["git", "rev-parse"] + (["--short"] if short else []) + ["HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def create_release_tag(version: str, message: str, push: bool = False) -> None:
    """Create an annotated git tag for a release.

    Args:
        version: Semantic version string (e.g. v1.1.0).
        message: Tag annotation message.
        push: If True, pushes the tag to origin.
    """
    subprocess.run(["git", "tag", "-a", version, "-m", message], check=True)
    if push:
        subprocess.run(["git", "push", "origin", version], check=True)


def get_commits_since_tag(tag: str) -> List[str]:
    """Return conventional commit messages since the given tag.

    Used by changelog generation to identify what changed between releases.
    """
    result = subprocess.run(
        ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"],
        capture_output=True, text=True, check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def assert_clean_working_tree() -> None:
    """Raise RuntimeError if there are uncommitted changes.

    Called before production deployments to ensure the deployed version
    exactly matches the tagged commit with no accidental local modifications.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    )
    if result.stdout.strip():
        raise RuntimeError(
            f"Working tree has uncommitted changes.\n{result.stdout}"
        )
