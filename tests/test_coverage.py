#!/usr/bin/env python3
"""
Test Coverage Measurement Script

This script runs pytest with coverage measurement and generates reports.
It helps ensure test quality and bug prevention.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

if __name__ == "__main__":
    # Run pytest with coverage
    exit_code = pytest.main([
        "--cov=src",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-fail-under=80",  # Require at least 80% coverage
        "tests/"
    ])

    sys.exit(exit_code)
