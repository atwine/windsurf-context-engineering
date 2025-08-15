#!/usr/bin/env python3
"""
Standalone Pytest Suite Runner for Windsurf Context Engineering Framework

Purpose:
- Run pytest over the `tests/` directory with the same options used by
  `test_pytest_suite()` but avoid recursive invocation by explicitly
  ignoring `tests/comprehensive_system_test.py`.

Notes:
- Pytest default discovery looks for files named `test_*.py` or `*_test.py`.
  This runner's filename intentionally avoids that pattern, so it won't be
  collected as a test when running `pytest`.
- The `--ignore` CLI option is used to exclude the comprehensive system test
  file to prevent recursion.

References:
- Pytest invocation and default discovery patterns:
  https://docs.pytest.org/en/stable/how-to/usage.html
- Pytest command-line flags reference (includes --ignore):
  https://docs.pytest.org/en/stable/reference/reference.html#command-line-flags
"""

import sys
import time
import subprocess
from pathlib import Path

# Resolve project root (one directory above this file's directory)
project_root = Path(__file__).parent.parent


def run_pytest_suite(pytest_args=None) -> int:
    """Run the pytest suite with standard options, ignoring the comprehensive system test.

    Returns the pytest exit code (0 = success).
    """
    if pytest_args is None:
        pytest_args = []

    # Mirror the original options from `test_pytest_suite()` and add `--ignore` to avoid recursion
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(project_root / "tests"),
        "-v",
        "--tb=short",
        "--maxfail=5",
        "--ignore=tests/comprehensive_system_test.py",
    ]

    # Allow callers to pass through extra pytest args (e.g., -k expr)
    if pytest_args:
        cmd.extend(pytest_args)

    print("🧪 Running pytest:", " ".join(cmd))
    start = time.time()

    # Capture output for summary, execute from project root
    result = subprocess.run(cmd, cwd=str(project_root), text=True, capture_output=True)
    duration = time.time() - start

    print(f"⏱️ Duration: {duration:.2f}s")

    # Stream captured output (stdout first, then stderr on failure)
    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print("❌ Pytest suite FAILED")
        if result.stderr:
            print(result.stderr)
    else:
        print("✅ Pytest suite PASSED")

    return result.returncode


def main():
    # Forward any additional CLI args to pytest (excluding script name)
    extra_args = sys.argv[1:]
    exit_code = run_pytest_suite(extra_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
