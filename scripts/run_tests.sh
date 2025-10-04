#!/bin/bash
# Test runner that provides access to system CLI tools
# Usage: ./run_tests.sh [pytest args]

# Activate virtual environment
source .venv/bin/activate

# Add common CLI tool paths to PATH (for homebrew, system, etc.)
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:$PATH"

# Run pytest with system PATH available
if [ $# -eq 0 ]; then
    # Default: run safe tests only
    python -m pytest tests/test_simple.py tests/test_isolated.py -v
else
    # Run with provided arguments
    python -m pytest "$@"
fi
